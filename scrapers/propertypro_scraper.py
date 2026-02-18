# scrapers/propertypro_scraper.py
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime
import re
from .base_scraper import BaseScraper

class PropertyProScraper(BaseScraper):
    def __init__(self, delay: float = 3):
        super().__init__(
            source_name="PropertyPro",
            base_url="https://propertypro.co.ke",
            delay=delay
        )
    
    def get_page_url(self, page: int) -> str:
        """Get URL for a specific page"""
        return f"{self.base_url}/properties-for-sale/nairobi?page={page}"
    
    def scrape_page(self, url: str) -> List[Dict]:
        """Scrape a single page of listings"""
        response = self._make_request(url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'lxml')
        listings = []
        
        # Find all property cards
        property_cards = soup.find_all('div', class_=re.compile(r'property-item|card|listing'))
        
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
        title_elem = card.find(['h4', 'h5', 'h6'], class_=re.compile(r'title|property-name|heading'))
        title = title_elem.text.strip() if title_elem else ""
        
        # Extract location
        location_elem = card.find(['div', 'p'], class_=re.compile(r'location|address|neighborhood'))
        location_text = location_elem.text.strip() if location_elem else ""
        
        # Extract price
        price_elem = card.find('div', class_=re.compile(r'price|cost|amount'))
        price_text = price_elem.text.strip() if price_elem else ""
        price_kes = self.parse_price(price_text)
        
        # Skip if no price
        if not price_kes:
            return None
        
        # Get card text for feature extraction
        card_text = card.get_text().lower()
        
        # Extract bedrooms, bathrooms, size from details section
        details = card.find_all('span', class_=re.compile(r'detail|feature|spec'))
        
        bedrooms = None
        bathrooms = None
        size_sqft = None
        
        for detail in details:
            detail_text = detail.text.lower()
            if 'bed' in detail_text:
                bedrooms = self.parse_bedrooms(detail_text)
            elif 'bath' in detail_text:
                bathrooms = self.parse_bathrooms(detail_text)
            elif 'sq' in detail_text or 'm²' in detail_text:
                size_sqft = self.parse_size(detail_text)
        
        # If not found in details, try the full text
        if not bedrooms:
            bedrooms = self.parse_bedrooms(card_text)
        if not bathrooms:
            bathrooms = self.parse_bathrooms(card_text)
        if not size_sqft:
            size_elem = card.find(['div', 'span'], string=re.compile(r'\d+\s*(sq|m²)', re.I))
            if size_elem:
                size_sqft = self.parse_size(size_elem.text)
        
        # Extract amenities
        amenities = self.extract_amenities(card_text)
        
        # Get listing URL
        link_elem = card.find('a', href=True)
        listing_url = f"{self.base_url}{link_elem['href']}" if link_elem and link_elem['href'].startswith('/') else (
            link_elem['href'] if link_elem else ""
        )
        
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