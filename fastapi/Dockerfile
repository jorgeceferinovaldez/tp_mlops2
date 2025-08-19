FROM python:3.8-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl

# Copy requirements first for better caching
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt

# Copy proto files first to generate gRPC code
COPY proto ./proto/

# Generate gRPC Python files
RUN python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/star_classification.proto

# Copy the rest of the application
COPY . .

# Expose ports for FastAPI and gRPC
EXPOSE 8800 50051
