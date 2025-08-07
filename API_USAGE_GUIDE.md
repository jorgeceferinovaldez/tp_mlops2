# Star Classification Multi-Protocol API Usage Guide

This guide explains how to use the enhanced Star Classification API that now supports multiple communication protocols: REST, GraphQL, gRPC, and Kafka Streaming.

## Overview

The Star Classification API has been enhanced to provide the same machine learning inference functionality through four different protocols:

1. **REST API**: Traditional HTTP-based API (existing functionality)
2. **GraphQL API**: Flexible query language for APIs
3. **gRPC Service**: High-performance RPC framework with Protocol Buffers
4. **Kafka Streaming**: Real-time streaming predictions via Apache Kafka

## Service Endpoints

| Service | Endpoint/Port | Description |
|---------|---------------|-------------|
| REST API | `http://localhost:8800/predict/` | Traditional HTTP POST endpoint |
| GraphQL | `http://localhost:8800/graphql` | GraphQL queries and mutations |
| gRPC | `localhost:50051` | gRPC service with Protocol Buffers |
| Kafka Streaming | Topics: `star_features_input`, `star_predictions_output` | Real-time streaming |

## Starting the Services

### Full Stack (All Services)
```bash
docker compose --profile all up -d
```

### Individual Service Profiles
```bash
# MLflow and API only
docker compose --profile mlflow up -d

# With Kafka streaming support
docker compose --profile streaming up -d

# Airflow data pipeline
docker compose --profile airflow up -d
```

## Usage Examples

### 1. REST API (HTTP)

**Traditional POST request:**
```bash
curl -X POST "http://localhost:8800/predict/" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "obj_ID": 1237663784734294016.0,
      "alpha": 135.689,
      "delta": 32.494,
      "u": 23.87882,
      "g": 22.27530,
      "r": 20.39398,
      "i": 19.16763,
      "z": 18.79371,
      "run_ID": 3606,
      "cam_col": 4,
      "field_ID": 587,
      "spec_obj_ID": 6.543777825301504e17,
      "redshift": 0.644,
      "plate": 5812,
      "MJD": 56354,
      "fiber_ID": 171
    }
  }'
```

**Python example:**
```python
import requests

data = {
    "features": {
        "obj_ID": 1237663784734294016.0,
        "alpha": 135.689,
        "delta": 32.494,
        "u": 23.87882,
        "g": 22.27530,
        "r": 20.39398,
        "i": 19.16763,
        "z": 18.79371,
        "run_ID": 3606,
        "cam_col": 4,
        "field_ID": 587,
        "spec_obj_ID": 6.543777825301504e17,
        "redshift": 0.644,
        "plate": 5812,
        "MJD": 56354,
        "fiber_ID": 171
    }
}

response = requests.post("http://localhost:8800/predict/", json=data)
print(response.json())
```

### 2. GraphQL API

**Access the GraphQL playground at:** `http://localhost:8800/graphql`

**Example mutation:**
```graphql
mutation PredictStar {
  predict(features: {
    objID: 1237663784734294016.0,
    alpha: 135.689,
    delta: 32.494,
    u: 23.87882,
    g: 22.27530,
    r: 20.39398,
    i: 19.16763,
    z: 18.79371,
    runID: 3606,
    camCol: 4,
    fieldID: 587,
    specObjID: 6.543777825301504e17,
    redshift: 0.644,
    plate: 5812,
    MJD: 56354,
    fiberID: 171
  }) {
    intOutput
    strOutput
  }
}
```

**Python example with requests:**
```python
import requests
import json

query = """
mutation PredictStar($features: StarClassificationInput!) {
    predict(features: $features) {
        intOutput
        strOutput
    }
}
"""

variables = {
    "features": {
        "objID": 1237663784734294016.0,
        "alpha": 135.689,
        "delta": 32.494,
        # ... other fields
    }
}

response = requests.post(
    "http://localhost:8800/graphql",
    json={"query": query, "variables": variables}
)
print(response.json())
```

### 3. gRPC Service

First, generate the Python client files:
```bash
cd dockerfiles/fastapi
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/star_classification.proto
```

