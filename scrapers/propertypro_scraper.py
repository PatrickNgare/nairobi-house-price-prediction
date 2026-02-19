# scrapers/propertypro_scraper.py
"""
PropertyPro Selenium-based scraper for property listings.
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

class PropertyProScraper(SeleniumBaseScraper):
    def __init__(self):
        super().__init__(
            name="PropertyPro",
            base_url="https://propertypro.co.ke",
            headless=True
        )
    
    def get_page_url(self, page):
        return f"{self.base_url}/properties-for-sale?page={page}"
    
    def get_listing_elements(self, soup):
        """Get PropertyPro listing elements"""
        # PropertyPro uses specific listing classes
        elements = soup.find_all(['div', 'article'], class_=lambda x: x and any(
            cls in x.lower() for cls in ['property', 'listing', 'card', 'item', 'result']
        ))
        if not elements:
            elements = soup.find_all(['div', 'li'], attrs={'data-property-id': True})
        if not elements:
            # Fallback
            elements = []
            for div in soup.find_all('div'):
                text = div.get_text()
                if 'KSh' in text and ('bed' in text.lower() or 'bath' in text.lower()):
                    elements.append(div)
                if len(elements) >= 30:
                    break
        return elements[:30]
    
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
            
            # Skip rental listings (looking for "for sale" only)
            if re.search(r'\bto let\b|\brent\b|\bleased\b', container_text, re.IGNORECASE):
                return None
            
            # Extract price - FIRST occurrence only
            price_match = re.search(r'KSh\s*([\d,]+(?:\.?\d+)?)\s*(?:M|K|Bn)?', container_text, re.IGNORECASE)
            if not price_match:
                price_match = re.search(r'([\d,]+(?:\.?\d+)?)\s*(?:M|K)?', container_text)
            if not price_match:
                return None
            
            try:
                price_str = price_match.group(1)
                price = int(float(price_str.replace(',', '')))
                # Sanity check - reasonable house prices in Nairobi (sale prices)
                if price < 500000 or price > 2000000000:
                    return None
            except:
                return None
            
            # Extract PID
            pid_match = re.search(r'PID\s*:?\s*([A-Z0-9]+)', container_text)
            pid = pid_match.group(1) if pid_match else generate_id(container_text[:50])
            
            # Extract title
            title_elem = container.find(['h3', 'h4', 'h5', 'a']) if hasattr(container, 'find') else None
            title = title_elem.get_text(strip=True) if title_elem else f"Property {pid}"
            
            # Robust location extraction
            location = "Nairobi"
            for area in ALL_AREAS:
                area_norm = area.replace('-', ' ').lower()
                if re.search(rf'\b{area_norm}\b', container_text.lower()):
                    location = area.title().replace('-', ' ')
                    break
            
            if location == "Nairobi":
                # Try to extract from common Nairobi neighborhoods
                nairobi_keywords = ['Westlands', 'Kilimani', 'Kileleshwa', 'Lavington', 'Karen', 'Runda', 
                                   'Parklands', 'Langata', 'Hurlingham', 'Buruburu', 'Donholm', 'Komarock', 
                                   'Embakasi', 'Kasarani', 'Roysambu', 'Zimmerman', 'Githurai', 'Ruiru', 
                                   'Juja', 'Ongata Rongai', 'Ngong', 'Syokimau', 'Kitengela']
                for kw in nairobi_keywords:
                    if re.search(rf'\b{kw.lower()}\b', container_text.lower()):
                        location = kw
                        break
            
            # Extract bedrooms
            bedrooms = None
            bed_match = re.search(r'(\d+)\s*(?:Beds?|Bedrooms?|Bed)', container_text, re.IGNORECASE)
            if bed_match:
                bedrooms = int(bed_match.group(1))
            
            # Extract bathrooms
            bathrooms = None
            bath_match = re.search(r'(\d+)\s*(?:Baths?|Bathrooms?|Bath)', container_text, re.IGNORECASE)
            if bath_match:
                bathrooms = int(bath_match.group(1))
            
            # Extract size
            size_sqft = None
            size_match = re.search(r'(\d+[.,]?\d*)\s*(?:m²|sqm|m2|sqft|sq ft)', container_text, re.IGNORECASE)
            if size_match:
                try:
                    size_val = float(size_match.group(1).replace(',', '.'))
                    if re.search(r'm²|sqm|m2', container_text, re.IGNORECASE):
                        size_sqft = round(size_val * 10.764, 2)
                    else:
                        size_sqft = size_val
                except Exception:
                    size_sqft = None
            
            # Property type classification
            property_type = "Unknown"
            type_keywords = {
                'apartment': 'Apartment', 'flat': 'Apartment', 'studio': 'Apartment', 'penthouse': 'Apartment',
                'house': 'House', 'villa': 'Villa', 'bungalow': 'Bungalow', 'maisonette': 'Maisonette', 
                'townhouse': 'Townhouse', 'duplex': 'Maisonette', 'land': 'Land', 'plot': 'Land', 
                'commercial': 'Commercial', 'office': 'Commercial', 'shop': 'Commercial', 
                'godown': 'Commercial', 'warehouse': 'Commercial'
            }
            for keyword, ptype in type_keywords.items():
                if re.search(rf'\b{keyword}\b', container_text, re.IGNORECASE):
                    property_type = ptype
                    break
            
            # Amenities extraction
            amenities = []
            amenity_keywords = ['pool', 'gym', 'parking', 'security', 'garden', 'cctv', 'fence', 
                               'backup generator', 'internet', 'balcony', 'furnished', 'playground', 
                               'clubhouse', 'ac', 'borehole', 'sauna', 'tennis', 'lift', 'generator', 
                               'water', 'wifi', 'fireplace', 'laundry', 'pet', 'solar', 'alarm', 
                               'intercom', 'air conditioning', 'spa']
            for amenity in amenity_keywords:
                if re.search(rf'\b{amenity}\b', container_text, re.IGNORECASE):
                    amenities.append(amenity)
            
            # Get URL
            url = f"{self.base_url}/property/{pid}" if pid else ""
            
            listing = {
                'source': self.name,
                'listing_id': pid,
                'title': title[:200] if title else "Property",
                'location': location,
                'property_type': property_type,
                'bedrooms': bedrooms if bedrooms and bedrooms > 0 else None,
                'bathrooms': bathrooms if bathrooms and bathrooms > 0 else None,
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