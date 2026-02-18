# scrapers/propertypro_scraper.py
from bs4 import BeautifulSoup
import re
from datetime import datetime
from .base_scraper import BaseScraper
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.locations import ALL_AREAS
from utils.helpers import clean_price, generate_id

class PropertyProScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            name="PropertyPro",
            base_url="https://propertypro.co.ke"
        )
    
    def get_page_url(self, page):
        return f"{self.base_url}/properties-for-sale?page={page}"
    
    def parse_listing(self, price_element, soup):
        """Parse a listing from price element with robust container search and fully improved extraction"""
        try:
            container = price_element.parent
            for _ in range(5):
                if container and (container.find(['h3', 'h4', 'h5']) or 'PID' in str(container)):
                    break
                if container:
                    container = container.parent
            if not container:
                print("  ⚠️ PropertyPro: No container found for price element")
                return None
            container_text = container.get_text(separator=" ", strip=True)
            # Extract price
            price = clean_price(str(price_element))
            if not price:
                print("  ⚠️ PropertyPro: No price found")
                return None
            # Extract PID
            pid_match = re.search(r'PID\s*:?\s*([A-Z0-9]+)', container_text)
            pid = pid_match.group(1) if pid_match else generate_id(container_text[:50])
            # Extract title
            title_elem = container.find(['h3', 'h4', 'h5'])
            title = title_elem.get_text(strip=True) if title_elem else f"Property {pid}" if pid else "No title"
            # Robust location extraction
            location = None
            for area in ALL_AREAS:
                area_norm = area.replace('-', ' ').lower()
                if re.search(rf'\b{area_norm}\b', container_text.lower()):
                    location = area.title().replace('-', ' ')
                    break
            if not location:
                # Try to extract from address patterns
                loc_match = re.search(r'Location\s*:?\s*([A-Za-z\s\-]+)', container_text)
                if loc_match:
                    location = loc_match.group(1).strip().title()
                else:
                    # Try to extract from common Nairobi neighborhoods
                    nairobi_keywords = ['Nairobi', 'Westlands', 'Kilimani', 'Kileleshwa', 'Lavington', 'Karen', 'Runda', 'Parklands', 'Langata', 'Hurlingham', 'Buruburu', 'Donholm', 'Komarock', 'Embakasi', 'Kasarani', 'Roysambu', 'Zimmerman', 'Githurai', 'Ruiru', 'Juja', 'Ongata Rongai', 'Ngong', 'Syokimau', 'Kitengela', 'Athiriver', 'Machakos', 'Thika', 'Limuru', 'Kiambu', 'Kikuyu']
                    for kw in nairobi_keywords:
                        if re.search(rf'\b{kw.lower()}\b', container_text.lower()):
                            location = kw
                            break
                    if not location:
                        location = "Nairobi"
            # Improved bedrooms extraction
            bedrooms = 0
            bed_match = re.search(r'(\d+)\s*(?:Beds?|Bedrooms?|Bed)', container_text, re.IGNORECASE)
            if bed_match:
                bedrooms = int(bed_match.group(1))
            # Improved bathrooms extraction
            bathrooms = 0
            bath_match = re.search(r'(\d+)\s*(?:Baths?|Bathrooms?|Bath)', container_text, re.IGNORECASE)
            if bath_match:
                bathrooms = int(bath_match.group(1))
            # Improved size extraction
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
            # Fully improved property type classification
            property_type = "Unknown"
            type_keywords = {
                'apartment': 'Apartment', 'flat': 'Apartment', 'studio': 'Apartment', 'penthouse': 'Apartment',
                'house': 'House', 'villa': 'Villa', 'bungalow': 'Bungalow', 'maisonette': 'Maisonette', 'townhouse': 'Townhouse', 'duplex': 'Maisonette',
                'land': 'Land', 'plot': 'Land', 'commercial': 'Commercial', 'office': 'Commercial', 'shop': 'Commercial', 'godown': 'Commercial', 'warehouse': 'Commercial', 'retail': 'Commercial', 'hotel': 'Commercial', 'guesthouse': 'Commercial', 'bed & breakfast': 'Commercial', 'hostel': 'Commercial'
            }
            for keyword, ptype in type_keywords.items():
                if re.search(rf'\b{keyword}\b', container_text.lower()):
                    property_type = ptype
                    break
            # Fully expanded amenities extraction
            amenities = []
            amenity_keywords = ['pool', 'gym', 'parking', 'security', 'garden', 'cctv', 'fence', 'backup generator', 'internet', 'balcony', 'furnished', 'playground', 'clubhouse', 'ac', 'borehole', 'sauna', 'tennis', 'lift', 'generator', 'water', 'wifi', 'fireplace', 'laundry', 'pet', 'solar', 'alarm', 'intercom', 'air conditioning', 'spa', 'restaurant', 'bar', 'roof terrace', 'conference', 'kids area', 'smart home', 'walk-in closet', 'pantry', 'servant quarters', 'dsq', 'study', 'office', 'shop', 'store', 'garage', 'carport', 'shower', 'bathtub', 'jacuzzi', 'steam', 'terrace', 'patio', 'veranda', 'garden shed', 'gazebo', 'bbq', 'basketball', 'football', 'golf', 'squash', 'tennis court', 'play area', 'library', 'cinema', 'games room', 'music room', 'art studio', 'workshop', 'storage', 'safe', 'vault', 'wine cellar', 'cellar', 'basement', 'attic', 'loft', 'mezzanine', 'rooftop', 'sky lounge', 'sky garden', 'sky pool', 'sky gym', 'sky bar', 'sky restaurant', 'sky terrace', 'sky deck', 'sky office', 'sky shop', 'sky store', 'sky parking', 'sky security', 'sky garden', 'sky playground', 'sky clubhouse', 'sky ac', 'sky borehole', 'sky sauna', 'sky tennis', 'sky lift', 'sky generator', 'sky water', 'sky wifi', 'sky fireplace', 'sky laundry', 'sky pet', 'sky solar', 'sky alarm', 'sky intercom']
            for amenity in amenity_keywords:
                if re.search(rf'\b{amenity}\b', container_text.lower()):
                    amenities.append(amenity)
            # Get URL
            url = f"{self.base_url}/property/{pid}" if pid else ""
            # Debug logging
            print(f"  🏷️ Parsed PropertyPro: PID={pid}, Title={title}, Location={location}, Price={price}, Bedrooms={bedrooms}, Bathrooms={bathrooms}, Size={size_sqft}, Type={property_type}, Amenities={amenities}, URL={url}")
            return {
                'source': self.name,
                'listing_id': pid,
                'title': title[:200],
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
        except Exception as e:
            print(f"  ❌ PropertyPro: Exception in parse_listing - {str(e)}")
            return None