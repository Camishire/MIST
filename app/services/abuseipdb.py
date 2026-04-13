from app.config import settings
import requests

def check_ip_abuse(ip_address):
    url = f"https://api.abuseipdb.com/api/v2/check"
    params = {
        'ipAddress': ip_address,
        'maxAgeInDays': 90
    }
    headers = {
        'Key': settings.abuseipdb_api_key,
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        abuse_data = data.get('data', {})
        
        return {
            "ipAddress": ip_address,
            "abuseConfidenceScore": abuse_data.get('abuseConfidenceScore', 0),
            "countryCode": abuse_data.get('countryCode', 'N/A'),
            "domain": abuse_data.get('domain', 'N/A'),
            "totalReports": abuse_data.get('totalReports', 0),
            "isWhitelisted": abuse_data.get('isWhitelisted', False),
            "usageType": abuse_data.get('usageType', 'N/A')
        }
    except requests.RequestException as e:
        return {
            "ipAddress": ip_address,
            "error": str(e),
            "abuseConfidenceScore": 0,
            "totalReports": 0
        }
    

def check_ip_abuse_bulk(ip_addresses):
    print(ip_addresses)
    results = []
    for ip in ip_addresses:
        result = check_ip_abuse(ip)
        print(result)
        results.append(result)
    return results