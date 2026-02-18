# config.py
import os
from datetime import datetime

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_FILE = os.path.join(DATA_DIR, 'raw_listings.csv')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Scraping settings
REQUEST_DELAY = 3  # seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30

# Target: 300-800 listings
TARGET_LISTINGS = 500
MIN_LISTINGS = 300
MAX_LISTINGS = 800

# Websites configuration
WEBSITES = {
    'buyrentkenya': {
        'base_url': 'https://www.buyrentkenya.com',
        'search_url': '/property-for-sale/nairobi?page={}',
        'enabled': True,
        'max_pages': 20,
        'listings_per_page': 20  # estimated
    },
    'propertypro': {
        'base_url': 'https://propertypro.co.ke',
        'search_url': '/properties-for-sale/nairobi?page={}',
        'enabled': True,
        'max_pages': 20,
        'listings_per_page': 20
    },
    'property24': {
        'base_url': 'https://www.property24.co.ke',
        'search_url': '/for-sale/nairobi/{}',
        'enabled': True,
        'max_pages': 15,
        'listings_per_page': 25
    }
}

# Standardized amenities list
STANDARD_AMENITIES = [
    'pool', 'gym', 'parking', 'security', 'generator', 'elevator',
    'garden', 'balcony', 'furnished', 'serviced', 'wifi', 'play area',
    'clubhouse', 'cctv', 'ac', 'backup water', 'dsl', 'sauna', 'tennis'
]

# Nairobi areas by category
NAIROBI_AREAS = {
    'high_end': [
        'karen', 'runda', 'kitisuru', 'lavington', 'kileleshwa',
        'kilimani', 'westlands', 'spring valley', 'nyari', 'gigiri',
        'lower kabete', 'upper kabete', 'muthaiga'
    ],
    'middle': [
        'south b', 'south c', 'buruburu', 'donholm', 'komarock',
        'langata', 'madaraka', 'parklands', 'hurlingham', 'brookside',
        'highridge', 'riverside', 'mountain view'
    ],
    'satellite': [
        'ongata rongai', 'ngong', 'syokimau', 'athi river', 'kitengela',
        'juja', 'ruiru', 'thika', 'limuru', 'kiambu', 'kikuyu'
    ],
    'lower': [
        'embakasi', 'kayole', 'dandora', 'kasarani', 'roysambu',
        'githurai', 'zimmerman', 'umoja', 'eastleigh', 'pangani',
        'maringo', 'kimathi', 'kaloleni'
    ]
}

# Flatten areas list for validation
ALL_NAIROBI_AREAS = [area for sublist in NAIROBI_AREAS.values() for area in sublist]

# Property types
PROPERTY_TYPES = [
    'apartment', 'house', 'villa', 'bungalow', 
    'maisonette', 'townhouse', 'land', 'commercial'
]

# Data validation rules
VALIDATION_RULES = {
    'price_min': 500000,      # Minimum 500K KES
    'price_max': 500000000,   # Maximum 500M KES
    'bedrooms_min': 0,
    'bedrooms_max': 10,
    'bathrooms_min': 0,
    'bathrooms_max': 10,
    'size_min': 100,          # Minimum 100 sq ft
    'size_max': 50000,        # Maximum 50,000 sq ft
}

# Scraping metadata
SCRAPE_METADATA = {
    'start_time': None,
    'end_time': None,
    'total_listings': 0,
    'sources_success': [],
    'sources_failed': []
}