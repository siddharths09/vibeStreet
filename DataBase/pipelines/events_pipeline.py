import requests
from datetime import datetime, timedelta
from config import EVENTBRITE_TOKEN, EVENTBRITE_SEARCH_URL, NEIGHBORHOOD_COORDS
from utils.normalizers import normalize_to_percentage

def search_eventbrite(latitude, longitude, radius_km=3):
    """
    Search Eventbrite for events near coordinates
    Returns event count as proxy for "happening" score
    """
    if not EVENTBRITE_TOKEN or EVENTBRITE_TOKEN == 'your_eventbrite_token_here':
        return None  # Signal to use fallback
    
    headers = {'Authorization': f'Bearer {EVENTBRITE_TOKEN}'}
    
    # Search for events in next 7 days
    now = datetime.utcnow()
    end_date = now + timedelta(days=7)
    
    params = {
        'location.latitude': latitude,
        'location.longitude': longitude,
        'location.within': f'{radius_km}km',
        'start_date.range_start': now.isoformat() + 'Z',
        'start_date.range_end': end_date.isoformat() + 'Z',
        'expand': 'venue',
    }
    
    try:
        response = requests.get(EVENTBRITE_SEARCH_URL, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('events', [])
        else:
            print(f"⚠️  Eventbrite API returned status {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️  Eventbrite error: {e}")
        return None

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
    Calculate 'happening' score based on events density
    Falls back to curated data if API unavailable or returns no events
    """
    event_counts = {}
    api_working = False
    
    if EVENTBRITE_TOKEN and EVENTBRITE_TOKEN != 'your_eventbrite_token_here':
        print("  Attempting to fetch Eventbrite data...")
        
        for hood, coords in NEIGHBORHOOD_COORDS.items():
            if hood not in neighborhoods:
                continue
            
            events = search_eventbrite(coords[0], coords[1])
            
            if events is None:  # API error
                break
            
            event_counts[hood] = len(events)
            if len(events) > 0:
                api_working = True
        
        # Only use API data if we got meaningful results
        if api_working and event_counts:
            print("  ✅ Using Eventbrite API data")
            min_events = min(event_counts.values())
            max_events = max(event_counts.values())
            
            if max_events > 0:
                return {
                    hood: normalize_to_percentage(count, min_events, max_events)
                    for hood, count in event_counts.items()
                }
    
    # Fallback to curated data
    print("  ⚠️  Using fallback happening scores (curated data)")
    return get_fallback_happening_scores()