import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add src to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from data_preprocessing import get_dataloaders, generate_dummy_data

def test_generate_dummy_data(tmp_path):
    """Test the generation of dummy data."""
    raw_data_dir = tmp_path / "data" / "raw"
    os.makedirs(raw_data_dir, exist_ok=True)
    
    generate_dummy_data(str(raw_data_dir), num_samples=10)
    
    # Check if directories were created
    assert os.path.exists(os.path.join(raw_data_dir, "Cat"))
    assert os.path.exists(os.path.join(raw_data_dir, "Dog"))
    
    # Check if files were created
    cat_files = os.listdir(os.path.join(raw_data_dir, "Cat"))
    dog_files = os.listdir(os.path.join(raw_data_dir, "Dog"))
    
    assert len(cat_files) == 5
    assert len(dog_files) == 5

@patch('data_preprocessing.train_test_split')
def test_get_dataloaders(mock_split, tmp_path):
    """Test getting dataloaders with dummy data."""
    raw_data_dir = tmp_path / "data" / "raw"
    os.makedirs(raw_data_dir, exist_ok=True)
    generate_dummy_data(str(raw_data_dir), num_samples=20)
    
    # Simple mock for train_test_split to avoid dealing with stratification of small samples in tests
    mock_split.side_effect = [
        # First split (TrainVal, Test)
        (list(range(16)), list(range(16, 20)), list(range(16)), list(range(16, 20))),
        # Second split (Train, Val)
        (list(range(12)), list(range(12, 16)), list(range(12)), list(range(12, 16)))
    ]
    
    # We patch glob to return dummy valid files and avoid actual image validation in this simple test
    with patch('data_preprocessing.glob.glob') as mock_glob, \
         patch('PIL.Image.open') as mock_open:
        
        # Setup mock files
        cat_files = [f"cat_{i}.jpg" for i in range(10)]
        dog_files = [f"dog_{i}.jpg" for i in range(10)]
        mock_glob.side_effect = [cat_files, dog_files]
        
        # Mock image open to avoid FileNotFoundError
        mock_img = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_img
        
        train_loader, val_loader, test_loader = get_dataloaders(str(raw_data_dir), batch_size=4)
        
        assert train_loader is not None
        assert val_loader is not None
        assert test_loader is not None
