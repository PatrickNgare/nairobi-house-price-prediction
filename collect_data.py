# day1_collect_data.py
import pandas as pd
import os
from datetime import datetime
import logging

# Import your scrapers
from scrapers.buyrentkenya_scraper import BuyRentKenyaScraper
from scrapers.propertypro_scraper import PropertyProScraper
from scrapers.property24_scraper import Property24Scraper
import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'data/scraping_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Main")

def create_data_dictionary():
    """Create a simple data dictionary"""
    dictionary = """# Nairobi House Price Prediction - Data Dictionary

| Column Name | Description | Example |
|------------|-------------|---------|
| listing_id | Unique ID for each property | "abc123def" |
| source | Website source | "BuyRentKenya" |
| title | Listing title | "3 Bedroom Apartment in Kilimani" |
| location | Area in Nairobi | "Kilimani" |
| property_type | Type of property | "Apartment" |
| bedrooms | Number of bedrooms | 3 |
| bathrooms | Number of bathrooms | 2 |
| size_sqft | Size in square feet | 1500 |
| price_kes | Price in Kenyan Shillings | 15000000 |
| listing_date | Date listed | 2024-01-15 |
| listing_url | URL to original listing | https://... |
"""
    
    with open('data/data_dictionary.md', 'w') as f:
        f.write(dictionary)
    logger.info("Data dictionary created")

def main():
    print("\n" + "="*60)
    print("🏠 NAIROBI HOUSE PRICE PREDICTION - DAY 1")
    print("="*60)
    print(f"Target: {config.TARGET_LISTINGS} listings")
    print("="*60 + "\n")
    
    start_time = datetime.now()
    all_listings = []
    
    # Initialize scrapers
    scrapers = []
    
    if config.WEBSITES['buyrentkenya']['enabled']:
        scrapers.append(BuyRentKenyaScraper(delay=config.REQUEST_DELAY))
        print("✓ BuyRentKenya scraper initialized")
    
    if config.WEBSITES['propertypro']['enabled']:
        scrapers.append(PropertyProScraper(delay=config.REQUEST_DELAY))
        print("✓ PropertyPro scraper initialized")
    
    if config.WEBSITES['property24']['enabled']:
        scrapers.append(Property24Scraper(delay=config.REQUEST_DELAY))
        print("✓ Property24 scraper initialized")
    
    print("\n" + "-"*60)
    print("Starting scraping process...")
    print("-"*60 + "\n")
    
    # Run each scraper
    for scraper in scrapers:
        print(f"\n>>> Scraping from {scraper.source_name}...")
        
        try:
            # Get max pages for this scraper
            source_key = scraper.source_name.lower()
            if source_key == 'buyrentkenya':
                max_pages = config.WEBSITES['buyrentkenya']['max_pages']
            elif source_key == 'propertypro':
                max_pages = config.WEBSITES['propertypro']['max_pages']
            else:
                max_pages = config.WEBSITES['property24']['max_pages']
            
            # Scrape listings
            listings = scraper.scrape(max_pages=max_pages)
            
            # Add to collection
            all_listings.extend(listings)
            
            print(f"✓ Got {len(listings)} listings from {scraper.source_name}")
            print(f"  Total so far: {len(all_listings)}")
            
            # Stop if we have enough
            if len(all_listings) >= config.TARGET_LISTINGS:
                print(f"\n✓ Reached target of {config.TARGET_LISTINGS} listings!")
                break
                
        except Exception as e:
            print(f"✗ Error with {scraper.source_name}: {str(e)}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("✅ SCRAPING COMPLETE")
    print("="*60)
    print(f"📊 Total listings collected: {len(all_listings)}")
    print(f"⏱️  Time taken: {duration:.1f} seconds")
    
    if len(all_listings) == 0:
        print("\n❌ No listings were collected!")
        print("Possible issues:")
        print("1. Website structure may have changed")
        print("2. You might be getting blocked (try increasing delay in config.py)")
        print("3. Check your internet connection")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(all_listings)
    
    # Show breakdown by source
    print("\n📈 Breakdown by source:")
    source_counts = df['source'].value_counts()
    for source, count in source_counts.items():
        print(f"   • {source}: {count} listings")
    
    # Save to CSV
    df.to_csv(config.RAW_DATA_FILE, index=False)
    print(f"\n💾 Data saved to: {config.RAW_DATA_FILE}")
    
    # Create data dictionary
    create_data_dictionary()
    
    # Show sample
    print("\n📋 Sample of collected data (first 5 rows):")
    print(df[['source', 'location', 'property_type', 'bedrooms', 'price_kes']].head())
    
    # Show basic stats
    print("\n📊 Price statistics:")
    print(f"   Min: KSh {df['price_kes'].min():,.0f}")
    print(f"   Max: KSh {df['price_kes'].max():,.0f}")
    print(f"   Average: KSh {df['price_kes'].mean():,.0f}")
    print(f"   Median: KSh {df['price_kes'].median():,.0f}")
    
    print("\n" + "="*60)
    print("📁 Files created:")
    print(f"   • {config.RAW_DATA_FILE}")
    print(f"   • data/data_dictionary.md")
    print(f"   • data/scraping_[timestamp].log")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Review the data in data/raw_listings.csv")
    print("2. Initialize git: git init")
    print("3. Add files: git add .")
    print("4. Commit: git commit -m 'Day 1: Data Collection'")
    print("5. Create GitHub repo and push")
    print("="*60)

if __name__ == "__main__":
    main()