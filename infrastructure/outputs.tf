output "vm_public_ip_address" {
  value = azurerm_public_ip.vm_public_ip.ip_address
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
}
