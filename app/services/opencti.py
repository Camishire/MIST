from app.config import settings
import requests
import re
import json
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta

def check_ip_in_opencti(ip_address: str) -> Dict[str, Any]:

    SIGHTINGS_QUERY = """{
      stixSightingRelationships(
        first: 100
        orderBy: last_seen
        orderMode: desc
        filters: {
          mode: and
          filters: [
            { key: "fromTypes", values: ["IPv4-Addr"] }
          ]
          filterGroups: []
        }
      ) {
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
            to { 
              ... on Identity { 
                name 
                entity_type
              }
            }
          }
        }
      }
    }"""
    
    try:
        response = requests.post(
            f"{settings.opencti_url}/graphql",
            json={"query": SIGHTINGS_QUERY},
            headers={
                'Authorization': f'Bearer {settings.opencti_api_key}',
                'Content-Type': 'application/json'
            },
            timeout=30,
            verify=False
        )
        response.raise_for_status()
        
        data = response.json()
        sightings = data.get("data", {}).get("stixSightingRelationships", {}).get("edges", [])
        
        ip_sightings = []
        ip_info = None
        
        for edge in sightings:
            node = edge["node"]
            from_obj = node.get("from", {})
            
            if from_obj.get("value") == ip_address:
                ip_sightings.append(node)
                if not ip_info:
                    ip_info = from_obj
        
        if not ip_sightings:
            return {
                "ipAddress": ip_address,
                "found": False,
                "message": "No data found in OpenCTI"
            }
        
        score = ip_info.get("x_opencti_score", 0)
        ip_description = ip_info.get("x_opencti_description", "")
        created_by = ip_info.get("createdBy", {}).get("name", "Unknown")
        
        first_sighting = ip_sightings[0]
        sighting_desc = first_sighting.get("description", "")
        threat_type = parse_threat(sighting_desc, ip_description)
        country = parse_country(ip_description, sighting_desc)
        
        systems = []
        for sighting in ip_sightings:
            to_obj = sighting.get("to", {})
            system_name = to_obj.get("name")
            if system_name and system_name not in systems:
                systems.append(system_name)
        
        total_sightings = sum(s.get("attribute_count", 1) for s in ip_sightings)
        
        last_seen = ip_sightings[0].get("last_seen")
        first_seen = min(
            (s.get("first_seen") for s in ip_sightings if s.get("first_seen")),
            default=None
        )
        
        return {
            "ipAddress": ip_address,
            "found": True,
            "score": score,
            "threat_type": threat_type,
            "country": country,
            "source": created_by,
            "systems": systems,
            "total_sightings": total_sightings,
            "first_seen": first_seen,
            "last_seen": last_seen,
            "description": ip_description,
            "sightings_count": len(ip_sightings)
        }
        
    except requests.RequestException as e:
        return {
            "ipAddress": ip_address,
            "error": str(e),
            "found": False
        }


def parse_threat(sighting_desc: str, ip_desc: str) -> str:
    desc = sighting_desc or ""
    
    m = re.search(r'Threat indicators?:\s*(.+)', desc)
    if m:
        indicators = m.group(1).strip()
        
        http_m = re.search(r'HTTP methods?:\s*(.+)', desc)
        if http_m:
            methods = http_m.group(1).strip()
            indicators = re.sub(r',?\s*HTTP \w+ request', '', indicators).strip().strip(',').strip()
            raw = f"HTTP {methods}" + (f" | {indicators}" if indicators else "")
        else:
            raw = indicators
        
        return normalize_threat(raw)
    
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', desc, re.DOTALL)
    if json_match:
        try:
            log_data = json.loads(json_match.group(1))
            threat = (
                log_data.get("threat", {}).get("indicator", {}).get("name")
                or log_data.get("message")
            )
            if threat:
                return normalize_threat(threat)
        except Exception:
            pass
    
    return "Unknown / Other"


def parse_country(ip_desc: str, sighting_desc: str) -> str:
    if ip_desc:
        m = re.search(r'countryCode:\s*([A-Z]{2})', ip_desc)
        if m:
            return m.group(1)
    
    # Try JSON in sighting
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', sighting_desc or "", re.DOTALL)
    if json_match:
        try:
            log_data = json.loads(json_match.group(1))
            country = log_data.get("source", {}).get("geo", {}).get("country_iso_code")
            if country:
                return country
        except Exception:
            pass
    
    return "Unknown"


def normalize_threat(threat: str) -> str:
    threat = re.sub(r'Non-standard port \(\d+\)', 'Non-standard port', threat)
    
    # Remove duplicates
    parts = [p.strip() for p in threat.split(',')]
    seen = set()
    unique_parts = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            unique_parts.append(p)
    
    threat = ', '.join(unique_parts)
    
    if threat == "AbuseIPDB score=100":
        return "Unknown / Other"
    
    return threat


def format_opencti_result_for_comment(data: Dict[str, Any]) -> str:
    if data.get("error"):
        return f"OpenCTI error: {data['error']}"
    
    if not data.get("found"):
        return "OpenCTI: No data found"
    
    lines = ["OpenCTI:"]
    
    score = data.get("score", 0)
    if score > 0:
        lines.append(f"  • Score: {score}/100")
    
    threat = data.get("threat_type")
    if threat and threat != "Unknown / Other":
        lines.append(f"  • Threat: {threat}")
    
    country = data.get("country")
    if country and country != "Unknown":
        lines.append(f"  • Country: {country}")
    
    systems = data.get("systems", [])
    if systems:
        systems_str = ", ".join(systems[:3])
        if len(systems) > 3:
            systems_str += f" +{len(systems)-3} more"
        lines.append(f"  • Detected by: {systems_str}")
    
    total = data.get("total_sightings", 0)
    if total > 0:
        lines.append(f"  • Sightings: {total}")
    
    last_seen = data.get("last_seen")
    if last_seen:
        try:
            dt = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
            lines.append(f"  • Last seen: {dt.strftime('%Y-%m-%d')}")
        except:
            pass
    
    return "\n".join(lines) if len(lines) > 1 else "OpenCTI: No threat data"