# FitOps-AI-App
Architected and deployed a 3-tier FitOps Flask application on AWS EKS using a fully automated DevSecOps pipeline, integrating SAST/DAST scanning workflows to ensure secure and scalable delivery.

# Terraweek_Challenge

<img width="289" height="248" alt="image" src="https://github.com/user-attachments/assets/2ac0d5fc-f220-429b-b8b3-7c08e1811e10" />           <img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/9eec047e-ecac-4c25-ae74-e9a307dd7767" />

1.Infrastructure as Code (IAC) 

Infrastructure as Code is the ability to provision and manage the IT Infrastructure by using the machine readable code instead of going through manual process for provisioning. IAC in DevOps is critical in automating, rapidly deploying of software and its supported infrastructure. IAC is idempotent by nature as it apply same script multiple times and the result will be the same outcomes without creating duplicate resources.



2.What problems does IaC solve compared to manually creating resources in the AWS console or any cloud platform? 

-> It Automates the Infrastructure Setup using scripts and eliminate the lengthy touching and clicking procedure of creating the resources to setup the infrastructure.

-> Ensures consistent environments across development, testing, and production and also reduces the human error which is caused by manual 
configuration and provisioning.


3.How is Terraform different from AWS CloudFormation, Ansible, and Pulumi?

-> Services like AWS CloudFormation are exclusive to specific cloud platforms like AWS. But Terraform is cloud agnostic and supports providers across the cloud platforms like AWS, GCP, Azure, etc. In Terraform, user is responsible of handling of state file (generally stored in S3). While in CloudFormation there is no state file for user to store as it is managed by AWS internally. Terraform uses HCL
(HashiCorp Configuration Language) to provision infrastructure, as for AWS CloudFormation, it uses JSON or YAML Scripts.

-> As for Terraform and Ansible, Terraform provisions the whole infrastructure like Servers, DBs, etc while Ansible is a Configuration
management tool which installs and manages applications, dependencies, etc. Consider like this, Terraform Builds you a House and Ansible 
installs furniture and appliances in your house. Also Terraform communicates eith cloud APIs while Ansible uses SSH to manage Nodes or 
Endpoints.

-> As for Pulumi, infrastructure codes can be written in python, java, go, etc. unlike Terraform which uses HCL only. Terraform is the industry standard for vast ecosystem while Pulumi is preferred by developer-centric teams who wants to use standard programming languages.


4.What does it mean that Terraform is "declarative" and "cloud-agnostic"?

-> Terraform is Declarative implies that terraform make sure the proper action is taken to reach the final desired state. And it is cloud-agnostic means that it can provision resources using one tool and HCL across multiple providers such as AWS, GCP, Azure, Oracle Cloud, etc. 

```
# macOS
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Linux (amd64)
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
sudo apt update && sudo apt install terraform

# Windows
choco install terraform
```



<img width="2400" height="870" alt="image" src="https://github.com/user-attachments/assets/de19163e-c388-4252-bf13-6cea18fbd1f3" />

