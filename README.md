# 🏠 Nairobi House Price Predictor

A comprehensive machine learning application for predicting residential property prices in Nairobi, Kenya. This project combines **Selenium-based web scraping**, **data processing**, **ML model training**, and a **Streamlit web interface** for interactive price predictions.

## 🎯 Project Overview

This end-to-end machine learning solution includes:

- **Web Scraping**: Selenium-based scrapers for multiple Nairobi property platforms
- **Data Pipeline**: Automated collection, cleaning, and feature engineering
- **Machine Learning**: Training and optimization of predictive models
- **Web Interface**: Interactive Streamlit dashboard for predictions
- **Data Analysis**: Jupyter notebooks for EDA and model development

**Supported Property Platforms**:
- BuyRentKenya
- PropertyPro
- Property24
- DiamondTrust

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Virtual environment (recommended)
- Chrome/Chromium browser (for Selenium scrapers)

### Installation

```sh
# Clone/navigate to project
cd nairobi-house-price-prediction

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

**Start the Streamlit web interface**:
```sh
streamlit run app.py
```
Opens interactive dashboard at `http://localhost:8501`

**Run data collection**:
```sh
python main.py
```
Orchestrates all scrapers and collects property listings

## 📁 Project Structure

```
nairobi-house-price-prediction/
├── app.py                         # Streamlit web interface (MAIN APP)
├── main.py                        # Data collection orchestrator
├── quick_collect.py               # Quick sample collection
├── bulk_collect.py                # Bulk data collection
├── generate_demo_data.py          # Generate synthetic data
├── requirements.txt               # Python dependencies
├── README.md                      # This file
│
├── config/                        # Configuration & settings
│   ├── config.py                  # Main config settings
│   ├── settings.py                # App settings & paths
│   ├── locations.py               # Nairobi locations/areas
│   └── location_utils.py          # Location helper functions
│
├── scrapers/                      # Web scraping modules
│   ├── base_scraper.py            # Base scraper class
│   ├── selenium_base_scraper.py   # Selenium base class
│   ├── buyrentkenya_scraper.py    # BuyRentKenya scraper
│   ├── propertypro_scraper.py     # PropertyPro scraper
│   ├── property24_scraper.py      # Property24 scraper
│   └── diamondtrust_scraper.py    # DiamondTrust scraper
│
├── utils/                         # Utility functions
│   ├── helpers.py                 # Helper functions
│   └── location_utils.py          # Location utilities
│
├── data/                          # Data storage (git-ignored)
│   ├── raw/                       # Raw scraped listings
│   ├── processed/                 # Cleaned data
│   └── archives/                  # Historical data
│
├── datas/                         # Example datasets
│   ├── all_listings_raw.csv
│   ├── complete_listings.csv
│   └── simple_listings.csv
│
├── models/                        # Trained ML models
│   ├── model.pkl                  # Trained model pickle
│   ├── feature_columns_*.pkl      # Feature column names
│   └── model_metadata.json        # Model metrics
│
├── Notebooks/                     # Jupyter notebooks
│   ├── Model_Training.ipynb
│   ├── Data_Cleaning.ipynb
│   └── EDA.ipynb
│
└── .gitignore                     # Git ignore rules
```

## 🔧 Core Components

### 1. Streamlit Web Application (`app.py`)

**Interactive prediction dashboard** with:
- 🎨 Beautiful UI with custom CSS styling
- 📊 Multiple input tabs for property details
- 🔄 Real-time predictions from trained model
- 📈 Prediction confidence and metrics
- 💾 Model caching for fast loading
- 🎯 Support for multiple property types

**Key Features**:
```python
# Page configuration
- Title: "🏠 Nairobi House Price Predictor"
- Layout: Wide (optimized for desktop)
- Sidebar: Expanded by default

# Tabs
1. Single Prediction - Predict one property
2. Batch Predictions - Upload CSV for bulk predictions
3. Model Info - View model metrics and feature importance
4. About - Project information
```

**Model Loading**:
- Automatically loads `models/model.pkl`
- Caches model with `@st.cache_resource` for performance
- Handles missing model files gracefully
- Loads feature columns from pickle files

