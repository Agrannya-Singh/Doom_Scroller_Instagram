#!/bin/bash

# Exit on error
set -e

# Wait for the database to be ready (if using a database)
# Example: 
# while ! nc -z $DB_HOST $DB_PORT; do
#   echo "Waiting for PostgreSQL..."
#   sleep 1
# done

echo "Running database migrations (if any)"
# Example: python manage.py migrate

echo "Starting application..."
if [[ "$DEBUG" == "true" ]]; then
    echo "Running in development mode"
    python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
else
    echo "Running in production mode"
    python -m uvicorn main:app --host 0.0.0.0 --port 8080
fi
