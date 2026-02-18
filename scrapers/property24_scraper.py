# scrapers/property24_scraper.py
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime
import re
from .base_scraper import BaseScraper

class Property24Scraper(BaseScraper):
    def __init__(self, delay: float = 3):
        super().__init__(
            source_name="Property24",
            base_url="https://www.property24.co.ke",
            delay=delay
        )
    
    def get_page_url(self, page: int) -> str:
        """Get URL for a specific page"""
        return f"{self.base_url}/for-sale/nairobi/{page}"
    
    def scrape_page(self, url: str) -> List[Dict]:
        """Scrape a single page of listings"""
        response = self._make_request(url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'lxml')
        listings = []
        
        # Find all property cards - Property24 uses specific classes
        property_cards = soup.find_all('div', class_=re.compile(r'p24_content|propertyListing'))
        
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
        title_elem = card.find('span', class_=re.compile(r'p24_title'))
        title = title_elem.text.strip() if title_elem else ""
        
        # Extract location
        location_elem = card.find('span', class_=re.compile(r'p24_location'))
        location_text = location_elem.text.strip() if location_elem else ""
        
        # Extract price
        price_elem = card.find('span', class_=re.compile(r'p24_price'))
        price_text = price_elem.text.strip() if price_elem else ""
        price_kes = self.parse_price(price_text)
        
        # Skip if no price
        if not price_kes:
            return None
        
        # Get card text
        card_text = card.get_text().lower()
        
        # Extract features from description
        description_elem = card.find('div', class_=re.compile(r'p24_description'))
        description = description_elem.text.lower() if description_elem else ""
        
        # Parse bedrooms, bathrooms, size
        bedrooms = self.parse_bedrooms(description) or self.parse_bedrooms(card_text)
        bathrooms = self.parse_bathrooms(description) or self.parse_bathrooms(card_text)
        
        # Parse size from description
        size_sqft = None
        size_match = re.search(r'(\d+)\s*(?:m²|sqm|sq m)', description)
        if size_match:
            size_sqft = float(size_match.group(1)) * 10.764  # Convert to sqft
        
        # Extract amenities
        amenities = self.extract_amenities(description)
        
        # Get listing URL
        link_elem = card.find('a', href=True)
        listing_url = f"{self.base_url}{link_elem['href']}" if link_elem else ""
        
        # Determine property type
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