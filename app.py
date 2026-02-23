import streamlit as st
import pickle
import numpy as np
import pandas as pd
import json
import os

# Page configuration
st.set_page_config(
    page_title="🏠 Nairobi House Price Predictor",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Load model and metadata
@st.cache_resource
def load_model():
    """Load trained model from pickle file"""
    model_path = 'models/model.pkl'
    if not os.path.exists(model_path):
        st.error("❌ Model file not found. Please ensure model.pkl exists in the models/ directory.")
        st.stop()
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

@st.cache_resource
def load_features():
    """Load feature columns from pickle file"""
    # Try to find the feature file
    models_dir = 'models'
    if not os.path.exists(models_dir):
        return None
    
    feature_files = [f for f in os.listdir(models_dir) if f.startswith('feature_columns')]
    if not feature_files:
        return None
    
    feature_path = os.path.join(models_dir, feature_files[0])
    with open(feature_path, 'rb') as f:
        features = pickle.load(f)
    return features

@st.cache_resource
def load_metadata():
    """Load model metadata from JSON file"""
    models_dir = 'models'
    if not os.path.exists(models_dir):
        return None
    
    metadata_files = [f for f in os.listdir(models_dir) if f.startswith('model_metadata')]
    if not metadata_files:
        return None
    
    metadata_path = os.path.join(models_dir, metadata_files[0])
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return metadata

# Load model, features, and metadata
model = load_model()
features = load_features()
metadata = load_metadata()

# Title
st.title("🏠 Nairobi House Price Predictor")
st.markdown("*Predict house prices in Nairobi using Machine Learning*")

# Sidebar - Model Info
with st.sidebar:
    st.header("📊 Model Information")
    if metadata:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("R² Score", f"{metadata.get('r2_score', 0):.4f}")
            st.metric("MAE", f"KES {metadata.get('mae', 0):,.0f}")
        with col2:
            st.metric("RMSE", f"KES {metadata.get('rmse', 0):,.0f}")
            st.metric("MAPE", f"{metadata.get('mape', 0):.2f}%")
        
        st.divider()
        st.write(f"**Model Type:** {metadata.get('model_type', 'N/A')}")
        st.write(f"**Training Samples:** {metadata.get('training_samples', 'N/A')}")
        st.write(f"**Test Samples:** {metadata.get('test_samples', 'N/A')}")

# Main content
tab1, tab2, tab3 = st.tabs(["🎯 Make Prediction", "📈 Model Details", "📋 Batch Predictions"])

# ==================== TAB 1: Make Prediction ====================
with tab1:
    st.subheader("Enter Property Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        bedrooms = st.slider(
            "Bedrooms",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of bedrooms in the property"
        )
        
        bathrooms = st.slider(
            "Bathrooms",
            min_value=1,
            max_value=8,
            value=2,
            help="Number of bathrooms in the property"
        )
        
        size_sqft = st.number_input(
            "Size (sq ft)",
            min_value=500,
            max_value=50000,
            value=2500,
            step=100,
            help="Property size in square feet"
        )
        
        location = st.selectbox(
            "Location",
            options=[
                "Westlands", "Kilimani", "Parklands", "Lavington", "Upper Hill",
                "Nairobi West", "Langata", "Karen", "Muthaiga", "Karura",
                "Ridgeways", "Limuru", "Ruaka", "Kikuyu", "Thika",
                "Mombasa Road", "South C", "South B", "Embakasi", "Umoja",
                "Dandora", "Kayole", "Mathare", "Kibra", "Korogocho"
            ],
            help="Select property location"
        )
        
        property_type = st.selectbox(
            "Property Type",
            options=["Apartment", "House", "Townhouse", "Maisonette", "Bungalow"],
            help="Type of property"
        )
    
    with col2:
        has_amenities = st.checkbox(
            "Has Amenities (Pool, Gym, etc.)",
            value=True,
            help="Does the property have amenities?"
        )
        
        amenity_count = st.slider(
            "Number of Amenities",
            min_value=0,
            max_value=15,
            value=3,
            disabled=not has_amenities,
            help="Number of amenities available"
        ) if has_amenities else 0
        
        st.info("💡 Tip: The model will automatically calculate derived features like price_per_bed and price_per_sqft")
    
    # Make Prediction
    if st.button("🔮 Predict Price", use_container_width=True, type="primary"):
        try:
            # Encode location and property type (using simple encoding)
            locations = [
                "Westlands", "Kilimani", "Parklands", "Lavington", "Upper Hill",
                "Nairobi West", "Langata", "Karen", "Muthaiga", "Karura",
                "Ridgeways", "Limuru", "Ruaka", "Kikuyu", "Thika",
                "Mombasa Road", "South C", "South B", "Embakasi", "Umoja",
                "Dandora", "Kayole", "Mathare", "Kibra", "Korogocho"
            ]
            property_types = ["Apartment", "House", "Townhouse", "Maisonette", "Bungalow"]
            
            location_encoded = locations.index(location)
            property_type_encoded = property_types.index(property_type)
            
            # Calculate derived features
            price_per_bed = 0  # Will be calculated by model prediction
            price_per_sqft = 0  # Will be calculated by model prediction
            bed_bath_ratio = bedrooms / (bathrooms + 1)
            total_rooms = bedrooms + bathrooms
            
            # Create feature vector (initial price_per_bed and price_per_sqft as 0)
            feature_vector = np.array([[
                bedrooms,
                bathrooms,
                size_sqft,
                location_encoded,
                property_type_encoded,
                price_per_bed,  # Placeholder
                price_per_sqft,  # Placeholder
                bed_bath_ratio,
                total_rooms,
                int(has_amenities),
                amenity_count
            ]])
            
            # Make prediction
            predicted_price = model.predict(feature_vector)[0]
            
            # Recalculate derived features with predicted price
            price_per_bed_actual = predicted_price / (bedrooms + 1)
            price_per_sqft_actual = predicted_price / (size_sqft + 1)
            
            # Update feature vector and predict again for better accuracy
            feature_vector = np.array([[
                bedrooms,
                bathrooms,
                size_sqft,
                location_encoded,
                property_type_encoded,
                price_per_bed_actual,
                price_per_sqft_actual,
                bed_bath_ratio,
                total_rooms,
                int(has_amenities),
                amenity_count
            ]])
            
            predicted_price = model.predict(feature_vector)[0]
            
            # Display results
            st.divider()
            st.subheader("🎯 Prediction Result")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Predicted Price",
                    f"KES {predicted_price:,.0f}",
                    delta=None
                )
            
            with col2:
                price_per_sqft_final = predicted_price / size_sqft
                st.metric(
                    "Price per Sq Ft",
                    f"KES {price_per_sqft_final:,.0f}"
                )
            
            with col3:
                price_per_bed_final = predicted_price / (bedrooms + 1)
                st.metric(
                    "Price per Bedroom",
                    f"KES {price_per_bed_final:,.0f}"
                )
            
            # Summary table
            st.subheader("📋 Property Summary")
            summary_data = {
                "Feature": ["Bedrooms", "Bathrooms", "Size (sq ft)", "Location", "Property Type", "Amenities", "Amenity Count"],
                "Value": [bedrooms, bathrooms, f"{size_sqft:,}", location, property_type, "Yes" if has_amenities else "No", amenity_count]
            }
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
            
            st.success(f"✅ Prediction complete! The estimated price for this property is **KES {predicted_price:,.0f}**")
        
        except Exception as e:
            st.error(f"❌ Error making prediction: {str(e)}")

