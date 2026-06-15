.PHONY: all init plan apply bootstrap deploy update-kubeconfig clean destroy

# Configuration variables
CLUSTER_NAME ?= fitops-eks
REGION       ?= eu-north-1
ENV          ?= prod

all: bootstrap

backends:
	@echo "==> Initializing and Provisioning Remote Backend..."
	cd terraform/remote-backends && terraform init && terraform apply -auto-approve

init:
	@echo "==> Initializing Terraform Infrastructure..."
	cd terraform && terraform init

migrate:
	@echo "==> Migrating local state file to S3 remote backend..."
	cd terraform && terraform init -input=false -force-copy

plan: init
	@echo "==> Planning Infrastructure Changes..."
	cd terraform && terraform plan -out=tfplan

apply:
	@echo "==> Deploying Infrastructure Components..."
	cd terraform && terraform apply -auto-approve

update-kubeconfig:
	@echo "==> Updating Kubeconfig context for cluster: $(CLUSTER_NAME)..."
	aws eks update-kubeconfig --region $(REGION) --name $(CLUSTER_NAME)

bootstrap:
	@echo "==> Executing Bootstrap Phase & Component Sync..."
	@bash scripts/bootstrap.sh $(CLUSTER_NAME) $(REGION)

clean:
	@echo "==> Cleaning local ephemeral build caches..."
	rm -f terraform/tfplan
	rm -rf terraform/.terraform/providers

destroy:
	@echo "==> CRITICAL: Destroying environment resources..."
	cd terraform && terraform destroy -auto-approve

destroy-backends:
	@echo "==> CRITICAL: Destroying the Remote Backends..."
	cd terraform/remote-backends && terraform destroy -auto-approve

monitoring: credentials-info
	@echo "==> Starting Grafana local proxy on http://localhost:3000..."
	@echo "==> Keep this terminal open to maintain connection. Press Ctrl+C to stop."
	kubectl port-forward -n monitoring deployment/kube-prometheus-stack-grafana 3000:3000

# Grafana Port Forwarding for local access
dashboard-app:
	@echo "==> Starting Banking Application proxy on http://localhost:8080..."
	kubectl port-forward -n fitops deployment/fitops 8080:8080

# Internal helper to pull and format monitoring credentials
credentials-info:
	@echo "==> Fetching Grafana Administrative Credentials..."
	@GRAFANA_PWD=$$(kubectl get secret kube-prometheus-stack-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode); \
	mkdir -p .secret_backup; \
	echo "URL: http://localhost:3000" > .secret_backup/grafana-creds.txt; \
	echo "Username: admin" >> .secret_backup/grafana-creds.txt; \
	echo "Password: $$GRAFANA_PWD" >> .secret_backup/grafana-creds.txt; \
	echo "----------------------------------------------------"; \
	echo " Grafana URL      : http://localhost:3000"; \
	echo " Admin Username   : admin"; \
	echo " Admin Password   : $$GRAFANA_PWD"; \
	echo "----------------------------------------------------"; \
	echo "Credentials written to: .secret_backup/grafana-creds.txt"
