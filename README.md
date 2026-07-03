<h1 align="center">FitOps-AI-App</h1>

<p align="center">
  Architected and deployed a 3-tier FitOps AI application on AWS EKS using a fully automated GitOps pipeline with integrated DevSecOps workflows. Provisioned the entire infrastructure using Terraform and configured comprehensive observability. Utilized ArgoCD to maintain GitHub as the Single Source of Truth (SSoT).
</p>


<div align="center">

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-000000?logo=flask)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql)](https://www.mysql.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-000000?logo=ollama)](https://ollama.com/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-844FBA?logo=terraform)](https://www.terraform.io/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?logo=githubactions)](https://github.com/features/actions)
[![Docker](https://img.shields.io/badge/Docker-Containers-2496ED?logo=docker)](https://www.docker.com/)
[![Amazon EKS](https://img.shields.io/badge/Amazon%20EKS-1.35-FF9900?logo=amazoneks)](https://aws.amazon.com/eks/)
[![Helm](https://img.shields.io/badge/Helm-3.19-0F1689?logo=helm)](https://helm.sh/)
[![ArgoCD](https://img.shields.io/badge/ArgoCD-GitOps-EF7B4D?logo=argo)](https://argo-cd.readthedocs.io/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestration-326CE5?logo=kubernetes)](https://kubernetes.io/)
[![AWS](https://img.shields.io/badge/AWS-Cloud-232F3E?logo=amazonaws)](https://aws.amazon.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?logo=grafana)](https://grafana.com/)
[![Trivy](https://img.shields.io/badge/Trivy-Security%20Scan-1904DA?logo=aquasecurity)](https://trivy.dev/)

</div>

---

## Application Features

- **🧠 Dynamic BMI Calculation** - Computes precise Body Mass Index utilizing age, height, weight, and gender metrics.
- **📋 Tailored Fitness & Nutrition** - Generates custom workout regimes and premium, A-grade dietary plans mapped to specific BMI results.
- **📊 Analytics & Exportable Reports** - Features interactive height-to-weight ratio charts and instant PDF downloads for fitness profiles.
- **🤖 Local AI Fitness Assistant** - Integrates an intelligent, privacy-focused Ollama chatbot acting as a 24/7 personal trainer.
- **🎨 Glassmorphism Gym Dashboard** - Boasts a visually striking UI crafted specifically for fitness enthusiasts.

## Architecture Features

- **Infrastructure** - Terraform Provisions whole Infra (EKS, ArgoCD, VPC) and statefile saved in remote backends(S3+DynamoDB).
- **EKS Cluster** - K8s v1.35 and Instances(t3.medium) all in different AZs.
- **Autoscaling** - Configured HPA which will scales upto 4 pods, 2 replicas and Rolling Updates.
- **App-of-Apps Setup** - Deploy and Manage the child apps by executing a single Root Application Configuration File. No need to execute all the manifests, just one single root-app.yml
- **Automation** - Automation Scripts like Makefile and Bootstrap.sh will automate the deployment of the App along with whole Infrastructure.
- **GitOps with ArgoCD** - Auto Sync and Self-Heal.

---

## Architecture Diagram

<img width="1408" height="768" alt="FitOps-Workflow" src="https://github.com/user-attachments/assets/4c026815-d769-4936-9fcb-151fc958ede0" />



<h3 align="left">⚙️ Tech Stack & DevOps Toolchain</h3>

| Tool | Purpose |
|------|---------|
| **Terraform(IaC)** | Infrastructure Provisioning |
| **Github Actions** | Continuous Integration |
| **DockerHub** | Image Registry |
| **ArgoCD** | CD Job/GitOps |
| **Cert-Manager** | TLS |
| **Gateway API CRDs+ Envoy Gateway** | Ingress |
| **Ollama Hosted on EKS** | AI Chatbot |
| **Kube-Prometheus-Stack** | Monitoring and Visualizing on Grafana Dashboards |
| **EBS CSI** | Storage/Persistant Volume |
| **MySQL** | Relational Database |
