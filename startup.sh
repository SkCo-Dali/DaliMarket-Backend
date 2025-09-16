#!/bin/bash
set -e

# Instalar dependencias de SQL Server
export ACCEPT_EULA=Y
apt-get update && apt-get install -y msodbcsql17 unixodbc-dev

pip install -r requirements.txt

# Arrancar la aplicación con uvicorn
python -m uvicorn presentation.main:app --host 0.0.0.0 --port 8000
