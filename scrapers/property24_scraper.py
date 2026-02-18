# scrapers/property24_selenium_scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import logging

class Property24SeleniumScraper:
    def __init__(self, delay: int = 3):
        self.source_name = "Property24"
        self.base_url = "https://www.property24.co.ke"
        self.delay = delay
        self.logger = logging.getLogger("Property24Selenium")
        
        # Set up Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 10)
    
    def scrape(self, max_pages: int = 3):
        """Main scraping method using Selenium"""
        all_listings = []
        
        try:
            # Go to the for-sale page
            self.logger.info("Loading Property24 for-sale page...")
            self.driver.get(f"{self.base_url}/for-sale")
            time.sleep(self.delay)
            
            # Look for and fill the search form
            self.logger.info("Looking for search form...")
            
            # Try to find the location/search input
            try:
                # Common selectors for search inputs
                search_selectors = [
                    "input[placeholder*='Search']",
                    "input[placeholder*='City']",
                    "input[placeholder*='Suburb']",
                    "input[type='search']",
                    ".search-input",
                    "#search-box"
                ]
                
                search_input = None
                for selector in search_selectors:
                    try:
                        search_input = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if search_input:
                            self.logger.info(f"Found search input with selector: {selector}")
                            break
                    except:
                        continue
                
                if search_input:
                    # Type "Nairobi"
                    search_input.clear()
                    search_input.send_keys("Nairobi")
                    time.sleep(1)
                    
                    # Try to find and click search button
                    button_selectors = [
                        "button[type='submit']",
                        ".search-button",
                        "button:contains('Search')",
                        "input[type='submit']"
                    ]
                    
                    for selector in button_selectors:
                        try:
                            search_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            search_button.click()
                            self.logger.info("Clicked search button")
                            break
                        except:
                            continue
                    
                    # Wait for results to load
                    time.sleep(5)
                    
            except Exception as e:
                self.logger.error(f"Error with search form: {str(e)}")
            
            # Now try to scrape the results
            for page in range(1, max_pages + 1):
                self.logger.info(f"Scraping page {page}")
                
                # Wait for property listings to load
                time.sleep(3)
                
                # Get page source and parse with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Find property listings
                listings = self.find_listings(soup)
                self.logger.info(f"Found {len(listings)} listings on page {page}")
                
                for listing in listings[:15]:
                    try:
                        parsed = self.parse_listing(listing)
                        if parsed:
                            all_listings.append(parsed)
                    except Exception as e:
                        continue
                
                # Try to go to next page
                try:
                    next_button = self.driver.find_element(By.LINK_TEXT, "Next")
                    next_button.click()
                except:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, ".pagination-next")
                        next_button.click()
                    except:
                        self.logger.info("No next page found")
                        break
            
        except Exception as e:
            self.logger.error(f"Scraping error: {str(e)}")
        
        finally:
            self.driver.quit()
        
        return all_listings
    
    def find_listings(self, soup):
        """Find listing elements in the page"""
        # Try various selectors that might contain listings
        selectors = [
            soup.find_all('div', class_=re.compile(r'property|listing|card|result')),
            soup.find_all('article'),
            [div for div in soup.find_all('div') 
             if div.get_text() and 'KSh' in div.get_text() 
             and len(div.get_text().strip()) > 100]
        ]
        
        for selector in selectors:
            if selector and len(selector) > 0:
                return selector
        return []
    
    def parse_listing(self, element):
        """Parse a listing element"""
        try:
            text = element.get_text()
            
            # Extract price
            price_match = re.search(r'KSh\s*([\d,]+(?:\.\d+)?)', text, re.IGNORECASE)
            if not price_match:
                return None
            
            price_str = price_match.group(1).replace(',', '')
            price = int(float(price_str))
            
            # Extract title
            title_elem = element.find(['h3', 'h4', 'h5', 'h6'])
            title = title_elem.text.strip() if title_elem else "Property"
            
            # Extract location
            location = "Nairobi"
            for area in ['Kilimani', 'Kileleshwa', 'Karen', 'Westlands', 'Lavington', 'Runda']:
                if area.lower() in text.lower():
                    location = area
                    break
            
            # Extract bedrooms
            bedrooms = None
            bed_match = re.search(r'(\d+)\s*(?:bed|bedroom|br)', text, re.IGNORECASE)
            if bed_match:
                bedrooms = int(bed_match.group(1))
            
            return {
                'listing_id': self.generate_id(text[:50]),
                'source': self.source_name,
                'title': title[:100],
                'location': location,
                'property_type': 'Unknown',
                'bedrooms': bedrooms,
                'bathrooms': None,
                'size_sqft': None,
                'price_kes': price,
                'listing_date': datetime.now().strftime('%Y-%m-%d'),
                'listing_url': ''
            }
            
        except Exception as e:
            return None
    
    def generate_id(self, text):
        """Generate a simple ID"""
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()[:10]