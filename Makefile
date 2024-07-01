.PHONY: setup up d b ps node

setup-infra:
	cd infrastructure && \
	terraform init && \
	terraform plan -out main.tfout && \
	terraform apply main.tfout && \
	chmod +x ../scripts/shell/update_env.sh && \
	../scripts/shell/update_env.sh && \
	cd ..
destroy-infra:
	cd infrastructure && \
	terraform destroy -auto-approve && \
	cd ..
docker-up:
	docker-compose up -d --build
docker-down:
	docker-compose down
