import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
YELP_API_KEY = os.getenv('YELP_API_KEY')
EVENTBRITE_TOKEN = os.getenv('EVENTBRITE_TOKEN')
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH', 'firebase-credentials.json')

# San Francisco Neighborhoods (Expanded)
NEIGHBORHOODS = [
    # Central/Downtown
    "Financial District",
    "SoMa",
    "South Beach",
    
    # Northern Waterfront
    "North Beach",
    "Russian Hill",
    "Nob Hill",
    "Chinatown",
    
    # Western
    "Marina",
    "Cow Hollow",
    "Pacific Heights",
    "Presidio Heights",
    "Inner Richmond",
    "Outer Richmond",
    "Sunset",
    "Parkside",
    "Lake Merced",
    
    # Central
    "Hayes Valley",
    "Western Addition",
    "Japantown",
    "Haight Ashbury",
    "Twin Peaks",
    "Forest Hill",
    
    # Eastern
    "Mission",
    "Mission Bay",
    "Potrero Hill",
    
    # Castro/Noe Valley Area
    "Castro",
    "Noe Valley",
    "Glen Park",
    
    # Southern
    "Bernal Heights",
    "Outer Mission",
    "Excelsior",
    "Visitacion Valley",
    "Bayview",
    "Ingleside",
    "Oceanview",
    "Portola",
]

# Neighborhood approximate centers (lat, lon) for API queries
NEIGHBORHOOD_COORDS = {
    # Central/Downtown
    "Financial District": (37.7946, -122.3999),
    "SoMa": (37.7749, -122.4194),
    "South Beach": (37.7844, -122.3892),
    
    # Northern Waterfront
    "North Beach": (37.8006, -122.4103),
    "Russian Hill": (37.8014, -122.4205),
    "Nob Hill": (37.7919, -122.4147),
    "Chinatown": (37.7941, -122.4078),
    
    # Western
    "Marina": (37.8021, -122.4363),
    "Pacific Heights": (37.7919, -122.4364),
    "Presidio Heights": (37.7872, -122.4539),
    "Inner Richmond": (37.7805, -122.4647),
    "Outer Richmond": (37.7758, -122.4922),
    "Sunset": (37.7436, -122.4947),
    "Parkside": (37.7366, -122.4959),
    "Lake Merced": (37.7183, -122.4850),
    
    # Central
    "Hayes Valley": (37.7753, -122.4256),
    "Western Addition": (37.7836, -122.4317),
    "Japantown": (37.7853, -122.4309),
    "Haight Ashbury": (37.7693, -122.4482),
    "Cole Valley": (37.7644, -122.4506),
    "Twin Peaks": (37.7544, -122.4477),
    "Forest Hill": (37.7449, -122.4592),
    
    # Eastern
    "Mission": (37.7599, -122.4148),
    "Mission Bay": (37.7706, -122.3922),
    "Potrero Hill": (37.7587, -122.3988),
    
    # Castro/Noe Valley Area
    "Castro": (37.7609, -122.4350),
    "Noe Valley": (37.7487, -122.4308),
    "Glen Park": (37.7332, -122.4339),
    
    # Southern
    "Bernal Heights": (37.7419, -122.4200),
    "Outer Mission": (37.7247, -122.4467),
    "Excelsior": (37.7247, -122.4261),
    "Visitacion Valley": (37.7133, -122.4039),
    "Bayview": (37.7295, -122.3814),
    "Ingleside": (37.7244, -122.4453),
    "Oceanview": (37.7236, -122.4539),
    "Portola": (37.7264, -122.4181),
}

# API Endpoints
SF_CRIME_DATA_URL = "https://data.sfgov.org/resource/wg3w-h783.json"
YELP_SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
EVENTBRITE_SEARCH_URL = "https://www.eventbriteapi.com/v3/events/search/"