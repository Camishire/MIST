from pymisp import PyMISP, MISPEvent, MISPAttribute
from app.config import settings
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MISPService:
    def __init__(self):
        self.misp = PyMISP(
            url=settings.misp_url,
            key=settings.misp_api_key,
            ssl=False  # Self-signed cert
        )
    
    def create_event(self, title: str, info: str = "") -> Dict[str, Any]:
        """Sukurti naują MISP event"""
        try:
            # Sukuriame MISPEvent objektą
            event = MISPEvent()
            event.info = info or title
            event.distribution = 2  # Connected communities
            event.threat_level_id = 2  # Medium
            event.analysis = 1  # Ongoing
            
            # Siunčiame į MISP
            result = self.misp.add_event(event)
            
            if 'errors' in result:
                raise Exception(f"MISP error: {result['errors']}")
            
            logger.info(f"Created MISP event: {result['Event']['id']}")
            return result['Event']
        except Exception as e:
            logger.error(f"Failed to create MISP event: {e}")
            raise
    
    def add_attribute(
        self, 
        event_id: str, 
        attr_type: str, 
        value: str,
        comment: str = ""
    ) -> Dict[str, Any]:
        """Pridėti attribute į event"""
        try:
            attribute = self.misp.add_attribute(
                event_id,
                {
                    'type': attr_type,
                    'value': value,
                    'comment': comment,
                    'to_ids': True,
                    'category': 'Network activity'
                }
            )
            
            if 'errors' in attribute:
                raise Exception(f"MISP error: {attribute['errors']}")
            
            logger.info(f"Added attribute to event {event_id}: {attr_type}={value}")
            return attribute['Attribute']
        except Exception as e:
            logger.error(f"Failed to add attribute: {e}")
            raise
    
    def add_tag(self, event_id: str, tag_name: str) -> bool:
        """Pridėti tag į event"""
        try:
            result = self.misp.tag(event_id, tag_name)
            logger.info(f"Added tag to event {event_id}: {tag_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add tag: {e}")
            # Ne kritinė klaida - tag gali neegzistuoti
            return False
    
    def get_event(self, event_id: str) -> Dict[str, Any]:
        """Gauti event pagal ID"""
        try:
            event = self.misp.get_event(event_id)
            if 'errors' in event:
                raise Exception(f"MISP error: {event['errors']}")
            return event['Event']
        except Exception as e:
            logger.error(f"Failed to get event: {e}")
            raise

# Singleton instance
misp_service = MISPService()