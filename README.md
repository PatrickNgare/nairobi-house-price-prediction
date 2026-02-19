# Nairobi House Price Prediction

Machine learning project to predict house prices in Nairobi using web-scraped property listing data.

## Quick Start

### 1. Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Collect Data
```bash
# Quick collection (500-800 listings, 5-10 min)
python quick_collect.py

# Or bulk collection (1000+ listings, 15-30 min)
python bulk_collect.py
```

### 3. Check Data
```bash
# View collected listings
head -20 data/raw/all_listings_raw.csv

# Count records
wc -l data/raw/all_listings_raw.csv
```

## Project Structure
```
scrapers/          # Web scrapers (BuyRentKenya, PropertyPro, DiamondTrust)
config/            # Configuration & locations
data/
  raw/             # Scraped CSV files
utils/             # Helper functions
main.py            # Standard collection script
quick_collect.py   # Fast collection (5-10 min)
bulk_collect.py    # Bulk collection (15-30 min)
```

## Data Fields
- **source**: Website source (BuyRentKenya, PropertyPro, DiamondTrust)
- **listing_id**: Unique property identifier
- **location**: Nairobi area/neighborhood
- **property_type**: Apartment, House, Townhouse, etc.
- **bedrooms, bathrooms, size_sqft**: Property features
- **price_kes**: Price in Kenyan Shillings
- **amenities**: Available features
- **scrape_date**: Collection timestamp

## Technology Stack
- **Web Scraping**: Selenium 4 + BeautifulSoup
- **Data Processing**: Pandas
- **ML Framework**: (scikit-learn, TensorFlow, etc. - to be added)
- **Language**: Python 3.8+

## Next Steps
- [ ] Collect 1000+ listings
- [ ] Clean & preprocess data
- [ ] Build ML model (regression)
- [ ] Train & evaluate
- [ ] Deploy predictions API

## Issues
- Chrome/Chromium browser required for scraping
- Some websites may block automated requests
- Data quality varies by source

