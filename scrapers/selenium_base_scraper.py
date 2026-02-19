# scrapers/selenium_base_scraper.py
"""
Base Selenium scraper for all property websites.
Handles browser initialization, navigation, and common scraping patterns.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
import logging
import sys
import os
from datetime import datetime
from fake_useragent import UserAgent

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import clean_price, generate_id
from config.settings import REQUEST_DELAY, TIMEOUT

class SeleniumBaseScraper:
    """Base class for Selenium-based web scrapers"""
    
    def __init__(self, name, base_url, headless=True, wait_timeout=10):
        self.name = name
        self.base_url = base_url
        self.ua = UserAgent()
        self.wait_timeout = wait_timeout
        self.listings = []
        self.stats = {
            'pages_scraped': 0,
            'listings_found': 0,
            'errors': 0
        }
        
        # Set up logging
        self.logger = logging.getLogger(f"Selenium-{name}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Initialize WebDriver
        self.driver = self._init_driver(headless)
        self.wait = WebDriverWait(self.driver, wait_timeout)
    
    def _init_driver(self, headless=True):
        """Initialize Chrome WebDriver with optimized options"""
        import os
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = webdriver.ChromeOptions()
        
        # Performance optimizations
        if headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-web-resources')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-images')  # Disable image loading for speed
        options.add_argument(f'user-agent={self.ua.random}')
        
        # Stealth options to avoid detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Prefs
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            # Get the driver manager path
            driver_path = ChromeDriverManager().install()
            
            # Handle the case where webdriver-manager returns a path that needs correction
            # The path might be something like: /path/to/chromedriver-linux64/THIRD_PARTY_NOTICES.chromedriver
            # We need the actual chromedriver executable
            if not os.path.isfile(driver_path) or driver_path.endswith('.txt') or driver_path.endswith('.chromedriver'):
                # Search for the actual chromedriver binary
                base_path = os.path.dirname(driver_path)
                if 'chromedriver-linux64' in base_path:
                    # Look in the parent directory
                    search_path = base_path
                else:
                    # Look in current and subdirectories
                    search_path = driver_path if os.path.isdir(driver_path) else base_path
                
                # Find the actual chromedriver executable
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if file == 'chromedriver':
                            driver_path = os.path.join(root, file)
                            break
                    if file == 'chromedriver':
                        break
            
            # Make sure the driver is executable
            if os.path.exists(driver_path):
                os.chmod(driver_path, 0o755)
            
            self.logger.info(f"Using ChromeDriver from: {driver_path}")
            
            driver = webdriver.Chrome(
                service=Service(driver_path),
                options=options
            )
            self.logger.info(f"WebDriver initialized successfully")
            return driver
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise
    
    def get_headers(self):
        """Get random headers for requests"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def load_page(self, url, wait_element=None, wait_condition=EC.presence_of_all_elements_located):
        """Load a page using Selenium"""
        try:
            self.logger.info(f"Loading: {url}")
            self.driver.get(url)
            
            # Random delay to appear human-like
            time.sleep(REQUEST_DELAY + random.uniform(1, 3))
            
            # Wait for specific element if provided
            if wait_element:
                try:
                    if isinstance(wait_element, tuple):
                        self.wait.until(wait_condition((wait_element[0], wait_element[1])))
                    else:
                        self.wait.until(wait_condition(wait_element))
                    self.logger.info("Page element loaded successfully")
                except:
                    self.logger.warning("Timeout waiting for element, continuing anyway")
            
            # JavaScript rendering time
            time.sleep(2)
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading page: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def get_page_source(self):
        """Get current page source as BeautifulSoup object"""
        try:
            page_source = self.driver.page_source
            return BeautifulSoup(page_source, 'html.parser')
        except Exception as e:
            self.logger.error(f"Error getting page source: {str(e)}")
            return None
    
    def find_element(self, by, value, timeout=None):
        """Find a single element with timeout"""
        try:
            wait = WebDriverWait(self.driver, timeout or self.wait_timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
        except:
            return None
    
    def find_elements(self, by, value, timeout=None):
        """Find multiple elements with timeout"""
        try:
            wait = WebDriverWait(self.driver, timeout or self.wait_timeout)
            return wait.until(EC.presence_of_all_elements_located((by, value)))
        except:
            return []
    
    def click_element(self, element, retry_count=3):
        """Click an element with retry logic"""
        for attempt in range(retry_count):
            try:
                element.click()
                self.logger.info("Element clicked successfully")
                time.sleep(1)
                return True
            except Exception as e:
                if attempt < retry_count - 1:
                    self.logger.warning(f"Click failed (attempt {attempt + 1}), retrying...")
                    time.sleep(1)
                else:
                    self.logger.error(f"Failed to click element: {str(e)}")
                    return False
        return False
    
    def scroll_page(self, pause_time=2):
        """Scroll page to load dynamic content"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll down
                self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
                time.sleep(pause_time)
                
                # Check if we reached the bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
            self.logger.info("Page scrolled to bottom")
            return True
        except Exception as e:
            self.logger.error(f"Error scrolling page: {str(e)}")
            return False
    
    def get_listing_elements(self, soup):
        """Get listing container elements - can be overridden by subclasses"""
        # Default: find all divs and articles that might be listings
        elements = soup.find_all(['div', 'article', 'li'], class_=lambda x: x and ('property' in x.lower() or 'listing' in x.lower() or 'card' in x.lower()))
        if not elements:
            # Fallback: find all divs with price indicators
            elements = []
            for div in soup.find_all('div'):
                text = div.get_text()
                if 'KSh' in text or 'KES' in text or '₹' in text:
                    elements.append(div)
                if len(elements) >= 50:  # Limit to avoid too many
                    break
        return elements[:50]  # Limit to 50 listings per page
    
    def parse_listing(self, html_element):
        """Parse individual listing - to be implemented by child classes"""
        raise NotImplementedError("parse_listing must be implemented by subclass")
    
    def scrape_page(self, url, listings_selector=None):
        """Scrape a single page"""
        if not self.load_page(url):
            return []
        
        soup = self.get_page_source()
        if not soup:
            return []
        
        page_listings = []
        
        try:
            # Find listing elements using site-specific selectors
            elements = self.get_listing_elements(soup)
            
            self.logger.info(f"Found {len(elements)} potential listing elements")
            
            for element in elements:
                try:
                    # Convert element to HTML string for parsing
                    element_html = str(element)
                    listing = self.parse_listing(element_html)
                    if listing:
                        page_listings.append(listing)
                except Exception as e:
                    self.logger.debug(f"Parse error: {e}")
                    continue
            
            self.stats['pages_scraped'] += 1
            self.stats['listings_found'] += len(page_listings)
            self.logger.info(f"Extracted {len(page_listings)} listings from page")
            
        except Exception as e:
            self.logger.error(f"Error scraping page: {str(e)}")
            self.stats['errors'] += 1
        
        return page_listings
    
    def scrape(self, max_pages=5):
        """Main scraping method"""
        self.logger.info(f"Starting {self.name} scraper...")
        print(f"\n📱 Starting {self.name} scraper...")
        
        try:
            for page in range(1, max_pages + 1):
                url = self.get_page_url(page)
                print(f"  📄 Page {page}: {url}")
                self.logger.info(f"Scraping page {page}")
                
                listings = self.scrape_page(url)
                self.listings.extend(listings)
                
                print(f"    ✅ Found {len(listings)} listings (Total: {len(self.listings)})")
                
                if len(listings) == 0:
                    self.logger.info("No listings found, stopping pagination")
                    break
            
            print(f"  ✅ {self.name} complete: {len(self.listings)} listings")
            self.logger.info(f"{self.name} scraping complete: {len(self.listings)} listings")
            
        except Exception as e:
            self.logger.error(f"Error in scraping loop: {str(e)}")
            self.stats['errors'] += 1
        
        return self.listings
    
    def get_page_url(self, page):
        """Get URL for page - to be implemented"""
        raise NotImplementedError("get_page_url must be implemented by subclass")
    
    def close(self):
        """Close the WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing WebDriver: {str(e)}")
    
    def __del__(self):
        """Ensure driver is closed when object is destroyed"""
        self.close()
