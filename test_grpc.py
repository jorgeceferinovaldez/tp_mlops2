import grpc
import star_classification_pb2
import star_classification_pb2_grpc

channel = grpc.insecure_channel("localhost:50051")
stub = star_classification_pb2_grpc.StarClassificationServiceStub(channel)

features = star_classification_pb2.StarFeatures(
    obj_ID=123456789.0,
    alpha=180.0,
    delta=45.0,
    u=22.4, g=21.6, r=21.1, i=20.9, z=20.7,
    run_ID=756, cam_col=3, field_ID=674,
    spec_obj_ID=567890123.0, redshift=0.123,
    plate=2345, MJD=58583, fiber_ID=456
)

try:
    response = stub.Predict(features)
    print(f"gRPC Response: {response}")
except Exception as e:
    print(f"gRPC Error: {e}")