### 2. Data Collection (`main.py`)

**Orchestrates all web scrapers** to collect property listings:

```python
Main Workflow:
1. Initialize all scrapers (BuyRentKenya, PropertyPro, Property24, DiamondTrust)
2. Run scrapers sequentially
3. Validate collected data
4. Save raw CSV to data/raw/
5. Generate statistics and logs
```

**Scrapers Used**:
- `BuyRentKenyaScraper()` - Scrapes BuyRentKenya.com listings
- `PropertyProScraper()` - Scrapes PropertyPro.co.ke listings
- `Property24Scraper()` - Scrapes Property24.co.ke listings
- `DiamondTrustScraper()` - Scrapes DiamondTrust listings

**Configuration** (from `config/settings.py`):
- `TARGET_LISTINGS`: Target number of listings to collect (default: 800+)
- `MIN_LISTINGS_PER_SOURCE`: Minimum per source (default: 100+)
- `RAW_DIR`: Directory for raw data output
- `PROCESSED_DIR`: Directory for processed data
- `MASTER_FILE`: Master combined dataset
- `TODAY_FILE`: Today's collection file

### 3. Web Scrapers (`scrapers/`)

#### Base Classes

**`base_scraper.py`** - Base abstract scraper
- Defines scraper interface
- Common data validation
- Error handling

**`selenium_base_scraper.py`** - Selenium-based scraper
- Handles browser automation
- JavaScript-rendered content
- Login handling
- Pagination management
- Data extraction from dynamic pages

#### Specific Scrapers

**`buyrentkenya_scraper.py`**
- Platform: BuyRentKenya.com
- Method: Selenium (JavaScript content)
- Features extracted: Price, bedrooms, bathrooms, location, amenities

**`propertypro_scraper.py`**
- Platform: PropertyPro.co.ke
- Method: Selenium (JavaScript content)
- Features extracted: Price, property type, size, location details

**`property24_scraper.py`**
- Platform: Property24.co.ke
- Method: BeautifulSoup + Requests
- Features extracted: Standard property details

**`diamondtrust_scraper.py`**
- Platform: DiamondTrust Property
- Method: Mixed (API + BeautifulSoup)
- Features extracted: Property specifications, pricing

### 4. Configuration (`config/`)

**`config.py`** - Main configuration
- File paths and directories
- API endpoints
- Scraper settings

**`settings.py`** - Application settings
```python
RAW_DIR = 'data/raw/'
PROCESSED_DIR = 'data/processed/'
MASTER_FILE = 'data/processed/master_listings.csv'
TODAY_FILE = 'data/raw/listings_{date}.csv'
TARGET_LISTINGS = 800
MIN_LISTINGS_PER_SOURCE = 100
```

**`locations.py`** - Nairobi locations
```python
NAIROBI_LOCATIONS = {
    'Westlands': {...},
    'Karen': {...},
    'Nyaya': {...},
    'Upper Hill': {...},
    # ... 50+ more locations
}
```

**`location_utils.py`** - Location utilities
- Location validation
- Area mapping
- Distance calculations
- Neighborhood lookup

### 5. Utilities (`utils/`)

**`helpers.py`** - Helper functions
- Data validation
- Format conversion
- String utilities
- Date/time helpers

**`location_utils.py`** - Location helpers
- Location encoding/decoding
- Geocoding support
- Area classification

## 📦 Dependencies

### Web Scraping
```
selenium==4.15.2          # Browser automation
beautifulsoup4==4.14.3    # HTML parsing
lxml==6.0.2               # XML/HTML processing
webdriver-manager==4.0.1  # WebDriver management
requests==2.32.5          # HTTP requests
fake-useragent==2.2.0     # Random user agents
timeout-decorator==0.5.0  # Timeout handling
```

### Data Processing
```
pandas==3.0.1    # Data manipulation
numpy==2.4.2     # Numerical computing
pydantic==2.4.0  # Data validation
```

### Web Interface
```
streamlit==1.x.x  # (Add to requirements.txt)
```

