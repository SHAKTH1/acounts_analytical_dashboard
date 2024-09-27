#!/bin/bash

# Define the remote server and project directory variables
REMOTE_USER="crmadmin"
REMOTE_HOST="139.59.73.56"
REMOTE_DIR="/home/crmadmin/accounts"
LOCAL_PROJECT_DIR="/mnt/d/github/accounts_analytical_dashboard/"

# Sync local files to the remote server (make sure to use a trailing slash for proper file transfer)
echo "Syncing local files to the remote server..."
rsync -avz --exclude 'node_modules' --exclude '__pycache__' "${LOCAL_PROJECT_DIR}/" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"

# SSH into the remote server to build and run the Docker container
echo "Connecting to the remote server to deploy..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
  # Change to the project directory
  cd /home/crmadmin/accounts

  # Check if Dockerfile exists in the directory
  if [ ! -f Dockerfile ]; then
    echo "Dockerfile not found in the project directory. Exiting..."
    exit 1
  fi

  # Stop and remove the specific container if it exists
  if [ "$(docker ps -aq -f name=accounts_dashboard_container)" ]; then
    echo "Stopping and removing existing accounts_dashboard_container..."
    docker stop accounts_dashboard_container
    docker rm accounts_dashboard_container
  fi

  # Remove the Docker image for the project if it exists
  if [ "$(docker images -q accounts_dashboard)" ]; then
    echo "Removing existing Docker image accounts_dashboard..."
    docker rmi accounts_dashboard
  fi

  # Build the Docker image using the Dockerfile in the current directory
  echo "Building Docker image..."
  docker build -t accounts_dashboard .

  # Run the Docker container on port 5051 and map it to internal port 5000
  echo "Running Docker container..."
  docker run -d -p 5051:5000 --name accounts_dashboard_container accounts_dashboard

ENDSSH

echo "Deployment complete. Visit http://posspole.line.pm:5051 to view your dashboard."
