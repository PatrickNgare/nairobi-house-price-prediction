# config.py (UPDATED with working URLs)
import os

os.makedirs('data', exist_ok=True)

REQUEST_DELAY = 3
TARGET_LISTINGS = 500

WEBSITES = {
    'buyrentkenya': {
        'enabled': True,
        'max_pages': 5,
        'base_url': 'https://www.buyrentkenya.com',
        'search_url': '/search?category=for-sale&location=nairobi&page={}'  # Working URL with pagination
    },
    'propertypro': {
        'enabled': True,
        'max_pages': 5,
        'base_url': 'https://propertypro.co.ke',
        'search_url': '/properties-for-sale?page={}'  # Working URL
    }
}

RAW_DATA_FILE = 'data/raw_listings.csv'