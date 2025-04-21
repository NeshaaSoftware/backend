#!/bin/bash

# Stop script for Tutor Open edX

echo "Stopping Tutor for Open edX..."

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

# Ask if user wants to stop Open edX containers first
read -p "Do you want to stop the Open edX containers first? (recommended) [Y/n]: " stop_openedx
stop_openedx=${stop_openedx:-Y}

if [[ $stop_openedx =~ ^[Yy]$ ]]; then
    echo "Stopping Open edX containers..."
    docker-compose exec -T tutor tutor local stop || {
        echo "Warning: Could not stop Open edX containers. They may not be running or the Tutor container is not accessible."
    }
fi

# Stop the Tutor container
echo "Stopping Tutor container..."
docker-compose down

# Ask if user wants to remove volumes
read -p "Do you want to remove all Tutor data volumes? This will DELETE ALL DATA! [y/N]: " remove_volumes
remove_volumes=${remove_volumes:-N}

if [[ $remove_volumes =~ ^[Yy]$ ]]; then
    echo "Removing Tutor data volumes..."
    docker volume rm tutor-data
    echo "Tutor data volumes removed."
else
    echo "Tutor data volumes preserved."
fi

echo "Tutor has been stopped."
