import requests
import time

def get_distance(postnummer_from, postnummer_to):
    """
    Hämtar bilvägsavstånd via OpenStreetMap Nominatim + OSRM
    """
    
    # Steg 1: Geocoda postnummer
    def geocode(postnummer):
        url = f"https://nominatim.openstreetmap.org/search?postalcode={postnummer}&country=Sweden&format=json"
        headers = {'User-Agent': 'ESG App/1.0'}
        
        try:
            response = requests.get(url, headers=headers)
            time.sleep(1)  # Rate limiting
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return float(data[0]['lat']), float(data[0]['lon'])
        except:
            pass
        return None
    
    coords_from = geocode(postnummer_from)
    coords_to = geocode(postnummer_to)
    
    if not coords_from or not coords_to:
        # Fallback: Fågelväg × 1.3
        import math
        R = 6371  # Jordens radie i km
        
        lat1, lon1 = coords_from if coords_from else (58.4, 15.6)  # Linköping default
        lat2, lon2 = coords_to if coords_to else (58.6, 16.2)
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c * 1.3  # Omvägsfaktor
    
    # Steg 2: Hämta bilvägsavstånd via OSRM
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_from[1]},{coords_from[0]};{coords_to[1]},{coords_to[0]}?overview=false"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data['routes']:
                distance_m = data['routes'][0]['distance']
                return distance_m / 1000  # Returnera km
    except:
        pass
    
    return 15  # Default fallback