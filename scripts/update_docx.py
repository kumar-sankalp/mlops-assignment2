from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
# Title
title = doc.add_heading('MLOps Assignment 2: Comprehensive Project Report', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph('This document provides an exhaustive, step-by-step technical breakdown of the end-to-end MLOps pipeline implemented for the binary image classification assignment. The architecture encompasses a robust stack: PyTorch for deep learning, FastAPI for API serving, Docker for containerization, GitHub Actions for Continuous Integration (CI), Minikube and Kubernetes for Continuous Deployment (CD), and Prometheus alongside Streamlit for real-time observability.')
doc.add_page_break()

# Module 1
doc.add_heading('Module 1: Containerization and API Enhancement', level=1)
doc.add_paragraph('The foundational step of this MLOps pipeline involved exposing the trained PyTorch ResNet-18 model via a robust, production-ready REST API and ensuring the environment was perfectly reproducible.')
doc.add_heading('FastAPI Backend Implementation', level=2)
doc.add_paragraph('FastAPI was chosen for the backend due to its high performance (powered by Starlette and Pydantic) and automatic OpenAPI documentation generation. The application (app/main.py) exposes two primary endpoints:')
doc.add_paragraph('1. /health: A lightweight GET endpoint utilized by Kubernetes readiness/liveness probes and smoke tests to verify the API is alive.')
doc.add_paragraph('2. /predict: A POST endpoint that accepts multipart form data (images), processes them through the PyTorch transforms, runs inference through the loaded model.pt artifact, and returns the predicted class (Cat/Dog) along with confidence probabilities.')
doc.add_heading('Strict Dependency Management', level=2)
doc.add_paragraph('A significant engineering challenge encountered during containerization was dependency resolution. The combination of torchvision, Streamlit, and FastAPI resulted in strict versioning conflicts, specifically regarding the Pillow library. To resolve this, exact versions were pinned in requirements.txt (e.g., Pillow==9.5.0), adhering to PEP guidelines for deterministic builds. This ensures that the Docker container builds identically across all environments.')
doc.add_heading('Dockerization Strategy', level=2)
doc.add_paragraph('The application was containerized using a multi-stage-like approach utilizing the python:3.9-slim base image to minimize the final image footprint. The Dockerfile was optimized for caching: requirements are copied and installed first, ensuring that code changes in the src/ or app/ directories do not trigger a full re-installation of heavy PyTorch binaries.')
doc.add_paragraph('[ INSERT FASTAPI SWAGGER DOCS SCREENSHOT HERE ]')
doc.add_page_break()

# Module 2
doc.add_heading('Module 2: Continuous Integration (CI)', level=1)
doc.add_paragraph('To ensure code quality and prevent regressions, a fully automated Continuous Integration pipeline was configured using GitHub Actions.')
doc.add_heading('Automated Testing', level=2)
doc.add_paragraph('Before any code is permitted to be built into a Docker image, it must pass a suite of Pytest unit tests. These tests validate the integrity of the data preprocessing pipelines (ensuring image tensors match expected shapes) and perform mock requests against the FastAPI endpoints.')
doc.add_heading('Cloud Build and Registry Push', level=2)
doc.add_paragraph('The CI pipeline (.github/workflows/ci-cd.yml) runs on a cloud-hosted ubuntu-latest runner. Upon successful completion of the tests, it executes a docker build. The resulting image is tagged dynamically using the unique Git SHA of the commit (for traceability) and latest (for easy consumption). The pipeline then automatically authenticates with Docker Hub using securely stored repository secrets and pushes the newly built images to the remote registry.')
doc.add_paragraph('[ INSERT GITHUB ACTIONS CI PIPELINE SCREENSHOT HERE ]')
doc.add_page_break()

# Module 3 & 4
doc.add_heading('Module 3 & 4: Continuous Deployment (CD) and Testing', level=1)
doc.add_paragraph('The deployment strategy required transitioning from a local Docker Compose setup to a scalable Kubernetes environment using Minikube.')
doc.add_heading('Kubernetes Manifests', level=2)
doc.add_paragraph('Declarative YAML manifests were authored for both the backend (mlops-inference) and frontend (streamlit-ui). Each component features a Deployment (to manage pod replicas and rollout strategies) and a Service (to provide stable internal Cluster IP networking). The Streamlit frontend is configured via environment variables to route traffic to the internal DNS name of the backend service (http://mlops-inference-service:8000).')
doc.add_heading('Self-Hosted Runner Integration', level=2)
doc.add_paragraph('To facilitate deployment directly into the local macOS Minikube cluster, a Self-Hosted GitHub Runner was configured. The deploy-to-local job in the GitHub Actions pipeline is triggered only after the CI job passes. It dynamically rewrites the Kubernetes manifests using sed to inject the exact Git SHA image tag built in the CI phase, preventing "latest tag caching" issues in Kubernetes. It then applies the manifests and issues a kubectl rollout restart.')
doc.add_heading('Automated Smoke Testing and Networking Solutions', level=2)
doc.add_paragraph('Immediately following deployment, the pipeline executes an automated smoke test (scripts/smoke_test.py). A significant challenge on macOS is that Minikube runs inside a lightweight VM, making its internal IP address unroutable from the host OS. To bypass this, the CI/CD pipeline dynamically establishes a kubectl port-forward tunnel in the background, allowing the Python test script to successfully hit the cluster at localhost:8000. The script verifies the /health endpoint and submits a dummy payload to /predict, failing the deployment if the API responds improperly.')
doc.add_paragraph('[ INSERT TERMINAL SCREENSHOT SHOWING PODS RUNNING HERE ]')
doc.add_page_break()

# Module 5
doc.add_heading('Module 5: Monitoring, Logs, and Observability', level=1)
doc.add_paragraph('To fulfill the requirements of MLOps maturity, real-time monitoring and post-deployment performance tracking were integrated.')
doc.add_heading('Prometheus Metrics Integration', level=2)
doc.add_paragraph('The FastAPI application was instrumented using the prometheus-fastapi-instrumentator library. This automatically exposes a /metrics endpoint that scrapes and formats system-level data (Process CPU time, Resident Memory) and HTTP request data (Total Request Counts, Latency histograms) into the Prometheus exposition format.')
doc.add_heading('Custom Streamlit Dashboard', level=2)
doc.add_paragraph('Rather than relying purely on terminal logs, a bespoke "Monitoring Dashboard" tab was engineered directly into the Streamlit UI.')
doc.add_paragraph('1. Live Metric Parsing: The dashboard makes internal requests to the API /metrics endpoint and utilizes complex regular expressions to parse the scientific notation output from Prometheus. It dynamically visualizes Total API Requests, Average Latency, Memory Usage (MB), and API Uptime directly in the browser.')
doc.add_paragraph('2. Model Performance Tracking (Data Drift Simulation): To test the live model against potential data drift, a "Run Performance Benchmark" button was implemented. This tool pulls a batch of real, pre-labeled images from the data/raw folder (which were explicitly bundled into the application assets). It sends these images sequentially to the live API, measures the round-trip latency, compares the model prediction against the true label, and calculates the overall live Model Accuracy on screen.')
doc.add_paragraph('[ INSERT STREAMLIT MONITORING DASHBOARD SCREENSHOT HERE ]')

doc.save('docs/Assignment_Report.docx')
print("Successfully generated detailed docs/Assignment_Report.docx")
