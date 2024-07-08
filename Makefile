.PHONY: setup up d b ps node setup-infra destroy-infra docker-up docker-down

# Load environment variables
define load_env
$(eval ENV_VARS := $(shell bash ./scripts/shell/load_env.sh))
$(foreach var,$(ENV_VARS),$(eval $(var)))
endef

setup-infra:
	cd infrastructure && \
	terraform init && \
	terraform plan -out main.tfout && \
	terraform apply main.tfout && \
	chmod +x ../scripts/shell/update_env.sh && \
	terraform refresh && \
	terraform output -json | ../scripts/shell/update_env.sh && \
	cd ..

destroy-infra:
	cd infrastructure && \
	terraform destroy -auto-approve && \
	cd ..

docker-up:
	chmod +x ./scripts/shell/load_env.sh
	$(call load_env)
	MLFLOW_ARTIFACT_URL="$(MLFLOW_ARTIFACT_URL)" docker compose up -d --build

docker-down:
	docker compose down
