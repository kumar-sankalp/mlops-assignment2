from docx import Document

doc = Document()
doc.add_heading('MLOps Assignment 2: Cats vs Dogs Classification', 0)

doc.add_paragraph('This document outlines the completion of the end-to-end MLOps pipeline for the binary image classification assignment. The tech stack includes FastAPI, Docker, GitHub Actions, Minikube (Kubernetes), Prometheus, and Streamlit.')

doc.add_heading('M1: Model Development & Experiment Tracking', level=1)
doc.add_paragraph('- Git was used for code versioning, and DVC for dataset tracking.')
doc.add_paragraph('- A PyTorch CNN baseline model was implemented in src/model.py.')
doc.add_paragraph('- The MLflow tracking URI was utilized to log parameters and metrics during training. The final serialized model (model.pt) was logged as an artifact.')
doc.add_paragraph('[ INSERT MLFLOW DASHBOARD SCREENSHOT HERE ]')

doc.add_heading('M2: Model Packaging & Containerization', level=1)
doc.add_paragraph('- The model was wrapped in a FastAPI REST API (app/main.py) with /health and /predict endpoints.')
doc.add_paragraph('- Dependencies were explicitly pinned in requirements.txt to prevent conflict issues (e.g., Pillow==9.5.0).')
doc.add_paragraph('- A Dockerfile was created to containerize the FastAPI service.')
doc.add_paragraph('[ INSERT FASTAPI SWAGGER DOCS SCREENSHOT HERE ]')

doc.add_heading('M3: CI Pipeline', level=1)
doc.add_paragraph('- Pytest was used to write automated tests for data preprocessing and API endpoints.')
doc.add_paragraph('- A GitHub Actions CI/CD workflow (.github/workflows/ci-cd.yml) was configured to run tests, build the Docker image, and push it to DockerHub automatically.')
doc.add_paragraph('[ INSERT GITHUB ACTIONS SUCCESS SCREENSHOT HERE ]')

doc.add_heading('M4: CD Pipeline & Deployment', level=1)
doc.add_paragraph('- Kubernetes manifests (deployments & services) were created for both the FastAPI backend and Streamlit UI.')
doc.add_paragraph('- A Continuous Deployment job using a Self-Hosted Runner automatically deploys updates to a local Minikube cluster.')
doc.add_paragraph('- A robust post-deployment smoke test script automatically runs via port-forwarding to verify the live API endpoint.')
doc.add_paragraph('[ INSERT KUBERNETES PODS RUNNING SCREENSHOT HERE ]')

doc.add_heading('M5: Monitoring, Logs & Final Submission', level=1)
doc.add_paragraph('- Prometheus FastAPI Instrumentator was integrated to expose an automated /metrics endpoint.')
doc.add_paragraph('- A dedicated Monitoring Dashboard was built directly into Streamlit to visually track Live API Requests, Memory Usage, Average Latency, and API Uptime.')
doc.add_paragraph('- A Performance Tracking benchmark was built into the UI, which pulls real sample images to evaluate live model accuracy and simulate data drift detection.')
doc.add_paragraph('[ INSERT STREAMLIT MONITORING DASHBOARD SCREENSHOT HERE ]')

doc.save('docs/Assignment_Report.docx')
print("Successfully generated docs/Assignment_Report.docx")
