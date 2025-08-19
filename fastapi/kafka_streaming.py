import json
import threading
import time
import numpy as np
import pandas as pd
import os
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable
import logging

from model_manager import model, data_dict, check_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StarClassificationStreamer:
    def __init__(self, bootstrap_servers=None):
        if bootstrap_servers is None:
            # Use environment variable or default
            kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
            self.bootstrap_servers = kafka_servers.split(',')
        else:
            self.bootstrap_servers = bootstrap_servers
        self.input_topic = 'star_features_input'
        self.output_topic = 'star_predictions_output'
        self.consumer = None
        self.producer = None
        self.running = False
        
    def _create_consumer(self):
        """Create Kafka consumer"""
        try:
            self.consumer = KafkaConsumer(
                self.input_topic,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='star-classification-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                consumer_timeout_ms=1000
            )
            logger.info(f"Connected to Kafka consumer for topic: {self.input_topic}")
            return True
        except NoBrokersAvailable:
            logger.warning("No Kafka brokers available for consumer")
            return False
        except Exception as e:
            logger.error(f"Error creating consumer: {e}")
            return False
    
    def _create_producer(self):
        """Create Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            logger.info("Connected to Kafka producer")
            return True
        except NoBrokersAvailable:
            logger.warning("No Kafka brokers available for producer")
            return False
        except Exception as e:
            logger.error(f"Error creating producer: {e}")
            return False
    
    def start_streaming(self):
        """Start the streaming consumer in a background thread"""
        if not self._create_consumer() or not self._create_producer():
            logger.warning("Kafka streaming not available - broker connection failed")
            return False
            
        self.running = True
        streaming_thread = threading.Thread(target=self._consume_and_predict, daemon=True)
        streaming_thread.start()
        logger.info("Kafka streaming started in background thread")
        return True
    
    def stop_streaming(self):
        """Stop the streaming consumer"""
        self.running = False
        if self.consumer:
            self.consumer.close()
        if self.producer:
            self.producer.close()
        logger.info("Kafka streaming stopped")
    
    def _consume_and_predict(self):
        """Main loop to consume messages and make predictions"""
        logger.info(f"Starting to consume from topic: {self.input_topic}")
        
        while self.running:
            try:
                # Poll for messages
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        try:
                            # Process each message
                            self._process_message(message.value)
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _process_message(self, features_data):
        """Process a single message and send prediction"""
        try:
            # Check for model updates
            check_model()
            
            # Validate input data
            required_fields = [
                'obj_ID', 'alpha', 'delta', 'u', 'g', 'r', 'i', 'z',
                'run_ID', 'cam_col', 'field_ID', 'spec_obj_ID', 
                'redshift', 'plate', 'MJD', 'fiber_ID'
            ]
            
            if not all(field in features_data for field in required_fields):
                logger.error(f"Missing required fields in message: {features_data}")
                return
            
            # Extract features from the message
            features_list = [features_data[field] for field in required_fields]
            features_key = required_fields

            # Convert features into a pandas DataFrame
            features_df = pd.DataFrame(np.array(features_list).reshape([1, -1]), columns=features_key)

            # Scale the data using standard scaler
            features_df = (features_df - data_dict["standard_scaler_mean"]) / data_dict["standard_scaler_std"]

            # Make the prediction using the trained model
            prediction = model.predict(features_df)

            # Convert prediction result into string format
            str_pred = "Star"
            if prediction == 0:
                str_pred = "Galaxy"
            elif prediction == 1:
                str_pred = "OSO"

            # Create prediction result
            prediction_result = {
                'input_data': features_data,
                'prediction': {
                    'int_output': int(prediction[0]),
                    'str_output': str_pred
                },
                'timestamp': time.time(),
                'model_version': 'star_class_model_prod'
            }
            
            # Send prediction to output topic
            self.producer.send(self.output_topic, value=prediction_result)
            self.producer.flush()
            
            logger.info(f"Processed prediction: {str_pred} (confidence: {prediction[0]})")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def send_test_data(self, features_data):
        """Send test data to input topic (for testing purposes)"""
        if not self.producer:
            if not self._create_producer():
                logger.error("Cannot send test data - producer not available")
                return False
        
        try:
            self.producer.send(self.input_topic, value=features_data)
            self.producer.flush()
            logger.info("Test data sent to input topic")
            return True
        except Exception as e:
            logger.error(f"Error sending test data: {e}")
            return False


# Global streaming instance
streaming_service = StarClassificationStreamer()


def start_kafka_streaming():
    """Initialize and start Kafka streaming service"""
    return streaming_service.start_streaming()


def stop_kafka_streaming():
    """Stop Kafka streaming service"""
    streaming_service.stop_streaming()


def send_test_prediction(features_data):
    """Send test data for prediction via Kafka"""
    return streaming_service.send_test_data(features_data)