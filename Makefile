
prep: py go

py:
	python -m grpc_tools.protoc -I. --python_out=./client --grpc_python_out=./client document.proto

go:
	protoc --go_out=./server --go-grpc_out=./server document.proto

clean:
	rm -rf dist/ build/ client.spec client/document_pb2.py client/document_pb2_grpc.py server/document/ \
	run-logger run-server run-client document_changes.log
