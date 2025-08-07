import numpy as np
import pandas as pd

from typing import Literal
from fastapi import FastAPI, Body, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from strawberry.fastapi import GraphQLRouter
from model_manager import model, data_dict, check_model


class ModelInput(BaseModel):
    """
    Input schema for the star classification model.

    This class defines the input fields required by the star classification model along with their descriptions
    and validation constraints.

    :param obj_ID: Object identifier, a unique value that identifies the object in the image catalog used by CAS.
    :param alpha: Right Ascension angle (in epoch J2000) as a floating point number.
    :param delta: Declination angle (in epoch J2000) as a floating point number.
    :param u: Ultraviolet filter in the photometric system as a floating point number.
    :param g: Green filter in the photometric system as a floating point number.
    :param r: Red filter in the photometric system as a floating point number.
    :param i: Near-infrared filter in the photometric system as a floating point number.
    :param z: Infrared filter in the photometric system as a floating point number.
    :param run_ID: Run number used to identify the specific analysis as an integer.
    :param cam_col: Camera column to identify the scan line within the run. Integer values indicating the camera column position.
    :param field_ID: Field number to identify each field as an integer.
    :param spec_obj_ID: Unique ID used for optical spectroscopic objects (this means that 2 different observations with the same spec_obj_ID should share the output class) as a floating point number.
    :param redshift: Redshift value based on the wavelength increase as a floating point number.
    :param plate: Plate ID, identifies each plate in SDSS as an integer.
    :param MJD: Modified Julian Date, used to indicate when a particular SDSS data was taken as an integer.
    :param fiber_ID: Fiber ID that identifies the fiber that directed light to the focal plane in each observation as an integer.

    """

    obj_ID: float = Field(
    description="Object identifier, a unique value that identifies the object in the image catalog used by CAS.",
    ge=0.0
    )
    alpha: float = Field(
        description="Right Ascension angle (in epoch J2000).",
        ge=0.0,
        le=360.0
    )
    delta: float = Field(
        description="Declination angle (in epoch J2000).",
        ge=-90.0,
        le=90.0
    )
    u: float = Field(
        description="Ultraviolet filter in the photometric system.",
        ge=0.0
    )
    g: float = Field(
        description="Green filter in the photometric system.",
        ge=0.0
    )
    r: float = Field(
        description="Red filter in the photometric system.",
        ge=0.0
    )
    i: float = Field(
        description="Near-infrared filter in the photometric system.",
        ge=0.0
    )
    z: float = Field(
        description="Infrared filter in the photometric system.",
        ge=0.0
    )
    run_ID: int = Field(
        description="Run number used to identify the specific analysis.",
        ge=0
    )
    cam_col: int = Field(
        description="Camera column to identify the scan line within the run.",
        ge=1,
        le=6
    )
    field_ID: int = Field(
        description="Field number to identify each field.",
        ge=0
    )
    spec_obj_ID: float = Field(
        description="Unique ID used for optical spectroscopic objects.",
        ge=0.0
    )
    redshift: float = Field(
        description="Redshift value based on the wavelength increase.",
        ge=0.0
    )
    plate: int = Field(
        description="Plate ID, identifies each plate in SDSS.",
        ge=0
    )
    MJD: int = Field(
        description="Modified Julian Date, used to indicate when a particular SDSS data was taken.",
        ge=0
    )
    fiber_ID: int = Field(
        description="Fiber ID that identifies the fiber that directed light to the focal plane in each observation.",
        ge=0
    )


    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "obj_ID": 123456789.0,
                    "alpha": 180.0,
                    "delta": 45.0,
                    "u": 22.4,
                    "g": 21.6,
                    "r": 21.1,
                    "i": 20.9,
                    "z": 20.7,
                    "run_ID": 756,
                    "cam_col": 3,
                    "field_ID": 674,
                    "spec_obj_ID": 567890123.0,
                    "redshift": 0.123,
                    "plate": 2345,
                    "MJD": 58583,
                    "fiber_ID": 456
                }
            ]
        }
    }


class ModelOutput(BaseModel):
    """
    Output schema for the star classification model.

    This class defines the output fields returned by the star classification model along with their descriptions
    and possible values.

    :param str_output: Output of the model in string form. Can be "Healthy patient" or "Heart disease detected".
    """

    int_output: int = Field(
        description="Output of the model. 0 for Galaxy, 1 for OSO and 2 for Star",
    )
    str_output: Literal["Galaxy", "OSO","Star"] = Field(
        description="Output of the model in string form",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "int_output": 2,
                    "str_output": "Star",
                }
            ]
        }
    }



# Model is loaded in model_manager module

app = FastAPI(
    title="Star Classification API",
    description="Multi-protocol API for star classification supporting REST, GraphQL, gRPC and Streaming",
    version="2.0.0"
)

