# scrapers/buyrentkenya_scraper.py
"""
BuyRentKenya Selenium-based scraper for property listings.
"""
from bs4 import BeautifulSoup
import re
from datetime import datetime
from .selenium_base_scraper import SeleniumBaseScraper
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.locations import ALL_AREAS
from utils.helpers import clean_price, generate_id

class BuyRentKenyaScraper(SeleniumBaseScraper):
    def __init__(self):
        super().__init__(
            name="BuyRentKenya",
            base_url="https://www.buyrentkenya.com",
            headless=True
        )
    
    def get_page_url(self, page):
        return f"{self.base_url}/search?category=for-sale&location=nairobi&page={page}"
    
    def parse_listing(self, element):
        """Parse a listing from HTML element"""
        try:
            # Convert element to string if necessary
            if not isinstance(element, str):
                element_text = str(element)
            else:
                element_text = element
            
            # Parse HTML if needed
            if '<' in element_text:
                soup = BeautifulSoup(element_text, 'html.parser')
                container = soup.find(['div', 'article', 'li'])
            else:
                container = element.parent if hasattr(element, 'parent') else None
                if not container:
                    return None
            
            if not container:
                return None
            
            container_text = container.get_text(separator=" ", strip=True) if hasattr(container, 'get_text') else str(container)
            
            # Extract price
            price = clean_price(container_text)
            if not price:
                return None
            
            # Extract title
            title_elem = container.find(['h3', 'h4', 'h5', 'a']) if hasattr(container, 'find') else None
            title = title_elem.get_text(strip=True) if title_elem else "Property"
            
            # Extract location
            location = "Nairobi"
            for area in ALL_AREAS:
                area_pattern = area.replace('-', ' ').lower()
                if area_pattern in container_text.lower() or area.lower() in container_text.lower():
                    location = area.title().replace('-', ' ')
                    break
            
            # Extract bedrooms
            bedrooms = None
            bed_match = re.search(r'(\d+)\s*(?:bed|bedroom|br)', container_text, re.IGNORECASE)
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
            
            # Extract property type
            property_type = "Unknown"
            type_keywords = {
                'apartment': 'Apartment', 'flat': 'Apartment',
                'house': 'House', 'villa': 'Villa',
                'bungalow': 'Bungalow', 'maisonette': 'Maisonette',
                'townhouse': 'Townhouse', 'land': 'Land', 'commercial': 'Commercial'
            }
            for keyword, ptype in type_keywords.items():
                if re.search(rf'\b{keyword}\b', container_text, re.IGNORECASE):
                    property_type = ptype
                    break
            
            # Extract amenities
            amenities = []
            amenity_keywords = ['pool', 'gym', 'parking', 'security', 'garden', 
                               'balcony', 'furnished', 'cctv', 'internet', 'lift', 'security']
            for amenity in amenity_keywords:
                if amenity.lower() in container_text.lower():
                    amenities.append(amenity)
            
            # Get URL
            link = container.find('a', href=True) if hasattr(container, 'find') else None
            url = link['href'] if link else ""
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"
            
            listing = {
                'source': self.name,
                'listing_id': generate_id(url or container_text[:50]),
                'title': title[:200] if title else "Property",
                'location': location,
                'property_type': property_type,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'size_sqft': size_sqft,
                'price_kes': price,
                'amenities': '|'.join(amenities) if amenities else None,
                'listing_url': url,
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            return listing
            
        except Exception as e:
            self.logger.error(f"Error parsing listing: {str(e)}")
            return None