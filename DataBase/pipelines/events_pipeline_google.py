import requests
import time
from config import NEIGHBORHOOD_COORDS
from utils.normalizers import normalize_to_percentage
import os

GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

def count_nightlife_venues(latitude, longitude, radius=1500):
    """
    Count nightlife venues (bars, clubs, music venues) as proxy for "happening"
    Using Google Places API
    """
    if not GOOGLE_PLACES_API_KEY or GOOGLE_PLACES_API_KEY == 'your_google_key':
        return None
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    types = ['night_club', 'bar', 'restaurant']
    total_count = 0
    
    for place_type in types:
        params = {
            'location': f'{latitude},{longitude}',
            'radius': radius,
            'type': place_type,
            'key': GOOGLE_PLACES_API_KEY
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                total_count += len(results)
                time.sleep(0.5)  # Rate limiting
            else:
                return None
        except Exception as e:
            print(f"⚠️  Google Places error: {e}")
            return None
    
    return total_count

def get_fallback_happening_scores():
    """Curated happening scores based on nightlife/events reputation"""
    return {
        "Mission": 95,
        "SoMa": 90,
        "Castro/Upper Market": 85,
        "North Beach": 82,
        "Hayes Valley": 78,
        "Marina": 75,
        "Haight Ashbury": 72,
        "Financial District/South Beach": 70,
        "Nob Hill": 65,
        "Potrero Hill": 60,
        "Noe Valley": 55,
        "Inner Richmond": 52,
        "Bernal Heights": 50,
        "Chinatown": 48,
        "Pacific Heights": 45,
        "Outer Mission": 42,
        "Glen Park": 38,
        "Sunset/Parkside": 35,
        "Excelsior": 32,
        "Outer Richmond": 30,
        "Bayview Hunters Point": 28,
        "Visitacion Valley": 25,
        "Twin Peaks": 20,
        "West of Twin Peaks": 22,
        "Lake Merced": 15,
    }

def process_happening_index(neighborhoods):
    """
    Calculate 'happening' score based on nightlife venue density
    """
    venue_counts = {}
    api_working = False
    
    if GOOGLE_PLACES_API_KEY and GOOGLE_PLACES_API_KEY != 'your_google_key':
        print("  Attempting to fetch Google Places data...")
        
        for hood, coords in NEIGHBORHOOD_COORDS.items():
            if hood not in neighborhoods:
                continue
            
            count = count_nightlife_venues(coords[0], coords[1])
            
            if count is None:
                break
            
            venue_counts[hood] = count
            if count > 0:
                api_working = True
            
            print(f"  {hood}: {count} venues")
        
        # Use API data if meaningful
        if api_working and venue_counts:
            print("  ✅ Using Google Places data")
            min_count = min(venue_counts.values())
            max_count = max(venue_counts.values())
            
            if max_count > 0:
                return {
                    hood: normalize_to_percentage(count, min_count, max_count)
                    for hood, count in venue_counts.items()
                }
    
    # Fallback
    print("  ⚠️  Using fallback happening scores (curated data)")
    return get_fallback_happening_scores()