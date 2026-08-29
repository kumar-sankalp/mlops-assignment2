import sys
import os
import requests
import time

def read_image(filepath, label):
    """Read a real image from the dataset."""
    with open(filepath, 'rb') as f:
        return f.read(), label

def main(base_url):
    print(f"Starting post-deployment performance tracking against {base_url}...")
    
    # We will grab a couple of real images from your local dataset to get real accuracy!
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Safely try to load real images. If they don't exist, we fallback.
    try:
        simulated_batch = [
            read_image(os.path.join(base_dir, "data/raw/Cat/train_cat.6141.jpg"), 'Cat'),
            read_image(os.path.join(base_dir, "data/raw/Cat/train_cat.9272.jpg"), 'Cat'),
            read_image(os.path.join(base_dir, "data/raw/Dog/train_dog.2665.jpg"), 'Dog'),
            read_image(os.path.join(base_dir, "data/raw/Dog/train_dog.9730.jpg"), 'Dog'),
        ]
    except FileNotFoundError:
        print("Warning: Real dataset images not found in data/raw/. Ensure you run this on a machine with the data.")
        return
    
    correct_predictions = 0
    total_requests = len(simulated_batch)
    
    print("\nProcessing batch...")
    for i, (img_bytes, true_label) in enumerate(simulated_batch):
        files = {'file': (f'image_{i}.jpg', img_bytes, 'image/jpeg')}
        
        start_time = time.time()
        response = requests.post(f"{base_url}/predict", files=files)
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            prediction = result['prediction']
            
            is_correct = prediction == true_label
            if is_correct:
                correct_predictions += 1
                
            print(f"Request {i+1}: True Label={true_label} | Prediction={prediction} | Correct={is_correct} | Latency={latency:.2f}ms")
        else:
            print(f"Request {i+1}: Failed with status code {response.status_code}")
            
    accuracy = (correct_predictions / total_requests) * 100 if total_requests > 0 else 0
    
    print("\n==================================")
    print(" Performance Tracking Summary")
    print("==================================")
    print(f"Total Requests Processed : {total_requests}")
    print(f"Correct Predictions      : {correct_predictions}")
    print(f"Model Accuracy           : {accuracy:.2f}%")
    print("==================================")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    main(url)
