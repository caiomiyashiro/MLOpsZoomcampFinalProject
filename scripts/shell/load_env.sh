#!/bin/bash

# File: ./scripts/shell/load_env.sh

###########################################################################
# When running docker-compose up in the makefile, check if MLFlow should  #
# use local or remote storage and update the env variable accordingly     #
###########################################################################

# Load environment variables from .env file in the root directory
if [ -f .env ]; then
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip empty lines and comments
        if [[ $line =~ ^[[:space:]]*$ ]] || [[ $line =~ ^[[:space:]]*# ]]; then
            continue
        fi

        # Extract variable name and value
        if [[ $line =~ ^([^=]+)=\"?([^\"]*)\"?$ ]]; then
            var_name="${BASH_REMATCH[1]}"
            var_value="${BASH_REMATCH[2]}"
            export "$var_name=$var_value"
        fi
    done < .env
fi

if [ "$IS_MLFLOW_REMOTE_STORAGE" = "true" ]; then
    echo MLFLOW_ARTIFACT_URL=wasbs://$AZURE_STORAGE_CONTAINER_NAME@$AZURE_STORAGE_ACCOUNT_NAME.blob.core.windows.net
else
    echo MLFLOW_ARTIFACT_URL=./mlflow_data/artifacts
fi
