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
        AbuseConfidenceScore = data.get('data', {}).get('abuseConfidenceScore', 0)
        CountryCode = data.get('data', {}).get('countryCode', 'N/A')
        Domain = data.get('data', {}).get('domain', 'N/A')
        response = {
            "ipAddress": ip_address,
            "abuseConfidenceScore": AbuseConfidenceScore,
            "countryCode": CountryCode,
            "domain": Domain
        }
        return response
    except requests.RequestException as e:
        raise Exception(f"Error checking IP abuse: {str(e)}")
    

def check_ip_abuse_bulk(ip_addresses):
    print(ip_addresses)
    results = []
    for ip in ip_addresses:
        try:
            result = check_ip_abuse(ip)
            print(result)
            results.append(result)
        except Exception as e:
            results.append({
                "ipAddress": ip,
                "error": str(e)
            })
    return results