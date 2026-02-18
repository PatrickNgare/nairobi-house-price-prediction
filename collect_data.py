# collect_data.py
import pandas as pd
from datetime import datetime
from scrapers.buyrentkenya_scraper import BuyRentKenyaScraper
from scrapers.propertypro_scraper import PropertyProScraper
import config.config as config

print("="*60)
print("🏠 NAIROBI HOUSE PRICE PREDICTION - DAY 1")
print("="*60)

all_listings = []

# Run BuyRentKenya scraper
print("\n📱 Scraping BuyRentKenya...")
try:
    scraper1 = BuyRentKenyaScraper(delay=3)
    listings1 = scraper1.scrape(max_pages=3)  # Start with 3 pages
    print(f"✅ Found {len(listings1)} listings")
    all_listings.extend(listings1)
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Run PropertyPro scraper
print("\n📱 Scraping PropertyPro...")
try:
    scraper2 = PropertyProScraper(delay=3)
    listings2 = scraper2.scrape(max_pages=3)  # Start with 3 pages
    print(f"✅ Found {len(listings2)} listings")
    all_listings.extend(listings2)
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Save results
if all_listings:
    df = pd.DataFrame(all_listings)
    df.to_csv(config.RAW_DATA_FILE, index=False)
    print(f"\n✅ TOTAL LISTINGS COLLECTED: {len(df)}")
    print("\n💾 Data saved to:", config.RAW_DATA_FILE)
else:
    print("\n❌ No listings collected")