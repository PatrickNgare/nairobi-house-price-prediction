# scrapers/base_scraper.py
import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
from datetime import datetime
import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import clean_price, generate_id
from config.settings import REQUEST_DELAY, TIMEOUT

class BaseScraper:
    def __init__(self, name, base_url):
        self.name = name
        self.base_url = base_url
        self.ua = UserAgent()
        self.session = requests.Session()
        self.listings = []
        self.stats = {
            'pages_scraped': 0,
            'listings_found': 0,
            'errors': 0
        }
    
    def get_headers(self):
        """Get random headers"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def make_request(self, url):
        """Make HTTP request with retry"""
        try:
            time.sleep(REQUEST_DELAY + random.uniform(1, 3))
            
            response = self.session.get(
                url,
                headers=self.get_headers(),
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                return response
            else:
                print(f"  ⚠️ {self.name}: Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ❌ {self.name}: Request failed - {str(e)}")
            self.stats['errors'] += 1
            return None
    
    def parse_listing(self, html_element):
        """Parse individual listing - to be implemented by child classes"""
        raise NotImplementedError
    
    def scrape_page(self, url):
        """Scrape a single page"""
        response = self.make_request(url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        page_listings = []
        
        # Find price elements - common across sites
        price_elements = soup.find_all(string=lambda t: t and 'KSh' in str(t))
        
        for price_elem in price_elements[:20]:  # Limit per page
            try:
                listing = self.parse_listing(price_elem, soup)
                if listing:
                    page_listings.append(listing)
            except Exception as e:
                continue
        
        self.stats['pages_scraped'] += 1
        self.stats['listings_found'] += len(page_listings)
        
        return page_listings
    
    def scrape(self, max_pages=5):
        """Main scraping method"""
        print(f"\n📱 Starting {self.name} scraper...")
        
        for page in range(1, max_pages + 1):
            url = self.get_page_url(page)
            print(f"  📄 Page {page}: {url}")
            
            listings = self.scrape_page(url)
            self.listings.extend(listings)
            
            print(f"    ✅ Found {len(listings)} listings (Total: {len(self.listings)})")
            
            if len(listings) == 0:  # No more listings
                break
        
        print(f"  ✅ {self.name} complete: {len(self.listings)} listings")
        return self.listings
    
    def get_page_url(self, page):
        """Get URL for page - to be implemented"""
        raise NotImplementedError