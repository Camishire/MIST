from enum import Enum
from app.config import settings

# ============================================
# TAGS (paprastieji)
# ============================================

class TLPTags(Enum):
    CLEAR = ("tlp:clear", "You can share this with anyone, without restriction.")
    GREEN = ("tlp:green", "You can share this with members of your organization only.")
    AMBER = ("tlp:amber", "You can share this with members of your organization and other organizations you trust.")
    AMBER_STRICT = ("tlp:amber+strict", "You can share this with members of your organization and other organizations you trust, but not outside of your organization.")
    RED = ("tlp:red", "You can share this with members of your organization only.")

class ThreatLevelTags(Enum):
    HIGH = ('cert-ist:threat_level="high"', 'High severity threat that requires immediate attention.')
    MEDIUM = ('cert-ist:threat_level="medium"', 'Medium severity threat that requires monitoring.')
    LOW = ('cert-ist:threat_level="low"', 'Low severity threat that requires minimal attention.')

class MalwareActionTags(Enum):
    BACKDOOR = ('veris:action:malware:variety="Backdoor"', 'A type of malware that allows unauthorized access to a computer or network.')
    C2 = ('veris:action:malware:variety="C2"', 'A type of malware that communicates with a command and control server.')
    RANSOMWARE = ('veris:action:malware:variety="Ransomware"', 'A type of malware that encrypts files and demands payment for decryption.')

class HackingActionTags(Enum):
    BRUTE_FORCE = ('veris:action:hacking:variety="Brute force"', 'A type of hacking that involves trying many possible passwords or keys to gain access.')
    SQLI = ('veris:action:hacking:variety="SQLi"', 'A type of hacking that exploits vulnerabilities in SQL databases.')
    BACKDOOR_USE = ('veris:action:hacking:variety="Use of backdoor or C2"', 'A type of hacking that involves using a backdoor or command and control server.')

class SocialActionTags(Enum):
    PHISHING = ('veris:action:social:variety="Phishing"', 'A type of social engineering that involves tricking individuals into providing sensitive information.')

# ============================================
# GALAXIES (sudėtingesni)
# ============================================

class CountryGalaxies(Enum):
    LITHUANIA = ('misp-galaxy:country="lithuania"', "Tag for Origin country.")
    TARGET_LITHUANIA = ('misp-galaxy:target-information="Lithuania"', "Tag for Target country.")

class SectorGalaxies(Enum):
    HIGHER_EDUCATION = ('misp-galaxy:sector="Higher education"', "Higher education sector tag.")

class MITREAttackPatterns(Enum):
    BRUTE_FORCE = ('misp-galaxy:mitre-attack-pattern="Brute Force - T1110"', 'A type of attack that involves trying many possible passwords or keys to gain access.')
    EXPLOIT_PUBLIC_APP = ('misp-galaxy:mitre-attack-pattern="Exploit Public-Facing Application - T1190"', 'A type of attack that exploits vulnerabilities in public-facing applications.')
    PORT_SCAN = ('misp-galaxy:mitre-attack-pattern="Network Service Discovery - T1046"', 'A type of attack that involves discovering network services.')
    ACTIVE_SCANNING = ('misp-galaxy:mitre-attack-pattern="Active Scanning - T1595"', 'A type of attack that involves actively scanning the network for information.')
    DDOS = ('misp-galaxy:mitre-attack-pattern="Network Denial of Service - T1498"', 'A type of attack that aims to make a network service unavailable.')
    PHISHING = ('misp-galaxy:mitre-attack-pattern="Phishing - T1566"', 'A type of attack that involves tricking individuals into providing sensitive information.')
    VALID_ACCOUNTS = ('misp-galaxy:mitre-attack-pattern="Valid Accounts - T1078"', 'A type of attack that involves using valid user credentials.')

# ============================================
# ATTRIBUTE CATEGORIES
# ============================================

class AttributeCategories(str, Enum):
    PAYLOAD_DELIVERY = 'Payload delivery'
    NETWORK_ACTIVITY = 'Network activity'
    OTHER = 'Other'

# ============================================
# CATEGORY TYPES
# ============================================

CATEGORY_TYPES = {
    AttributeCategories.PAYLOAD_DELIVERY: [
        'comment',
        'ip-src',
        'email-src',
        'email-dst',
        'url',
        'campaign-name',
        'domain'
    ],
    AttributeCategories.NETWORK_ACTIVITY: [
        'ip-src',
        'ip-dst',
        'comment',
        'domain',
        'url'
    ],
    AttributeCategories.OTHER: [
        'comment',
        'text'
    ]
}

DISTRIBUTION_OPTIONS = {
    0: "Your organisation only",
    1: "This community only",
    2: "Connected communities",
    3: "All communities",
    4: "Sharing group",
}

THREAT_LEVEL_OPTIONS = {
    1: "High",
    2: "Medium",
    3: "Low",
    4: "Undefined"
}

ANALYSIS_OPTIONS = {
    0: "Initial",
    1: "Ongoing",
    2: "Completed",
}

CREATOR_APIS ={
    settings.misp_aurelija_api_key: "Aurelija",
    settings.misp_evija_api_key: "Evija",
    settings.misp_kamile_api_key: "Kamile",
    settings.misp_viktorija_api_key: "Viktorija"
}


# ============================================
# Helper funkcijos
# ============================================

def get_distribution_options():
    return DISTRIBUTION_OPTIONS

def get_threat_level_options():
    return THREAT_LEVEL_OPTIONS

def get_analysis_options():
    return ANALYSIS_OPTIONS

def get_all_tags():
    return {
        "tlp": [tag.value for tag in TLPTags],
        "threat_level": [tag.value for tag in ThreatLevelTags],
        "malware_action": [tag.value for tag in MalwareActionTags],
        "hacking_action": [tag.value for tag in HackingActionTags],
        "social_action": [tag.value for tag in SocialActionTags]
    }

def get_all_galaxies():
    return {
        "country": [g.value for g in CountryGalaxies],
        "sector": [g.value for g in SectorGalaxies],
        "mitre_attack": [g.value for g in MITREAttackPatterns]
    }

def get_all_categories():
    return [category.value for category in AttributeCategories]

def get_types_for_category(category: str):
    for cat_enum in AttributeCategories:
        if cat_enum.value == category:
            return CATEGORY_TYPES.get(cat_enum, CATEGORY_TYPES[AttributeCategories.OTHER])
    
    return CATEGORY_TYPES[AttributeCategories.OTHER]

def get_creator_options():
    return CREATOR_APIS