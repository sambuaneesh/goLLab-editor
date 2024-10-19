
py:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. document.proto

go:
	protoc --go_out=. --go-grpc_out=. document.proto
