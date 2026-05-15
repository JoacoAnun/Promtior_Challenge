#!/bin/bash
set -e

echo "Creating virtual environment..."
uv venv .venv

echo "Installing dependencies..."
uv pip install -r requirements.txt --python .venv/bin/python

echo "Installing dbt packages..."
source .venv/bin/activate
cd electric_vehicles && dbt deps && cd ..
deactivate

echo "Starting Docker services..."
docker compose up -d

echo "Done. Services running:"
echo "  Airflow:  http://localhost:8080"
echo "  Superset: http://localhost:8088"
echo ""
echo "Airflow credentials:"
docker compose logs airflow 2>&1 | grep "Password for user" || echo "  (still starting, run: docker compose logs airflow | grep 'Password for user')"
