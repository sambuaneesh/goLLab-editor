# Implementation Report

## Implementation Details and Functionality

### Shared Document and Client Interface (Objective 1)

Our system implements a shared document accessible through a graphical user interface:

- **Client Interface**: Implemented in `client/client.py` using Python's Tkinter library.
  - Provides a text editor widget for document modification.
  - Displays real-time updates from other clients.
  - Shows connection status and cursor position in the status bar.

This meets the requirement of a shared document with a suitable interface for modification.

### Text Operations (Objective 2)

The system supports adding, editing, and deleting text:

- **Insertion**: Implemented in the `on_key_press` method of `CollaborativeEditor` class.
- **Deletion**: Handled in the same `on_key_press` method for backspace key.
- **Editing**: Combination of insertion and deletion operations.

Changes are immediately sent to the server via gRPC calls, meeting the requirement of real-time editing.

### Real-time View of Changes (Objective 2)

Clients can view changes made by other clients in real-time:

- The `receive_changes` method in `client/client.py` continuously listens for changes from the server.
- The `apply_change` method updates the local document content and UI when changes are received.

This fulfills the requirement of viewing changes made by other clients in real-time.

### Logging Changes (Objective 3)

All changes are logged to a separate logging program:

- The server (`server/server.go`) implements a `logChange` method that sends changes to the logger via gRPC.
- The logger (`server/logger.go`) receives these changes and writes them to a log file.

This meets the requirement of logging all changes using gRPC.

### Server Forwarding Changes (Objective 4)

The server forwards changes to all clients using bidirectional gRPC streams:

- The `Collaborate` method in `server/server.go` maintains a stream for each connected client.
- The `broadcastChange` method sends changes to all connected clients except the sender.

This fulfills the requirement of using bidirectional asynchronous gRPC calls for change propagation.

### Error Handling (Objective 5)

The system implements robust error handling:

- In `client/client.py`, the `receive_changes` method includes reconnection logic in case of gRPC failures.
- The `handle_disconnection` method updates the UI and disables editing when disconnected.
- The server gracefully handles client disconnections in the `Collaborate` method.

This meets the requirement of handling gRPC failures and displaying appropriate error messages.

### Consistency (Objective 6)

Consistency is maintained through the server's implementation:

- The `applyChange` method in `server/server.go` uses a mutex to ensure that changes are applied sequentially.
- This approach ensures consistency except in cases where multiple users modify the same location simultaneously, as specified in the requirements.

### Multiple Clients Support (Objective 7)

The system fully supports multiple clients:

- The server maintains a map of connected clients in the `clients` field of the `server` struct.
- Each client is assigned a unique ID upon connection.
- Changes are broadcast to all connected clients in the `broadcastChange` method.

## Implementation Logic

1. **Client-Server Communication**: We use gRPC for efficient, bidirectional streaming between clients and the server. This allows for real-time updates and low-latency communication.

2. **Change Representation**: Changes are represented as `Change` objects (defined in `document.proto`) containing the client ID, timestamp, operation type, position, and character.

3. **Concurrency Handling**: We use Go's concurrency primitives (goroutines and channels) in the server to handle multiple clients efficiently. The `processChanges` method runs in a separate goroutine, processing changes from a buffered channel.

4. **UI Updates**: We use Tkinter's `after` method to apply changes from other clients in the main UI thread, ensuring thread-safe updates.

5. **Reconnection Logic**: The client implements a reconnection mechanism that attempts to re-establish the connection if it's lost, providing a seamless experience for users.

