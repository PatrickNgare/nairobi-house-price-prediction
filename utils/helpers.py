# utils/helpers.py
import re
import hashlib
import random
import time
from datetime import datetime

def generate_id(text, length=10):
    """Generate unique ID from text"""
    return hashlib.md5(text.encode()).hexdigest()[:length]

def clean_price(price_str):
    """Clean and convert price string to integer"""
    if not price_str or not isinstance(price_str, str):
        return None
    
    # Remove common patterns
    price_str = price_str.replace('KSh', '').replace('KES', '').strip()
    price_str = re.sub(r'[^\d.,]', '', price_str)
    
    # Handle ranges (take average)
    if '-' in price_str:
        parts = price_str.split('-')
        try:
            return (float(parts[0].replace(',', '')) + float(parts[1].replace(',', ''))) // 2
        except:
            pass
    
    # Standard conversion
    try:
        return int(float(price_str.replace(',', '')))
    except:
        return None

def clean_text(text):
    """Clean text by removing extra whitespace"""
    if not text:
        return ''
    return ' '.join(text.split())

def safe_request(url, headers=None, delay=2):
    """Make safe request with delay"""
    import requests
    time.sleep(delay + random.uniform(0, 1))
    
    if not headers:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response
        else:
            print(f"⚠️ Status {response.status_code} for {url}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return None

def save_checkpoint(data, filename):
    """Save intermediate data"""
    import pandas as pd
    pd.DataFrame(data).to_csv(filename, index=False)
    print(f"💾 Checkpoint saved: {filename}")