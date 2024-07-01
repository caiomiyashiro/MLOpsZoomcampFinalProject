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
