#!/bin/bash
set -e

# Instalar dependencias de SQL Server
apt-get update
apt-get install -y msodbcsql17 unixodbc-dev

# Arrancar la aplicación con uvicorn
python -m uvicorn presentation.main:app --host 0.0.0.0 --port 8000
