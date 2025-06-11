#!/bin/bash
# Этот скрипт останавливает все запущенные контейнеры и запускает проект заново.

echo "Stopping existing containers..."
docker-compose down --remove-orphans

echo "Building and starting new containers..."
docker-compose up --build -d

echo "Project started successfully!"
echo "Checking status of services:"
docker-compose ps 