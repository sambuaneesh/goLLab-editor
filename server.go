package main

import (
	"log"
	"net"
	pb "server/document"
	"sync"

	"google.golang.org/grpc"
	"google.golang.org/protobuf/types/known/timestamppb"
)

type server struct {
	pb.UnimplementedDocumentServiceServer
	mu       sync.Mutex
	clients  map[string]pb.DocumentService_CollaborateServer
	document []rune
}

func newServer() *server {
	return &server{
		clients:  make(map[string]pb.DocumentService_CollaborateServer),
		document: []rune{},
	}
}

func (s *server) Collaborate(stream pb.DocumentService_CollaborateServer) error {
	// Receive initial message with client_id
	firstChange, err := stream.Recv()
	if err != nil {
		return err
	}
	clientID := firstChange.ClientId
	log.Printf("Client connected: %s", clientID)

	s.mu.Lock()
	s.clients[clientID] = stream
	s.mu.Unlock()

	// Send full document content to the new client immediately
	s.sendFullContent(clientID)

	defer func() {
		s.mu.Lock()
		delete(s.clients, clientID)
		s.mu.Unlock()
		log.Printf("Client disconnected: %s", clientID)
	}()

	// Listen for changes from the client
	for {
		change, err := stream.Recv()
		if err != nil {
			log.Printf("Error receiving from client %s: %v", clientID, err)
			return err
		}

		if change.Operation == pb.OperationType_REQUEST_CONTENT {
			// Send full document content to the client
			s.sendFullContent(clientID)
		} else {
			// Apply the change to the document
			s.applyChange(change)

			// Log the change
			s.logChange(change)

			// Broadcast the change to other clients
			s.broadcastChange(change, clientID)
		}
	}
}

func (s *server) sendFullContent(clientID string) {
	s.mu.Lock()
	content := string(s.document)
	s.mu.Unlock()

	change := &pb.Change{
		ClientId:       "server",
		Timestamp:      timestamppb.Now(),
		Operation:      pb.OperationType_FULL_CONTENT,
		Position:       0,
		Character:      content,
		CursorPosition: 0,
	}

	if stream, ok := s.clients[clientID]; ok {
		err := stream.Send(change)
		if err != nil {
			log.Printf("Error sending full content to client %s: %v", clientID, err)
		}
	}
}

func (s *server) applyChange(change *pb.Change) {
	s.mu.Lock()
	defer s.mu.Unlock()

	position := int(change.Position)
	if position < 0 {
		position = 0
	}
	if position > len(s.document) {
		position = len(s.document)
	}

	switch change.Operation {
	case pb.OperationType_INSERT:
		s.document = append(s.document[:position], append([]rune(change.Character), s.document[position:]...)...)
	case pb.OperationType_DELETE:
		if position < len(s.document) {
			s.document = append(s.document[:position], s.document[position+1:]...)
		}
	}
}

func (s *server) broadcastChange(change *pb.Change, senderID string) {
	s.mu.Lock()
	defer s.mu.Unlock()

	for clientID, clientStream := range s.clients {
		if clientID != senderID {
			err := clientStream.Send(change)
			if err != nil {
				log.Printf("Error sending to client %s: %v", clientID, err)
			}
		}
	}
}

func (s *server) logChange(change *pb.Change) {
	// For simplicity, log to console. You can write to a file or external logger.
	log.Printf("Change from client %s: %v", change.ClientId, change)
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Failed to listen on port 50051: %v", err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterDocumentServiceServer(grpcServer, newServer())

	log.Println("Server is running on port 50051...")
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Failed to serve gRPC server: %v", err)
	}
}
