package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"
	pb "server/document"

	"google.golang.org/grpc"
)

type LoggerServer struct {
	pb.UnimplementedLoggingServiceServer
	logFile *os.File
}

func NewLoggerServer(logFilePath string) *LoggerServer {
	file, err := os.OpenFile(logFilePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Failed to open log file: %v", err)
	}

	return &LoggerServer{
		logFile: file,
	}
}

func (s *LoggerServer) LogChange(ctx context.Context, change *pb.Change) (*pb.LogResponse, error) {
	logEntry := fmt.Sprintf("Client: %s, Operation: %s, Position: %d, Character: %s, Cursor: %d, Timestamp: %s\n",
		change.ClientId,
		change.Operation,
		change.Position,
		change.Character,
		change.CursorPosition,
		change.Timestamp.AsTime().String())

	_, err := s.logFile.WriteString(logEntry)
	if err != nil {
		log.Printf("Error writing to log file: %v", err)
		return &pb.LogResponse{Success: false}, err
	}

	return &pb.LogResponse{Success: true}, nil
}

func main() {
	lis, err := net.Listen("tcp", ":50052")
	if err != nil {
		log.Fatalf("Failed to listen on port 50052: %v", err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterLoggingServiceServer(grpcServer, NewLoggerServer("document_changes.log"))

	log.Println("Logger is running on port 50052...")
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Failed to serve gRPC server: %v", err)
	}
}
