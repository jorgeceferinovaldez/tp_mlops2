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
from fastapi.middleware.cors import CORSMiddleware

# --- CREA LA APP PRIMERO ---
app = FastAPI(
    title="Star Classification API",
    description="Multi-protocol API for star classification supporting REST, GraphQL, gRPC and Streaming",
    version="2.0.0"
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------
# Schemas
# ---------------------------

class ModelInput(BaseModel):
    obj_ID: float = Field(description="Object identifier, a unique value that identifies the object in the image catalog used by CAS.", ge=0.0)
    alpha: float = Field(description="Right Ascension angle (in epoch J2000).", ge=0.0, le=360.0)
    delta: float = Field(description="Declination angle (in epoch J2000).", ge=-90.0, le=90.0)
    u: float = Field(description="Ultraviolet filter in the photometric system.", ge=0.0)
    g: float = Field(description="Green filter in the photometric system.", ge=0.0)
    r: float = Field(description="Red filter in the photometric system.", ge=0.0)
    i: float = Field(description="Near-infrared filter in the photometric system.", ge=0.0)
    z: float = Field(description="Infrared filter in the photometric system.", ge=0.0)
    run_ID: int = Field(description="Run number used to identify the specific analysis.", ge=0)
    cam_col: int = Field(description="Camera column to identify the scan line within the run.", ge=1, le=6)
    field_ID: int = Field(description="Field number to identify each field.", ge=0)
    spec_obj_ID: float = Field(description="Unique ID used for optical spectroscopic objects.", ge=0.0)
    redshift: float = Field(description="Redshift value based on the wavelength increase.", ge=0.0)
    plate: int = Field(description="Plate ID, identifies each plate in SDSS.", ge=0)
    MJD: int = Field(description="Modified Julian Date, used to indicate when a particular SDSS data was taken.", ge=0)
    fiber_ID: int = Field(description="Fiber ID that identifies the fiber that directed light to the focal plane in each observation.", ge=0)

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
    int_output: int = Field(description="Output of the model. 0 for Galaxy, 1 for OSO and 2 for Star")
    str_output: Literal["Galaxy", "OSO", "Star"] = Field(description="Output of the model in string form")

    model_config = {
        "json_schema_extra": {"examples": [{"int_output": 2, "str_output": "Star"}]}
    }

# ---------------------------
# Lifecycles / startup
# ---------------------------

# GraphQL router se agrega en startup para evitar imports circulares
@app.on_event("startup")
async def startup_event():
    """Initialize additional services on startup"""
    from graphql_schema import schema
    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")

    from grpc_server import start_grpc_server_thread
    from kafka_streaming import start_kafka_streaming

    # gRPC
    try:
        start_grpc_server_thread()
    except Exception as e:
        print(f"Warning: gRPC server failed to start: {e}")

    # Kafka
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

# ---------------------------
# Endpoints
# ---------------------------

@app.get("/")
async def read_root():
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
    Recibe un JSON con los campos de ModelInput (raíz) y lo envía al tópico de entrada.
    Tu frontend MUI ya hace: body = JSON.stringify(payload)  ✅
    """
    from kafka_streaming import send_test_prediction

    features_dict = features.dict()
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
    features: Annotated[ModelInput, Body(embed=True)],  # <-- el frontend envía { features: {...} }
    background_tasks: BackgroundTasks
):
    """
    Recibe { features: {...} } y devuelve la clase (Galaxy/OSO/Star).
    """
    # Vectorización
    features_list = [*features.dict().values()]
    features_key = [*features.dict().keys()]
    features_df = pd.DataFrame(np.array(features_list).reshape([1, -1]), columns=features_key)

    # Escalado
    features_df = (features_df - data_dict["standard_scaler_mean"]) / data_dict["standard_scaler_std"]

    # Predicción
    prediction = model.predict(features_df)
    str_pred = "Star"
    if prediction == 0:
        str_pred = "Galaxy"
    elif prediction == 1:
        str_pred = "OSO"

    # Chequeo de modelo en background
    background_tasks.add_task(check_model)

    return ModelOutput(int_output=int(prediction[0]), str_output=str_pred)
