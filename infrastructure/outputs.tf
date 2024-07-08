output "vm_public_ip_address" {
  value = azurerm_public_ip.vm_public_ip.ip_address
  depends_on  = [azurerm_public_ip.vm_public_ip]
}

output "storage_account_connection_string" {
  value = azurerm_storage_account.mlopsproject.primary_connection_string
  sensitive = true
}

output "private_key_pem" {
  value = tls_private_key.vm_ssh.private_key_pem
  sensitive = true
}

output "public_key_openssh" {
  value = tls_private_key.vm_ssh.public_key_openssh
  sensitive = true
}

output "storage_account_name" {
  value = azurerm_storage_account.mlopsproject.name
}

output "storage_container_name" {
  value = azurerm_storage_container.vm_storage_container.name
}
