import os

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.extensions import model_pipeline
from src.model import controller as model_apis

app = FastAPI()

def prepare_model():
    """
    Search and load the model before exposing model api.
    """
    print("Preparing model...")
    try:
        model_pipeline.prepare_pipeline()
    except Exception as e:
        print("[!] Could not prepare environment.")
        print(str(e))
        raise Exception(str(e))


prepare_model()

app.include_router(model_apis.router)