# GraphQL router will be added in startup event to avoid circular import

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    """Initialize additional services on startup"""
    # Add GraphQL router to avoid circular import
    from graphql_schema import schema
    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")
    
    from grpc_server import start_grpc_server_thread
    from kafka_streaming import start_kafka_streaming
    
    # Start gRPC server in background thread
    try:
        start_grpc_server_thread()
    except Exception as e:
        print(f"Warning: gRPC server failed to start: {e}")
    
    # Start Kafka streaming service
    try:
        kafka_started = start_kafka_streaming()
        if kafka_started:
            print("Kafka streaming service started successfully")
        else:
            print("Warning: Kafka streaming service failed to start (broker might not be available)")
    except Exception as e:
        print(f"Warning: Kafka streaming failed to start: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    from kafka_streaming import stop_kafka_streaming
    try:
        stop_kafka_streaming()
        print("Kafka streaming service stopped")
    except Exception as e:
        print(f"Error stopping Kafka streaming: {e}")


@app.get("/")
async def read_root():
    """
    Root endpoint of the Star Classifier API.

    This endpoint returns a JSON response with a welcome message to indicate that the API is running.
    """
    return JSONResponse(content=jsonable_encoder({
        "message": "Welcome to the Multi-Protocol Star Classifier API",
        "version": "2.0.0",
        "available_endpoints": {
            "REST": "/predict/",
            "GraphQL": "/graphql",
            "gRPC": "port 50051",
            "Kafka_Streaming": "topics: star_features_input, star_predictions_output",
            "API_Docs": "/docs",
            "Services_Info": "/services"
        }
    }))


@app.get("/services")
async def services_info():
    """
    Information about available services and their endpoints.
    """
    return JSONResponse(content=jsonable_encoder({
        "services": {
            "REST_API": {
                "description": "Traditional REST API for star classification",
                "endpoint": "POST /predict/",
                "port": 8800,
                "documentation": "/docs"
            },
            "GraphQL_API": {
                "description": "GraphQL API with flexible querying",
                "endpoint": "/graphql",
                "port": 8800,
                "playground": "Available at /graphql for interactive queries",
                "example_query": """
                mutation {
                  predict(features: {
                    objID: 123456789.0,
                    alpha: 180.0,
                    delta: 45.0,
                    u: 22.4, g: 21.6, r: 21.1,
                    i: 20.9, z: 20.7,
                    runID: 756, camCol: 3,
                    fieldID: 674,
                    specObjID: 567890123.0,
                    redshift: 0.123,
                    plate: 2345, MJD: 58583,
                    fiberID: 456
                  }) {
                    intOutput
                    strOutput
                  }
                }
                """
            },
            "gRPC_Service": {
                "description": "High-performance gRPC service with streaming support",
                "port": 50051,
                "proto_file": "proto/star_classification.proto",
                "methods": ["Predict", "HealthCheck", "PredictStream"]
            },
            "Kafka_Streaming": {
                "description": "Real-time streaming predictions via Apache Kafka",
                "input_topic": "star_features_input",
                "output_topic": "star_predictions_output",
                "test_endpoint": "POST /stream/test"
            }
        }
    }))


@app.post("/stream/test")
async def test_streaming(features: ModelInput):
    """
    Test the Kafka streaming functionality by sending data to the input topic.
    """
    from kafka_streaming import send_test_prediction
    
    # Convert features to dictionary
    features_dict = features.dict()
    
    # Send to Kafka
    success = send_test_prediction(features_dict)
    
    if success:
        return JSONResponse(content=jsonable_encoder({
            "message": "Test data sent to Kafka streaming service",
            "input_topic": "star_features_input",
            "output_topic": "star_predictions_output",
            "note": "Check the output topic for prediction results"
        }))
    else:
        return JSONResponse(
            status_code=503,
            content=jsonable_encoder({
                "error": "Kafka streaming service not available",
                "message": "Make sure Kafka broker is running and accessible"
            })
        )


@app.post("/predict/", response_model=ModelOutput)
def predict(
    features: Annotated[
        ModelInput,
        Body(embed=True),
    ],
    background_tasks: BackgroundTasks
):
    """
    Endpoint for classifying stars.

    This endpoint receives features related to spectral features and predicts whether it is a galaxy, OSO or star using a trained model. 
    It returns the prediction result in both integer and string formats.
    """

    # Extract features from the request and convert them into a list and dictionary
    features_list = [*features.dict().values()]
    features_key = [*features.dict().keys()]

    # Convert features into a pandas DataFrame
    features_df = pd.DataFrame(np.array(features_list).reshape([1, -1]), columns=features_key)

    # Scale the data using standard scaler
    features_df = (features_df-data_dict["standard_scaler_mean"])/data_dict["standard_scaler_std"]

    # Make the prediction using the trained model
    prediction = model.predict(features_df)

    # Convert prediction result into string format
    str_pred = "Star"
    if prediction==0:
        str_pred = "Galaxy"
    elif prediction==1:
        str_pred = "OSO"

    # Check if the model has changed asynchronously
    background_tasks.add_task(check_model)

    # Return the prediction result
    return ModelOutput(int_output=int(prediction[0]), str_output=str_pred)

