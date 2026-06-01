#!/usr/bin/env bash

set -euo pipefail

# Inputs with default fallbacks matching your architecture config
CLUSTER_NAME=${1:-"bankapp-eks"}
REGION=${2:-"eu-north-1"}

log() {
    echo -e "\033[1;34m[BOOTSTRAP]\033[0m $1"
}

log "Validating that required CLI dependencies exist locally..."
for cmd in aws kubectl helm terraform nslookup; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: Required binary dependency '$cmd' is not found in PATH." >&2
        exit 1
    fi
done


log "Syncing local environment context configuration for EKS..."
aws eks update-kubeconfig --region "${REGION}" --name "${CLUSTER_NAME}"


log "Installing Experimental Gateway API CRDs..."
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.1.0/experimental-install.yaml


log "Waiting for ArgoCD Server deployment to stabilize..."
kubectl wait --namespace argocd \
  --for=condition=available deployment/argocd-server \
  --timeout=300s

log "Extracting initial Administrative Credentials..."
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 --decode)


mkdir -p .secret_backup
echo "URL: Managed via App Gateway / Port-Forward" > .secret_backup/argocd-creds.txt
echo "Username: admin" >> .secret_backup/argocd-creds.txt
echo "Password: ${ARGOCD_PASSWORD}" >> .secret_backup/argocd-creds.txt
chmod 600 .secret_backup/argocd-creds.txt
log "Credentials successfully written to local file: .secret_backup/argocd-creds.txt"


log "Deploying Application-of-Applications Root Manifest..."
kubectl apply -f manifests/argocd/root-app.yml


log "Waiting for Envoy Gateway controller to spin up the AWS LoadBalancer..."
log "Note: This can take 1-3 minutes as AWS allocates the physical Network Load Balancer (NLB)."

while true; do
    LB_DNS=$(kubectl get gateway fitops-gateway -n fitops -o jsonpath='{.status.addresses[0].value}' 2>/dev/null || echo "")
    if [ -n "$LB_DNS" ]; then
        log "Found AWS LoadBalancer DNS Endpoint: $LB_DNS"
        break
    fi
    echo "Waiting for LoadBalancer address mapping to appear..."
    sleep 15
done

log "Resolving Public IP for LoadBalancer via nslookup..."
PUBLIC_IP=$(nslookup "$LB_DNS" | awk '/^Address: / { print $2; exit }')

if [ -z "$PUBLIC_IP" ] && command -v dig &> /dev/null; then
    PUBLIC_IP=$(dig +short "$LB_DNS" | tail -n1)
fi

if [ -z "$PUBLIC_IP" ]; then
    echo "CRITICAL: Unable to resolve public IP address for infrastructure. Manual intervention required." >&2
    exit 1
fi

log "Successfully resolved Public IP: $PUBLIC_IP"

log "Generating final gateway.yml configuration file from template pattern..."
sed "s/__PUBLIC_IP__/${PUBLIC_IP}/g" k8s/platform/gateway.template.yml > k8s/platform/gateway.yml

log "Gateway configuration successfully updated automated for ${PUBLIC_IP}.nip.io"
log "Automation Bootstrap Sequence Complete! Monitor synchronization progress via your ArgoCD dashboard."
