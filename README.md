# Objective

This repository contains the final project for the [MLOpsZoomcamp course](https://github.com/DataTalksClub/mlops-zoomcamp).

The goal of the project is to apply what has been learned during the MLOps Zoomcamp. This project has as background a machine learning model to predict the quality of wines based on a selection of available attributes. However, the main goal was to build the plataform that support the development and operacionalization of such model:

1. **Cloud elements**: VMs, Databases, Blob Storages, etc. Automatization (Architecture as Code) with Terraform
2. **Experiment Tracking**: Tracking of model performance and hiperparameter tunning
3. **Workflow Orchestration**: Automatization of data processing and training procedures
4. **Model Deployment**: Common architectures for deployment models as batch, online or streaming
5. **Model Monitoring**: Tracking of machine learning specific metrics, such as model performance and data drift
6. **Software Engineering Best Practices**:
    * Unit Tests
    * Integration Tests
    * Linter and code formatters
    * Makefile
    * Pre-commit Hooks
    * CI/CD pipelines

# Introduction

In this project I focused in exposing an online API that receives requests with the model's input data and output the wine quality prediction. Again, the goal is not to focus on the ML Model quality, but on the architecture around supporting it.

In order to support this API and the overall DevOps cycle the following architecture was developed:

![Alt text](images/mlops_proj_diagram.png)

1 - Folder `infrastructure` contains the files needed to create the **Azure** infrastructure, including:
    - Virtual Machine (VM)
    - Virtual Networks
    - Azure Storage Containers (Similar to AWS S3)
    - Azure Key Vault

2 - The VM is created and then automatically initialized with the script `infrastructure/cloud-config.yaml` that installs all the required packages to build and run a docker-container containing all the services needed for this project:

- **Prediction service** (folder `prediction_service`): API to receive requests and return the predictions. The model will load the registered model from MLFlow and use it to make new predictions. In the first times that the service is run, there won't be a model trained and registered yet in MLFlow, so I added a `prediction_service/sample_model.pkl` that will be loaded temporarily while there are no models in the MLFlow registry.

- **Prometheus** (folder `prometheus`): Scrape metrics about the system's condition and model metrics

- **Grafana** (folder `grafana`): Collect metrics from Prometheus and display dashboards and alerts

- **MLFlow** (folder `mlflow`): Track and version model training

- **PostgreSQL** (no folder, downloaded directly from docker): Store metrics from MLFlow

## Data and Model Summary

The data that it was used for this project was the Wine Quality dataset by UCI [Link](https://archive.ics.uci.edu/dataset/186/wine+quality). It relates to red and white vinho verde wine samples, from the north of Portugal and the goal is to model wine quality based on physicochemical tests. An initial data analysis can be found at `./data_analysis.ipynb`, with variables and variables types and distributions.

# Setup Instructions

## Requisites

* Docker >= 20.0.0
* Linux or Mac (or Windows SWL) for execution of .sh scripts
* Python >= 3.9
* Git

## Infrastructure - Terraform

1 - Setup a free account in [Azure](https://azure.microsoft.com/ja-jp/free/) and get the free credits (Sorry, the page is in Japanese but you can use a translator)

2 - In order to be able to create Azure Resources via Terraform, you need to manually create an application that contains the necessary permissions. In case you don't know, follow the steps in this video, https://youtu.be/wB52Rd5N9IQ?si=TviEVsM8N9uUsh29&t=754 (the specific timestamp is already selected). Add the variables `subscription_id`, `client_id`, `client_secret`, `tenant_id` to the `infrastructure/terraform.tfvars` as shown in `infrastructure/terraform.tfvars.sample`.

3 - Proceed with the infrastructure creation with `make setup-infra` commands from the **project root folder**.

The above command will:
- Create the infra represented by diagram showed above.
- Execute the command `scripts/shell/update_env.sh` that will create the `.env` file based on `.env.sample` file but with the newly created `AZURE_STORAGE_CONNECTION_STRING` and `REMOTE_URL` environment variables.
    - If you can't to execute the `.sh` script, please get the connection string variable from the newly created Storage Account  (check [here](https://youtu.be/x2A0i8OMheA?si=mgYngRX5qAXh_kFI&t=74) for a tutorial), replace it in the `.env.sample` file and rename it to `.env`. Also, replace the <VARNAME__REMOTE__VARNAME> variables with the VM's public IP address and port. They will be used by the docker-compose services.

4 - When you're done testing the services, you can delete all cloud resources with `make destroy-infra`

------------------------------------------------------------------------------------------------
**Observation**: In case you want to SSH the VM from your local computer, execute the following steps **from the same terminal you used to execute the terraform scripts**:
    * `terraform output -raw private_key_pem > <local_folder>` - This will export the private key needed to access the VM into your local folder
    * `ssh -i ~/.ssh/id_rsa.pem azureuser@$(terraform output -raw vm_public_ip_address)`. If it doesn't work, confirm if the VM's public IP in Azure Portal is correct with what terraform outputs with `terraform output -raw vm_public_ip_address`. In case it's not, replace the command by the correct IP.

--------------------------------

## Local scripts to interact with services

For the sake of testing the project, there are 3 scripts that simulates scripts running outside from the VM, that would be executed by the ML Engineer or Data Scientist, **after the VM docker-compose setup is completed**. I also recommend creating a virtual environment using the `./requirements.txt` file.

- Folder `scripts`: Contains the scripts used to train and register the models using MLFlow and to simulate real-time data being sent to the service. You can execute them by typing `python script_file_name.py`, without any parameters.
    - `**Please wait between 5-10 minutes to run the scripts after the remote vm is created as it takes time to install and configure all the services.**`
    - Running `modelling_scripts/training.py` will train the data on a Regression Tree, test 50 models and track their performance and hiperparameters into MLFlow. You'll be able to check MLFlow UI by the URL indicated in the `MLFLOW_<LOCAL_REMOTE>_TRACKING_URL` variable in `.env` file.
    - The script `modelling_scripts/register_model.py` will then automatically select the best model among those and register it into MLFlow registry.
    - The script `modelling_scripts/real_data_simulator.py` simulates data being sent to the prediction_service in an unregular interval, in order to see the metrics arriving and being displayed in Grafana.

## Accessing services front-end

Depending on whether you're running the services in the remote VM or locally (check [local-docker-compose-services](#local-docker-compose-services)), the endpoints's host will be the local address or the VM's public IP address. In case the addresses `127.0.0.1` don't work when typing in the browser, try changing them to `locahost` instead.

Initially, the following endpoints will be available when the services are up:

| Service    | Local                   | Remote                           | Other
|------------|-------------------------|----------------------------------|------------|
| Prediction Service | http://127.0.0.1:9696   | http://\<VM-public-ip\>:9696     |                        |
| Prometheus | http://127.0.0.1:9090   | http://\<VM-public-ip\>:9090     |                        |
| Adminer    | http://127.0.0.1:8080   | http://\<VM-public-ip\>:8080     |                        |
| MLFlow     | http://127.0.0.1:5001   | http://\<VM-public-ip\>:5001     |                        |
| Grafana    | http://127.0.0.1:3000   | http://\<VM-public-ip\>:3000     | user: admin pass:admin |

## Local docker-compose services

You can also run all the services locally and use the `local scripts` to interact with them.

**Before you run it locally**, you should pay attention to:

* If you don't have the file `.env`, copy the `.env.sample` and rename it to `.env`, as the services will depend on those variables to run. Besides **change the variable IS_MLFLOW_REMOTE_STORAGE and IS_SERVICE_REMOTE to false**, so the service and MLFLow knows that it should process the data locally and store it in a temporary folder inside the container.

* Change the `DATA_TIMEZONE` variable in the `.env` file to your timezone, as leaving it to *JAPAN* might lead to your data not being show in Grafana in your timezone.

Finally, run `make docker-up` **from the project root folder** to build and run the services and execute any of the local scripts.

# Best practices

1. Unit tests were developed for the prediction service and are available at `prediction_service/tests/`.
2. Integration test was developed to test the overall request and API response and is available also at `prediction_service/tests/`.
3. Linter and black code-formatter are set as pre-commit hooks. Pre-commit hooks configuration is available at `.pre-commit-config.yaml`.
4. Makefile is provided to setup and delete infra and to setup and delete docker-compose services
5. Pre-commit hooks are available and configured at `.pre-commit-config.yaml`.
6. Only CI pipeline is developed at `.github/ci-main.yml` that is triggered when there's a pull request into the main branch. CD pipeline will be developed in future iterations.

# Things to improve

* Centralize password, keys, and secrets management to Azure Vault. For now, only github actions for CI pipeline is importing the secrets from key vault but I'd like to make it a standard for the services as well that, for now, rely on the `.env` variable.
* For now, there's no CD pipeline, so I'd like to integrate it when I have more time.
* I'm centralizing all services into one VM with docker-compose. I'd like to use separate docker containers in Azure with ACR (Azure Container Registry) and ACS (Azure Container Services) to have a better management of resources and cost saving.
* Unit tests covered only a part the `prediction_service` code. I'd like to improve them and make them better quality.
* There's some duplicated code regarding `utils` functions. I'd like to make that a package for easier maintanance.

# Self Evaluation (for reference)

* Problem description
    - 0 points: The problem is not described
    - 1 point: The problem is described but shortly or not clearly
    - **2 points: The problem is well described and it's clear what the problem the project solves**
* Cloud
    - 0 points: Cloud is not used, things run only locally
    - 2 points: The project is developed on the cloud OR uses localstack (or similar tool) OR the project is deployed to Kubernetes or similar container management platforms
    - **4 points: The project is developed on the cloud and IaC tools are used for provisioning the infrastructure**
* Experiment tracking and model registry
    - 0 points: No experiment tracking or model registry
    - 2 points: Experiments are tracked or models are registered in the registry
    - **4 points: Both experiment tracking and model registry are used**
* Workflow orchestration
    - **0 points: No workflow orchestration** - Dataset is directly applied to model.
    - 2 points: Basic workflow orchestration
    - 4 points: Fully deployed workflow
* Model deployment
    - 0 points: Model is not deployed
    - 2 points: Model is deployed but only locally
    - **4 points: The model deployment code is containerized and could be deployed to cloud or special tools for model deployment are used**
* Model monitoring
    - 0 points: No model monitoring
    - 2 points: Basic model monitoring that calculates and reports metrics
    - **4 points: Comprehensive model monitoring that sends alerts or runs a conditional workflow (e.g. retraining, generating debugging dashboard, switching to a different model) if the defined metrics threshold is violated**
* Reproducibility
    - 0 points: No instructions on how to run the code at all, the data is missing
    - 2 points: Some instructions are there, but they are not complete OR instructions are clear and complete, the code works, but the data is missing
    - **4 points: Instructions are clear, it's easy to run the code, and it works. The versions for all the dependencies are specified.**
* Best practices
     - **There are unit tests (1 point)**
     - **There is an integration test (1 point)**
     - **Linter and/or code formatter are used (1 point)**
     - **There's a Makefile (1 point)**
     - **There are pre-commit hooks (1 point)**
     - There's a CI/CD pipeline (2 points) - Only CI
