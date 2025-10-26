import requests
from collections import defaultdict
from config import SF_CRIME_DATA_URL, NEIGHBORHOOD_COORDS

def fetch_crime_data():
    """
    Fetch crime data from SF Open Data Portal
    Using 2023-2024 incident reports
    
    API Documentation: https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-2018-to-Present/wg3w-h783
    """
    params = {
        '$limit': 100000,
        '$where': "incident_datetime >= '2023-01-01T00:00:00.000'",
        '$select': 'analysis_neighborhood,incident_category,incident_subcategory'
    }
    
    try:
        print("  Fetching from SF Open Data API...")
        response = requests.get(SF_CRIME_DATA_URL, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"  ⚠️  Crime API returned {response.status_code}, using fallback data")
            return None
        
        data = response.json()
        print(f"  ✅ Fetched {len(data)} crime incidents")
        return data
        
    except Exception as e:
        print(f"  ⚠️  Error fetching crime data: {e}")
        return None


def get_fallback_crime_data():
    """
    Fallback crime estimates based on SFPD 2023 reports
    Values represent crime incidents per 1000 residents annually
    
    Source: SFPD Crime Dashboard, SF Chronicle, Neighborhood Scout
    Lower values = safer neighborhoods
    """
    crime_incidents_per_1000 = {
        # Downtown/Central - High Crime
        "SoMa": 140,
        "Civic Center": 165,
        "Financial District": 110,
        "Mission": 95,
        "Western Addition": 105,
        
        # Waterfront
        "South Beach": 85,
        "Mission Bay": 65,
        
        # Northern
        "North Beach": 70,
        "Chinatown": 75,
        "Nob Hill": 80,
        "Russian Hill": 55,
        
        # Western - Generally Safer
        "Marina": 35,
        "Cow Hollow": 30,
        "Pacific Heights": 25,
        "Presidio Heights": 20,
        "Inner Richmond": 32,
        "Outer Richmond": 20,
        "Sunset": 28,
        "Parkside": 25,
        "Lake Merced": 15,
        
        # Central
        "Hayes Valley": 65,
        "Japantown": 50,
        "Haight Ashbury": 85,
        "Twin Peaks": 18,
        "Forest Hill": 20,
        
        # Eastern
        "Potrero Hill": 55,
        
        # Castro/Noe Valley - Moderate to Safe
        "Castro": 65,
        "Noe Valley": 28,
        "Glen Park": 30,
        
        # Southern - Mixed
        "Bernal Heights": 45,
        "Outer Mission": 95,
        "Excelsior": 80,
        "Visitacion Valley": 85,
        "Bayview": 120,
        "Ingleside": 70,
        "Oceanview": 68,
        "Portola": 65,
    }
    return crime_incidents_per_1000


def assign_crime_severity_weight(category, subcategory=None):
    """
    Assign severity weights to different crime types
    
    Weight Scale:
    - 1.0: Minor incidents (vandalism, petty theft)
    - 2.0: Property crimes (burglary, vehicle theft)
    - 3.5: Violent crimes (assault, robbery)
    - 5.0: Serious violent crimes (weapons, aggravated assault, homicide)
    """
    
    if not category:
        return 1.5
    
    category_lower = category.lower()
    
    # Serious violent crimes
    if any(crime in category_lower for crime in [
        'homicide', 'rape', 'sex offense, forcible', 'kidnapping',
        'human trafficking'
    ]):
        return 5.0
    
    # Violent crimes with weapons
    if any(crime in category_lower for crime in [
        'assault, aggravated', 'robbery', 'weapons'
    ]):
        return 3.5
    
    # Simple assault and threats
    if any(crime in category_lower for crime in [
        'assault', 'battery', 'threats'
    ]):
        return 2.5
    
    # Property crimes
    if any(crime in category_lower for crime in [
        'burglary', 'larceny', 'motor vehicle theft', 'stolen property',
        'arson', 'vandalism'
    ]):
        return 2.0
    
    # Minor crimes
    if any(crime in category_lower for crime in [
        'fraud', 'forgery', 'embezzlement', 'drug', 'disorderly',
        'loitering', 'trespassing'
    ]):
        return 1.0
    
    # Default
    return 1.5


