import os
import sys
from fastapi.testclient import TestClient
from PIL import Image
import io

# Add app to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_predict_endpoint_valid_image():
    # Create a dummy image
    img = Image.new('RGB', (224, 224), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    files = {'file': ('test.jpg', img_byte_arr, 'image/jpeg')}
    response = client.post("/predict", files=files)
    
    assert response.status_code == 200
    json_data = response.json()
    assert "prediction" in json_data
    assert "probability" in json_data
    assert json_data["prediction"] in ["Cat", "Dog"]

def test_predict_endpoint_invalid_file():
    # Provide a text file instead of an image
    files = {'file': ('test.txt', b"Hello World", 'text/plain')}
    response = client.post("/predict", files=files)
    
    assert response.status_code == 400
    assert "not an image" in response.json()["detail"]
