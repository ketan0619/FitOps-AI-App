#!/bin/bash

# --- HELPER FUNCTIONS ---
# This fixes the "log: command not found" error
log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] \033[1;32mINFO:\033[0m $*"
}

# --- INFRASTRUCTURE BOOTSTRAP ---
log "creating the remote backend"
make backends

log "Creating the EKS Cluster"
make init
make migrate
make apply

CLUSTER_NAME=${1:-"fitops-eks"}
REGION=${2:-"eu-north-1"}

log "Syncing local environment context configuration for EKS..."
aws eks update-kubeconfig --region "${REGION}" --name "${CLUSTER_NAME}"

log "Installing Experimental Gateway API CRDs..."
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.1.0/experimental-install.yaml

log "Waiting for ArgoCD Server deployment to stabilize..."
kubectl wait --namespace argocd \
  --for=condition=available deployment/argocd-server \
  --timeout=120s

log "Deploying Application-of-Applications Root Manifest..."
kubectl apply -f manifests/argocd/root-app.yml

log "Waiting for AWS LoadBalancer to spin up..."
log "Note: This can take 1-3 minutes as AWS allocates the physical Network Load Balancer (NLB)."

TIMEOUT_SECONDS=300
SLEEP_INTERVAL=15
ELAPSED_TIME=0

while true; do
    # Updated to target the correct Service instead of a Gateway object
    LB_DNS=$(kubectl get svc fitops-service -n fitops -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
    
    # Success condition: DNS endpoint is found
    if [ -n "$LB_DNS" ]; then
        log "Found AWS LoadBalancer DNS Endpoint: $LB_DNS"
        break
    fi
    
    # Failure condition: Timeout reached
    if [ "$ELAPSED_TIME" -ge "$TIMEOUT_SECONDS" ]; then
        echo "CRITICAL: Timed out waiting for AWS LoadBalancer DNS after ${TIMEOUT_SECONDS} seconds." >&2
        exit 1
    fi
    
    echo "Waiting for LoadBalancer address mapping to appear... (${ELAPSED_TIME}/${TIMEOUT_SECONDS}s elapsed)"
    sleep "$SLEEP_INTERVAL"
    ELAPSED_TIME=$((ELAPSED_TIME + SLEEP_INTERVAL))
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
sed "s/__PUBLIC_IP__/${PUBLIC_IP}/g" manifests/platform/gateway.template.yml > manifests/platform/gateway.yml

log "Extracting initial ArgoCD Administrative Credentials..."
ARGOCD_URL=$(kubectl get svc argocd-server -n argocd -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "ClusterIP/Internal")
echo "ARGOCD_USER=admin"
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 --decode)
echo "ARGOCD_PASSWORD: $ARGOCD_PASSWORD"

log "Getting the Grafana URL"
# Adjusted to standard prometheus-grafana naming schema to fix the NotFound error
kubectl get svc prometheus-grafana -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "ClusterIP/Internal"

log "Getting the Grafana Credentials"
echo "Grafana_User: admin"
Grafana_Password=$(kubectl get secret prometheus-grafana -n monitoring -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d; echo)
echo "Grafana_Password: $Grafana_Password"

log "Gateway configuration successfully updated automated for ${PUBLIC_IP}.nip.io"
log "Automation Bootstrap Sequence Complete! Monitor synchronization progress via your ArgoCD dashboard."

