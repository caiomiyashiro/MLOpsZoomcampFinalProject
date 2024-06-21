variable "subscription_id" {
  description = "The Subscription ID for the Azure account"
  type        = string
}

variable "client_id" {
  description = "The Client ID for the Azure Service Principal"
  type        = string
  sensitive   = true
}

variable "client_secret" {
  description = "The Client Secret for the Azure Service Principal"
  type        = string
  sensitive   = true
}

variable "tenant_id" {
  description = "The Tenant ID for the Azure Service Principal"
  type        = string
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

variable "postgres_login_credentials" {
    description = "The login credentials for the PostgreSQL database"
    type        = map
    sensitive   = true
}
