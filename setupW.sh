#!/bin/bash
set -e

echo "Installing required packages on Worker..."
sudo apt update
sudo apt install -y docker.io apt-transport-https ca-certificates curl gpg
sudo systemctl enable --now docker

# Disable Swap (Mandatory for Kubernetes)
sudo swapoff -a
sudo sed -i '/swap/s/^/#/' /etc/fstab

# Repository setup
sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

echo "Worker environment ready. Waiting for join command from workflow..."
