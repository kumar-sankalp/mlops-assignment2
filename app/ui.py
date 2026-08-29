import streamlit as st
import requests
from PIL import Image
import io
import os
import time
import re

# Setup page config
st.set_page_config(page_title="MLOps Dashboard", page_icon="🐾", layout="wide")

API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Setup Tabs
tab1, tab2 = st.tabs(["🐾 Inference", "📊 Monitoring Dashboard"])

with tab1:
    st.title("🐾 Cats vs Dogs Image Classifier")
    st.write("Upload an image of a cat or a dog, and the model will classify it!")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', width=400)
        
        if st.button("Classify Image", type="primary"):
            with st.spinner("Classifying..."):
                try:
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)}
                    response = requests.post(f"{API_URL}/predict", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        prediction = result["prediction"]
                        probability = result["probability"]
                        st.success("Classification Complete!")
                        st.markdown(f"### Prediction: **{prediction}**")
                        confidence = probability if prediction == "Dog" else 1 - probability
                        st.metric(label="Confidence", value=f"{confidence * 100:.2f}%")
                    else:
                        st.error(f"Error from API: {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

with tab2:
    st.title("📊 Model Monitoring & Performance Dashboard")
    st.write("Real-time observability into the MLOps pipeline.")
    
    # 1. Prometheus Metrics
    st.subheader("Live Prometheus Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        metrics_resp = requests.get(f"{API_URL}/metrics")
        if metrics_resp.status_code == 200:
            text = metrics_resp.text
            # Parse total requests
            req_match = re.search(r'http_requests_total\{.*?\} ([0-9.]+)', text)
            total_reqs = int(float(req_match.group(1))) if req_match else 0
            
            # Parse latency
            sum_match = re.search(r'http_request_duration_seconds_sum\{.*?\} ([0-9.]+)', text)
            count_match = re.search(r'http_request_duration_seconds_count\{.*?\} ([0-9.]+)', text)
            
            avg_latency = 0
            if sum_match and count_match:
                s = float(sum_match.group(1))
                c = float(count_match.group(1))
                if c > 0:
                    avg_latency = (s / c) * 1000 # in ms
            
            # Parse memory usage
            mem_match = re.search(r'process_resident_memory_bytes ([0-9.]+)', text)
            mem_mb = (float(mem_match.group(1)) / (1024 * 1024)) if mem_match else 0
            
            # Parse uptime
            start_match = re.search(r'process_start_time_seconds ([0-9.]+)', text)
            uptime_s = (time.time() - float(start_match.group(1))) if start_match else 0
            
            col1.metric("Total API Requests", total_reqs)
            col2.metric("Average Latency", f"{avg_latency:.2f} ms")
            col3.metric("Memory Usage", f"{mem_mb:.2f} MB")
            
            # Format uptime nicely
            mins, secs = divmod(int(uptime_s), 60)
            hours, mins = divmod(mins, 60)
            uptime_str = f"{hours}h {mins}m {secs}s" if hours > 0 else f"{mins}m {secs}s"
            col4.metric("API Uptime", uptime_str)
            
        else:
            st.error("Failed to fetch metrics.")
    except Exception as e:
        st.error(f"Could not connect to /metrics: {e}")
        
    st.markdown("---")
    
    # 2. Post-Deployment Performance Tracking
    st.subheader("Post-Deployment Performance Tracker")
    st.write("Simulates a batch of requests with known labels to calculate live model accuracy.")
    
    if st.button("Run Performance Benchmark"):
        with st.spinner("Processing batch..."):
            def generate_dummy(color):
                img = Image.new('RGB', (224, 224), color=color)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                return img_byte_arr.getvalue()
                
            simulated_batch = [
                (generate_dummy('red'), 'Cat'),
                (generate_dummy('blue'), 'Dog'),
                (generate_dummy('green'), 'Cat'),
                (generate_dummy('yellow'), 'Dog'),
            ]
            
            results = []
            correct_predictions = 0
            
            for i, (img_bytes, true_label) in enumerate(simulated_batch):
                files = {'file': (f'dummy_{i}.jpg', img_bytes, 'image/jpeg')}
                start_t = time.time()
                resp = requests.post(f"{API_URL}/predict", files=files)
                latency = (time.time() - start_t) * 1000
                
                if resp.status_code == 200:
                    pred = resp.json()['prediction']
                    is_correct = (pred == true_label)
                    if is_correct: correct_predictions += 1
                    
                    results.append({
                        "Request": f"Image {i+1}",
                        "True Label": true_label,
                        "Prediction": pred,
                        "Correct?": "✅" if is_correct else "❌",
                        "Latency (ms)": f"{latency:.2f}"
                    })
            
            st.table(results)
            accuracy = (correct_predictions / len(simulated_batch)) * 100
            st.metric("Model Accuracy (Batch)", f"{accuracy:.2f}%")
