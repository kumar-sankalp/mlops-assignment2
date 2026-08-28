import streamlit as st
import requests
from PIL import Image
import io

# Setup page config
st.set_page_config(page_title="Cats vs Dogs Classifier", page_icon="🐾", layout="centered")

st.title("🐾 Cats vs Dogs Image Classifier")
st.write("Upload an image of a cat or a dog, and the model will classify it!")

import os

# Define the API endpoint
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Sidebar for Health Check and Smoke Test
st.sidebar.title("API Operations")

st.sidebar.subheader("System Health")
if st.sidebar.button("Check Health"):
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            st.sidebar.success("API is running and healthy!")
        else:
            st.sidebar.error(f"API returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.sidebar.error("Cannot connect to API. Is it running?")

st.sidebar.subheader("Automated Smoke Test")
st.sidebar.write("Simulates end-to-end testing post-deployment.")
if st.sidebar.button("Run Smoke Test"):
    st.sidebar.info("Running smoke test...")
    try:
        # 1. Test Health
        h_resp = requests.get(f"{API_URL}/health")
        if h_resp.status_code != 200:
            st.sidebar.error("❌ Health check failed!")
        else:
            st.sidebar.success("✅ Health check passed!")
            
            # 2. Test Prediction with Dummy Image
            img = Image.new('RGB', (224, 224), color = 'blue')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            files = {'file': ('dummy.jpg', img_byte_arr, 'image/jpeg')}
            p_resp = requests.post(f"{API_URL}/predict", files=files)
            
            if p_resp.status_code == 200:
                st.sidebar.success(f"✅ Prediction passed! Result: {p_resp.json()['prediction']}")
            else:
                st.sidebar.error(f"❌ Prediction failed! Status: {p_resp.status_code}")
                
    except Exception as e:
        st.sidebar.error(f"❌ Smoke test error: {str(e)}")

# Main upload section
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_container_width=True)
    
    st.write("")
    
    # Add a button to make prediction
    if st.button("Classify Image", type="primary"):
        with st.spinner("Classifying..."):
            try:
                # Prepare the file for sending via POST
                # Reset file pointer
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)}
                
                # Make the POST request to the prediction endpoint
                response = requests.post(f"{API_URL}/predict", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    prediction = result["prediction"]
                    probability = result["probability"]
                    
                    st.success("Classification Complete!")
                    st.markdown(f"### Prediction: **{prediction}**")
                    
                    # Optional: display confidence metric
                    confidence = probability if prediction == "Dog" else 1 - probability
                    st.metric(label="Confidence", value=f"{confidence * 100:.2f}%")
                    
                else:
                    st.error(f"Error from API: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Please make sure the backend is running.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
