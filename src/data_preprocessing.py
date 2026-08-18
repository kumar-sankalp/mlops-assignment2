import os
import glob
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from sklearn.model_selection import train_test_split
import numpy as np

class CatsDogsDataset(Dataset):
    def __init__(self, file_paths, labels, transform=None):
        self.file_paths = file_paths
        self.labels = labels
        self.transform = transform
        
    def __len__(self):
        return len(self.file_paths)
    
    def __getitem__(self, idx):
        img_path = self.file_paths[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
            
        return image, torch.tensor([label], dtype=torch.float32)

def generate_dummy_data(raw_data_dir, num_samples=100):
    """Generates dummy data for testing if real data is not found."""
    print(f"Generating {num_samples} dummy images in {raw_data_dir}...")
    cats_dir = os.path.join(raw_data_dir, 'Cat')
    dogs_dir = os.path.join(raw_data_dir, 'Dog')
    os.makedirs(cats_dir, exist_ok=True)
    os.makedirs(dogs_dir, exist_ok=True)
    
    for i in range(num_samples // 2):
        # Create a random RGB image for Cat
        img = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
        img.save(os.path.join(cats_dir, f"{i}.jpg"))
        
        # Create a random RGB image for Dog
        img = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
        img.save(os.path.join(dogs_dir, f"{i}.jpg"))

def get_dataloaders(raw_data_dir='data/raw', batch_size=32):
    cat_files = glob.glob(os.path.join(raw_data_dir, 'Cat', '*.jpg'))
    dog_files = glob.glob(os.path.join(raw_data_dir, 'Dog', '*.jpg'))
    
    if len(cat_files) == 0 or len(dog_files) == 0:
        print("Real dataset not found. Generating dummy dataset for testing purposes.")
        generate_dummy_data(raw_data_dir)
        cat_files = glob.glob(os.path.join(raw_data_dir, 'Cat', '*.jpg'))
        dog_files = glob.glob(os.path.join(raw_data_dir, 'Dog', '*.jpg'))
        
    all_files = cat_files + dog_files
    # 0 for cat, 1 for dog
    labels = [0]*len(cat_files) + [1]*len(dog_files)
    
    # Check for valid images
    valid_files, valid_labels = [], []
    for f, l in zip(all_files, labels):
        try:
            with Image.open(f) as img:
                img.verify()
            valid_files.append(f)
            valid_labels.append(l)
        except Exception:
            print(f"Invalid image file: {f}")
            
    # Train (80%), Val (10%), Test (10%)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        valid_files, valid_labels, test_size=0.1, random_state=42, stratify=valid_labels
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.1111, random_state=42, stratify=y_train_val # 0.1111 * 0.9 ≈ 0.1
    )
    
    # Data Augmentation for training
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Basic transform for validation/testing
    val_test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    train_dataset = CatsDogsDataset(X_train, y_train, transform=train_transform)
    val_dataset = CatsDogsDataset(X_val, y_val, transform=val_test_transform)
    test_dataset = CatsDogsDataset(X_test, y_test, transform=val_test_transform)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader, test_loader

if __name__ == '__main__':
    train_loader, val_loader, test_loader = get_dataloaders()
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}, Test batches: {len(test_loader)}")
