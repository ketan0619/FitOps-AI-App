#!/bin/bash
set -e

# 1. CHECK IF ALREADY INSTALLED
if command -v kubeadm &> /dev/null; then
    echo "Kubernetes is already installed on Worker. Skipping package installation..."
else
    echo "Installing required packages on Worker..."
    sudo apt update
    sudo apt install -y docker.io apt-transport-https ca-certificates curl gpg
    sudo systemctl enable --now docker

    # Disable Swap (Mandatory for Kubernetes)
    sudo swapoff -a
    sudo sed -i '/swap/s/^/#/' /etc/fstab

    # Repository setup - FIXED URL to v1.31
    sudo mkdir -p -m 755 /etc/apt/keyrings
    
    # Use the full versioned path to avoid "invalid data" errors
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.34/deb/Release.key | \
    sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.34/deb/ /' | \
    sudo tee /etc/apt/sources.list.d/kubernetes.list

    sudo apt update
    sudo apt install -y kubelet kubeadm kubectl
    sudo apt-mark hold kubelet kubeadm kubectl
fi

# 2. CHECK IF WORKER HAS ALREADY JOINED
if [ -f /etc/kubernetes/kubelet.conf ]; then
    echo "Worker is already part of a cluster. Skipping join prep..."
else
    echo "Worker environment ready. Waiting for join command from workflow..."
fi
