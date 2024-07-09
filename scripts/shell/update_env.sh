#!/bin/bash

###########################################################################
# After terraform infra is created, get azure connection string from      #
# terraform output and update the .env file with the connection string.   #
###########################################################################

# Get the storage account data from Terraform output
connection_string=$(terraform output -raw storage_account_connection_string)
storage_account_name=$(terraform output -raw storage_account_name)
storage_container_name=$(terraform output -raw storage_container_name)
vm_public_ip_address=$(terraform output -raw vm_public_ip_address)

# Check if any of the variables are empty
if [ -z "$connection_string" ] || [ -z "$storage_account_name" ] || [ -z "$storage_container_name" ]; then
    echo "Error: Failed to retrieve one or more required values from Terraform output."

    # Provide more detailed error messages
    [ -z "$connection_string" ] && echo "- Connection string is empty"
    [ -z "$storage_account_name" ] && echo "- Storage account name is empty"
    [ -z "$storage_container_name" ] && echo "- Storage container name is empty"
    [ -z "$vm_public_ip_address" ] && echo "- VM public address is empty"

    exit 1
fi

# Create a new .env file from .env.sample
cp ../.env.sample ../.env

# Use Perl to update the lines in the .env file
perl -i -pe 's/^#AZURE_STORAGE_CONNECTION_STRING=.*$/AZURE_STORAGE_CONNECTION_STRING="'"$(printf '%s\n' "$connection_string" | sed 's/[\/&]/\\&/g')"'"/' ../.env
perl -i -pe 's/^#?AZURE_STORAGE_ACCOUNT_NAME=.*$/AZURE_STORAGE_ACCOUNT_NAME="'"$(printf '%s\n' "$storage_account_name" | sed 's/[\/&]/\\&/g')"'"/' ../.env
perl -i -pe 's/^#?AZURE_STORAGE_CONTAINER_NAME=.*$/AZURE_STORAGE_CONTAINER_NAME="'"$(printf '%s\n' "$storage_container_name" | sed 's/[\/&]/\\&/g')"'"/' ../.env
perl -i -pe 's/^#?MLFLOW_REMOTE_TRACKING_URL=.*$/MLFLOW_REMOTE_TRACKING_URL="http:\/\/'"$(printf '%s\n' "$vm_public_ip_address" | sed 's/[\/&]/\\&/g')"':5001"/' ../.env
perl -i -pe 's/^#?PREDICTION_SERVICE_REMOTE_URL=.*$/PREDICTION_SERVICE_REMOTE_URL="http:\/\/'"$(printf '%s\n' "$vm_public_ip_address" | sed 's/[\/&]/\\&/g')"':9696"/' ../.env


# Function to check if a variable is set correctly in the .env file
check_variable() {
    local var_name=$1
    local var_value=$2
    if grep -q "${var_name}=\"${var_value}\"" ../.env; then
        echo "${var_name} has been successfully updated in ../.env file."
    else
        echo "Failed to update ${var_name} in ../.env file."
        echo "Raw ${var_name}:"
        echo "${var_value}"
        echo "End of ${var_name}"
        return 1
    fi
}

# Check all variables
failed=0
check_variable "AZURE_STORAGE_CONNECTION_STRING" "$connection_string" || failed=1
check_variable "AZURE_STORAGE_ACCOUNT_NAME" "$storage_account_name" || failed=1
check_variable "AZURE_STORAGE_CONTAINER_NAME" "$storage_container_name" || failed=1
check_variable "MLFLOW_REMOTE_TRACKING_URL" "http://$vm_public_ip_address:5001" || failed=1
check_variable "PREDICTION_SERVICE_REMOTE_URL" "http://$vm_public_ip_address:9696" || failed=1

# Final status
if [ $failed -eq 0 ]; then
    echo "All variables have been successfully updated in ../.env file."
else
    echo "------------------------------------------------------------------------------------------"
    echo "Failed to update one or more variables in ../.env file."
    echo "docker-compose up --build will not work correctly. Please update the variables manually."
    echo "------------------------------------------------------------------------------------------"
    exit 1
fi
