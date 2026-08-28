import os
import subprocess
import sys
import shutil

def download_kaggle_dataset(dataset_name="salader/dogsvscats", download_path="data/raw"):
    """
    Downloads and extracts a Kaggle dataset using the Kaggle API.
    Requires ~/.kaggle/kaggle.json to be set up.
    """
    print(f"Attempting to download {dataset_name} from Kaggle...")
    
    # Check if kaggle is installed
    try:
        import kaggle
    except ImportError:
        print("Kaggle Python package is not installed. Please install it.")
        sys.exit(1)
        
    os.makedirs(download_path, exist_ok=True)
    
    try:
        # Run kaggle CLI command to download and unzip
        subprocess.run([
            "kaggle", "datasets", "download", 
            "-d", dataset_name, 
            "-p", download_path, 
            "--unzip"
        ], check=True)
        print(f"Dataset downloaded and extracted to {download_path}")
        
        # The salader/dogs-vs-cats dataset extracts to train and test folders.
        # We need to map it to our expected Cat and Dog folder structure in data/raw for data_preprocessing.py
        # Actually it extracts `train/dogs`, `train/cats` and `test/dogs`, `test/cats`.
        # Let's move them all into `data/raw/Cat` and `data/raw/Dog`
        
        cat_dir = os.path.join(download_path, "Cat")
        dog_dir = os.path.join(download_path, "Dog")
        os.makedirs(cat_dir, exist_ok=True)
        os.makedirs(dog_dir, exist_ok=True)
        
        for split in ['train', 'test']:
            split_dir = os.path.join(download_path, split)
            if not os.path.exists(split_dir):
                continue
                
            for class_name in ['cats', 'dogs']:
                src_dir = os.path.join(split_dir, class_name)
                if not os.path.exists(src_dir):
                    continue
                    
                dest_dir = cat_dir if class_name == 'cats' else dog_dir
                
                # Move all files
                for f in os.listdir(src_dir):
                    if f.endswith('.jpg'):
                        # To avoid name conflicts between train and test
                        new_name = f"{split}_{f}"
                        shutil.move(os.path.join(src_dir, f), os.path.join(dest_dir, new_name))
                        
            # Remove empty split dir
            shutil.rmtree(split_dir)
            
        print("Data reorganized successfully into Cat and Dog folders.")
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to download dataset. Error: {e}")
        print("\nMake sure you have your Kaggle API credentials set up:")
        print("1. Create an account on kaggle.com")
        print("2. Go to 'Account' and click 'Create New API Token'")
        print("3. Save the downloaded kaggle.json to ~/.kaggle/kaggle.json")
        print("4. Ensure permissions are correct: chmod 600 ~/.kaggle/kaggle.json")
        sys.exit(1)

if __name__ == "__main__":
    download_kaggle_dataset()
