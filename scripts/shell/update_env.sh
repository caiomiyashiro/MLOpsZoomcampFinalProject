#!/bin/bash

###########################################################################
# After terraform infra is created, get azure connection string from      #
# terraform output and update the .env file with the connection string.   #
###########################################################################

# Get the connection string from Terraform output
connection_string=$(terraform output -raw storage_account_connection_string)

# Check if the connection string is empty
if [ -z "$connection_string" ]; then
    echo "Error: Failed to retrieve the connection string from Terraform output."
    exit 1
fi

# Create a new .env file from .env.sample
cp ../.env.sample ../.env

# Use Perl to replace the line
perl -i -pe 's/^#AZURE_STORAGE_CONNECTION_STRING=.*$/AZURE_STORAGE_CONNECTION_STRING="'"$(printf '%s\n' "$connection_string" | sed 's/[\/&]/\\&/g')"'"/' ../.env

# Check if the replacement was successful
if grep -q "AZURE_STORAGE_CONNECTION_STRING=\"$connection_string\"" ../.env; then
    echo "Connection string has been successfully updated in ../.env file."
else
    echo "Failed to update the connection string in ../.env file."
    echo "Raw connection string:"
    echo "$connection_string"
    echo "End of connection string"
fi
