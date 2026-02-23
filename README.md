# 🏠 Nairobi House Price Prediction

A machine learning application for predicting residential property prices in Nairobi, Kenya. This project implements a complete pipeline from web scraping property listings to training predictive models and serving predictions through a web interface.

## 📋 Overview

This end-to-end ML project includes:
- **Data Collection**: Web scrapers for gathering property listings
- **Data Processing**: Cleaning, validation, and feature engineering
- **Model Training**: Multiple ML algorithms with hyperparameter tuning
- **Web Interface**: Flask-based application for making predictions
- **Analytics**: Jupyter notebooks for exploration and analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Virtual environment (recommended)
- Linux/macOS or Windows

### Installation

```sh
# Navigate to project directory
cd nairobi-house-price-prediction

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 📁 Project Structure

```
nairobi-house-price-prediction/
├── app.py                    # Flask web application (main entry point)
├── main.py                   # Alternative CLI entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore               # Git ignore rules
│
├── config/                  # Configuration modules
│   ├── __init__.py
│   ├── config.py            # Main configuration settings
│   ├── settings.py          # App-specific settings
│   ├── locations.py         # Supported locations/areas
│   └── location_utils.py    # Location utility functions
│
├── data/                    # Data storage (git-ignored)
│   ├── raw/                 # Raw scraped listings
│   ├── processed/           # Cleaned & processed data
│   └── archives/            # Historical/backup datasets
│
├── datas/                   # Example/sample datasets
│   ├── all_listings_raw.csv
│   ├── complete_listings.csv
│   └── simple_listings.csv
│
├── models/                  # Trained model artifacts
│   ├── *.joblib            # Serialized trained models
│   ├── *.json              # Model metadata & metrics
│   └── feature_columns.joblib
│
├── Notebooks/              # Jupyter notebooks for analysis
│   ├── Model_Training.ipynb
│   ├── Data_Cleaning.ipynb
│   └── EDA.ipynb
│
├── scrapers/               # Web scraping modules
│   ├── __init__.py
│   └── ... (scraper implementations)
│
├── utils/                  # Utility functions
│   ├── __init__.py
│   └── ... (helper modules)
│
└── venv/                   # Virtual environment (git-ignored)
```

## 🛠️ Development & Usage

### 1. Data Collection

#### Quick Sample Collection
Collect a small sample of recent listings for testing:
```sh
python quick_collect.py
```
- **Output**: `data/raw/` directory
- **Use case**: Quick testing and validation

#### Bulk Collection
Collect large amounts of data from multiple sources:
```sh
python bulk_collect.py
```
- **Output**: `data/raw/` directory
- **Use case**: Building complete training datasets

#### Generate Demo Data
Create synthetic test data for development:
```sh
python generate_demo_data.py
```
- **Output**: `datas/` directory
- **Use case**: Testing without needing live data

### 2. Data Processing

Process raw data through the pipeline:

**Key Steps**:
1. Load raw CSV files from `data/raw/`
2. Handle missing values in critical columns (price, bedrooms, bathrooms, size, location)
3. Remove duplicates and invalid entries
4. Encode categorical features (location, property_type)
5. Engineer derived features
6. Output cleaned data to `data/processed/`

**Feature Engineering**:
- `price_per_bed`: Price divided by number of bedrooms
- `price_per_sqft`: Price per square foot
- `bed_bath_ratio`: Bedrooms to bathrooms ratio
- `total_rooms`: Sum of bedrooms and bathrooms
- `amenity_count`: Number of available amenities
- Location and property type encoding

See [Notebooks/Data_Cleaning.ipynb](Notebooks/Data_Cleaning.ipynb) for detailed cleaning workflow.

### 3. Model Training

Train and evaluate ML models through Jupyter notebook:

```sh
# Open and run Notebooks/Model_Training.ipynb
jupyter notebook Notebooks/Model_Training.ipynb
```

**Training Pipeline**:
1. Load processed data from `data/processed/`
2. Split: 80% training, 20% testing
3. Train baseline models (6 algorithms)
4. Hyperparameter tuning with GridSearchCV
5. Compare and select best model
6. Save artifacts to `models/` directory

**Models Evaluated**:
- Linear Regression (baseline)
- Decision Tree
- Random Forest
- Gradient Boosting ✅ **BEST**
- XGBoost
- LightGBM

**Model Artifacts Saved**:
- `best_model_*.joblib` - Trained model
- `feature_columns_*.joblib` - Feature list
- `*.json` - Model metadata & metrics

### 4. Run the Web Application

#### Option 1: Flask Web Interface
```sh
python app.py
```
- Starts web server (typically on `http://localhost:5000`)
- Provides UI for making predictions
- Interactive input forms for property features

