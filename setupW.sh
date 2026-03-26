#!/bin/bash
echo "Installing required packages..."
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable docker
sudo apt install -y apt-transport-https curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
sudo apt install -y kubelet kubeadm kubectl
sudo kubeadm init
sudo ${{ steps.master_init.outputs.stdout }}
