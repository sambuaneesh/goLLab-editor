import grpc
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from google.protobuf.timestamp_pb2 import Timestamp
import time

import document_pb2 as pb
import document_pb2_grpc as pb_grpc


class CollaborativeEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤝 gOLLAB Editor")
        self.root.geometry("800x600")
        
        # Configure styles
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')  # You can choose other themes like 'alt', 'default', 'classic'
        self.configure_styles()

        # Set up the main frame
        self.main_frame = ttk.Frame(self.root, padding="5 5 5 5")
        self.main_frame.pack(expand=True, fill='both')

        # Setup Menu
        self.create_menu()

        # Setup Toolbar
        # self.create_toolbar()

        # Setup Text Area with Scrollbar
        self.text = ScrolledText(self.main_frame, wrap='word', font=("Helvetica", 12))
        self.text.pack(expand=True, fill='both', padx=5, pady=5)

        # Bind events
        self.text.bind('<KeyPress>', self.on_key_press)
        self.text.bind('<KeyRelease>', self.on_key_release)
        self.text.bind('<<Modified>>', self.on_modified)
        self.text.bind('<Motion>', self.update_cursor_position)
        self.text.bind('<Button-1>', self.update_cursor_position)

        # Status Bar
        self.status_bar = ttk.Label(self.root, text="Not Connected", anchor='w')
        self.status_bar.pack(side='bottom', fill='x')

        # Client and cursor info
        self.client_id = str(int(time.time() * 1000))
        self.cursor_position = 0

        # Threading and synchronization
        self.lock = threading.Lock()
        self.changes = []
        self.pending_changes = []

        # gRPC setup
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = pb_grpc.DocumentServiceStub(self.channel)
        self.change_stream = None
        self.connected = False

        self.connection_event = threading.Event()
        self.initial_content_received = threading.Event()

        self.document_content = ""

        # Initialize UI state
        self.text.config(state='disabled')

        # Connect to server
        self.connect_to_server()

        # Start thread to receive changes
        self.receive_thread = threading.Thread(target=self.receive_changes, daemon=True)
        self.receive_thread.start()

        # Send initial change with client_id
        initial_change = pb.Change(
            client_id=self.client_id,
            timestamp=Timestamp(seconds=int(time.time()))
        )
        self.changes.append(initial_change)

    def configure_styles(self):
        # Configure fonts and colors
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', foreground='#333333')
        self.style.configure('TButton', padding=5)
        self.style.configure('Status.TLabel', background='#f0f0f0', foreground='#555555', relief='sunken')

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    # def create_toolbar(self):
    #     toolbar = ttk.Frame(self.main_frame, relief='raised', padding="2 2 2 2")
    #     toolbar.pack(side='top', fill='x')

    #     bold_btn = ttk.Button(toolbar, text="Bold", command=self.make_bold)
    #     bold_btn.pack(side='left', padx=2)

    #     italic_btn = ttk.Button(toolbar, text="Italic", command=self.make_italic)
    #     italic_btn.pack(side='left', padx=2)

    #     underline_btn = ttk.Button(toolbar, text="Underline", command=self.make_underline)
    #     underline_btn.pack(side='left', padx=2)

    def make_bold(self):
        # Placeholder for Bold functionality
        # Implement text styling as needed
        messagebox.showinfo("Bold", "Bold functionality not implemented yet.")

    def make_italic(self):
        # Placeholder for Italic functionality
        messagebox.showinfo("Italic", "Italic functionality not implemented yet.")

    def make_underline(self):
        # Placeholder for Underline functionality
        messagebox.showinfo("Underline", "Underline functionality not implemented yet.")

    def show_about(self):
        messagebox.showinfo("About", "gOLLAB Editor\nVersion 1.0\nPowered by gRPC, golang, and py-tkinter.")

    def connect_to_server(self):
        while True:
            try:
                self.change_stream = self.stub.Collaborate(self.change_generator())
                self.connected = True
                self.update_status("Connected to server")
                self.text.config(state='normal')
                self.request_initial_content()
                self.connection_event.set()
                return
            except grpc.RpcError as e:
                self.update_status(f"Failed to connect to server: {e}")
                self.connected = False
                self.text.config(state='disabled')
                time.sleep(5)

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
        elif len(event.char) == 1 and event.char.isprintable():
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
        self.update_cursor_position()

    def on_modified(self, event):
        self.text.edit_modified(False)  # Reset the modified flag

    def get_cursor_index(self):
        try:
            position = self.text.index(tk.INSERT)
            line, column = map(int, position.split('.'))
            return sum(len(self.text.get(f"{i}.0", f"{i}.end")) for i in range(1, line)) + column
        except Exception as e:
            print(f"Error in get_cursor_index: {e}")
            return 0

    def receive_changes(self):
        self.connection_event.wait()  # Wait until connected
        while True:
            try:
                for change in self.change_stream:
                    if change.operation == pb.OperationType.FULL_CONTENT:
                        self.root.after(0, self.update_full_content, change.character)
                    elif change.client_id != self.client_id:
                        self.root.after(0, self.apply_change, change)
            except grpc.RpcError as e:
                self.update_status(f"RPC error: {e}")
                self.connected = False
                self.text.config(state='disabled')
                self.connection_event.clear()
                self.connect_to_server()
                self.connection_event.wait()

    def update_full_content(self, content):
        self.text.config(state='normal')
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', content)
        self.document_content = content
        self.initial_content_received.set()

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
            end_position = f"{position}+1c"
            self.text.delete(position, end_position)
            self.document_content = (
                self.document_content[:change.position] +
                self.document_content[change.position + 1:]
            )
        self.text.config(state='normal')

    def index_to_position(self, index):
        return f"1.0 + {index} chars"

    def update_status(self, message):
        self.status_bar.config(text=message)

    def update_cursor_position(self, event=None):
        try:
            position = self.text.index(tk.INSERT)
            line, column = position.split('.')
            self.status_bar.config(text=f"Connected | Cursor Position: Line {line}, Column {column}")
        except Exception as e:
            self.status_bar.config(text=f"Error: {e}")

    def start(self):
        self.root.mainloop()


if __name__ == '__main__':
    editor = CollaborativeEditor()
    editor.start()
