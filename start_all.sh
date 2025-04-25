#!/bin/bash

echo "Starting Development ERP..."
docker-compose -f "$(dirname "$0")/development-erp/docker-compose.yml" up --build -d
echo "Waiting for 20 seconds until move to the next docker..."
sleep 20

echo "Starting Development Web App..."
docker-compose -f "$(dirname "$0")/development-web-app/docker-compose.yml" up --build -d

# No need now for the demo because:
# A. The database already contains the ML model and SKU metrics data for the demo user
# B. Includes heavy libraries, which makes the compose process too long
#echo "Starting Development ML..."
#docker-compose -f "$(dirname "$0")/development-ml/docker-compose.yml" up --build -d
#echo "Waiting for 20 seconds until move to the next docker"
#sleep 20

echo "All components started successfully!"
read -p "Press any key to exit..."
