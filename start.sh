#!/bin/bash
# Start all services with docker-compose

if [ ! -f .env ]; then
    echo "Creating .env file"
    touch .env
fi

docker-compose up -d

echo "Services started. Access URLs:"