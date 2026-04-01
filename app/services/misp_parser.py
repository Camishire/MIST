import re
from app.constants import AttributeCategories, get_types_for_category

def parse_bulk_upload(data: list[str]) -> dict:
    parsed_attributes = []
    
    for item in data:
        item = item.strip()
        if not item:
            continue
        
        attribute = detect_attribute_type(item)
        
        if attribute:
            parsed_attributes.append(attribute)
    
    return {
        "message": "Bulk upload processed",
        "count": len(parsed_attributes),
        "attributes": parsed_attributes
    }


def detect_attribute_type(value: str) -> dict:
    # EMAIL pattern
    if re.search(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
        return {
            "category": AttributeCategories.PAYLOAD_DELIVERY.value,
            "type": "email-src",
            "value": value
        }
    
    if re.search(r'^(\d{1,3}\.){3}\d{1,3}$', value):
        parts = value.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            return {
                "category": AttributeCategories.NETWORK_ACTIVITY.value,
                "type": "ip-dst",
                "value": value
            }
    
    if re.search(r'^https?://', value, re.IGNORECASE):
        return {
            "category": AttributeCategories.NETWORK_ACTIVITY.value,
            "type": "url",
            "value": value
        }
    
    if re.search(r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$', value):
        return {
            "category": AttributeCategories.NETWORK_ACTIVITY.value,
            "type": "domain",
            "value": value
        }
    
    
    # Default: jei nepažįstame - komentaras
    return {
        "category": AttributeCategories.OTHER.value,
        "type": "comment",
        "value": value
    }