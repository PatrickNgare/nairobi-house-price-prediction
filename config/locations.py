# config/locations.py
"""
Nairobi areas categorized for better data collection and analysis
"""

# All Nairobi areas to scrape
NAIROBI_AREAS = {
    # High-end/Executive areas
    'high_end': [
        'kilimani', 'kileleshwa', 'lavington', 'karen', 'runda',
        'kitisuru', 'gigiri', 'spring-valley', 'nyari', 'muthaiga'
    ],
    
    # Middle-income areas
    'middle': [
        'westlands', 'parklands', 'langata', 'hurlingham', 'brookside',
        'south-b', 'south-c', 'madaraka', 'highridge', 'riverside'
    ],
    
    # Eastern suburbs
    'eastern': [
        'buruburu', 'donholm', 'komarock', 'embakasi', 'kasarani',
        'roysambu', 'zimmerman', 'githurai', 'ruiru', 'juja'
    ],
    
    # Satellite towns
    'satellite': [
        'ongata-rongai', 'ngong', 'syokimau', 'kitengela', 'athiriver',
        'machakos', 'thika', 'limuru', 'kiambu', 'kikuyu'
    ],
    
    # Coastal (for comparison)
    'coastal': [
        'nyali', 'mombasa', 'kilifi', 'diani', 'malindi', 'watamu'
    ]
}

# Flatten for easy iteration
ALL_AREAS = []
for category, areas in NAIROBI_AREAS.items():
    ALL_AREAS.extend(areas)

# Location metadata for feature engineering
LOCATION_FEATURES = {
    'kilimani': {'category': 'high_end', 'distance_to_cbd': 3, 'avg_rent': 80000},
    'kileleshwa': {'category': 'high_end', 'distance_to_cbd': 4, 'avg_rent': 75000},
    'lavington': {'category': 'high_end', 'distance_to_cbd': 5, 'avg_rent': 100000},
    'karen': {'category': 'high_end', 'distance_to_cbd': 15, 'avg_rent': 120000},
    'westlands': {'category': 'middle', 'distance_to_cbd': 2, 'avg_rent': 60000},
    'langata': {'category': 'middle', 'distance_to_cbd': 8, 'avg_rent': 45000},
    'buruburu': {'category': 'eastern', 'distance_to_cbd': 10, 'avg_rent': 35000},
    'embakasi': {'category': 'eastern', 'distance_to_cbd': 12, 'avg_rent': 25000},
    'ongata-rongai': {'category': 'satellite', 'distance_to_cbd': 20, 'avg_rent': 30000},
}