**Python gRPC client example:**
```python
import grpc
import star_classification_pb2
import star_classification_pb2_grpc

# Create channel and stub
channel = grpc.insecure_channel('localhost:50051')
stub = star_classification_pb2_grpc.StarClassificationServiceStub(channel)

# Create request
request = star_classification_pb2.StarFeatures(
    obj_ID=1237663784734294016.0,
    alpha=135.689,
    delta=32.494,
    u=23.87882,
    g=22.27530,
    r=20.39398,
    i=19.16763,
    z=18.79371,
    run_ID=3606,
    cam_col=4,
    field_ID=587,
    spec_obj_ID=6.543777825301504e17,
    redshift=0.644,
    plate=5812,
    MJD=56354,
    fiber_ID=171
)

# Make prediction
response = stub.Predict(request)
print(f"Prediction: {response.int_output} ({response.str_output})")

# Health check
health_request = star_classification_pb2.HealthCheckRequest()
health_response = stub.HealthCheck(health_request)
print(f"Health: {health_response.status}")
```

**gRPC Streaming example:**
```python
def stream_predictions():
    # Create multiple requests
    requests = [request] * 5  # Send same request 5 times
    
    # Stream predictions
    for response in stub.PredictStream(iter(requests)):
        print(f"Streamed prediction: {response.int_output} ({response.str_output})")

stream_predictions()
```

### 4. Kafka Streaming

**Producer example (sending data for prediction):**
```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

data = {
    "obj_ID": 1237663784734294016.0,
    "alpha": 135.689,
    "delta": 32.494,
    "u": 23.87882,
    "g": 22.27530,
    "r": 20.39398,
    "i": 19.16763,
    "z": 18.79371,
    "run_ID": 3606,
    "cam_col": 4,
    "field_ID": 587,
    "spec_obj_ID": 6.543777825301504e17,
    "redshift": 0.644,
    "plate": 5812,
    "MJD": 56354,
    "fiber_ID": 171
}

producer.send('star_features_input', value=data)
producer.flush()
producer.close()
```

**Consumer example (receiving predictions):**
```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'star_predictions_output',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    prediction = message.value
    print(f"Received prediction: {prediction}")
```

**REST API test endpoint:**
```bash
curl -X POST "http://localhost:8800/stream/test" \
  -H "Content-Type: application/json" \
  -d '{
    "obj_ID": 1237663784734294016.0,
    "alpha": 135.689,
    "delta": 32.494,
    "u": 23.87882,
    "g": 22.27530,
    "r": 20.39398,
    "i": 19.16763,
    "z": 18.79371,
    "run_ID": 3606,
    "cam_col": 4,
    "field_ID": 587,
    "spec_obj_ID": 6.543777825301504e17,
    "redshift": 0.644,
    "plate": 5812,
    "MJD": 56354,
    "fiber_ID": 171
  }'
```

## Testing All Services

Use the provided test client to benchmark all services:

```bash
python test_clients.py
```

This will provide an interactive menu to test each service individually or run a comprehensive performance comparison.

## Service Information

Get information about all available services:
```bash
curl http://localhost:8800/services
```

## Performance Characteristics

| Protocol | Latency | Throughput | Streaming | Use Case |
|----------|---------|------------|-----------|----------|
| REST | Medium | Medium | No | Web APIs, simple integration |
| GraphQL | Medium | Medium | Limited | Flexible data fetching |
| gRPC | Low | High | Yes | High-performance, typed APIs |
| Kafka | High (async) | Very High | Yes | Real-time streaming, decoupled systems |

## Troubleshooting

### gRPC Issues
- Ensure port 50051 is not blocked
- Regenerate proto files if needed:
  ```bash
  python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/star_classification.proto
  ```

### Kafka Issues
- Check if Kafka and Zookeeper are running:
  ```bash
  docker compose ps
  ```
- Verify topic creation:
  ```bash
  docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list
  ```
- Create topics manually if needed:
  ```bash
  docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --create --topic star_features_input --partitions 3 --replication-factor 1
  docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --create --topic star_predictions_output --partitions 3 --replication-factor 1
  ```

### GraphQL Issues
- Access the GraphQL playground for interactive testing
- Check schema documentation in the playground

## Production Considerations

1. **Security**: Add authentication and authorization
2. **Monitoring**: Implement health checks and metrics
3. **Scaling**: Use load balancers and multiple replicas
4. **Error Handling**: Implement proper error responses and logging
5. **Rate Limiting**: Add rate limiting to prevent abuse
6. **SSL/TLS**: Use encrypted connections in production

## Next Steps

- Implement authentication across all protocols
- Add more comprehensive logging and monitoring
- Create client SDKs for different programming languages
- Add data validation and schema evolution strategies