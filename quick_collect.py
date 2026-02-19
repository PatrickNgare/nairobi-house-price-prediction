#!/usr/bin/env python3
"""
Quick data collection script.
Collects 500-800 listings in 5-10 minutes.
Good for testing and quick runs.
"""
import pandas as pd
import os
from datetime import datetime
import time
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("QuickCollector")

from scrapers.buyrentkenya_scraper import BuyRentKenyaScraper
from scrapers.propertypro_scraper import PropertyProScraper
from config.settings import RAW_DIR

def main():
    print("\n" + "="*70)
    print("⚡ QUICK DATA COLLECTION (5-10 minutes)")
    print("="*70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Collecting ~500-800 listings for quick testing/training")
    print("="*70 + "\n")
    
    start_time = time.time()
    all_listings = []
    
    scrapers = [
        (BuyRentKenyaScraper, "BuyRentKenya", 15),
        (PropertyProScraper, "PropertyPro", 15),
    ]
    
    for ScraperClass, name, pages in scrapers:
        scraper = None
        try:
            print(f"\n📱 {name} ({pages} pages)...")
            scraper = ScraperClass()
            listings = scraper.scrape(max_pages=pages)
            all_listings.extend(listings)
            print(f"✅ {name}: {len(listings)} listings")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
        finally:
            if scraper:
                try:
                    scraper.close()
                except:
                    pass
            time.sleep(15)
    
    if not all_listings:
        print("❌ No data collected")
        return
    
    # Save data
    os.makedirs(RAW_DIR, exist_ok=True)
    df = pd.DataFrame(all_listings)
    
    # Save file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    today_file = os.path.join(RAW_DIR, f'listings_{timestamp}.csv')
    df.to_csv(today_file, index=False)
    print(f"\n💾 Saved: {today_file}")
    
    # Update master
    master_raw = os.path.join(RAW_DIR, 'all_listings_raw.csv')
    if os.path.exists(master_raw):
        existing = pd.read_csv(master_raw)
        df = pd.concat([existing, df], ignore_index=True)
    
    df = df.drop_duplicates(subset=['listing_id'], keep='last')
    df.to_csv(master_raw, index=False)
    
    # Stats
    elapsed = time.time() - start_time
    print(f"\n📊 Results:")
    print(f"   • Total collected: {len(all_listings):,}")
    print(f"   • After dedup: {len(df):,}")
    print(f"   • Time: {elapsed/60:.1f} minutes")
    print(f"   • File: {master_raw}")
    print("\n✅ Collection complete!\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
