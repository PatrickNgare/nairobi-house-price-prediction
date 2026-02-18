# scrapers/base_scraper.py
import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
from retry import retry
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, source_name: str, base_url: str, delay: float = 3):
        self.source_name = source_name
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.ua = UserAgent()
        self.logger = logging.getLogger(f"{source_name}Scraper")
        self.stats = {
            'pages_scraped': 0,
            'listings_found': 0,
            'listings_parsed': 0,
            'errors': 0
        }
        
    def _get_headers(self) -> Dict:
        """Generate random headers"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
        }
    
    @retry(tries=3, delay=2, backoff=2)
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        try:
            time.sleep(self.delay + random.uniform(1, 3))  # Add randomness
            response = self.session.get(
                url, 
                headers=self._get_headers(),
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                return response
            elif response.status_code == 404:
                self.logger.warning(f"Page not found: {url}")
                return None
            elif response.status_code == 403:
                self.logger.error(f"Access forbidden (403): {url}")
                time.sleep(60)  # Wait longer if blocked
                return None
            else:
                response.raise_for_status()
                
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {str(e)}")
            return None
    
    def generate_listing_id(self, url: str) -> str:
        """Generate unique ID from URL"""
        return hashlib.md5(url.encode()).hexdigest()[:8]
    
    def parse_price(self, price_str: str) -> Optional[int]:
        """Parse price string to integer KES"""
        if not price_str or not isinstance(price_str, str):
            return None
        
        # Remove common patterns
        price_str = price_str.lower()
        
        # Check for "POA" or "Call for price"
        if any(x in price_str for x in ['poa', 'call', 'contact', 'price on application']):
            return None
        
        # Remove currency symbols and text
        price_str = re.sub(r'(ksh|kes|k\.?shs?|price|ksh\.?|sh\.?|/=)', '', price_str, flags=re.IGNORECASE)
        price_str = re.sub(r'[^\d\s\.,-]', '', price_str)
        
        # Handle ranges (take average)
        if '-' in price_str:
            prices = re.findall(r'\d+[\d,]*\.?\d*', price_str)
            if len(prices) >= 2:
                try:
                    p1 = float(prices[0].replace(',', ''))
                    p2 = float(prices[1].replace(',', ''))
                    return int((p1 + p2) / 2)
                except:
                    pass
        
        # Handle "million" or "m"
        if 'million' in price_str or 'm' in price_str:
            numbers = re.findall(r'\d+\.?\d*', price_str)
            if numbers:
                try:
                    return int(float(numbers[0]) * 1000000)
                except:
                    pass
        
        # Standard number extraction
        numbers = re.findall(r'\d+[\d,]*\.?\d*', price_str)
        if numbers:
            try:
                # Remove commas and convert to float
                return int(float(numbers[0].replace(',', '')))
            except:
                pass
        
        return None
    
    def parse_size(self, size_str: str) -> Optional[float]:
        """Parse size string to square feet"""
        if not size_str or not isinstance(size_str, str):
            return None
        
        size_str = size_str.lower()
        
        # Extract numbers
        numbers = re.findall(r'\d+\.?\d*', size_str)
        if not numbers:
            return None
        
        try:
            size_value = float(numbers[0])
        except:
            return None
        
        # Check if in sq meters (m², sqm, sq m)
        if any(x in size_str for x in ['m²', 'sqm', 'sq m', 'm2']):
            # Convert to sq ft (1 sqm = 10.764 sqft)
            return round(size_value * 10.764, 2)
        
        # Already in sq ft (sqft, sq ft)
        if any(x in size_str for x in ['sqft', 'sq ft', 'ft²']):
            return size_value
        
        # If no unit specified, assume sq ft
        return size_value
    
    def parse_bedrooms(self, text: str) -> Optional[int]:
        """Extract number of bedrooms from text"""
        if not text:
            return None
        
        text = text.lower()
        
        # Look for patterns like "3 bed", "3 bedroom", "3br"
        patterns = [
            r'(\d+)\s*bed(?:room)?s?',
            r'(\d+)\s*br',
            r'(\d+)-bedroom',
            r'bedrooms?\s*(\d+)',
            r'(\d+)\s*room'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        # Check for "studio"
        if 'studio' in text:
            return 0
            
        return None
    
    def parse_bathrooms(self, text: str) -> Optional[int]:
        """Extract number of bathrooms from text"""
        if not text:
            return None
        
        text = text.lower()
        
        patterns = [
            r'(\d+)\s*bath(?:room)?s?',
            r'(\d+)\s*br',
            r'bathrooms?\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        return None
    
    def extract_amenities(self, text: str) -> List[str]:
        """Extract amenities from text"""
        if not text:
            return []
        
        text = text.lower()
        amenities_found = []
        
        # Common Nairobi amenities
        amenity_patterns = {
            'pool': r'pool|swimming',
            'gym': r'gym|fitness',
            'parking': r'parking|car park',
            'security': r'security|guard|24hr',
            'generator': r'generator|backup power',
            'elevator': r'elevator|lift',
            'garden': r'garden|yard',
            'balcony': r'balcony',
            'furnished': r'furnished',
            'serviced': r'serviced',
            'wifi': r'wifi|internet',
            'play area': r'playground|play area',
            'clubhouse': r'clubhouse',
            'cctv': r'cctv|camera',
            'ac': r'ac|air condition|aircon',
            'backup water': r'backup water|borehole|tank',
            'dsl': r'dsl|satellite',
            'sauna': r'sauna',
            'tennis': r'tennis'
        }
        
        for amenity, pattern in amenity_patterns.items():
            if re.search(pattern, text):
                amenities_found.append(amenity)
        
        return list(set(amenities_found))  # Remove duplicates
    
    def standardize_location(self, location: str) -> Optional[str]:
        """Standardize location name"""
        if not location:
            return None
        
        location = location.lower().strip()
        
        # Remove common prefixes/suffixes
        location = re.sub(r'(nairobi|along|off|near|in|at|,|\.|road|drive|avenue|lane)', '', location)
        location = location.strip()
        
        return location
    
    def validate_listing(self, listing: Dict) -> bool:
        """Validate if listing has minimum required data"""
        required_fields = ['price_kes', 'location', 'property_type']
        
        # Must have at least price and location
        if not listing.get('price_kes') or not listing.get('location'):
            return False
        
        # Basic type validation
        if listing.get('price_kes', 0) < 500000:  # Too cheap
            return False
            
        if listing.get('price_kes', 0) > 500000000:  # Too expensive
            return False
            
        return True
    
    def scrape_page(self, url: str) -> List[Dict]:
        """Scrape a single page - to be implemented by child classes"""
        raise NotImplementedError
    
    def scrape(self, start_page: int = 1, max_pages: int = 10) -> List[Dict]:
        """Main scraping method"""
        all_listings = []
        
        for page in range(start_page, start_page + max_pages):
            url = self.get_page_url(page)
            self.logger.info(f"Scraping page {page}: {url}")
            
            listings = self.scrape_page(url)
            
            if not listings:
                self.logger.info(f"No listings found on page {page}, stopping")
                break
            
            all_listings.extend(listings)
            self.stats['listings_found'] += len(listings)
            
            # Stop if we have enough listings
            if len(all_listings) >= 300:  # Minimum target
                self.logger.info(f"Reached target of {len(all_listings)} listings")
                break
        
        return all_listings[:500]  # Cap at 500
    
    def get_page_url(self, page: int) -> str:
        """Get URL for a specific page - to be implemented"""
        raise NotImplementedError