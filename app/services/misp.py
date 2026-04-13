from pymisp import PyMISP, MISPEvent, MISPAttribute
from app.config import settings

def create_misp_event(
    creator_key: str,
    date: str,
    distribution: int,
    threat_level_id: int,
    analysis: int,
    info: str,
    tags: list[str],
    galaxies: list[str],
    attributes: list[dict]
) -> dict:

    misp = PyMISP(
        url=settings.misp_url,
        key=creator_key,
        ssl=False
    )
    
    event = MISPEvent()
    event.info = info
    event.distribution = distribution
    event.threat_level_id = threat_level_id
    event.analysis = analysis
    event.date = date
    
    for tag in tags:
        event.add_tag(tag)
    
    for galaxy in galaxies:
        event.add_tag(galaxy)
    
    for attr in attributes:
        event.add_attribute(
            type=attr['type'],
            value=attr['value'],
            category=attr.get('category', 'Network activity'),
            comment=attr.get('comment', ''),
            to_ids=attr.get('to_ids', False)
        )
    
    try:
        result = misp.add_event(event)
        return result
    except Exception as e:
        raise Exception(f"Failed to create MISP event: {str(e)}")


# Backwards compatibility
def create_misp_event_simple(
    title: str, 
    ips: list, 
    distribution: int = 2,
    threat_level_id: int = 2,
    analysis: int = 1
):
    
    misp = PyMISP(
        url=settings.misp_url,
        key=settings.misp_api_key,
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