def calculate_weighted_crime_score(crime_data, neighborhoods):
    """
    Calculate weighted crime scores based on incident severity
    Returns total weighted crime incidents per neighborhood
    """
    weighted_scores = defaultdict(float)
    incident_counts = defaultdict(int)
    
    for incident in crime_data:
        neighborhood = incident.get('analysis_neighborhood', '')
        category = incident.get('incident_category', '')
        subcategory = incident.get('incident_subcategory', '')
        
        if not neighborhood:
            continue
        
        weight = assign_crime_severity_weight(category, subcategory)
        weighted_scores[neighborhood] += weight
        incident_counts[neighborhood] += 1
    
    print(f"  📊 Processed {sum(incident_counts.values())} incidents across {len(weighted_scores)} neighborhoods")
    
    return dict(weighted_scores), dict(incident_counts)


def map_to_standard_neighborhood_names(crime_scores, neighborhoods):
    """
    Map SF Open Data neighborhood names to our standardized names
    
    SF Open Data uses specific naming conventions that differ from common usage.
    This function handles all variations and aliases.
    """
    results = {}
    
    # Comprehensive mapping based on SF Open Data Portal naming
    # Format: "Our Name": ["SF Open Data variations", "Alternate names"]
    name_mapping = {
        # Downtown/Central
        "Financial District": [
            "Financial District/South Beach",
            "Financial District",
            "Financial District / South Beach",
            "Downtown",
        ],
        "South Beach": [
            "Financial District/South Beach",
            "South Beach",
        ],
        "SoMa": [
            "South of Market",
            "SoMa",
            "SOMA",
        ],
        "Civic Center": [
            "Civic Center",
            "Civic Center/Downtown",
        ],
        
        # Northern Waterfront
        "North Beach": [
            "North Beach",
            "North Beach/Telegraph Hill",
            "Telegraph Hill",
        ],
        "Russian Hill": [
            "Russian Hill",
            "Nob Hill/Russian Hill",
        ],
        "Nob Hill": [
            "Nob Hill",
            "Nob Hill/Russian Hill",
        ],
        "Chinatown": [
            "Chinatown",
            "Chinatown/North Beach",
        ],
        
        # Western
        "Marina": [
            "Marina",
            "Marina/Cow Hollow",
            "Marina District",
        ],
        "Cow Hollow": [
            "Cow Hollow",
            "Marina/Cow Hollow",
        ],
        "Pacific Heights": [
            "Pacific Heights",
            "Pac Heights",
        ],
        "Presidio Heights": [
            "Presidio Heights",
            "Presidio",
            "Laurel Heights/Presidio Heights",
        ],
        "Inner Richmond": [
            "Inner Richmond",
            "Richmond District",
        ],
        "Outer Richmond": [
            "Outer Richmond",
            "Richmond District",
        ],
        "Sunset": [
            "Sunset/Parkside",
            "Inner Sunset",
            "Outer Sunset",
            "Sunset",
            "Sunset District",
        ],
        "Parkside": [
            "Parkside",
            "Sunset/Parkside",
            "Outer Parkside",
        ],
        "Lake Merced": [
            "Lake Merced",
            "Lakeshore",
            "Merced Heights",
        ],
        
        # Central
        "Hayes Valley": [
            "Hayes Valley",
            "Hayes Valley/Civic Center",
        ],
        "Western Addition": [
            "Western Addition",
            "NOPA",
            "North of Panhandle",
            "Fillmore",
        ],
        "Japantown": [
            "Japantown",
            "Western Addition",
        ],
        "Haight Ashbury": [
            "Haight Ashbury",
            "Haight",
            "Upper Haight",
        ],
        "Twin Peaks": [
            "Twin Peaks",
            "Midtown Terrace",
        ],
        "Forest Hill": [
            "Forest Hill",
            "West of Twin Peaks",
            "Forest Hill Extension",
        ],
        
        # Eastern
        "Mission": [
            "Mission",
            "Mission District",
            "The Mission",
        ],
        "Mission Bay": [
            "Mission Bay",
        ],
        "Potrero Hill": [
            "Potrero Hill",
            "Potrero",
        ],
        
        # Castro/Noe Valley Area
        "Castro": [
            "Castro/Upper Market",
            "Castro",
            "Upper Market",
            "Eureka Valley",
        ],
        "Noe Valley": [
            "Noe Valley",
        ],
        "Glen Park": [
            "Glen Park",
        ],
        
        # Southern
        "Bernal Heights": [
            "Bernal Heights",
        ],
        "Outer Mission": [
            "Outer Mission",
        ],
        "Excelsior": [
            "Excelsior",
        ],
        "Visitacion Valley": [
            "Visitacion Valley",
            "Vis Valley",
        ],
        "Bayview": [
            "Bayview Hunters Point",
            "Bayview",
            "Bayview/Hunters Point",
            "Hunters Point",
        ],
        "Ingleside": [
            "Ingleside",
            "Oceanview/Merced/Ingleside",
            "OMI",
        ],
        "Oceanview": [
            "Oceanview",
            "Oceanview/Merced/Ingleside",
            "OMI",
        ],
        "Portola": [
            "Portola",
        ],
    }
    
    # Reverse mapping for quick lookup
    reverse_mapping = {}
    for standard_name, variations in name_mapping.items():
        for variation in variations:
            reverse_mapping[variation.lower()] = standard_name
    
    # Step 1: Direct matches
    for hood in neighborhoods:
        if hood in crime_scores:
            results[hood] = crime_scores[hood]
            continue
        
        # Check if our neighborhood name is in the mapping
        if hood in name_mapping:
            for variation in name_mapping[hood]:
                if variation in crime_scores:
                    results[hood] = crime_scores[variation]
                    print(f"  ✓ Mapped '{variation}' -> '{hood}'")
                    break
    
    # Step 2: Reverse mapping (SF name -> our name)
    for sf_name, crime_score in crime_scores.items():
        sf_name_lower = sf_name.lower()
        
        if sf_name_lower in reverse_mapping:
            our_name = reverse_mapping[sf_name_lower]
            if our_name in neighborhoods and our_name not in results:
                results[our_name] = crime_score
                print(f"  ✓ Mapped '{sf_name}' -> '{our_name}'")
    
    # Step 3: Fuzzy matching for remaining neighborhoods
    for hood in neighborhoods:
        if hood in results:
            continue
        
        hood_lower = hood.lower()
        hood_words = set(hood_lower.split())
        
        best_match = None
        best_score = 0
        
        for crime_hood, crime_score in crime_scores.items():
            crime_lower = crime_hood.lower()
            crime_words = set(crime_lower.split())
            
            # Substring match
            if hood_lower in crime_lower or crime_lower in hood_lower:
                word_overlap = len(hood_words & crime_words)
                if word_overlap > best_score:
                    best_score = word_overlap
                    best_match = (crime_hood, crime_score)
        
        if best_match:
            results[hood] = best_match[1]
            print(f"  ~ Fuzzy matched '{best_match[0]}' -> '{hood}'")
    
    return results


