from pymisp import PyMISP, MISPEvent, MISPAttribute
from app.config import settings  # ← Pridėk "app."

def create_misp_event(
    title: str, 
    ips: list, 
    distribution: int = 2,
    threat_level_id: int = 2,
    analysis: int = 1):

    misp = PyMISP(
        url=settings.misp_url,      # ✅ Dabar skaito iš .env!
        key=settings.misp_api_key,  # ✅ Dabar skaito iš .env!
        ssl=False
    )

    event = MISPEvent()
    event.info = title
    event.distribution = distribution
    event.threat_level_id = threat_level_id
    event.analysis = analysis

    for ip in ips:
        event.add_attribute('ip-dst', ip)

    result = misp.add_event(event)
    return result