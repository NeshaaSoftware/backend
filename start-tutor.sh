#!/bin/bash

# Start-up script for Tutor Open edX

echo "Starting Tutor for Open edX..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Build and start the container
echo "Building and starting Tutor container..."
docker-compose up -d

# Check if the container started successfully
if [ $? -eq 0 ]; then
    echo "Tutor container started successfully!"
    echo ""
    echo "To access the Tutor shell, run:"
    echo "docker-compose exec tutor bash"
    echo ""
    echo "Once inside the container, you can start Open edX with:"
    echo "tutor local quickstart"
    echo ""
    echo "After Open edX is running, you can access:"
    echo "- LMS (Learning Management System): http://localhost"
    echo "- Studio (Course Management): http://studio.localhost"
else
    echo "Error: Failed to start Tutor container."
    exit 1
fi