def convert_crime_to_safety_percentage(crime_scores):
    """
    Convert crime scores to safety percentages using MIN/MAX SCALING
    
    Process:
    1. Find min and max crime scores across all neighborhoods
    2. Inverse normalize: lower crime = higher safety percentage
    3. Scale to 0-100%
    
    Formula: Safety% = ((max - value) / (max - min)) * 100
    
    This means:
    - Neighborhood with LOWEST crime gets ~100% safety
    - Neighborhood with HIGHEST crime gets ~0% safety
    - Others distributed proportionally in between
    
    Returns:
        dict: {neighborhood: safety_percentage (0-100)}
    """
    if not crime_scores:
        return {}
    
    min_crime = min(crime_scores.values())
    max_crime = max(crime_scores.values())
    
    # Handle edge case where all values are the same
    if max_crime == min_crime:
        return {hood: 50.0 for hood in crime_scores.keys()}
    
    safety_percentages = {}
    
    for neighborhood, crime_score in crime_scores.items():
        # Inverse normalization: higher crime = lower safety
        safety_pct = ((max_crime - crime_score) / (max_crime - min_crime)) * 100
        safety_percentages[neighborhood] = round(safety_pct, 1)
    
    return safety_percentages


def process_crime_data(neighborhoods):
    """
    Main function to process crime data and return safety percentages
    Uses MIN/MAX SCALING for consistent relative comparisons
    
    Returns:
        dict: {neighborhood: safety_percentage}
        Where safety_percentage is 0-100% (scaled between min and max)
    """
    
    # Step 1: Fetch crime data from API
    data = fetch_crime_data()
    
    # Step 2: Process based on whether API worked
    if data and len(data) > 0:
        print("  📊 Processing API crime data...")
        
        # Calculate weighted crime scores
        crime_scores, incident_counts = calculate_weighted_crime_score(data, neighborhoods)
        
        print(f"\n  🗺️  Mapping neighborhood names...")
        # Map to our neighborhood names
        crime_scores = map_to_standard_neighborhood_names(crime_scores, neighborhoods)
        
        # For missing neighborhoods, use average
        if len(crime_scores) < len(neighborhoods):
            avg_score = sum(crime_scores.values()) / len(crime_scores) if crime_scores else 50
            for hood in neighborhoods:
                if hood not in crime_scores:
                    crime_scores[hood] = avg_score
                    print(f"  ⚠️  No data for '{hood}', using average")
        
        # Convert to safety percentages with min/max scaling
        safety_percentages = convert_crime_to_safety_percentage(crime_scores)
        
    else:
        # Use fallback data
        print("  📊 Using fallback crime data...")
        crime_rates = get_fallback_crime_data()
        
        # Ensure all neighborhoods have values
        for hood in neighborhoods:
            if hood not in crime_rates:
                crime_rates[hood] = 60  # Default moderate crime rate
        
        # Convert to safety percentages with min/max scaling
        safety_percentages = convert_crime_to_safety_percentage(crime_rates)
    
    # Step 3: Print summary
    print("\n  " + "="*76)
    print("  Safety Percentages (Scaled: Min=0%, Max=100%)")
    print("  " + "="*76)
    
    sorted_hoods = sorted(safety_percentages.items(), key=lambda x: x[1], reverse=True)
    
    print("\n  🟢 Safest Neighborhoods (Top 10):")
    for hood, safety in sorted_hoods[:10]:
        print(f"    {hood:40} {safety:5.1f}%")
    
    print("\n  🔴 Least Safe Neighborhoods (Bottom 10):")
    for hood, safety in sorted_hoods[-10:]:
        print(f"    {hood:40} {safety:5.1f}%")
    
    # Statistics
    avg_safety = sum(safety_percentages.values()) / len(safety_percentages)
    print(f"\n  📊 Statistics:")
    print(f"    Average Safety:  {avg_safety:.1f}%")
    print(f"    Safest:          {sorted_hoods[0][0]} ({sorted_hoods[0][1]:.1f}%)")
    print(f"    Least Safe:      {sorted_hoods[-1][0]} ({sorted_hoods[-1][1]:.1f}%)")
    print(f"    Range:           {sorted_hoods[0][1] - sorted_hoods[-1][1]:.1f} percentage points")
    print(f"\n  💡 Note: Values are scaled between the safest and least safe neighborhoods")
    
    return safety_percentages