### Analysis & Visualization
```
matplotlib==3.7.2  # Plotting
seaborn==0.12.2    # Statistical visualization
jupyter==1.0.0     # Jupyter notebooks
```

### Utilities
```
tqdm==4.66.1              # Progress bars
python-dateutil==2.9.0    # Date utilities
certifi==2026.1.4         # SSL certificates
```

## 🛠️ Development Workflow

### Phase 1: Data Collection

**Quick Sample** (for testing):
```sh
python quick_collect.py
# Collects ~100 listings for testing
# Output: data/raw/sample_listings.csv
```

**Full Collection** (production):
```sh
python main.py
# Runs all 4 scrapers
# Target: 800+ listings
# Output: data/raw/listings_2026-02-23.csv
```

**Generate Demo Data** (for development):
```sh
python generate_demo_data.py
# Creates synthetic property data
# Output: datas/demo_listings.csv
```

### Phase 2: Data Processing

Open `Notebooks/Data_Cleaning.ipynb`:

**Steps**:
1. Load raw CSV from `data/raw/`
2. Data quality checks (missing values, duplicates)
3. Feature engineering:
   - Price normalization
   - Location encoding
   - Amenity parsing
   - Derived features (price_per_bed, etc.)
4. Output to `data/processed/master_listings.csv`

### Phase 3: Model Training

Open `Notebooks/Model_Training.ipynb`:

**Process**:
1. Load processed data from `data/processed/`
2. Split: 80% train, 20% test
3. Train multiple models (Random Forest, XGBoost, etc.)
4. Hyperparameter tuning
5. Select best model
6. Save to `models/model.pkl`

### Phase 4: Deployment

**Run Streamlit app**:
```sh
streamlit run app.py
```

**Features**:
- Load trained model from `models/model.pkl`
- Input property features in UI
- Display predicted price
- Show confidence metrics
- Batch prediction from CSV upload

## 📊 Data Format

### Input CSV Columns (Raw Data)

```
source              - Website source (BuyRentKenya, PropertyPro, etc.)
listing_id          - Unique listing identifier
title               - Property title
location            - Nairobi location/area
property_type       - Apartment, House, Villa, Townhouse, etc.
bedrooms            - Number of bedrooms
bathrooms           - Number of bathrooms
size_sqft           - Property size in square feet
price_kes           - Price in Kenyan Shillings (TARGET)
amenities           - Pipe-separated amenities (gym|pool|parking)
listing_url         - Original listing URL
scrape_date         - Date when listing was scraped
```

### Data Types & Validation

| Column | Type | Example | Validation |
|--------|------|---------|-----------|
| price_kes | int | 2500000 | > 0, not null |
| bedrooms | int | 3 | > 0, not null |
| bathrooms | int | 2 | > 0, not null |
| size_sqft | int | 1500 | > 0 |
| location | string | "Westlands" | Must be in locations.py |
| property_type | string | "Apartment" | Predefined categories |
| amenities | string | "gym\|pool" | Pipe-separated |

## 🔑 Key Features

### Web Scraping
✅ Multiple data sources (4 platforms)
✅ Selenium-based for JavaScript-heavy sites
✅ Robust error handling and retries
✅ User-agent rotation to avoid blocks
✅ Pagination support
✅ Data validation on collection

### Data Processing
✅ Automated cleaning pipeline
✅ Missing value handling
✅ Duplicate detection & removal
✅ Feature engineering
✅ Location encoding
✅ Amenity parsing

### Machine Learning
✅ Multiple model algorithms
✅ Hyperparameter optimization
✅ Cross-validation
✅ Feature importance analysis
✅ Model serialization (pickle)

### User Interface
✅ Interactive Streamlit dashboard
✅ Single & batch predictions
✅ Model information display
✅ Real-time feedback
✅ Beautiful, responsive design

## 🚨 Troubleshooting

### Problem: ChromeDriver not found
**Solution**: `webdriver-manager` auto-downloads drivers
```sh
pip install --upgrade webdriver-manager
```

