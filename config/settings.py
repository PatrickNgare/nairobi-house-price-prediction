# config/settings.py
import os
from datetime import datetime

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
ARCHIVE_DIR = os.path.join(DATA_DIR, 'archives')

# Create directories
for dir_path in [RAW_DIR, PROCESSED_DIR, ARCHIVE_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Scraping settings
REQUEST_DELAY = 2  # seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30
USER_AGENT_ROTATION = True

# Data collection targets
TARGET_LISTINGS = 1000
MIN_LISTINGS_PER_SOURCE = 100

# Output files
MASTER_FILE = os.path.join(PROCESSED_DIR, 'nairobi_properties_master.csv')
TODAY_DATE = datetime.now().strftime('%Y%m%d')
TODAY_FILE = os.path.join(RAW_DIR, f'listings_{TODAY_DATE}.csv')