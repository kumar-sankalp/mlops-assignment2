# MLOps Pipeline: Cats vs Dogs Image Classification

An end-to-end MLOps pipeline for a binary image classification task (Cats vs Dogs) designed for a pet adoption platform. This repository covers model development, artifact tracking, packaging, containerization, and a CI/CD-based deployment pipeline using modern open-source tools.

## Project Structure
```
.
├── .dvc/                  # DVC configuration for data versioning
├── .github/workflows/     # GitHub Actions for CI/CD pipelines
├── app/                   # FastAPI backend and Streamlit UI
│   ├── main.py            # FastAPI REST API serving the model
│   ├── ui.py              # Streamlit Web User Interface
│   └── tests/             # Pytest unit tests for API and Data
├── data/                  # Versioned datasets (not checked into git)
│   ├── raw/               # Raw downloaded Kaggle images
│   └── processed/         # Processed images (if applicable)
├── notebooks/             # Jupyter notebooks for interactive analysis
│   └── mlops_pipeline.ipynb
├── src/                   # Source code for model training and preprocessing
│   ├── data_preprocessing.py
│   ├── download_data.py   # Script to download data from Kaggle
│   ├── model.py           # PyTorch CNN architecture
│   └── train.py           # Training loop and MLflow tracking
├── docker-compose.yml     # Orchestration for multi-container deployment
├── Dockerfile             # Container image instructions
├── requirements.txt       # Python dependencies
└── smoke_test.py          # Post-deployment health verification script
```

## Setup Instructions

### 1. Environment & Dependencies
Create a Python 3.9+ virtual environment and install the dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Dataset Download
Ensure your Kaggle API key is configured at `~/.kaggle/kaggle.json`. Then download the dataset:
```bash
python src/download_data.py
```

### 3. Training & Experiment Tracking
Train the PyTorch baseline model. Metrics (loss, accuracy) and parameters are tracked automatically using MLflow.
```bash
python src/train.py
```
To view the MLflow UI:
```bash
mlflow ui --port 5001
```

### 4. Containerized Deployment
Deploy the FastAPI backend and Streamlit Web UI via Docker Compose:
```bash
docker compose up --build -d
```
- **Streamlit Web UI:** [http://localhost:8501](http://localhost:8501)
- **FastAPI Backend / Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Continuous Integration (CI)
Automated testing via GitHub Actions ensures stability. The pipeline automatically runs tests in `app/tests/` and builds the Docker container on every push to the `main` branch.

### 6. Smoke Testing
Post deployment, verify that the REST endpoints are functioning correctly:
```bash
python smoke_test.py
```
