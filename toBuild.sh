#!/bin/bash

# make sure to clean up before building
make clean

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

make prep

# Build Python client
pyinstaller --onefile --windowed --add-data "client/document_pb2.py:." --add-data "client/document_pb2_grpc.py:." client/client.py
mv dist/client run-client

# Clean up Python build artifacts
rm -rf dist/ build/ client.spec venv/

# Build Go server components
cd server
go mod tidy
go build -o ../run-logger logger.go
go build -o ../run-server server.go 

echo "Build complete. Executables: run-client, run-logger, run-server"
