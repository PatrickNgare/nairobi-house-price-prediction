# scrapers/buyrentkenya_scraper.py
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime
import re
from .base_scraper import BaseScraper

class BuyRentKenyaScraper(BaseScraper):
    def __init__(self, delay: float = 3):
        super().__init__(
            source_name="BuyRentKenya",
            base_url="https://www.buyrentkenya.com",
            delay=delay
        )
    
    def get_page_url(self, page: int) -> str:
        """Get URL for a specific page"""
        return f"{self.base_url}/property-for-sale/nairobi?page={page}"
    
    def scrape_page(self, url: str) -> List[Dict]:
        """Scrape a single page of listings"""
        response = self._make_request(url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'lxml')
        listings = []
        
        # Find all property cards - adjust selectors based on actual HTML
        property_cards = soup.find_all('div', class_=re.compile(r'property-card|listing-item|property-item'))
        
        if not property_cards:
            # Try alternative selectors
            property_cards = soup.find_all('article', class_=re.compile(r'property|listing'))
        
        self.logger.info(f"Found {len(property_cards)} potential listings")
        
        for card in property_cards:
            try:
                listing = self.parse_listing_card(card)
                if listing and self.validate_listing(listing):
                    listings.append(listing)
                    self.stats['listings_parsed'] += 1
            except Exception as e:
                self.logger.error(f"Error parsing listing: {str(e)}")
                self.stats['errors'] += 1
        
        return listings
    
    def parse_listing_card(self, card) -> Optional[Dict]:
        """Parse a single listing card"""
        
        # Extract title
        title_elem = card.find(['h3', 'h4', 'h5'], class_=re.compile(r'title|heading'))
        title = title_elem.text.strip() if title_elem else ""
        
        # Extract location
        location_elem = card.find(['div', 'span', 'p'], class_=re.compile(r'location|address|area'))
        location_text = location_elem.text.strip() if location_elem else ""
        
        # Extract price
        price_elem = card.find(['div', 'span'], class_=re.compile(r'price|cost'))
        price_text = price_elem.text.strip() if price_elem else ""
        price_kes = self.parse_price(price_text)
        
        # Skip if no price
        if not price_kes:
            return None
        
        # Get card text for feature extraction
        card_text = card.get_text().lower()
        
        # Extract bedrooms
        bedrooms = self.parse_bedrooms(card_text)
        
        # Extract bathrooms
        bathrooms = self.parse_bathrooms(card_text)
        
        # Extract size
        size_elem = card.find(['div', 'span'], class_=re.compile(r'size|area|sq'))
        size_text = size_elem.text.strip() if size_elem else ""
        size_sqft = self.parse_size(size_text) if size_text else None
        
        # Extract amenities
        amenities = self.extract_amenities(card_text)
        
        # Get listing URL
        link_elem = card.find('a', href=True)
        listing_url = f"{self.base_url}{link_elem['href']}" if link_elem and link_elem['href'].startswith('/') else (
            link_elem['href'] if link_elem else ""
        )
        
        # Determine property type from title
        property_type = "Unknown"
        title_lower = title.lower()
        for ptype in ['apartment', 'house', 'villa', 'bungalow', 'maisonette', 'townhouse', 'land', 'commercial']:
            if ptype in title_lower:
                property_type = ptype.capitalize()
                break
        
        return {
            'listing_id': self.generate_listing_id(listing_url),
            'source': self.source_name,
            'title': title,
            'location': self.standardize_location(location_text),
            'property_type': property_type,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'size_sqft': size_sqft,
            'price_kes': price_kes,
            'amenities': '|'.join(amenities) if amenities else '',
            'listing_date': datetime.now().strftime('%Y-%m-%d'),
            'listing_url': listing_url,
            'scraped_at': datetime.now().isoformat()
        }