import strawberry
import numpy as np
import pandas as pd
from typing import List

from model_manager import model, data_dict, check_model


@strawberry.type
class StarClassificationOutput:
    int_output: int
    str_output: str


@strawberry.input
class StarClassificationInput:
    objID: float
    alpha: float
    delta: float
    u: float
    g: float
    r: float
    i: float
    z: float
    runID: int
    camCol: int
    fieldID: int
    specObjID: float
    redshift: float
    plate: int
    MJD: int
    fiberID: int


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Star Classification GraphQL API is running!"
        
    @strawberry.field
    def api_info(self) -> str:
        return "GraphQL endpoint for star classification. Use the 'predict' mutation to classify stars."


@strawberry.type
class Mutation:
    @strawberry.field
    def predict(self, features: StarClassificationInput) -> StarClassificationOutput:
        """
        GraphQL mutation for classifying stars.
        
        Takes star features and returns classification result.
        """
        # Check for model updates
        check_model()
        
        # Convert input to dictionary
        features_dict = {
            'obj_ID': features.objID,
            'alpha': features.alpha,
            'delta': features.delta,
            'u': features.u,
            'g': features.g,
            'r': features.r,
            'i': features.i,
            'z': features.z,
            'run_ID': features.runID,
            'cam_col': features.camCol,
            'field_ID': features.fieldID,
            'spec_obj_ID': features.specObjID,
            'redshift': features.redshift,
            'plate': features.plate,
            'MJD': features.MJD,
            'fiber_ID': features.fiberID
        }
        
        # Extract features and convert them into a list
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
        return StarClassificationOutput(
            int_output=int(prediction[0]),
            str_output=str_pred
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)