#### Option 2: CLI Interface
```sh
python main.py
```
- Command-line interface for predictions
- Batch processing capabilities
- Direct API access

## 📊 Data Format

### Input CSV Columns
Expected columns in raw CSV files:
```
source, listing_id, title, location, property_type, 
bedrooms, bathrooms, size_sqft, price_kes, amenities, 
listing_url, scrape_date
```

### Data Types & Validation
| Column | Type | Example | Notes |
|--------|------|---------|-------|
| price_kes | int | 2500000 | Target variable (KES) |
| bedrooms | int | 3 | Must be > 0 |
| bathrooms | int | 2 | Must be > 0 |
| size_sqft | int | 1500 | Property size |
| location | string | "Westlands" | Supported locations only |
| property_type | string | "Apartment" | House, Apartment, Villa, etc. |
| amenities | string | "gym\|pool\|parking" | Pipe-separated values |

## 🔧 Configuration

### Key Configuration Files

**[config/config.py](config/config.py)**
- Main application configuration
- Model paths and settings
- Data directories

**[config/settings.py](config/settings.py)**
- Application-specific settings
- API endpoints
- Feature settings

**[config/locations.py](config/locations.py)**
- Supported Nairobi locations/areas
- Location encoding/decoding
- Location validation

**[config/location_utils.py](config/location_utils.py)**
- Location utility functions
- Distance calculations
- Area lookups

### Modifying Configuration
Edit relevant config files to:
- Change data paths
- Update location lists
- Adjust model parameters
- Configure web app settings

## 📦 Dependencies

Key Python packages (see [requirements.txt](requirements.txt)):

**Data Processing**:
- `pandas` - Data manipulation
- `numpy` - Numerical computing

**Machine Learning**:
- `scikit-learn` - ML algorithms & preprocessing
- `xgboost` - XGBoost implementation
- `lightgbm` - LightGBM implementation

**Web Framework**:
- `flask` - Web application framework

**Utilities**:
- `joblib` - Model serialization
- `requests` - HTTP requests
- `beautifulsoup4` - Web scraping

**Visualization** (notebooks):
- `matplotlib` - Plotting
- `seaborn` - Statistical visualization

Install all dependencies:
```sh
pip install -r requirements.txt
```

## 🎯 Typical Workflow

### For Data Scientists
1. Run `quick_collect.py` to get sample data
2. Open `Notebooks/Data_Cleaning.ipynb` to explore & clean
3. Open `Notebooks/Model_Training.ipynb` to train models
4. Compare model metrics and select best performer
5. Save model artifacts

### For Developers
1. Clone the repository
2. Set up virtual environment
3. Run `python app.py` to start web interface
4. Load existing models from `models/` directory
5. Make predictions on new listings

### For Production Deployment
1. Ensure trained model exists in `models/`
2. Load model in `app.py`
3. Run Flask app with production server (gunicorn, etc.)
4. Monitor prediction accuracy and retrain periodically

## 📈 Model Performance

### Evaluation Metrics
- **R² Score**: Coefficient of determination (0-1, higher is better)
- **MAE**: Mean Absolute Error in KES (lower is better)
- **RMSE**: Root Mean Squared Error in KES (lower is better)
- **MAPE**: Mean Absolute Percentage Error (%, lower is better)

