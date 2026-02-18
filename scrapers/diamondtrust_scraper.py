# scrapers/diamondtrust_scraper.py
from bs4 import BeautifulSoup
import re
from datetime import datetime
from .base_scraper import BaseScraper
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.locations import ALL_AREAS
from utils.helpers import clean_price, generate_id

class DiamondTrustScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            name="DiamondTrust",
            base_url="https://www.dtbkenya.co.ke"
        )
    
    def get_page_url(self, page):
        # Note: This URL pattern might need adjustment
        return f"{self.base_url}/property/property-for-sale?page={page}"
    
    def parse_listing(self, price_element, soup):
        """Parse a listing from price element"""
        try:
            # Get container
            container = price_element.parent
            for _ in range(5):
                if container and container.name == 'div':
                    break
                if container:
                    container = container.parent
            
            if not container:
                return None
            
            container_text = container.get_text()
            
            # Extract price
            price = clean_price(str(price_element))
            if not price:
                return None
            
            # Extract title
            title_elem = container.find(['h3', 'h4', 'h5'])
            title = title_elem.get_text(strip=True) if title_elem else "No title"
            
            # Extract location
            location = None
            for area in ALL_AREAS:
                if area.replace('-', ' ') in container_text.lower() or area in container_text.lower():
                    location = area.title().replace('-', ' ')
                    break
            if not location:
                location = "Nairobi"
            
            # Extract bedrooms
            bedrooms = None
            bed_match = re.search(r'(\d+)\s*(?:bed|bedroom)', container_text, re.IGNORECASE)
            if bed_match:
                bedrooms = int(bed_match.group(1))
            
            # Extract bathrooms
            bathrooms = None
            bath_match = re.search(r'(\d+)\s*(?:bath|bathroom)', container_text, re.IGNORECASE)
            if bath_match:
                bathrooms = int(bath_match.group(1))
            
            # Extract size
            size_sqft = None
            size_match = re.search(r'(\d+[.,]?\d*)\s*(?:m²|sqm|m2)', container_text, re.IGNORECASE)
            if size_match:
                try:
                    m2 = float(size_match.group(1).replace(',', '.'))
                    size_sqft = round(m2 * 10.764, 2)
                except:
                    pass
            
            return {
                'source': self.name,
                'listing_id': generate_id(container_text[:50]),
                'title': title[:200],
                'location': location,
                'property_type': 'Unknown',
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'size_sqft': size_sqft,
                'price_kes': price,
                'amenities': None,
                'listing_url': '',
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            return None