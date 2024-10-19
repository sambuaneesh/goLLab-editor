# Real-time Document - gRPC Implementation

## Introduction

This project implements a real-time collaborative document system using gRPC. The system allows multiple clients to open, edit, and sync changes to a shared document in real-time. Changes made by one client are propagated to other clients through a gRPC server, ensuring that all instances of the document remain synchronized.

### Objectives:

- The document is shared among multiple clients and can be modified through a suitable interface (e.g., terminal, web browser).
- Clients can:
  - Add, edit, and delete text.
  - View changes made by other clients in real-time.
- All changes made by clients are logged to a separate logging program (e.g., text file) using gRPC.
- The server forwards changes made by one client to all other clients using bidirectional asynchronous gRPC calls.

### Error Handling:

- If a gRPC call fails, the client should attempt to reload the document or display an appropriate error message.
- Consistency must be maintained, except when multiple collaborators attempt to modify the same location in the file simultaneously.

## Components

1. **Clients**:

   - Multiple clients acting as interfaces for users to modify the document.

2. **Server**:

   - Syncs the text between all clients.
   - Forwards changes to a logging program using gRPC.

3. **Logging Program**:

   - Logs the stream of changes from the server to maintain a history of document modifications.

4. **Database (Optional)**:
   - Stores the changes to the document, allowing it to be reopened later.

## Implementation Steps

1. **Client sends changes to the server**:

   - The client sends document changes to the server, which forwards them to other clients.

2. **Single-client initial setup**:

   - Implement a system with one client, one server, and one logging program. The server sends the changes to the logging program.

3. **Multiple clients synchronization**:
   - Extend the implementation to support multiple clients. Each client sends and receives updates to/from the server.

### gRPC Methods:

1. **SendChanges (Client → Server)**:
   - Clients send their document changes to the server.
2. **SyncChanges (Server → Clients)**:
   - The server forwards changes made by one client to all other clients.
3. **LogChanges (Server → Logger)**:
   - The server sends all changes to a logging program.

### Error Handling:

- Handle gRPC failures with appropriate error messages or by attempting to reload the document.

## Submission Requirements

### Protobuf Files:

- Define the gRPC services and messages using Protobuf.

### Build Script:

- Include a bash script (`toBuild.sh`) to build the project.

### README:

- Document the implementation details and any quirks in the system.

### Report:

- Explain the implementation in detail.
- Demonstrate that all required functionalities have been implemented.

## Notes:

- You can mix and match front-end and back-end languages based on your convenience.
- Python or JavaScript may be simpler for implementing this problem.

---