### Train/Test Split
- Training set: 80% of data
- Test set: 20% of data
- Random state: 42 (reproducibility)

## 🗂️ Data Management

### Data Directory Workflow
```
Collection → Raw Data → Processing → Processed Data → Modeling
quick_collect.py  data/raw/  Data_Cleaning.ipynb  data/processed/  Model_Training.ipynb
bulk_collect.py
```

### File Organization
- **`data/raw/`**: Store raw scraped CSVs here
- **`data/processed/`**: Output cleaned/processed data here
- **`data/archives/`**: Archive old runs for reference
- **`datas/`**: Example datasets for testing

### Cleaning Up Data
```sh
# Archive old raw data
mv data/raw/* data/archives/

# Keep only latest processed data
rm data/processed/old_*.csv
```

## 🚨 Troubleshooting

### Problem: ModuleNotFoundError when running app.py
**Solution**: Ensure virtual environment is activated
```sh
source .venv/bin/activate
python app.py
```

### Problem: No models found in models/ directory
**Solution**: Run model training notebook first
```sh
jupyter notebook Notebooks/Model_Training.ipynb
```

### Problem: FileNotFoundError for data files
**Solution**: Run data collection script
```sh
python quick_collect.py
# or
python generate_demo_data.py
```

### Problem: Missing dependencies
**Solution**: Reinstall requirements
```sh
pip install --upgrade -r requirements.txt
```

## 📚 Example Usage

### Making Predictions Programmatically
```python
import joblib
import pandas as pd

# Load model and feature columns
model = joblib.load('models/best_model_*.joblib')
features = joblib.load('models/feature_columns_*.joblib')

# Prepare property data
property_data = pd.DataFrame({
    'bedrooms': [3],
    'bathrooms': [2],
    'size_sqft': [1500],
    'location': ['Westlands'],
    'amenity_count': [4],
    # ... other features
})

# Make prediction
predicted_price = model.predict(property_data)
print(f"Predicted Price: KES {predicted_price[0]:,.0f}")
```

### Using the Web Interface
1. Run `python app.py`
2. Open browser to `http://localhost:5000`
3. Fill in property details
4. Submit form to get prediction
5. View predicted price and confidence

## 🔄 Retraining Models

To retrain models with new data:

1. Collect new listings:
   ```sh
   python bulk_collect.py
   ```

2. Clean and process data:
   - Open `Notebooks/Data_Cleaning.ipynb`
   - Run all cells

3. Train new models:
   - Open `Notebooks/Model_Training.ipynb`
   - Run all cells
   - New model artifacts saved to `models/`

4. Update app.py to use new model file

## 📞 Support & Contributing

### Reporting Issues
1. Check if issue already exists
2. Provide detailed error message
3. Include Python/environment version
4. Share sample data if applicable

### Contributing
1. Create feature branch
2. Make focused changes
3. Test thoroughly
4. Document changes
5. Submit pull request

### Code Standards
- Follow PEP 8 style guide
- Add docstrings to functions
- Comment complex logic
- Update README for new features

## 📄 Project Metadata

- **Created**: February 19, 2026
- **Python Version**: 3.12+
- **Project Type**: Machine Learning / Data Science
- **Location Focus**: Nairobi, Kenya
- **Data Target**: Residential property prices (KES)
- **Models**: Tree-based ensemble methods

## 🎓 Learning Resources

**Key Notebooks**:
- `Notebooks/Model_Training.ipynb` - Complete ML pipeline
- `Notebooks/Data_Cleaning.ipynb` - Data preprocessing
- `Notebooks/EDA.ipynb` - Exploratory data analysis

**Technologies**:
- scikit-learn documentation: https://scikit-learn.org/
- XGBoost guide: https://xgboost.readthedocs.io/
- Flask tutorial: https://flask.palletsprojects.com/

---

**Last Updated**: February 23, 2026
**Maintained by**:Patrick Ngare