terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "3.108.0"
    }
  }
}

provider "azurerm" {
    subscription_id = var.azure_credentials["subscription_id"]
    client_id       = var.azure_credentials["client_id"]
    client_secret   = var.azure_credentials["client_secret"]
    tenant_id       = var.azure_credentials["tenant_id"]
    features        {}
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "mlopsproject"{ # name of the resource to be referenced in terraform
    name     = var.resource_group_name            # Name of the resource group
    location = var.resource_group_location        # Location of the resource group
}

resource "azurerm_storage_account" "mlopsproject" {
  name                     = "cm37mlopsproject"
  resource_group_name      = azurerm_resource_group.mlopsproject.name
  location                 = azurerm_resource_group.mlopsproject.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  depends_on               = [azurerm_resource_group.mlopsproject]
}

resource "azurerm_storage_container" "vm_storage_container" {
  name                  = "vm-container"
  storage_account_name  = azurerm_storage_account.mlopsproject.name
  container_access_type = "private"
}

resource "azurerm_key_vault" "kv" {
  name                        = "mlopsproject-kv"
  location                    = azurerm_resource_group.mlopsproject.location
  resource_group_name         = azurerm_resource_group.mlopsproject.name
  tenant_id                   = var.azure_credentials["tenant_id"]
  sku_name                    = "standard"
}

resource "azurerm_key_vault_access_policy" "terraform_policy" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = [
    "Get", "List", "Set", "Delete", "Purge"
  ]
}

resource "azurerm_key_vault_secret" "storage_connection_string" {
  name         = "storage-connection-string"
  value        = azurerm_storage_account.mlopsproject.primary_connection_string
  key_vault_id = azurerm_key_vault.kv.id

  depends_on = [azurerm_key_vault_access_policy.terraform_policy]
}

resource "azurerm_user_assigned_identity" "uai" {
  resource_group_name = azurerm_resource_group.mlopsproject.name
  location            = azurerm_resource_group.mlopsproject.location
  name                = "kv-identity"
}

resource "azurerm_key_vault_access_policy" "access_kv_policy" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id    = var.azure_credentials["tenant_id"]
  object_id    = azurerm_user_assigned_identity.uai.principal_id

  secret_permissions = [
    "Get", "List"
  ]
}

resource "azurerm_network_security_group" "net_sec_group" {
  name                = "net-sec-group"
  location            = azurerm_resource_group.mlopsproject.location
  resource_group_name = azurerm_resource_group.mlopsproject.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_public_ip" "vm_public_ip" {
  name                = "vm-public-pip"
  location            = azurerm_resource_group.mlopsproject.location
  resource_group_name = azurerm_resource_group.mlopsproject.name
  allocation_method   = "Dynamic"
}

resource "azurerm_virtual_network" "vn" {
  name                = "vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.mlopsproject.location
  resource_group_name = azurerm_resource_group.mlopsproject.name
}

resource "azurerm_subnet" "subnet_vm" {
  name                 = "subnet-vm"
  resource_group_name  = azurerm_resource_group.mlopsproject.name
  virtual_network_name = azurerm_virtual_network.vn.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_network_interface" "vm_net_interface" {
  name                = "vm-net-interface"
  location            = azurerm_resource_group.mlopsproject.location
  resource_group_name = azurerm_resource_group.mlopsproject.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet_vm.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.vm_public_ip.id
  }
}

# Connect the security group to the network interface
resource "azurerm_network_interface_security_group_association" "ni_sg_ass" {
  network_interface_id      = azurerm_network_interface.vm_net_interface.id
  network_security_group_id = azurerm_network_security_group.net_sec_group.id
}

resource "tls_private_key" "vm_ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

data "cloudinit_config" "config" {
  gzip          = false
  base64_encode = true

  part {
    filename     = "cloud-config.yaml"
    content_type = "text/cloud-config"

    content = file(var.cloud_config_file_path)
  }
}

resource "azurerm_linux_virtual_machine" "vm" {

  name                  = "vm"
  location              = azurerm_resource_group.mlopsproject.location
  resource_group_name   = azurerm_resource_group.mlopsproject.name
  admin_username        = var.vm_login_credentials["username"]
  network_interface_ids = [azurerm_network_interface.vm_net_interface.id]
  size                  = "Standard_B2ms"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.uai.id]
  }

  custom_data = data.cloudinit_config.config.rendered

  admin_ssh_key {
    username   = var.vm_login_credentials["username"]
     public_key = tls_private_key.vm_ssh.public_key_openssh
  }

  os_disk {
    name              = "os-disk"
    caching           = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

}
