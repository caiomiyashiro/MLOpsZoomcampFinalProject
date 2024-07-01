variable "azure_credentials" {
    description = "The Azure credentials. Made of subscription_id, client_id, client_secret, and tenant_id."
    type        = map
    sensitive   = true
}

variable "resource_group_name" {
    description = "The name of the resource group"
    type        = string
    default = "app-grp-test"
}

variable "resource_group_location" {
    description = "The location of the resource group"
    type        = string
    default = "Japan East"
}

variable "vm_login_credentials" {
    description = "The login credentials for the VM"
    type        = map
    sensitive   = true
}

variable "cloud_config_file_path" {
  description = "The path to the cloud-config.yaml file"
  type        = string

  default     = "cloud-config.yaml"
}

variable "key-vault-secrets" {
  type = map(string)
  default = {
    "MLFLOW-EXPERIMENT-NAME" = "wine_quality_hyperparameter_optimization"
    "MLFLOW-TRACKING-URL" = "http://127.0.0.1:5001"
    "MLFLOW-TRACKING-URL-DOCKER" = "http://mlflow:5001"
    "MLFLOW-MODEL-REGISTRY-NAME" = "wine_quality"

    "POSTGRES-USER" = "example"
    "POSTGRES-PASSWORD" = "example" # pragma: allowlist secret
    "POSTGRES-DB" = "postgres"
    "POSTGRES-HOST" = "127.0.0.1"
    "POSTGRES-HOST-DOCKER" = "db"
    "POSTGRES-TABLE" = "wine_quality"

    "PREDICTION-SERVICE-URL" = "http://127.0.0.1:9696"
    "PREDICTION-SERVICE-URL-DOCKER" = "http://prediction_service:9696"

    "DATA-TIMEZONE" = "Japan"
  }
}
