# goLLab -  A Collaborative Document Editor

This project is a collaborative document editor with a client-server architecture using gRPC for communication.

## Quick Start

To quickly build and run the project:

1. Make the build script executable:
   ```
   chmod +x toBuild.sh
   ```

2. Run the build script:
   ```
   ./toBuild.sh
   ```

This will create three executables: `run-client`, `run-logger`, and `run-server`.

Run them in the following order:

1. `run-logger`
2. `run-server`
3. `run-client` (you can run multiple instances of this)

## Manual Setup and Running

If you prefer to set up and run the components manually, follow these steps:

### Prerequisites

- Python 3.x
- Go 1.x
- Make

### Setup

1. Prepare the project:
   ```
   make prep
   ```

2. Set up Python environment:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Tidy Go modules:
   ```
   cd server
   go mod tidy
   ```

### Running the Components

1. Start the logger:
   ```
   cd server
   go run logger.go
   ```

2. In a new terminal, start the server:
   ```
   cd server
   go run server.go
   ```

3. In another terminal, run the client:
   ```
   python client/client.py
   ```

## Project Structure

- `client/`: Contains the Python client code
- `server/`: Contains the Go server and logger code
- `document.proto`: Protocol Buffer definition file
- `Makefile`: Contains commands for building and cleaning components of the project
- `toBuild.sh`: Script for building all components
