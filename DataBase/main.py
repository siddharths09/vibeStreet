#!/usr/bin/env python3
import time
from config import NEIGHBORHOODS, NEIGHBORHOOD_COORDS
from firebase_client import initialize_firebase, save_neighborhood_data
from pipelines.crime_pipeline import process_crime_data
from pipelines.demographics_pipeline import process_demographics
from pipelines.property_pipeline import process_property_rates
from pipelines.yelp_pipeline import process_all_yelp_data
from pipelines.events_pipeline import process_happening_index

def main():
    print("🚀 vibeStreet Data Pipeline Starting...\n")
    start_time = time.time()
    
    # Initialize Firebase
    print("🔥 Connecting to Firebase...")
    db = initialize_firebase()
    
    # Step 1: Crime Data -> Safety Percentages
    print("\n🚨 Processing crime data and calculating safety scores...")
    safety_data = process_crime_data(NEIGHBORHOODS)  # Now returns safety percentages!
    
    # Step 2: Demographics
    print("\n👥 Processing demographics...")
    demographics = process_demographics(NEIGHBORHOODS)
    
    # Step 3: Property Rates
    print("\n🏠 Processing property rates...")
    property_rates = process_property_rates(NEIGHBORHOODS)
    
    # Step 4: Yelp Data (bars, restaurants, cafes)
    print("\n🍽️  Processing Yelp data...")
    yelp_data = process_all_yelp_data(NEIGHBORHOODS)
    
    # Step 5: Happening Index
    print("\n🎉 Processing happening index...")
    happening_data = process_happening_index(NEIGHBORHOODS)
    
    # Step 6: Combine and Save to Firebase
    print("\n💾 Saving to Firebase...")
    for hood in NEIGHBORHOODS:
        coords = NEIGHBORHOOD_COORDS.get(hood, (37.7749, -122.4194))
        
        neighborhood_data = {
            "neighborhood": hood,
            "coordinates": {
                "latitude": coords[0],
                "longitude": coords[1]
            },
            "safety": safety_data.get(hood, 50.0),  # Updated: now called "safety" instead of "crime_rate"
            "population_density": demographics.get(hood, {}).get('population_density', 50.0),
            "happening": happening_data.get(hood, 50.0),
            "age_demographic": demographics.get(hood, {}).get('age_demographic', 38.0),
            "property_rates": property_rates.get(hood, 3000.0),
            "bars": yelp_data['bars'].get(hood, {'avg_price': 2.0, 'avg_rating': 3.5, 'density': 0.0}),
            "restaurants": yelp_data['restaurants'].get(hood, {'avg_price': 2.0, 'avg_rating': 3.5, 'density': 0.0}),
            "cafes": yelp_data['cafes'].get(hood, {'avg_price': 2.0, 'avg_rating': 3.5, 'density': 0.0}),
        }
        
        save_neighborhood_data(db, hood, neighborhood_data)
    
    elapsed = time.time() - start_time
    print(f"\n✅ Pipeline completed in {elapsed:.1f} seconds!")
    print(f"📊 Processed {len(NEIGHBORHOODS)} neighborhoods")
    print(f"\n💡 Note: 'safety' values are now percentages (0-100%)")
    print(f"   Higher percentage = Safer neighborhood")

if __name__ == "__main__":
    main()