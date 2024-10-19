# Project Structure

project_root/
│
├── client/
│   ├── client.py
│   ├── document_pb2.py
│   └── document_pb2_grpc.py
│
├── server/
│   ├── server.go
│   ├── logger.go
│   └── document/
│       ├── document.pb.go
│       └── document_grpc.pb.go
│
├── docs/
│   ├── PROBLEM.md
│   ├── REPORT.md
│   └── STRUCTURE.md
│
├── document.proto
├── README.md
├── toBuild.sh
└── Makefile

## Explanation of Structure

1. **Client Directory (`client/`)**
   - `client.py`: Contains the main client application logic, including the GUI and gRPC client implementation.
   - `document_pb2.py` and `document_pb2_grpc.py`: Auto-generated Python files from the Protocol Buffer definition.


2. **Server Directory (`server/`)**
   - `server.go`: Contains the main server logic, including the gRPC server implementation and document management.
   - `logger.go`: Implements the logging functionality for document changes.
   - `document/`: Contains the auto-generated Go files from the Protocol Buffer definition.

3. **Documentation Directory (`docs/`)**
   - `PROBLEM.md`: Describes the original problem statement and requirements.
   - `REPORT.md`: Contains the implementation report detailing how requirements were met.
   - `STRUCTURE.md`: This file, explaining the project structure.

4. **Root Directory**
   - `document.proto`: The Protocol Buffer definition file for the gRPC service and message types.
   - `README.md`: Project overview and setup instructions.
   - `toBuild.sh`: Build script to compile and prepare the project for execution.

## Reasoning Behind the Structure

I've organized this project with a few key ideas in mind:

1. I separated the client and server code to keep things clean and easy to work on independently.

2. Since I'm using Python for the client and Go for the server, I put them in separate folders to manage their specific needs better.

3. I kept the `document.proto` file in the root so I can easily update the gRPC service and regenerate code when needed.

4. I created a `toBuild.sh` script in the root to make building and setting up the project simple for anyone who wants to use or work on it.

5. I put all the docs in one place so it's easy to find information about the project.

6. The structure I chose makes it easy to add new parts to the project later without messing things up.

7. By using this structure and a bash script, I made sure the project can be set up and run on different systems that support Python and Go.

