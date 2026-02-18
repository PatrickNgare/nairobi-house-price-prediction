# find_correct_urls.py
import requests
from bs4 import BeautifulSoup

def explore_website(name, base_url, paths_to_try):
    print(f"\n=== Exploring {name} ===")
    
    for path in paths_to_try:
        url = base_url + path
        print(f"\nTrying: {url}")
        
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                print(f"Page title: {soup.title.text.strip() if soup.title else 'No title'}")
                
                # Look for any property listings
                potential_listings = []
                
                # Check for common listing indicators
                if 'KSh' in response.text:
                    print("✓ Page contains 'KSh' (price indicator)")
                    
                # Look for common listing classes
                for class_name in ['property', 'listing', 'card', 'item', 'advert']:
                    elements = soup.find_all(class_=lambda c: c and class_name in c.lower() if c else False)
                    if elements:
                        print(f"  Found {len(elements)} elements with class containing '{class_name}'")
                
                # Save HTML for inspection
                with open(f'debug_{name}_{path.replace("/", "_")}.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  ✓ Saved HTML to debug_{name}_{path.replace('/', '_')}.html")
                
        except Exception as e:
            print(f"Error: {str(e)}")

# Try different paths for BuyRentKenya
buyrentkenya_paths = [
    "/",
    "/buy",
    "/for-sale",
    "/properties",
    "/nairobi",
    "/nairobi/properties-for-sale",
    "/search?category=for-sale&location=nairobi",
    "/property/nairobi",
]

# Try different paths for PropertyPro
propertypro_paths = [
    "/",
    "/properties-for-sale",
    "/for-sale",
    "/nairobi",
    "/nairobi/properties-for-sale", 
    "/search?category=for-sale&location=nairobi",
    "/property/nairobi",
]

print("="*60)
print("WEBSITE STRUCTURE EXPLORER")
print("="*60)

explore_website("buyrentkenya", "https://www.buyrentkenya.com", buyrentkenya_paths)
explore_website("propertypro", "https://propertypro.co.ke", propertypro_paths)