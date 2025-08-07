"""
Test clients for all star classification API services:
- REST API
- GraphQL API  
- gRPC Service
- Kafka Streaming

This script demonstrates how to interact with each service and provides 
performance comparison capabilities.
"""

import grpc
import json
import time
import requests
import numpy as np
from kafka import KafkaProducer, KafkaConsumer
from typing import Dict, Any
import threading
import queue


# Sample star data for testing
SAMPLE_STAR_DATA = {
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

# Service URLs and configuration
REST_URL = "http://localhost:8800/predict/"
GRAPHQL_URL = "http://localhost:8800/graphql"
GRPC_HOST = "localhost:50051"
KAFKA_BOOTSTRAP_SERVERS = ["localhost:9094"]
KAFKA_INPUT_TOPIC = "star_features_input"
KAFKA_OUTPUT_TOPIC = "star_predictions_output"


class StarClassificationClient:
    """Unified client for testing all star classification services."""
    
    def __init__(self):
        self.sample_data = SAMPLE_STAR_DATA
        self.results_queue = queue.Queue()
    
    def test_rest_api(self, num_requests: int = 1) -> Dict[str, Any]:
        """Test REST API performance."""
        print(f"Testing REST API with {num_requests} requests...")
        
        start_time = time.time()
        responses = []
        
        for i in range(num_requests):
            try:
                response = requests.post(
                    REST_URL,
                    json={"features": self.sample_data},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                result = response.json()
                responses.append(result)
                if i == 0:  # Show first response
                    print(f"  First response: {result}")
            except Exception as e:
                print(f"  Error in request {i+1}: {e}")
                return {"error": str(e)}
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            "service": "REST",
            "requests": num_requests,
            "total_time": total_time,
            "avg_time_ms": (total_time / num_requests) * 1000,
            "requests_per_second": num_requests / total_time,
            "success_count": len(responses),
            "sample_response": responses[0] if responses else None
        }
    
    def test_graphql_api(self, num_requests: int = 1) -> Dict[str, Any]:
        """Test GraphQL API performance."""
        print(f"Testing GraphQL API with {num_requests} requests...")
        
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
                "objID": self.sample_data["obj_ID"],
                "alpha": self.sample_data["alpha"],
                "delta": self.sample_data["delta"],
                "u": self.sample_data["u"],
                "g": self.sample_data["g"],
                "r": self.sample_data["r"],
                "i": self.sample_data["i"],
                "z": self.sample_data["z"],
                "runID": self.sample_data["run_ID"],
                "camCol": self.sample_data["cam_col"],
                "fieldID": self.sample_data["field_ID"],
                "specObjID": self.sample_data["spec_obj_ID"],
                "redshift": self.sample_data["redshift"],
                "plate": self.sample_data["plate"],
                "MJD": self.sample_data["MJD"],
                "fiberID": self.sample_data["fiber_ID"]
            }
        }
        
        start_time = time.time()
        responses = []
        
        for i in range(num_requests):
            try:
                response = requests.post(
                    GRAPHQL_URL,
                    json={"query": query, "variables": variables},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                result = response.json()
                responses.append(result)
                if i == 0:  # Show first response
                    print(f"  First response: {result}")
            except Exception as e:
                print(f"  Error in request {i+1}: {e}")
                return {"error": str(e)}
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            "service": "GraphQL",
            "requests": num_requests,
            "total_time": total_time,
            "avg_time_ms": (total_time / num_requests) * 1000,
            "requests_per_second": num_requests / total_time,
            "success_count": len(responses),
            "sample_response": responses[0] if responses else None
        }
    
    def test_grpc_service(self, num_requests: int = 1) -> Dict[str, Any]:
        """Test gRPC service performance."""
        print(f"Testing gRPC service with {num_requests} requests...")
        
        try:
            # Import generated gRPC files
            import star_classification_pb2
            import star_classification_pb2_grpc
        except ImportError:
            print("  Error: gRPC proto files not found. Make sure to generate them first.")
            return {"error": "gRPC proto files not found"}
        
        start_time = time.time()
        responses = []
        
        try:
            with grpc.insecure_channel(GRPC_HOST) as channel:
                stub = star_classification_pb2_grpc.StarClassificationServiceStub(channel)
                
                for i in range(num_requests):
                    try:
                        request = star_classification_pb2.StarFeatures(
                            obj_ID=self.sample_data["obj_ID"],
                            alpha=self.sample_data["alpha"],
                            delta=self.sample_data["delta"],
                            u=self.sample_data["u"],
                            g=self.sample_data["g"],
                            r=self.sample_data["r"],
                            i=self.sample_data["i"],
                            z=self.sample_data["z"],
                            run_ID=self.sample_data["run_ID"],
                            cam_col=self.sample_data["cam_col"],
                            field_ID=self.sample_data["field_ID"],
                            spec_obj_ID=self.sample_data["spec_obj_ID"],
                            redshift=self.sample_data["redshift"],
                            plate=self.sample_data["plate"],
                            MJD=self.sample_data["MJD"],
                            fiber_ID=self.sample_data["fiber_ID"]
                        )
                        
                        response = stub.Predict(request)
                        result = {
                            "int_output": response.int_output,
                            "str_output": response.str_output
                        }
                        responses.append(result)
                        
                        if i == 0:  # Show first response
                            print(f"  First response: {result}")
                            
                    except Exception as e:
                        print(f"  Error in request {i+1}: {e}")
                        
        except Exception as e:
            print(f"  Connection error: {e}")
            return {"error": str(e)}
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            "service": "gRPC",
            "requests": num_requests,
            "total_time": total_time,
            "avg_time_ms": (total_time / num_requests) * 1000,
            "requests_per_second": num_requests / total_time,
            "success_count": len(responses),
            "sample_response": responses[0] if responses else None
        }
    
    def test_kafka_streaming(self, num_messages: int = 5, timeout: int = 30) -> Dict[str, Any]:
        """Test Kafka streaming performance."""
        print(f"Testing Kafka streaming with {num_messages} messages...")
        
        try:
            # Create producer
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            
            # Create consumer in separate thread
            def consume_messages():
                consumer = KafkaConsumer(
                    KAFKA_OUTPUT_TOPIC,
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    auto_offset_reset='latest',
                    group_id='test-client',
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                    consumer_timeout_ms=timeout * 1000
                )
                
                for message in consumer:
                    self.results_queue.put(message.value)
                    if self.results_queue.qsize() >= num_messages:
                        break
                consumer.close()
            
            # Start consumer thread
            consumer_thread = threading.Thread(target=consume_messages)
            consumer_thread.daemon = True
            consumer_thread.start()
            
            # Give consumer time to start
            time.sleep(2)
            
            # Send messages
            start_time = time.time()
            for i in range(num_messages):
                producer.send(KAFKA_INPUT_TOPIC, value=self.sample_data)
                time.sleep(0.1)  # Small delay between messages
            
            producer.flush()
            producer.close()
            
            # Wait for responses
            responses = []
            while len(responses) < num_messages:
                try:
                    result = self.results_queue.get(timeout=5)
                    responses.append(result)
                    if len(responses) == 1:  # Show first response
                        print(f"  First response: {result}")
                except queue.Empty:
                    print("  Timeout waiting for response")
                    break
            
            end_time = time.time()
            total_time = end_time - start_time
            
            return {
                "service": "Kafka Streaming",
                "messages_sent": num_messages,
                "messages_received": len(responses),
                "total_time": total_time,
                "avg_time_ms": (total_time / num_messages) * 1000 if num_messages > 0 else 0,
                "throughput_msg_per_sec": num_messages / total_time if total_time > 0 else 0,
                "sample_response": responses[0] if responses else None
            }
            
        except Exception as e:
            print(f"  Kafka error: {e}")
            return {"error": str(e)}
    
    def run_performance_comparison(self, num_requests: int = 100):
        """Run performance comparison across all services."""
        print(f"\n{'='*60}")
        print(f"STAR CLASSIFICATION API PERFORMANCE COMPARISON")
        print(f"{'='*60}")
        
        results = []
        
        # Test REST API
        rest_result = self.test_rest_api(num_requests)
        if "error" not in rest_result:
            results.append(rest_result)
        print()
        
        # Test GraphQL API
        graphql_result = self.test_graphql_api(num_requests)
        if "error" not in graphql_result:
            results.append(graphql_result)
        print()
        
        # Test gRPC Service
        grpc_result = self.test_grpc_service(num_requests)
        if "error" not in grpc_result:
            results.append(grpc_result)
        print()
        
        # Test Kafka Streaming (fewer messages due to async nature)
        streaming_messages = min(num_requests, 10)
        kafka_result = self.test_kafka_streaming(streaming_messages)
        if "error" not in kafka_result:
            results.append(kafka_result)
        print()
        
        # Display comparison
        if results:
            print(f"{'='*60}")
            print(f"PERFORMANCE SUMMARY")
            print(f"{'='*60}")
            print(f"{'Service':<20} {'Avg Time (ms)':<15} {'Req/Sec':<15} {'Success Rate'}")
            print(f"{'-'*60}")
            
            for result in results:
                service = result["service"]
                if service == "Kafka Streaming":
                    avg_time = result["avg_time_ms"]
                    throughput = result["throughput_msg_per_sec"]
                    success_rate = f"{result['messages_received']}/{result['messages_sent']}"
                else:
                    avg_time = result["avg_time_ms"]
                    throughput = result["requests_per_second"]
                    success_rate = f"{result['success_count']}/{result['requests']}"
                
                print(f"{service:<20} {avg_time:<15.2f} {throughput:<15.2f} {success_rate}")
        
        return results


