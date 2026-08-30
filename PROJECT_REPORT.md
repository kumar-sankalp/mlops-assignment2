# MLOps Assignment 2: Project Report

This document details the implementation steps and architecture of the complete MLOps pipeline built for the Cats vs. Dogs Image Classifier.

## Module 1: Containerization and API Enhancement
- **FastAPI Backend:** Developed a REST API (`app/main.py`) using FastAPI to serve the PyTorch ResNet-18 model.
- **Dockerization:** Created a lean `Dockerfile` using `python:3.9-slim` to containerize the application. 
- **Dependency Management:** All dependencies were strictly pinned in `requirements.txt` to guarantee reproducible builds, including resolving complex dependency conflicts between `torchvision` and `streamlit` (e.g., pinning `Pillow==9.5.0`).

## Module 2: Continuous Integration (CI)
- **GitHub Actions Pipeline:** Implemented a robust CI pipeline (`.github/workflows/ci-cd.yml`).
- **Build & Push Job:** Runs on `ubuntu-latest`. It sets up Python, installs dependencies, runs Pytest unit tests against the application, builds the Docker image, and automatically pushes it to Docker Hub with dynamic Git SHA tagging.

## Module 3: Continuous Deployment (CD)
- **Kubernetes Architecture:** Created Kubernetes deployment and service manifests for both the FastAPI backend (`k8s/deployment.yaml`) and the Streamlit UI (`k8s/streamlit-deployment.yaml`).
- **Self-Hosted Runner:** Configured the CD job (`deploy-to-local`) to run on a local macOS self-hosted runner, allowing the GitHub pipeline to deploy directly into the local Minikube cluster.
- **Deployment Script:** Developed `scripts/deploy_local.sh` to orchestrate Minikube initialization, local Docker daemon builds, manifest application, and automated port-forwarding.

## Module 4: Deployment Strategy & Testing
- **Automated Rollouts:** The CD pipeline dynamically updates the Kubernetes YAML files with the latest Docker image tag and triggers a rollout restart to ensure zero-downtime updates.
- **Smoke Testing:** Implemented an automated smoke test script (`scripts/smoke_test.py`) that executes immediately post-deployment. It checks the `/health` endpoint and verifies the `/predict` endpoint by sending dummy data to ensure the newly deployed model is fully operational.
- **Networking Fixes:** Bypassed macOS Minikube networking limitations by utilizing `kubectl port-forward` directly within the CI/CD pipeline to facilitate the smoke tests.

## Module 5: Monitoring & Logging
- **Prometheus Instrumentation:** Integrated `prometheus-fastapi-instrumentator` into the FastAPI backend to expose a `/metrics` endpoint, capturing critical system metrics (CPU, Memory, Uptime) and HTTP request metrics (Total Requests, Latency).
- **Streamlit Observability Dashboard:** Upgraded the Streamlit UI (`app/ui.py`) to include a dedicated "Monitoring Dashboard" tab.
    - **Live Metrics:** Parses the raw Prometheus text payload to visualize Total API Requests, Average Latency, Memory Usage, and API Uptime in real-time.
    - **Performance Tracking (Post-Deployment):** Implemented a visual benchmark tool that sends a batch of 4 real images (stored in `app/assets/`) through the live API to calculate and display the live model accuracy, simulating post-deployment model drift detection.