### Problem: "Model file not found"
**Solution**: Train model first
```sh
jupyter notebook Notebooks/Model_Training.ipynb
# Run all cells to generate models/model.pkl
```

### Problem: Scraper timeout/hangs
**Solution**: Increase timeout or skip that source
- Edit `config/settings.py`
- Adjust `TIMEOUT` values
- Or comment out problematic scraper in `main.py`

### Problem: Streamlit not found
**Solution**: Install missing dependency
```sh
pip install streamlit
```

### Problem: Data collection returns 0 listings
**Solution**: Check website structure hasn't changed
- Verify CSS selectors in scraper
- Check if website has anti-scraping measures
- Try with `fake-useragent` enabled

## 📈 Model Performance

### Expected Metrics
- **R² Score**: ~0.95-0.99 (higher is better)
- **MAE**: ~1-3M KES (lower is better)
- **RMSE**: ~2-4M KES (lower is better)
- **MAPE**: 3-5% (lower is better)

### Train/Test Split
- Training: 80% of collected data
- Testing: 20% of collected data
- Random state: 42 (reproducibility)

## 📝 Example Usage

### Using the Streamlit App
1. Run `streamlit run app.py`
2. Open browser to `http://localhost:8501`
3. Fill in property details (bedrooms, bathrooms, location, etc.)
4. Click "Predict Price"
5. View predicted price in KES

### Batch Prediction from CSV
1. Prepare CSV with property columns
2. Open "Batch Predictions" tab
3. Upload CSV file
4. Download results with predictions

### Programmatic Usage
```python
import pickle
import pandas as pd

# Load model
with open('models/model.pkl', 'rb') as f:
    model = pickle.load(f)

# Create property data
property_df = pd.DataFrame({
    'bedrooms': [3],
    'bathrooms': [2],
    'size_sqft': [1500],
    # ... other features
})

# Predict
price = model.predict(property_df)[0]
print(f"Predicted Price: KES {price:,.0f}")
```

## 🔄 Updating Models

**When to retrain**:
- Monthly data refresh
- Performance degrades
- New market trends
- Data quality issues

**Retraining steps**:
```sh
# 1. Collect new data
python main.py

# 2. Process data
jupyter notebook Notebooks/Data_Cleaning.ipynb
# Run all cells

# 3. Train models
jupyter notebook Notebooks/Model_Training.ipynb
# Run all cells - generates new models/model.pkl

# 4. Test the app
streamlit run app.py
```

## 📞 Support & Contributing

### Reporting Issues
1. Check existing issues first
2. Include error message and traceback
3. Specify Python version and OS
4. Share sample data if applicable

### Contributing
1. Fork repository
2. Create feature branch
3. Make focused changes
4. Test thoroughly
5. Document changes
6. Submit pull request

### Code Standards
- Follow PEP 8 style guide
- Add docstrings to functions
- Comment complex logic
- Test before submitting

## 📄 Project Information

- **Created**: February 19, 2026
- **Python Version**: 3.12+
- **Project Type**: ML / Data Science / Web Scraping
- **Focus Area**: Nairobi, Kenya
- **Data Target**: Residential property prices (KES)
- **Primary Framework**: Streamlit

## 🎓 Technology Stack

**Frontend**: Streamlit
**Scraping**: Selenium + BeautifulSoup
**Data**: Pandas, NumPy
**ML**: scikit-learn, XGBoost
**Serialization**: Pickle, JSON
**Browser Control**: Selenium WebDriver

## 📚 Jupyter Notebooks

### `Model_Training.ipynb`
Complete ML pipeline:
- Load processed data
- Train 6+ model algorithms
- Hyperparameter tuning
- Model comparison
- Feature importance
- Model serialization

### `Data_Cleaning.ipynb`
Data preprocessing:
- Raw data loading
- Cleaning & validation
- Feature engineering
- Output processed data

### `EDA.ipynb`
Exploratory analysis:
- Data distribution
- Feature correlations
- Price analysis by location
- Market insights

---

**Last Updated**: February 23, 2026
**Status**: Active Development
**Maintainer**: Patrick Ngare