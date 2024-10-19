package main

import (
	"context"
	"log"
	"net"
	pb "server/document"
	"sync"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/timestamppb"
)

type server struct {
	pb.UnimplementedDocumentServiceServer
	mu           sync.Mutex
	clients      map[string]pb.DocumentService_CollaborateServer
	document     []rune
	loggerClient pb.LoggingServiceClient
}

func newServer(loggerAddress string) *server {
	conn, err := grpc.Dial(loggerAddress, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("Failed to connect to logger: %v", err)
	}

	return &server{
		clients:      make(map[string]pb.DocumentService_CollaborateServer),
		document:     []rune{},
		loggerClient: pb.NewLoggingServiceClient(conn),
	}
}

func (s *server) Collaborate(stream pb.DocumentService_CollaborateServer) error {
	var clientID string
	defer func() {
		if clientID != "" {
			s.mu.Lock()
			delete(s.clients, clientID)
			s.mu.Unlock()
			log.Printf("Client disconnected: %s", clientID)
		}
	}()

	for {
		change, err := stream.Recv()
		if err != nil {
			if status.Code(err) == codes.Canceled {
				return nil
			}
			return err
		}

		if clientID == "" {
			clientID = change.ClientId
			s.mu.Lock()
			s.clients[clientID] = stream
			s.mu.Unlock()
			log.Printf("Client connected: %s", clientID)
			s.sendFullContent(clientID)
		}

		if change.Operation == pb.OperationType_REQUEST_CONTENT {
			s.sendFullContent(clientID)
		} else {
			s.applyChange(change)
			s.logChange(change) // Log the change only once
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

	// Removed the duplicate log call here
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
	_, err := s.loggerClient.LogChange(context.Background(), change)
	if err != nil {
		log.Printf("Error logging change: %v", err)
	}
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Failed to listen on port 50051: %v", err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterDocumentServiceServer(grpcServer, newServer("localhost:50052"))

	log.Println("Server is running on port 50051...")
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Failed to serve gRPC server: %v", err)
	}
}
