#!/bin/bash
set -e

# Always execute from the repository root
cd "$(dirname "$0")/.."

echo "Deploying to local Minikube cluster..."

# Ensure minikube is running
if ! minikube status > /dev/null 2>&1; then
    echo "Starting Minikube..."
    minikube start
fi

# Point docker to minikube's docker daemon
eval $(minikube docker-env)

# Build the image locally inside minikube
echo "Building Docker image..."
docker build -t kumarsankalp/catdog:latest .

# Apply K8s manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/streamlit-deployment.yaml
kubectl apply -f k8s/streamlit-service.yaml

# Force pods to restart to pick up the newly built Docker image
echo "Restarting deployments to pick up new image..."
kubectl rollout restart deployment/mlops-inference
kubectl rollout restart deployment/streamlit-ui

# Wait for rollout
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/mlops-inference
kubectl wait --for=condition=available --timeout=120s deployment/streamlit-ui

# Setup Python Virtual Environment for Smoke Test locally
echo "Setting up virtual environment for smoke tests..."
if [ ! -d "venv_smoke" ]; then
    python3 -m venv venv_smoke
fi
source venv_smoke/bin/activate
pip install -q requests pillow

# Setup Port Forwarding (macOS Minikube IP is often unreachable directly)
echo "Setting up port forwarding..."
# Kill any existing port-forward processes from previous runs
pkill -f "kubectl port-forward svc/mlops-inference-service" || true
pkill -f "kubectl port-forward svc/streamlit-service" || true

kubectl port-forward svc/mlops-inference-service 8000:8000 > /dev/null 2>&1 &
kubectl port-forward svc/streamlit-service 8501:8501 > /dev/null 2>&1 &

# Wait for port-forwards to initialize
sleep 3

echo "🎉 Streamlit UI is available at http://localhost:8501"
echo "API Service is up at http://localhost:8000"

echo "Running smoke tests..."
python scripts/smoke_test.py "http://localhost:8000"

deactivate
