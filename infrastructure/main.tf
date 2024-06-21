terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "3.108.0"
    }
  }
}

provider "azurerm" {
    subscription_id = var.subscription_id
    client_id       = var.client_id
    client_secret   = var.client_secret
    tenant_id       = var.tenant_id
    features        {}
}

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

  security_rule {
    name                       = "PostgreSQL"
    priority                   = 1002
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5432"
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

    content = file("/Users/caiomiyashiro/repo/Personal/MLOpsZoomcampFinalProject/infrastructure/cloud-config.yaml")
  }
}

resource "azurerm_linux_virtual_machine" "vm" {
  name                  = "vm"
  location              = azurerm_resource_group.mlopsproject.location
  resource_group_name   = azurerm_resource_group.mlopsproject.name
  admin_username        = var.vm_login_credentials["username"]
  network_interface_ids = [azurerm_network_interface.vm_net_interface.id]
  size                  = "Standard_B2ms"

  custom_data = data.cloudinit_config.config.rendered

  admin_ssh_key {
    username   = var.vm_login_credentials["username"]
    #public_key = file("~/.ssh/id_rsa.pub")
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

resource "azurerm_postgresql_server" "postgres_server" {
  name                = "cm37-postgresql-server"
  location            = azurerm_resource_group.mlopsproject.location
  resource_group_name = azurerm_resource_group.mlopsproject.name
  public_network_access_enabled = true

  # zone                = "1"  # Primary server zone

  administrator_login           = var.postgres_login_credentials["username"]
  administrator_login_password  = var.postgres_login_credentials["password"]

  sku_name                      = "B_Gen5_1"
  version                       = "11"
  storage_mb                    = 32768
  backup_retention_days         = 7
  geo_redundant_backup_enabled  = false

  # Disable SSL enforcement
  ssl_enforcement_enabled       = false
  ssl_minimal_tls_version_enforced = "TLSEnforcementDisabled"
}

resource "azurerm_postgresql_firewall_rule" "postgres_fwr_allow_vm_ip" {
  name                = "allow-vm-ip"
  resource_group_name = azurerm_resource_group.mlopsproject.name
  server_name         = azurerm_postgresql_server.postgres_server.name
  start_ip_address    = azurerm_public_ip.vm_public_ip.ip_address
  end_ip_address      = azurerm_public_ip.vm_public_ip.ip_address
}


resource "azurerm_postgresql_database" "mlflow" {
  name      = "mlflow"
  resource_group_name = azurerm_resource_group.mlopsproject.name
  server_name = azurerm_postgresql_server.postgres_server.name
  collation = "en_US.utf8"
  charset   = "utf8"
}
