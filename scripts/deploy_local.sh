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

# Wait for rollout
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/mlops-inference
kubectl wait --for=condition=available --timeout=120s deployment/streamlit-ui

# Show Streamlit URL
STREAMLIT_IP=$(minikube ip)
STREAMLIT_PORT=$(kubectl get svc streamlit-service -o go-template='{{(index .spec.ports 0).nodePort}}')
echo "🎉 Streamlit UI is available at http://$STREAMLIT_IP:$STREAMLIT_PORT"

# Run smoke test
SERVICE_IP=$(minikube ip)
SERVICE_PORT=$(kubectl get svc mlops-inference-service -o go-template='{{(index .spec.ports 0).nodePort}}')

echo "Service is up at http://$SERVICE_IP:$SERVICE_PORT"
echo "Running smoke tests..."
python scripts/smoke_test.py "http://$SERVICE_IP:$SERVICE_PORT"
