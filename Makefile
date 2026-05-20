.PHONY: all init plan apply bootstrap deploy update-kubeconfig clean destroy

# Configuration variables
CLUSTER_NAME ?= bankapp-eks
REGION       ?= eu-north-1
ENV          ?= dev

all: bootstrap

init:
	@echo "==> Initializing Terraform Infrastructure..."
	cd terraform && terraform init

plan: init
	@echo "==> Planning Infrastructure Changes..."
	cd terraform && terraform plan -out=tfplan

apply:
	@echo "==> Deploying Infrastructure Components..."
	cd terraform && terraform apply -auto-approve

update-kubeconfig:
	@echo "==> Updating Kubeconfig context for cluster: $(CLUSTER_NAME)..."
	aws eks update-kubeconfig --region $(REGION) --name $(CLUSTER_NAME)

bootstrap: apply update-kubeconfig
	@echo "==> Executing Bootstrap Phase & Component Sync..."
	@bash scripts/bootstrap.sh $(CLUSTER_NAME) $(REGION)

clean:
	@echo "==> Cleaning local ephemeral build caches..."
	rm -f terraform/tfplan
	rm -rf terraform/.terraform/providers

destroy:
	@echo "==> CRITICAL: Destroying environment resources..."
	cd terraform && terraform destroy -auto-approve
