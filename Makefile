.PHONY: setup up d b ps node

setup-infra:
	cd infrastructure && \
	terraform init && \
	terraform plan -out main.tfout && \
	terraform apply main.tfout && \
	cd ..
destroy-infra:
	cd infrastructure && \
	terraform destroy -auto-approve && \
	cd ..
docker-up:
	docker-compose up --build
docker-down:
	docker-compose down