# ==================== TAB 2: Model Details ====================
with tab2:
    st.subheader("📈 Model Performance Metrics")
    
    if metadata:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("R² Score", f"{metadata['r2_score']:.4f}", help="Coefficient of determination (0-1, higher is better)")
            st.metric("MAE", f"KES {metadata['mae']:,.0f}", help="Mean Absolute Error")
            st.metric("RMSE", f"KES {metadata['rmse']:,.0f}", help="Root Mean Squared Error")
        
        with col2:
            st.metric("MAPE", f"{metadata['mape']:.2f}%", help="Mean Absolute Percentage Error")
            st.metric("Training Samples", metadata['training_samples'])
            st.metric("Test Samples", metadata['test_samples'])
        
        st.divider()
        st.subheader("🔧 Model Configuration")
        st.write(f"**Model Type:** {metadata['model_type']}")
        st.write(f"**Number of Features:** {metadata['n_features']}")
        
        st.subheader("📊 Features Used")
        features_list = metadata['feature_names']
        cols = st.columns(2)
        for idx, feature in enumerate(features_list):
            with cols[idx % 2]:
                st.write(f"• {feature}")
        
        st.divider()
        st.subheader("📌 Model Interpretation")
        st.markdown("""
        - **R² Score (0.9903)**: The model explains 99.03% of the variance in house prices - excellent fit
        - **MAE (±KES 1,388,575)**: On average, predictions are off by about 1.4M KES
        - **MAPE (3.77%)**: Percentage error is quite low, indicating reliable predictions
        - **Model Type**: Gradient Boosting Regressor (tuned with GridSearchCV)
        """)
    else:
        st.warning("⚠️ Model metadata not available")

