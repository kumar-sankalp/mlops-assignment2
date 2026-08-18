import requests
import sys
import time

def run_smoke_test(base_url="http://localhost:8000"):
    print(f"Running smoke tests against {base_url}...")
    
    # Wait for service to be up
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health")
            if response.status_code == 200:
                print("Health check passed.")
                break
        except requests.exceptions.ConnectionError:
            if i == max_retries - 1:
                print("Failed to connect to the service.")
                sys.exit(1)
            print("Service not ready, retrying in 5 seconds...")
            time.sleep(5)
            
    # Test Prediction (Needs a dummy image)
    from PIL import Image
    import io
    
    print("Testing prediction endpoint...")
    img = Image.new('RGB', (224, 224), color = 'blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    files = {'file': ('dummy.jpg', img_byte_arr, 'image/jpeg')}
    try:
        response = requests.post(f"{base_url}/predict", files=files)
        if response.status_code == 200:
            print(f"Prediction successful: {response.json()}")
        else:
            print(f"Prediction failed with status {response.status_code}: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Prediction request failed: {e}")
        sys.exit(1)
        
    print("All smoke tests passed successfully!")

if __name__ == "__main__":
    run_smoke_test()
