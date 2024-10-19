import grpc
import threading
import tkinter as tk
from google.protobuf.timestamp_pb2 import Timestamp
import time

import document_pb2 as pb
import document_pb2_grpc as pb_grpc

class CollaborativeEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Collaborative Editor")

        self.text = tk.Text(self.root, wrap='word')
        self.text.pack(expand=1, fill='both')

        self.text.bind('<KeyPress>', self.on_key_press)
        self.text.bind('<KeyRelease>', self.on_key_release)
        self.text.bind('<<Modified>>', self.on_modified)

        self.client_id = str(int(time.time() * 1000))
        self.cursor_position = 0

        self.lock = threading.Lock()  # Move this line up
        self.changes = []
        self.pending_changes = []  # To store changes while disconnected

        # gRPC setup
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = pb_grpc.DocumentServiceStub(self.channel)
        self.change_stream = None
        self.connected = False

        self.connection_event = threading.Event()
        self.initial_content_received = threading.Event()

        self.document_content = ""  # Store the current document content

        self.text.config(state='disabled')  # Initially disable the text widget

        self.connect_to_server()  # Connect to server in the constructor

        # Start a thread to receive changes from the server
        self.receive_thread = threading.Thread(target=self.receive_changes)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # Send initial message with client_id
        initial_change = pb.Change(
            client_id=self.client_id,
            timestamp=Timestamp(seconds=int(time.time()))
        )
        self.changes.append(initial_change)

    def connect_to_server(self):
        while True:
            try:
                self.change_stream = self.stub.Collaborate(self.change_generator())
                self.connected = True
                print("Connected to server successfully")
                self.text.config(state='normal')
                self.request_initial_content()
                self.connection_event.set()  # Signal that the connection is established
                return  # Exit the method if connection is successful
            except grpc.RpcError as e:
                print(f"Failed to connect to server: {e}")
                self.connected = False
                self.text.config(state='disabled')
                time.sleep(5)  # Wait for 5 seconds before retrying

    def request_initial_content(self):
        initial_request = pb.Change(
            client_id=self.client_id,
            timestamp=Timestamp(seconds=int(time.time())),
            operation=pb.OperationType.REQUEST_CONTENT,
            position=0,
            character="",
            cursor_position=0
        )
        self.send_change(initial_request)

    def send_pending_changes(self):
        with self.lock:
            self.changes.extend(self.pending_changes)
            self.pending_changes.clear()

    def change_generator(self):
        while True:
            if self.changes:
                with self.lock:
                    change = self.changes.pop(0)
                yield change
            else:
                time.sleep(0.01)

    def on_key_press(self, event):
        if event.keysym == 'BackSpace':
            position = self.get_cursor_index()
            if position > 0:
                change = pb.Change(
                    client_id=self.client_id,
                    timestamp=Timestamp(seconds=int(time.time())),
                    operation=pb.OperationType.DELETE,
                    position=position - 1,
                    character='',
                    cursor_position=position - 1
                )
                self.send_change(change)
        elif len(event.char) == 1:
            position = self.get_cursor_index()
            change = pb.Change(
                client_id=self.client_id,
                timestamp=Timestamp(seconds=int(time.time())),
                operation=pb.OperationType.INSERT,
                position=position,
                character=event.char,
                cursor_position=position + 1
            )
            self.send_change(change)

    def send_change(self, change):
        if self.connected:
            with self.lock:
                self.changes.append(change)
        else:
            self.pending_changes.append(change)

    def on_key_release(self, event):
        pass

    def on_modified(self, event):
        # Reset the modified flag
        self.text.edit_modified(0)

    def get_cursor_index(self):
        try:
            position = self.text.index(tk.INSERT)
            line, column = map(int, position.split('.'))
            return sum(len(self.text.get(f"{i}.0", f"{i}.end")) for i in range(1, line)) + column
        except Exception as e:
            print(f"Error in get_cursor_index: {e}")
            return 0

    def receive_changes(self):
        self.connection_event.wait()  # Wait for the connection to be established
        while True:
            try:
                for change in self.change_stream:
                    if change.operation == pb.OperationType.FULL_CONTENT:
                        self.root.after(0, self.update_full_content, change.character)
                    elif change.client_id != self.client_id:
                        self.root.after(0, self.apply_change, change)
            except grpc.RpcError as e:
                print(f"RPC error: {e}")
                self.connected = False
                self.text.config(state='disabled')
                self.connection_event.clear()
                self.connect_to_server()  # Try to reconnect
                self.connection_event.wait()  # Wait for the reconnection

    def update_full_content(self, content):
        self.text.config(state='normal')
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', content)
        self.text.config(state='normal')
        self.document_content = content
        self.initial_content_received.set()  # Signal that initial content has been received

    def apply_change(self, change):
        self.text.config(state='normal')
        position = self.index_to_position(change.position)
        if change.operation == pb.OperationType.INSERT:
            self.text.insert(position, change.character)
            self.document_content = (
                self.document_content[:change.position] +
                change.character +
                self.document_content[change.position:]
            )
        elif change.operation == pb.OperationType.DELETE:
            end_position = self.text.index(f"{position}+1c")
            self.text.delete(position, end_position)
            self.document_content = (
                self.document_content[:change.position] +
                self.document_content[change.position + 1:]
            )
        self.text.config(state='normal')

    def index_to_position(self, index):
        # Convert index to Tkinter position (line.column)
        return f"1.0 + {index} chars"

    def start(self):
        self.root.mainloop()

if __name__ == '__main__':
    editor = CollaborativeEditor()
    editor.start()