def main():
    """Main function to run all tests."""
    client = StarClassificationClient()
    
    print("Star Classification API Multi-Protocol Test Client")
    print("=" * 60)
    
    while True:
        print("\nAvailable tests:")
        print("1. Test REST API")
        print("2. Test GraphQL API")
        print("3. Test gRPC Service")
        print("4. Test Kafka Streaming")
        print("5. Run Performance Comparison")
        print("6. Exit")
        
        choice = input("\nSelect test (1-6): ").strip()
        
        if choice == "1":
            requests_count = int(input("Number of requests (default 10): ") or "10")
            result = client.test_rest_api(requests_count)
            print(f"\nResult: {json.dumps(result, indent=2)}")
            
        elif choice == "2":
            requests_count = int(input("Number of requests (default 10): ") or "10")
            result = client.test_graphql_api(requests_count)
            print(f"\nResult: {json.dumps(result, indent=2)}")
            
        elif choice == "3":
            requests_count = int(input("Number of requests (default 10): ") or "10")
            result = client.test_grpc_service(requests_count)
            print(f"\nResult: {json.dumps(result, indent=2)}")
            
        elif choice == "4":
            messages_count = int(input("Number of messages (default 5): ") or "5")
            result = client.test_kafka_streaming(messages_count)
            print(f"\nResult: {json.dumps(result, indent=2)}")
            
        elif choice == "5":
            requests_count = int(input("Number of requests per service (default 50): ") or "50")
            client.run_performance_comparison(requests_count)
            
        elif choice == "6":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please select 1-6.")


if __name__ == "__main__":
    main()