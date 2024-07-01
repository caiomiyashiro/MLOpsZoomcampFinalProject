#!/bin/bash

###########################################################################
# After terraform infra is created, get azure connection string from      #
# terraform output and update the .env file with the connection string.   #
###########################################################################

# Flag to determine if we should update the .env file
update_env=true

# Check if AZURE_STORAGE_CONNECTION_STRING environment variable exists
if [ -n "$AZURE_STORAGE_CONNECTION_STRING" ]; then
    echo "AZURE_STORAGE_CONNECTION_STRING environment variable exists. Skipping .env file update."
    update_env=false
fi

if $update_env; then
    # Get the connection string from Terraform output
    connection_string=$(terraform output -raw storage_account_connection_string)

    # Check if the connection string is empty
    if [ -z "$connection_string" ]; then
        echo "Error: Failed to retrieve the connection string from Terraform output."
        # Don't exit, just set the flag to false
        update_env=false
    fi

    if $update_env; then
        # Create a new .env file from .env.sample
        cp ../.env.sample ../.env

        # Escape special characters in the connection string
        escaped_connection_string=$(printf '%s\n' "$connection_string" | sed 's/[\/&]/\\&/g')

        # Use Perl to replace the line
        perl -i -pe 's/^#AZURE_STORAGE_CONNECTION_STRING=.*$/AZURE_STORAGE_CONNECTION_STRING="'"$escaped_connection_string"'"/' ../.env

        # Check if the replacement was successful
        if grep -q "AZURE_STORAGE_CONNECTION_STRING=\"$connection_string\"" ../.env; then
            echo "Connection string has been successfully updated in ../.env file."
        else
            echo "Failed to update the connection string in ../.env file."
            echo "Raw connection string:"
            echo "$connection_string"
            echo "End of connection string"
        fi
    fi
else
    echo "No changes made to .env file."
fi
