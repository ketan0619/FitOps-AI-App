#!/bin/bash
 # Exit on any error
set -e

echo "Installing required packages..."
sudo apt update
sudo apt install -y docker.io apt-transport-https ca-certificates curl gpg
sudo systemctl enable --now docker

# Create directory for keyrings
sudo mkdir -p -m 755 /etc/apt/keyrings
# Download the new signing key
curl -fsSL https://pkgs.k8s.io | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
# Add the new repository
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update
sudo apt install -y kubelet kubeadm kubectl
# Prevent accidental updates
sudo apt-mark hold kubelet kubeadm kubectl 

# DISABLE SWAP (Required for Kubelet to start)
sudo swapoff -a
sudo sed -i '/swap/s/^/#/' /etc/fstab

# INITIALIZING MASTER
echo "Initializing Kubernetes Master..."
# Capturing full logs to a file for debugging, but keep stdout clean for the join token
sudo kubeadm init --pod-network-cidr=192.168.0.0/16 > ~/kubeadm-init.log 2>&1

# CONFIGURE KUBECONFIG
mkdir -p $HOME/.kube
sudo cp -f /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# INSTALL NETWORKING (Calico)
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/calico.yaml

# OUTPUT JOIN COMMAND
sudo kubeadm token create --print-join-command
