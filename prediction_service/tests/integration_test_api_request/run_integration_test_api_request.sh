#!/bin/bash

# Set the path to your docker-compose.yml file
DOCKER_COMPOSE_FILE="../../../docker-compose.yml"

# Services to start
SERVICES_TO_START="db mlflow prediction_service"

# Function to check if the service is ready
# if running locally, PREDICTION_SERVICE_URL is not set...
check_service() {
    curl -s -o /dev/null -w "%{http_code}" ${PREDICTION_SERVICE_URL}/healthcheck
}

# Start docker-compose in detached mode
docker-compose --verbose -f "$DOCKER_COMPOSE_FILE" up -d --build $SERVICES_TO_START
echo "Docker-compose services started"

echo "Waiting for services to be ready..."

# Wait for the service to be ready
while true; do
    status_code=$(check_service)
    if [ "$status_code" -eq 200 ]; then
        echo "Service is ready!"
        break
    fi
    echo "Service not ready yet. Waiting..."
    sleep 5
done

# Run the Python script
echo "Running Python script..."
python_output=$(python3 integration_test_api_request.py)
exit_code=$?

# Check the exit code of the Python script
if [ $exit_code -eq 0 ]; then
    echo "Test passed: Assert 200 successful"
    docker-compose down
    exit 0
else
    echo "Test failed: Python script exited with non-zero status"
    echo "Python script output:"
    echo "$python_output"
    docker-compose down
    exit 1
fi
