#!/usr/bin/env python3
"""
Generate realistic demo data for Nairobi house price prediction.
Uses realistic distributions based on actual Nairobi property market.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Nairobi neighborhoods with average prices
NEIGHBORHOODS = {
    'Westlands': (18000000, 80000000, 'high'),
    'Kilimani': (15000000, 60000000, 'high'),
    'Kileleshwa': (12000000, 50000000, 'high'),
    'Lavington': (14000000, 70000000, 'high'),
    'Karen': (25000000, 150000000, 'ultra-high'),
    'Runda': (30000000, 200000000, 'ultra-high'),
    'Upper Hill': (20000000, 100000000, 'high'),
    'Langata': (8000000, 35000000, 'mid'),
    'Buruburu': (3000000, 15000000, 'low'),
    'Donholm': (4000000, 20000000, 'low'),
    'Komarock': (3000000, 18000000, 'low'),
    'Embakasi': (2500000, 12000000, 'low'),
    'Kasarani': (3500000, 16000000, 'low'),
    'Parklands': (10000000, 40000000, 'mid'),
    'Ongata Rongai': (5000000, 25000000, 'low-mid'),
    'Ngong': (6000000, 30000000, 'low-mid'),
    'Kitengela': (4000000, 20000000, 'low'),
    'Thika Road': (3000000, 15000000, 'low'),
    'Syokimau': (3500000, 18000000, 'low'),
}

PROPERTY_TYPES = ['Apartment', 'House', 'Townhouse', 'Villa', 'Bungalow']
AMENITIES_POOL = ['pool', 'gym', 'parking', 'security', 'garden', 'cctv', 'balcony', 
                   'furnished', 'internet', 'lift', 'playground', 'water', 'generator']

def generate_price(neighborhood, bedrooms):
    """Generate realistic price based on neighborhood and bedrooms"""
    min_price, max_price, tier = NEIGHBORHOODS[neighborhood]
    
    # Adjust by bedrooms
    bedroom_multiplier = {
        1: 0.6,
        2: 0.85,
        3: 1.0,
        4: 1.3,
        5: 1.6,
    }.get(bedrooms, 1.0)
    
    # Add random variation
    base_price = np.random.uniform(min_price, max_price)
    price = int(base_price * bedroom_multiplier)
    
    # Ensure within bounds
    price = max(min_price, min(price, max_price * 1.5))
    return int(price)

def generate_property_size(bedrooms, property_type):
    """Generate realistic property size"""
    base_sqm = {
        'Apartment': {1: 50, 2: 80, 3: 120, 4: 150},
        'House': {2: 120, 3: 180, 4: 250, 5: 350},
        'Townhouse': {2: 100, 3: 150, 4: 200},
        'Villa': {3: 250, 4: 350, 5: 500},
        'Bungalow': {2: 150, 3: 200, 4: 300},
    }
    
    size_map = base_sqm.get(property_type, {2: 100, 3: 150})
    base = size_map.get(bedrooms, 100)
    
    # Add variation (±20%)
    variation = np.random.uniform(0.8, 1.2)
    size_sqm = int(base * variation)
    
    # Convert to sqft
    return int(size_sqm * 10.764)

def generate_demo_data(n_records=500):
    """Generate realistic demo dataset"""
    data = []
    sources = ['BuyRentKenya', 'PropertyPro', 'DiamondTrust']
    
    for i in range(n_records):
        neighborhood = random.choice(list(NEIGHBORHOODS.keys()))
        bedrooms = random.choices([1, 2, 3, 4, 5], weights=[10, 35, 30, 20, 5])[0]
        bathrooms = max(1, bedrooms - 1) + random.randint(0, 1)
        property_type = random.choice(PROPERTY_TYPES)
        
        # Generate features
        price = generate_price(neighborhood, bedrooms)
        size_sqft = generate_property_size(bedrooms, property_type)
        
        # Amenities (30-50% of listings have multiple)
        has_amenities = np.random.random() > 0.4
        amenities = '|'.join(random.sample(AMENITIES_POOL, k=random.randint(2, 5))) if has_amenities else None
        
        # Dates
        scrape_date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
        
        record = {
            'source': random.choice(sources),
            'listing_id': f"{chr(65 + i % 26)}{i % 1000:04d}",
            'title': f"{bedrooms}BR {property_type} in {neighborhood}",
            'location': neighborhood,
            'property_type': property_type,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'size_sqft': size_sqft,
            'price_kes': price,
            'amenities': amenities,
            'listing_url': f"https://example.com/property/{i}",
            'scrape_date': scrape_date,
        }
        data.append(record)
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("=" * 70)
    print("GENERATING DEMO DATASET FOR NAIROBI HOUSE PRICE PREDICTION")
    print("=" * 70)
    
    # Generate data
    df = generate_demo_data(n_records=800)
    
    # Save to CSV
    output_file = 'data/raw/all_listings_demo.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Generated {len(df)} realistic property listings")
    print(f"💾 Saved to: {output_file}")
    
    # Show statistics
    print("\n" + "=" * 70)
    print("DATA STATISTICS:")
    print("=" * 70)
    print(f"\nPrice Range:")
    print(f"  Min:    KES {df['price_kes'].min():>15,.0f}")
    print(f"  Max:    KES {df['price_kes'].max():>15,.0f}")
    print(f"  Mean:   KES {df['price_kes'].mean():>15,.0f}")
    print(f"  Median: KES {df['price_kes'].median():>15,.0f}")
    
    print(f"\nProperty Features:")
    print(f"  Bedrooms:  {df['bedrooms'].min()}-{df['bedrooms'].max()} (avg {df['bedrooms'].mean():.1f})")
    print(f"  Bathrooms: {df['bathrooms'].min()}-{df['bathrooms'].max()} (avg {df['bathrooms'].mean():.1f})")
    print(f"  Size sqft: {df['size_sqft'].min():.0f}-{df['size_sqft'].max():.0f} (avg {df['size_sqft'].mean():.0f})")
    
    print(f"\nLocations: {df['location'].nunique()} neighborhoods")
    print(f"  Top 5: {', '.join(df['location'].value_counts().head(5).index.tolist())}")
    
    print(f"\nProperty Types: {', '.join(df['property_type'].unique())}")
    
    print(f"\nData Sources:")
    for source in df['source'].unique():
        count = len(df[df['source'] == source])
        print(f"  {source}: {count} listings")
    
    print(f"\n✅ Demo data ready for analysis and ML modeling!")
