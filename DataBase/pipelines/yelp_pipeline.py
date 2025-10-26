import requests
import time
from config import YELP_API_KEY, YELP_SEARCH_URL, NEIGHBORHOOD_COORDS
from utils.normalizers import calculate_density_score, price_to_scale

def search_yelp(latitude, longitude, category, radius=2000):
    """
    Search Yelp for businesses in a category
    Radius in meters (2000m = ~1.25 miles)
    """
    headers = {'Authorization': f'Bearer {YELP_API_KEY}'}
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'categories': category,
        'radius': radius,
        'limit': 50  # Max results per request
    }
    
    try:
        response = requests.get(YELP_SEARCH_URL, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('businesses', [])
        else:
            print(f"⚠️  Yelp API error {response.status_code} for {category}")
            return []
    except Exception as e:
        print(f"⚠️  Yelp request failed: {e}")
        return []

def process_yelp_category(neighborhoods, category_key, yelp_category):
    """
    Process a single Yelp category (bars, restaurants, cafes)
    Returns: {neighborhood: {avg_price, avg_rating, count}}
    """
    results = {}
    all_counts = []
    
    for hood, coords in NEIGHBORHOOD_COORDS.items():
        if hood not in neighborhoods:
            continue
        
        businesses = search_yelp(coords[0], coords[1], yelp_category)
        time.sleep(0.5)  # Rate limiting
        
        if not businesses:
            results[hood] = {
                'avg_price': 2.0,
                'avg_rating': 3.5,
                'count': 0
            }
            all_counts.append(0)
            continue
        
        # Calculate averages
        prices = [price_to_scale(b.get('price', '$$')) for b in businesses]
        ratings = [b.get('rating', 3.5) for b in businesses]
        count = len(businesses)
        all_counts.append(count)
        
        results[hood] = {
            'avg_price': round(sum(prices) / len(prices), 1),
            'avg_rating': round(sum(ratings) / len(ratings), 1),
            'count': count  # Will normalize after loop
        }
    
    return results

def process_all_yelp_data(neighborhoods):
    """Process bars, restaurants, and cafes"""
    print("🍺 Fetching Yelp data for bars...")
    bars = process_yelp_category(neighborhoods, 'bars', 'bars,nightlife')
    
    print("🍽️  Fetching Yelp data for restaurants...")
    restaurants = process_yelp_category(neighborhoods, 'restaurants', 'restaurants')
    
    print("☕ Fetching Yelp data for cafes...")
    cafes = process_yelp_category(neighborhoods, 'cafes', 'cafes,coffee')
    
    return {
        'bars': bars,
        'restaurants': restaurants,
        'cafes': cafes
    }