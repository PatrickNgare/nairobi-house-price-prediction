#!/usr/bin/env python3
"""
Main orchestration script for Nairobi property data collection.
Uses Selenium-based web scrapers for robust data extraction.
"""
import pandas as pd
import os
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Main")

# Import scrapers
from scrapers.buyrentkenya_scraper import BuyRentKenyaScraper
from scrapers.propertypro_scraper import PropertyProScraper

# Import config
from config.settings import (
    RAW_DIR, PROCESSED_DIR, MASTER_FILE, TODAY_FILE,
    TARGET_LISTINGS, MIN_LISTINGS_PER_SOURCE
)

def print_header():
    """Print project header"""
    print("\n" + "="*80)
    print("🏠 NAIROBI PROPERTY DATA COLLECTION PROJECT - SELENIUM EDITION")
    print("="*80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: {TARGET_LISTINGS}+ listings")
    print("="*80)

def run_scrapers():
    """
    Run all scrapers sequentially and collect listings.
    """
    all_listings = []
    source_stats = {}
    
    scrapers = [
        BuyRentKenyaScraper(),
        PropertyProScraper(),
    ]
    
    for scraper in scrapers:
        try:
            print(f"\n{'─'*60}")
            logger.info(f"Starting scraper: {scraper.name}")
            
            # Scrape listings
            listings = scraper.scrape(max_pages=5)
            all_listings.extend(listings)
            
            # Record statistics
            source_stats[scraper.name] = {
                'count': len(listings),
                'pages': scraper.stats['pages_scraped'],
                'errors': scraper.stats['errors']
            }
            
            logger.info(f"{scraper.name} completed: {len(listings)} listings")
            print(f"✅ {scraper.name} complete: {len(listings)} listings collected")
            
        except Exception as e:
            logger.error(f"Error in {scraper.name}: {str(e)}", exc_info=True)
            print(f"❌ Error in {scraper.name}: {str(e)}")
            source_stats[scraper.name] = {'count': 0, 'pages': 0, 'errors': 1}
        
        finally:
            # Always close the driver
            try:
                scraper.close()
            except:
                pass
    
    return all_listings, source_stats

def save_raw_data(listings):
    """Save raw data to CSV files"""
    if not listings:
        print("❌ No data to save")
        logger.error("No listings collected")
        return None
    
    df = pd.DataFrame(listings)
    
    # Save today's data
    df.to_csv(TODAY_FILE, index=False)
    print(f"\n💾 Raw data saved: {TODAY_FILE}")
    logger.info(f"Today's data saved: {TODAY_FILE}")
    
    # Update master raw file
    master_raw = os.path.join(RAW_DIR, 'all_listings_raw.csv')
    if os.path.exists(master_raw):
        existing = pd.read_csv(master_raw)
        df = pd.concat([existing, df], ignore_index=True)
        df = df.drop_duplicates(subset=['listing_id', 'price_kes'], keep='last')
    
    df.to_csv(master_raw, index=False)
    print(f"💾 Master raw updated: {master_raw}")
    logger.info(f"Master raw updated: {master_raw}")
    
    return df

def print_statistics(all_listings, source_stats):
    """Print collection statistics"""
    print("\n" + "="*80)
    print("📊 COLLECTION STATISTICS")
    print("="*80)
    
    print(f"Total listings collected: {len(all_listings)}")
    print(f"\nBreakdown by source:")
    
    for source, stats in source_stats.items():
        print(f"  • {source}: {stats['count']} listings ({stats['pages']} pages, {stats['errors']} errors)")
    
    if all_listings:
        df = pd.DataFrame(all_listings)
        print(f"\nData Summary:")
        print(f"  • Unique locations: {df['location'].nunique()}")
        print(f"  • Price range: KSh {df['price_kes'].min():,.0f} - KSh {df['price_kes'].max():,.0f}")
        print(f"  • Property types: {', '.join(df['property_type'].unique()[:5])}")
        
        if 'bedrooms' in df.columns:
            avg_beds = df[df['bedrooms'].notna()]['bedrooms'].mean()
            print(f"  • Average bedrooms: {avg_beds:.1f}")

def main():
    """Main execution function"""
    start_time = time.time()
    
    print_header()
    print("\n🚀 Starting data collection with Selenium...\n")
    
    # Run all scrapers
    listings, source_stats = run_scrapers()
    
    if not listings:
        print("\n❌ No data collected. Exiting.")
        logger.error("No data collected from any scraper")
        return
    
    # Save the data
    raw_df = save_raw_data(listings)
    
    # Print statistics
    print_statistics(listings, source_stats)
    
    elapsed = time.time() - start_time
    print(f"\n⏱️  Time elapsed: {elapsed:.1f} seconds")
    print(f"✅ DATA COLLECTION COMPLETE!")
    print("="*80 + "\n")
    
    logger.info(f"Data collection completed successfully in {elapsed:.1f} seconds")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Data collection interrupted by user")
        logger.info("Data collection interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        logger.error(f"Fatal error: {str(e)}", exc_info=True)