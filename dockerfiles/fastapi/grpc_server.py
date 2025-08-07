import grpc
from concurrent import futures
import numpy as np
import pandas as pd
import threading
import star_classification_pb2
import star_classification_pb2_grpc

from app import model, data_dict, check_model


class StarClassificationServicer(star_classification_pb2_grpc.StarClassificationServiceServicer):
    def __init__(self):
        print("gRPC Star Classification Service initialized")
        
    def Predict(self, request, context):
        """
        Unary RPC for star classification prediction
        """
        try:
            # Check for model updates
            check_model()
            
            # Convert gRPC request to dictionary
            features_dict = {
                'obj_ID': request.obj_ID,
                'alpha': request.alpha,
                'delta': request.delta,
                'u': request.u,
                'g': request.g,
                'r': request.r,
                'i': request.i,
                'z': request.z,
                'run_ID': request.run_ID,
                'cam_col': request.cam_col,
                'field_ID': request.field_ID,
                'spec_obj_ID': request.spec_obj_ID,
                'redshift': request.redshift,
                'plate': request.plate,
                'MJD': request.MJD,
                'fiber_ID': request.fiber_ID
            }
            
            # Extract features from the request and convert them into a list and dictionary
            features_list = list(features_dict.values())
            features_key = list(features_dict.keys())

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

            # Return the prediction result
            return star_classification_pb2.StarPrediction(
                int_output=int(prediction[0]),
                str_output=str_pred
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Prediction failed: {str(e)}')
            return star_classification_pb2.StarPrediction()
    
    def HealthCheck(self, request, context):
        """
        Health check endpoint for gRPC service
        """
        return star_classification_pb2.HealthCheckResponse(
            status="healthy",
            message="Star Classification gRPC Service is running"
        )
    
    def PredictStream(self, request_iterator, context):
        """
        Bidirectional streaming RPC for star classification
        """
        try:
            for request in request_iterator:
                # Check for model updates
                check_model()
                
                # Convert gRPC request to dictionary
                features_dict = {
                    'obj_ID': request.obj_ID,
                    'alpha': request.alpha,
                    'delta': request.delta,
                    'u': request.u,
                    'g': request.g,
                    'r': request.r,
                    'i': request.i,
                    'z': request.z,
                    'run_ID': request.run_ID,
                    'cam_col': request.cam_col,
                    'field_ID': request.field_ID,
                    'spec_obj_ID': request.spec_obj_ID,
                    'redshift': request.redshift,
                    'plate': request.plate,
                    'MJD': request.MJD,
                    'fiber_ID': request.fiber_ID
                }
                
                # Extract features from the request and convert them into a list and dictionary
                features_list = list(features_dict.values())
                features_key = list(features_dict.keys())

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

                # Yield the prediction result for streaming
                yield star_classification_pb2.StarPrediction(
                    int_output=int(prediction[0]),
                    str_output=str_pred
                )
                
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Streaming prediction failed: {str(e)}')


def serve_grpc():
    """
    Start the gRPC server
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    star_classification_pb2_grpc.add_StarClassificationServiceServicer_to_server(
        StarClassificationServicer(), server
    )
    
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    server.start()
    print(f"gRPC server started on {listen_addr}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("gRPC server stopped")


def start_grpc_server_thread():
    """
    Start the gRPC server in a separate thread
    """
    grpc_thread = threading.Thread(target=serve_grpc, daemon=True)
    grpc_thread.start()
    print("gRPC server started in background thread")


if __name__ == '__main__':
    serve_grpc()