#!/bin/bash
set -e

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

# Wait for rollout
echo "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/mlops-inference

# Run smoke test
SERVICE_IP=$(minikube ip)
SERVICE_PORT=$(kubectl get svc mlops-inference-service -o go-template='{{(index .spec.ports 0).nodePort}}')

echo "Service is up at http://$SERVICE_IP:$SERVICE_PORT"
echo "Running smoke tests..."
python smoke_test.py "http://$SERVICE_IP:$SERVICE_PORT"