# ==================== TAB 3: Batch Predictions ====================
with tab3:
    st.subheader("📋 Batch Predictions")
    
    st.info("💡 Upload a CSV file with property details to make multiple predictions at once")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write(f"**Uploaded Data** ({len(df)} rows)")
            st.dataframe(df.head(), use_container_width=True)
            
            if st.button("🔮 Predict All Prices", use_container_width=True, type="primary"):
                # Prepare data for predictions
                predictions_list = []
                
                locations = [
                    "Westlands", "Kilimani", "Parklands", "Lavington", "Upper Hill",
                    "Nairobi West", "Langata", "Karen", "Muthaiga", "Karura",
                    "Ridgeways", "Limuru", "Ruaka", "Kikuyu", "Thika",
                    "Mombasa Road", "South C", "South B", "Embakasi", "Umoja",
                    "Dandora", "Kayole", "Mathare", "Kibra", "Korogocho"
                ]
                property_types = ["Apartment", "House", "Townhouse", "Maisonette", "Bungalow"]
                
                progress_bar = st.progress(0)
                
                for idx, row in df.iterrows():
                    location_encoded = locations.index(row['location'])
                    property_type_encoded = property_types.index(row['property_type'])
                    bed_bath_ratio = row['bedrooms'] / (row['bathrooms'] + 1)
                    total_rooms = row['bedrooms'] + row['bathrooms']
                    
                    feature_vector = np.array([[
                        row['bedrooms'],
                        row['bathrooms'],
                        row['size_sqft'],
                        location_encoded,
                        property_type_encoded,
                        0,  # Placeholder
                        0,  # Placeholder
                        bed_bath_ratio,
                        total_rooms,
                        int(row.get('has_amenities', 1)),
                        row.get('amenity_count', 0)
                    ]])
                    
                    predicted_price = model.predict(feature_vector)[0]
                    
                    # Recalculate with actual price
                    price_per_bed_actual = predicted_price / (row['bedrooms'] + 1)
                    price_per_sqft_actual = predicted_price / (row['size_sqft'] + 1)
                    
                    feature_vector = np.array([[
                        row['bedrooms'],
                        row['bathrooms'],
                        row['size_sqft'],
                        location_encoded,
                        property_type_encoded,
                        price_per_bed_actual,
                        price_per_sqft_actual,
                        bed_bath_ratio,
                        total_rooms,
                        int(row.get('has_amenities', 1)),
                        row.get('amenity_count', 0)
                    ]])
                    
                    predicted_price = model.predict(feature_vector)[0]
                    predictions_list.append(predicted_price)
                    
                    progress_bar.progress((idx + 1) / len(df))
                
                df['Predicted_Price'] = predictions_list
                df['Price_per_Sqft'] = df['Predicted_Price'] / df['size_sqft']
                
                st.success(f"✅ Predicted prices for {len(df)} properties!")
                st.dataframe(df, use_container_width=True)
                
                # Download results
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Predictions (CSV)",
                    data=csv,
                    file_name="predicted_prices.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Make sure your CSV has columns: bedrooms, bathrooms, size_sqft, location, property_type")

# Footer
st.divider()
st.markdown("""
---
**Nairobi House Price Prediction** | Powered by Machine Learning 🤖
""")
