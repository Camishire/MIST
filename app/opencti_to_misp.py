import argparse
import json
import logging
import re
import sys
import urllib3
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Konfigūracija
# ---------------------------------------------------------------------------
OPENCTI_URL   = "https://kranklys.vilniustech.lt/graphql"
OPENCTI_TOKEN = "0f19c21f-719b-4fe4-a25c-696b72684d9c"

MISP_URL        = "https://ziurke.vilniustech.lt"
MISP_KEY        = "YlrUoXhopmSqX2ttl4i2K7ghkjHcDAC935aWRNUp"
MISP_VERIFYCERT = False

MISP_DISTRIBUTION   = 2      # Connected communities
MISP_THREAT_LEVEL   = 2      # Medium
MISP_ANALYSIS       = 1      # Ongoing

MIN_IPS_PER_EVENT = 50

# Tag'ai pridedami prie VISŲ event'ų
COMMON_TAGS = [
    'misp-galaxy:country="lithuania"',
    'misp-galaxy:target-information="Lithuania"',
    'misp-galaxy:sector="Higher education"',
]

# State failas — atsimenama paskutinio paleidimo data
MISP_STATE_FILE = Path(__file__).parent / "state_misp.json"


def load_misp_state() -> dict:
    if MISP_STATE_FILE.exists():
        try:
            return json.loads(MISP_STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_misp_state(state: dict):
    MISP_STATE_FILE.write_text(json.dumps(state, indent=2))

# Šios grupės NIEKADA nekels į MISP
EXCLUDE_THREAT_TYPES = [
    "EsetIpBlacklist.A",
    "EsetIpBlacklist.B",
    "Unknown / Other",
]

# ---------------------------------------------------------------------------
# Threat tipo → tags mapingas
# ---------------------------------------------------------------------------
THREAT_TAGS = {
    # Brute force
    "brute force": [
        "tlp:amber",
        'misp-galaxy:mitre-attack-pattern="Brute Force - T1110"',
        'cert-ist:threat_level="high"',
        'attack-pattern:name="password brute forcing"',
    ],
    # Failed connection / port scan
    "failed connection": [
        "tlp:amber",
        'misp-galaxy:mitre-attack-pattern="Network Service Discovery - T1046"',
        'cert-ist:threat_level="medium"',
        'attack-pattern:name="port scanning"',
    ],
    "non-standard port": [
        "tlp:amber",
        'misp-galaxy:mitre-attack-pattern="Network Service Discovery - T1046"',
        'cert-ist:threat_level="medium"',
        'attack-pattern:name="port scanning"',
    ],
    # HTTP exploits
    "http get": [
        "tlp:amber",
        'misp-galaxy:mitre-attack-pattern="Exploit Public-Facing Application - T1190"',
        'cert-ist:threat_level="medium"',
        'cert-ist:attack_vector="Vulnerability Exploitation"',
    ],
    "http post": [
        "tlp:amber",
        'misp-galaxy:mitre-attack-pattern="Exploit Public-Facing Application - T1190"',
        'cert-ist:threat_level="high"',
        'cert-ist:attack_vector="Vulnerability Exploitation"',
    ],
    "exploit": [
        "tlp:amber",
        'misp-galaxy:mitre-attack-pattern="Exploit Public-Facing Application - T1190"',
        'cert-ist:threat_level="high"',
        'cert-ist:attack_vector="Vulnerability Exploitation"',
    ],
    "cve": [
        "tlp:amber",
        'misp-galaxy:mitre-attack-pattern="Exploit Public-Facing Application - T1190"',
        'cert-ist:threat_level="high"',
        'cert-ist:attack_vector="Vulnerability Exploitation"',
    ],
    # Scanning
    "port scan": [
        "tlp:amber",
        'misp-galaxy:mitre-attack-pattern="Network Service Discovery - T1046"',
        'cert-ist:threat_level="low"',
        'attack-pattern:name="port scanning"',
    ],
    "reconnaissance": [
        "tlp:amber",
        'misp-galaxy:mitre-attack-pattern="Active Scanning - T1595"',
        'cert-ist:threat_level="low"',
    ],
    # DDoS
    "ddos": [
        "tlp:amber",
        'misp-galaxy:mitre-attack-pattern="Network Denial of Service - T1498"',
        'cert-ist:threat_level="high"',
    ],
    # Default
    "default": [
        "tlp:amber",
        'cert-ist:threat_level="medium"',
    ],
}


def get_tags_for_threat(threat_type: str) -> list[str]:
    """
    Grąžina tag'us pagal threat tipą.
    Tikrinama pagal prioritetą — specifiškesni pirma.
    """
    threat_lower = threat_type.lower()

    # Pirma tikriname specifiškus (kad "http get" nebūtų sugautas "failed connection")
    priority_order = [
        "cve", "exploit",
        "http post", "http get",
        "ddos",
        "brute force",
        "reconnaissance", "port scan",
        "non-standard port", "failed connection",
    ]

    for key in priority_order:
        if key in threat_lower:
            return THREAT_TAGS.get(key, THREAT_TAGS["default"])

    return THREAT_TAGS["default"]


# ---------------------------------------------------------------------------
# OpenCTI GraphQL
# ---------------------------------------------------------------------------
SIGHTINGS_QUERY = """{
  stixSightingRelationships(
    first: %(page_size)s
    %(after_clause)s
    orderBy: created_at
    orderMode: desc
    filters: {
      mode: and
      filters: [
        { key: "fromTypes", values: ["IPv4-Addr"] }
        { key: "last_seen", values: ["%(since)s"], operator: gte }
      ]
      filterGroups: []
    }
  ) {
    pageInfo { hasNextPage endCursor globalCount }
    edges {
      node {
        id
        attribute_count
        first_seen
        last_seen
        description
        from {
          ... on IPv4Addr {
            value
            x_opencti_score
            x_opencti_description
            createdBy { name }
          }
        }
        to { ... on Identity { name } }
      }
    }
  }
}"""


def _gql(query: str) -> dict:
    r = requests.post(
        OPENCTI_URL,
        json={"query": query},
        headers={"Authorization": f"Bearer {OPENCTI_TOKEN}", "Content-Type": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def _since_iso(days_back: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_back)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _fmt_date(iso: str) -> str:
    if not iso:
        return "—"
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "—"


def _normalize_threat(threat: str) -> str:
    """
    Normalizuoja threat tipą grupavimui:
    - Pašalina konkrečius portų numerius: "Non-standard port (12345)" → "Non-standard port"
    - "AbuseIPDB score=100" → "Unknown / Other"
    """
    # Pašalinam konkretų porto numerį
    threat = re.sub(r'Non-standard port \(\d+\)', 'Non-standard port', threat)
    # Pašalinam kartojančius Non-standard port (jei keletas)
    parts = [p.strip() for p in threat.split(',')]
    seen  = set()
    unique_parts = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            unique_parts.append(p)
    threat = ', '.join(unique_parts)
    # Fallback pavadinimas
    if threat == "AbuseIPDB score=100":
        return "Unknown / Other"
    return threat


def parse_threat(sighting_desc: str, ip_desc: str) -> str:
    desc = sighting_desc or ""
    m = re.search(r'Threat indicators?:\s*(.+)', desc)
    if m:
        indicators = m.group(1).strip()
        http_m = re.search(r'HTTP methods?:\s*(.+)', desc)
        if http_m:
            methods    = http_m.group(1).strip()
            indicators = re.sub(r',?\s*HTTP \w+ request', '', indicators).strip().strip(',').strip()
            raw = f"HTTP {methods}" + (f" | {indicators}" if indicators else "")
        else:
            raw = indicators
        return _normalize_threat(raw)
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', desc, re.DOTALL)
    if json_match:
        try:
            log_data = json.loads(json_match.group(1))
            threat = (
                log_data.get("threat", {}).get("indicator", {}).get("name")
                or log_data.get("message")
            )
            if threat:
                return _normalize_threat(threat)
        except Exception:
            pass
    return "Unknown / Other"


def parse_country(ip_desc: str, sighting_desc: str) -> str:
    if ip_desc:
        m = re.search(r'countryCode:\s*([A-Z]{2})', ip_desc)
        if m:
            return m.group(1)
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', sighting_desc or "", re.DOTALL)
    if json_match:
        try:
            log_data = json.loads(json_match.group(1))
            country = log_data.get("source", {}).get("geo", {}).get("country_iso_code")
            if country:
                return country
        except Exception:
            pass
    return "??"


def fetch_ips_from_opencti_since(since_dt: datetime, min_score: int = 100) -> list[dict]:
    """Traukia IP nuo konkretaus datetime."""
    since = since_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    return _fetch_ips(since, label=f"nuo {since_dt.strftime('%Y-%m-%d %H:%M UTC')}", min_score=min_score)


def fetch_ips_from_opencti(days_back: int, min_score: int = 100) -> list[dict]:
    since = _since_iso(days_back)
    return _fetch_ips(since, label=f"paskutinės {days_back} d.", min_score=min_score)


def _fetch_ips(since: str, label: str, min_score: int = 100) -> list[dict]:
    page_size = 200
    log.info(f"OpenCTI: traukiami IP nuo {since} ({label})")

    results  = []
    seen_ips = set()
    cursor   = None
    page     = 1

    while True:
        after_clause = f'after: "{cursor}"' if cursor else ""
        query = SIGHTINGS_QUERY % {
            "page_size":    page_size,
            "after_clause": after_clause,
            "since":        since,
        }

        data      = _gql(query)
        sightings = data["data"]["stixSightingRelationships"]
        edges     = sightings["edges"]
        page_info = sightings["pageInfo"]

        if page == 1:
            log.info(f"  Iš viso sightings: {page_info.get('globalCount', '?')}")

        for edge in edges:
            node     = edge["node"]
            from_obj = node.get("from") or {}
            to_obj   = node.get("to")   or {}

            ip_val = from_obj.get("value")
            if not ip_val or ip_val in seen_ips:
                continue

            score      = from_obj.get("x_opencti_score", 0)
            created_by = (from_obj.get("createdBy") or {}).get("name", "")

            if score < min_score:
                continue

            seen_ips.add(ip_val)

            sighting_desc = node.get("description") or ""
            ip_desc       = from_obj.get("x_opencti_description") or ""

            results.append({
                "ip":         ip_val,
                "threat":     parse_threat(sighting_desc, ip_desc),
                "country":    parse_country(ip_desc, sighting_desc),
                "system":     to_obj.get("name", ""),
                "score":      score,
                "nb":         node.get("attribute_count", 1),
                "first_seen": node.get("first_seen"),
                "last_seen":  node.get("last_seen"),
                "ip_desc":    ip_desc,
            })

        log.info(f"  Puslapis {page}: iš viso {len(results)} IP")

        if not page_info["hasNextPage"]:
            break
        cursor = page_info["endCursor"]
        page  += 1

    return results


# ---------------------------------------------------------------------------
# MISP event kūrimas
# ---------------------------------------------------------------------------
def create_misp_event(misp, threat_type: str, ip_list: list[dict], dry_run: bool, date_str: str) -> bool:
    from pymisp import MISPEvent

    event_title = f"[AbuseIPDB] {threat_type} | {date_str} | {len(ip_list)} IPs"

    # Šalių statistika
    country_counts = defaultdict(int)
    for item in ip_list:
        if item["country"] != "??":
            country_counts[item["country"]] += 1
    top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    countries_str = ", ".join(f"{c} ({n})" for c, n in top_countries)

    # Sistemų sąrašas
    systems     = list(set(item["system"] for item in ip_list if item["system"]))
    systems_str = ", ".join(systems)

    event_desc = (
        f"Automatically generated from OpenCTI.\n"
        f"Source: AbuseIPDB (confidence score = 100)\n"
        f"Threat type: {threat_type}\n"
        f"Total IPs: {len(ip_list)}\n"
        f"Detected by: {systems_str}\n"
        f"Top countries: {countries_str}\n"
        f"Date: {date_str}"
    )

    tags = get_tags_for_threat(threat_type)

    if dry_run:
        log.info(f"[DRY-RUN] Event: '{event_title}'")
        log.info(f"  IP kiekis: {len(ip_list)}")
        log.info(f"  Tags: {tags}")
        log.info(f"  Top šalys: {countries_str}")
        log.info(f"  Pirmi 5 IP:")
        for item in ip_list[:5]:
            log.info(f"    - {item['ip']} ({item['country']}) | {item['system']} | NB: {item['nb']}")
        if len(ip_list) > 5:
            log.info(f"    ... ir dar {len(ip_list) - 5} IP")
        return True

    # Sukuriame event'ą
    event = MISPEvent()
    event.info            = event_title
    event.distribution    = MISP_DISTRIBUTION
    event.threat_level_id = MISP_THREAT_LEVEL
    event.analysis        = MISP_ANALYSIS

    result = misp.add_event(event)

    if "errors" in result or "Event" not in result:
        log.error(f"Event kūrimo klaida: {result}")
        return False

    event_id   = result["Event"]["id"]
    event_uuid = result["Event"]["uuid"]
    log.info(f"Event sukurtas: ID={event_id} | '{event_title}'")

    # Description kaip comment atributas
    misp.add_attribute(event_id, {
        "type":     "comment",
        "value":    event_desc,
        "comment":  "Auto-generated event description",
        "category": "Other",
        "to_ids":   False,
    })

    # IP atributai su komentarais
    added = 0
    for item in ip_list:
        comment_parts = [
            f"Country: {item['country']}",
            f"Detected by: {item['system']}",
            f"Sightings: {item['nb']}",
            f"First seen: {_fmt_date(item['first_seen'])}",
            f"Last seen: {_fmt_date(item['last_seen'])}",
        ]

        r = misp.add_attribute(event_id, {
            "type":     "ip-src",
            "value":    item["ip"],
            "comment":  " | ".join(comment_parts),
            "to_ids":   True,
            "category": "Network activity",
        })
        if "errors" not in r and "Attribute" in r:
            added += 1
        else:
            log.warning(f"  Atributo klaida ({item['ip']}): {r}")

    log.info(f"  Pridėta {added}/{len(ip_list)} IP atributų")

    # Tag'ai (threat-specific + bendri)
    all_tags = tags + COMMON_TAGS
    tags_ok = 0
    for tag in all_tags:
        try:
            r = misp.tag(event_uuid, tag)
            if isinstance(r, dict) and r.get("saved"):
                tags_ok += 1
            else:
                log.warning(f"  Tag '{tag}' nepridėtas: {r}")
        except Exception as e:
            log.warning(f"  Tag '{tag}' klaida: {e}")

    log.info(f"  Tag'ai: {tags_ok}/{len(all_tags)} pridėta")
    log.info(f"  ✓ Event NEPUBLIKUOTAS — reikia rankinio publish")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="OpenCTI → MISP IP exporter")
    p.add_argument("--dry-run", action="store_true", help="Nerodo realaus kėlimo")
    p.add_argument("--days",      type=int, default=None, help="Kiek dienų atgal (neigkite state'ą)")
    p.add_argument("--min-ips",   type=int, default=MIN_IPS_PER_EVENT, help=f"Min IP kiekis event'ui (default: {MIN_IPS_PER_EVENT})")
    p.add_argument("--min-score", type=int, default=100, help="Min score filtras (default: 100)")
    p.add_argument("--reset",     action="store_true", help="Ištrinti state'ą ir pradėti iš naujo")
    return p.parse_args()


def main():
    args = parse_args()

    # State valdymas
    state = load_misp_state()

    if args.reset:
        save_misp_state({})
        log.info("State ištryntas.")
        state = {}

    if args.days is not None:
        # Explicit --days nurodytas — naudojame jį
        days_back = args.days
        since_dt  = None
        log.info(f"Režimas: --days {days_back} (ignoruojamas state)")
    elif state.get("last_run"):
        # Naudojame state
        since_dt = datetime.fromisoformat(state["last_run"])
        days_back = None
        log.info(f"Režimas: nuo paskutinio paleidimo {since_dt.strftime('%Y-%m-%d %H:%M UTC')}")
    else:
        # Pirmas paleidimas — default 1 diena
        days_back = 1
        since_dt  = None
        log.info("Režimas: pirmas paleidimas — paskutinė 1 diena")

    # Fiksuojame laiką PRIEŠ traukiant (kad nesimestų sightings tarp traukimo ir pabaigos)
    run_start = datetime.now(timezone.utc)

    if since_dt:
        ip_data = fetch_ips_from_opencti_since(since_dt, min_score=args.min_score)
    else:
        ip_data = fetch_ips_from_opencti(days_back, min_score=args.min_score)
    log.info(f"Gauta iš viso: {len(ip_data)} IP (score>={args.min_score})")

    if not ip_data:
        log.info("Nėra IP — baigta.")
        return

    by_threat = defaultdict(list)
    for item in ip_data:
        by_threat[item["threat"]].append(item)

    log.info(f"\nGrupės (min {args.min_ips} IP):")
    for threat, items in sorted(by_threat.items()):
        if threat in EXCLUDE_THREAT_TYPES:
            status = "✗ (exclude sąraše)"
        elif len(items) >= args.min_ips:
            status = "✓"
        else:
            status = f"✗ (per mažai, reikia >={args.min_ips})"
        log.info(f"  '{threat}': {len(items)} IP {status}")

    filtered = {
        t: ips for t, ips in by_threat.items()
        if len(ips) >= args.min_ips and t not in EXCLUDE_THREAT_TYPES
    }
    skipped  = len(by_threat) - len(filtered)

    log.info(f"\nKuriama: {len(filtered)} event'ų (praleista: {skipped} grupių)")

    if not filtered:
        log.info("Nėra grupių su pakankamai IP — baigta.")
        return

    if args.dry_run:
        log.info("=== DRY-RUN REŽIMAS ===")

    if not args.dry_run:
        from pymisp import PyMISP
        misp = PyMISP(MISP_URL, MISP_KEY, MISP_VERIFYCERT)
        log.info("MISP prisijungta ✓")
    else:
        misp = None

    date_str = datetime.now().strftime("%Y-%m-%d")
    created  = 0

    for threat_type, items in sorted(filtered.items()):
        log.info(f"\nKuriamas event'as: '{threat_type}' — {len(items)} IP")
        if create_misp_event(misp, threat_type, items, args.dry_run, date_str):
            created += 1

    log.info(f"\n✓ Baigta: {created}/{len(filtered)} event'ų sukurta")
    if skipped > 0:
        log.info(f"  Praleista {skipped} grupių (< {args.min_ips} IP)")

    # Išsaugome state (net jei dry-run — kad nesikartoų duomenys)
    if not args.dry_run:
        save_misp_state({"last_run": run_start.isoformat()})
        log.info(f"  State išsaugotas: {run_start.strftime('%Y-%m-%d %H:%M UTC')}")
    else:
        log.info(f"  [DRY-RUN] State NEIŠSAUGOTAS (paleidimo laikas būtų: {run_start.strftime('%Y-%m-%d %H:%M UTC')})")


if __name__ == "__main__":
    main()