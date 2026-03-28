#!/bin/bash
set -e

# 1. CHECK IF K8S IS ALREADY INSTALLED
if command -v kubeadm &> /dev/null; then
    echo "Kubernetes is already installed. Skipping package installation..."
else
    echo "Installing required packages..."
    sudo apt update
    sudo apt install -y docker.io apt-transport-https ca-certificates curl gpg
    sudo systemctl enable --now docker

    sudo mkdir -p -m 755 /etc/apt/keyrings
    # FIX: Use the specific versioned URL (v1.31) to avoid GPG errors
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.34/deb/Release.key | \
    sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.34/deb/ /' | \
    sudo tee /etc/apt/sources.list.d/kubernetes.list

    sudo apt update
    sudo apt install -y kubelet kubeadm kubectl
    sudo apt-mark hold kubelet kubeadm kubectl 

    # DISABLE SWAP
    sudo swapoff -a
    sudo sed -i '/swap/s/^/#/' /etc/fstab
fi

# 2. CHECK IF CLUSTER IS ALREADY INITIALIZED
if [ -f /etc/kubernetes/admin.conf ]; then
    echo "Kubernetes Master is already initialized. Skipping init..."
else
    echo "Initializing Kubernetes Master..."
    sudo kubeadm init --pod-network-cidr=192.168.0.0/16 > ~/kubeadm-init.log 2>&1
    
    mkdir -p $HOME/.kube
    sudo cp -f /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config

    echo "Installing Networking (Calico)..."
    kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/calico.yaml
fi

# 3. ALWAYS OUTPUT JOIN COMMAND (Safe to run anytime)
sudo kubeadm token create --print-join-command | xargs
