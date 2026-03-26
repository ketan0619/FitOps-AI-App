#!/bin/bash
echo "Installing required packages..."
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable docker
sudo apt install -y apt-transport-https curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
sudo apt install -y kubelet kubeadm kubectl
sudo kubeadm init --pod-network-cidr=192.168.0.0/16 > /dev/null 2>&1
sudo kubeadm token create --print-join-command
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
