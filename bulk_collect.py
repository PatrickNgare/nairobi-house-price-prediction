#!/usr/bin/env python3
"""
Enhanced data collection script for bulk property data gathering.
Collects thousands of listings for robust machine learning models.
"""
import pandas as pd
import os
from datetime import datetime
import time
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BulkCollector")

# Import scrapers
from scrapers.buyrentkenya_scraper import BuyRentKenyaScraper
from scrapers.propertypro_scraper import PropertyProScraper
from scrapers.diamondtrust_scraper import DiamondTrustScraper

# Import config
from config.settings import RAW_DIR

def print_header():
    """Print project header"""
    print("\n" + "="*80)
    print("🏠 NAIROBI PROPERTY DATA - BULK COLLECTION ")
    print("="*80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Collecting thousands of listings for ML training")
    print("="*80)

def collect_bulk_data(max_pages_per_scraper=50):
    """
    Collect bulk data from all available scrapers.
    
    Args:
        max_pages_per_scraper: Number of pages to scrape per source
    """
    all_listings = []
    source_stats = {}
    
    scrapers_config = [
        (BuyRentKenyaScraper, "BuyRentKenya"),
        (PropertyProScraper, "PropertyPro"),
        (DiamondTrustScraper, "DiamondTrust"),
    ]
    
    for ScraperClass, name in scrapers_config:
        scraper = None
        try:
            print(f"\n{'─'*70}")
            print(f"📱 Initializing {name} scraper...")
            
            scraper = ScraperClass()
            logger.info(f"Starting scraper: {name}")
            
            print(f"🔄 Collecting from {name} ({max_pages_per_scraper} pages)...")
            
            # Scrape listings - collect many pages
            listings = scraper.scrape(max_pages=max_pages_per_scraper)
            all_listings.extend(listings)
            
            # Record statistics
            source_stats[name] = {
                'count': len(listings),
                'pages': scraper.stats['pages_scraped'],
                'errors': scraper.stats['errors']
            }
            
            logger.info(f"{name} completed: {len(listings)} listings")
            print(f"✅ {name} complete: {len(listings)} listings collected")
            
        except Exception as e:
            logger.error(f"Error in {name}: {str(e)}", exc_info=True)
            print(f"❌ Error in {name}: {str(e)}")
            source_stats[name] = {'count': 0, 'pages': 0, 'errors': 1}
        
        finally:
            # Always close the driver
            if scraper:
                try:
                    scraper.close()
                    logger.info(f"Closed {name} driver")
                except:
                    pass
            
            # Add delay between scrapers to avoid overwhelming the sites
            if ScraperClass != scrapers_config[-1][0]:
                print(f"⏳ Waiting 30 seconds before next scraper...")
                time.sleep(30)
    
    return all_listings, source_stats

def save_bulk_data(listings):
    """Save bulk data to CSV files"""
    if not listings:
        print("❌ No data to save")
        logger.error("No listings collected")
        return None
    
    df = pd.DataFrame(listings)
    
    # Ensure directories exist
    os.makedirs(RAW_DIR, exist_ok=True)
    
    # Save today's data with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    today_file = os.path.join(RAW_DIR, f'listings_{timestamp}.csv')
    df.to_csv(today_file, index=False)
    print(f"\n💾 Data saved: {today_file}")
    logger.info(f"Today's data saved: {today_file}")
    
    # Update master file with deduplication
    master_raw = os.path.join(RAW_DIR, 'all_listings_raw.csv')
    
    if os.path.exists(master_raw):
        existing_df = pd.read_csv(master_raw)
        df = pd.concat([existing_df, df], ignore_index=True)
        print(f"📊 Combined with existing {len(existing_df)} records")
    
    # Remove duplicates - keep most recent entry
    df = df.drop_duplicates(subset=['listing_id'], keep='last')
    print(f"🔄 After deduplication: {len(df)} unique records")
    
    df.to_csv(master_raw, index=False)
    print(f"💾 Master dataset updated: {master_raw}")
    logger.info(f"Master file saved with {len(df)} total unique listings")
    
    return df

def print_statistics(all_listings, source_stats, df):
    """Print collection statistics"""
    print("\n" + "="*80)
    print("📊 BULK COLLECTION STATISTICS")
    print("="*80)
    
    print(f"\n📈 Overall Results:")
    print(f"   • Total listings collected: {len(all_listings):,}")
    print(f"   • Unique listings after dedup: {len(df):,}")
    print(f"   • Duplicates removed: {len(all_listings) - len(df):,}")
    
    print(f"\n🏢 Breakdown by source:")
    for source, stats in source_stats.items():
        print(f"   • {source}: {stats['count']:,} listings ({stats['pages']} pages, {stats['errors']} errors)")
    
    if len(df) > 0:
        print(f"\n📍 Data Summary:")
        print(f"   • Unique locations: {df['location'].nunique()}")
        print(f"   • Price range: KSh {df['price_kes'].min():,.0f} - KSh {df['price_kes'].max():,.0f}")
        print(f"   • Average price: KSh {df['price_kes'].mean():,.0f}")
        print(f"   • Property types: {', '.join(df['property_type'].unique()[:5])}")
        
        if 'bedrooms' in df.columns:
            valid_beds = df[df['bedrooms'].notna()]
            if len(valid_beds) > 0:
                print(f"   • Average bedrooms: {valid_beds['bedrooms'].mean():.1f}")
        
        if 'bathrooms' in df.columns:
            valid_baths = df[df['bathrooms'].notna()]
            if len(valid_baths) > 0:
                print(f"   • Average bathrooms: {valid_baths['bathrooms'].mean():.1f}")
        
        print(f"\n🗺️  Top 5 locations:")
        for i, (loc, count) in enumerate(df['location'].value_counts().head(5).items(), 1):
            print(f"   {i}. {loc}: {count} listings")
        
        print(f"\n🏘️  Property type distribution:")
        for ptype, count in df['property_type'].value_counts().head(5).items():
            pct = (count / len(df)) * 100
            print(f"   • {ptype}: {count} ({pct:.1f}%)")

def main():
    """Main execution function"""
    start_time = time.time()
    
    print_header()
    
    # Ask user for pages to collect
    print(f"\n⚙️  Configuration:")
    print(f"   Current setting: 50 pages per scraper")
    print(f"   Estimated data: 1,500+ listings (50-100 per page × 3 sources)")
    print(f"   Estimated time: 15-30 minutes")
    
    print(f"\n🚀 Starting bulk data collection...")
    
    # Collect data (50 pages per scraper = ~1500+ records)
    listings, source_stats = collect_bulk_data(max_pages_per_scraper=50)
    
    if not listings:
        print("\n❌ No data collected. Exiting.")
        logger.error("No data collected from any scraper")
        return
    
    # Save the data
    df = save_bulk_data(listings)
    
    # Print statistics
    print_statistics(listings, source_stats, df)
    
    elapsed = time.time() - start_time
    print(f"\n⏱️  Time elapsed: {elapsed/60:.1f} minutes ({elapsed:.0f} seconds)")
    print(f"✅ BULK COLLECTION COMPLETE!")
    print("="*80 + "\n")
    
    logger.info(f"Bulk collection completed successfully in {elapsed:.1f} seconds with {len(df)} unique listings")
    
    print(f"💡 Next steps:")
    print(f"   1. Analyze the data: python analyze_data.py")
    print(f"   2. Clean and prepare: python preprocess_data.py")
    print(f"   3. Train ML model: python train_model.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Data collection interrupted by user")
        logger.info("Data collection interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
