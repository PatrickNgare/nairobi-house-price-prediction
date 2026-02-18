#!/usr/bin/env python3
import pandas as pd
import os
from datetime import datetime
import time

# Import scrapers
from scrapers.buyrentkenya_scraper import BuyRentKenyaScraper
from scrapers.propertypro_scraper import PropertyProScraper
# from scrapers.diamondtrust_scraper import DiamondTrustScraper

# Import config
from config.settings import (
    RAW_DIR, PROCESSED_DIR, MASTER_FILE, TODAY_FILE,
    TARGET_LISTINGS, MIN_LISTINGS_PER_SOURCE
)

def print_header():
    print("\n" + "="*80)
    print("🏠 NAIROBI PROPERTY DATA COLLECTION PROJECT")
    print("="*80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: {TARGET_LISTINGS}+ listings")
    print("="*80)

def run_scrapers():
    all_listings = []
    source_stats = {}
    scrapers = [
        BuyRentKenyaScraper(),
        PropertyProScraper(),
        # DiamondTrustScraper(),
    ]
    for scraper in scrapers:
        try:
            print(f"\n{'─'*50}")
            listings = scraper.scrape(max_pages=5)
            all_listings.extend(listings)
            source_stats[scraper.name] = {
                'count': len(listings),
                'pages': scraper.stats['pages_scraped'],
                'errors': scraper.stats['errors']
            }
        except Exception as e:
            print(f"❌ Error in {scraper.name}: {str(e)}")
            source_stats[scraper.name] = {'count': 0, 'pages': 0, 'errors': 1}
    return all_listings, source_stats

def save_raw_data(listings):
    if not listings:
        print("❌ No data to save")
        return None
    df = pd.DataFrame(listings)
    df.to_csv(TODAY_FILE, index=False)
    print(f"\n💾 Raw data saved: {TODAY_FILE}")
    master_raw = os.path.join(RAW_DIR, 'all_listings_raw.csv')
    if os.path.exists(master_raw):
        existing = pd.read_csv(master_raw)
        df = pd.concat([existing, df], ignore_index=True)
        df = df.drop_duplicates(subset=['listing_id', 'price_kes'], keep='last')
    df.to_csv(master_raw, index=False)
    print(f"💾 Master raw updated: {master_raw}")
    return df

def main():
    start_time = time.time()
    print_header()
    print("\n🚀 Starting data collection...")
    listings, source_stats = run_scrapers()
    if not listings:
        print("\n❌ No data collected. Exiting.")
        return
    raw_df = save_raw_data(listings)
    elapsed = time.time() - start_time
    print(f"\n⏱️  Time elapsed: {elapsed:.1f} seconds")
    print("\n✅ DAY 1 COMPLETE! Ready for modeling.")
if __name__ == "__main__":
    main()