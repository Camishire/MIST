from enum import Enum

# ============================================
# TAGS (paprastieji)
# ============================================

class TLPTags(str, Enum):
    CLEAR = "tlp:clear"
    GREEN = "tlp:green"
    AMBER = "tlp:amber"
    AMBER_STRICT = "tlp:amber+strict"
    RED = "tlp:red"

class ThreatLevelTags(str, Enum):
    HIGH = 'cert-ist:threat_level="high"'
    MEDIUM = 'cert-ist:threat_level="medium"'
    LOW = 'cert-ist:threat_level="low"'

class MalwareActionTags(str, Enum):
    BACKDOOR = 'veris:action:malware:variety="Backdoor"'
    C2 = 'veris:action:malware:variety="C2"'
    RANSOMWARE = 'veris:action:malware:variety="Ransomware"'

class HackingActionTags(str, Enum):
    BRUTE_FORCE = 'veris:action:hacking:variety="Brute force"'
    SQLI = 'veris:action:hacking:variety="SQLi"'
    BACKDOOR_USE = 'veris:action:hacking:variety="Use of backdoor or C2"'

class SocialActionTags(str, Enum):
    PHISHING = 'veris:action:social:variety="Phishing"'

# ============================================
# GALAXIES (sudėtingesni)
# ============================================

class CountryGalaxies(str, Enum):
    LITHUANIA = 'misp-galaxy:country="lithuania"'
    TARGET_LITHUANIA = 'misp-galaxy:target-information="Lithuania"'

class SectorGalaxies(str, Enum):
    HIGHER_EDUCATION = 'misp-galaxy:sector="Higher education"'

class MITREAttackPatterns(str, Enum):
    BRUTE_FORCE = 'misp-galaxy:mitre-attack-pattern="Brute Force - T1110"'
    EXPLOIT_PUBLIC_APP = 'misp-galaxy:mitre-attack-pattern="Exploit Public-Facing Application - T1190"'
    PORT_SCAN = 'misp-galaxy:mitre-attack-pattern="Network Service Discovery - T1046"'
    ACTIVE_SCANNING = 'misp-galaxy:mitre-attack-pattern="Active Scanning - T1595"'
    DDOS = 'misp-galaxy:mitre-attack-pattern="Network Denial of Service - T1498"'
    PHISHING = 'misp-galaxy:mitre-attack-pattern="Phishing - T1566"'
    VALID_ACCOUNTS = 'misp-galaxy:mitre-attack-pattern="Valid Accounts - T1078"'

# ============================================
# Helper funkcijos
# ============================================

def get_all_tags():
    """Gauti visus tag'us kaip dictionary pagal kategorijas"""
    return {
        "tlp": [tag.value for tag in TLPTags],
        "threat_level": [tag.value for tag in ThreatLevelTags],
        "malware_action": [tag.value for tag in MalwareActionTags],
        "hacking_action": [tag.value for tag in HackingActionTags],
        "social_action": [tag.value for tag in SocialActionTags]
    }

def get_all_galaxies():
    """Gauti visas galaxies kaip dictionary pagal kategorijas"""
    return {
        "country": [g.value for g in CountryGalaxies],
        "sector": [g.value for g in SectorGalaxies],
        "mitre_attack": [g.value for g in MITREAttackPatterns]
    }