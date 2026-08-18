import os
import torch
import torch.nn as nn
import torch.optim as optim
import mlflow
import mlflow.pytorch
from model import SimpleCNN
from data_preprocessing import get_dataloaders

def train_model():
    # Hyperparameters
    batch_size = 32
    learning_rate = 0.001
    num_epochs = 5
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load data
    train_loader, val_loader, _ = get_dataloaders(batch_size=batch_size)
    
    # Initialize model, loss function, and optimizer
    model = SimpleCNN().to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # Start MLflow run
    mlflow.set_experiment("Cats_vs_Dogs_Classification")
    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("batch_size", batch_size)
        mlflow.log_param("learning_rate", learning_rate)
        mlflow.log_param("num_epochs", num_epochs)
        mlflow.log_param("optimizer", "Adam")
        
        for epoch in range(num_epochs):
            model.train()
            running_loss = 0.0
            
            for inputs, labels in train_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                
                optimizer.zero_grad()
                
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
                running_loss += loss.item() * inputs.size(0)
                
            epoch_loss = running_loss / len(train_loader.dataset)
            print(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {epoch_loss:.4f}")
            mlflow.log_metric("train_loss", epoch_loss, step=epoch)
            
            # Validation
            model.eval()
            val_loss = 0.0
            correct = 0
            total = 0
            
            with torch.no_grad():
                for inputs, labels in val_loader:
                    inputs, labels = inputs.to(device), labels.to(device)
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    val_loss += loss.item() * inputs.size(0)
                    
                    predicted = (outputs > 0.0).float()
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()
                    
            epoch_val_loss = val_loss / len(val_loader.dataset)
            val_accuracy = correct / total
            
            print(f"Epoch {epoch+1}/{num_epochs}, Val Loss: {epoch_val_loss:.4f}, Val Acc: {val_accuracy:.4f}")
            mlflow.log_metric("val_loss", epoch_val_loss, step=epoch)
            mlflow.log_metric("val_accuracy", val_accuracy, step=epoch)
            
        # Save model
        model_path = "model.pt"
        torch.save(model.state_dict(), model_path)
        
        # Log model artifact
        mlflow.log_artifact(model_path)
        print(f"Model saved to {model_path} and logged to MLflow")

if __name__ == '__main__':
    train_model()
