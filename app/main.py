from fastapi import FastAPI, UploadFile, File, HTTPException
import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import sys
import os

# Add src to Python path so we can import model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
try:
    from model import SimpleCNN
except ImportError:
    # Handle the case where src is not accessible during some tests
    class SimpleCNN(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = torch.nn.Linear(3*224*224, 1)
        def forward(self, x):
            x = x.view(-1, 3*224*224)
            return self.fc(x)

app = FastAPI(title="Cats vs Dogs Classification API", version="1.0.0")

# Setup model
device = torch.device('cpu')
model = SimpleCNN()

# Path to trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model.pt')

try:
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        print("Model loaded successfully")
    else:
        print(f"Warning: Model file not found at {MODEL_PATH}. Using untrained model.")
except Exception as e:
    print(f"Warning: Could not load model: {e}")

model.eval()

# Preprocessing transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        # Preprocess
        input_tensor = transform(image).unsqueeze(0) # Add batch dimension
        
        # Predict
        with torch.no_grad():
            output = model(input_tensor)
            probability = torch.sigmoid(output).item()
            
        # Classify
        # 0 for cat, 1 for dog
        label = "Dog" if probability > 0.5 else "Cat"
        
        # Log request basic info
        print(f"Prediction made: {label} (Prob: {probability:.4f})")
        
        return {
            "prediction": label,
            "probability": probability
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
