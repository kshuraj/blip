import traceback

from src.extensions import model_pipeline
from src.pipelines.model_pipeline import RequiredInput
from src.pipelines.pipeline_base import as_form

from datetime import datetime
from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse


# Add decorator to the request body model
# Required to allow using same model class for json and multipart/form-data
# requests.
RequiredInput = as_form(RequiredInput)      # DO NOT REMOVE THIS


router = APIRouter(prefix="/api/v1")

@router.get('/config/{config_type}')
def get_config(config_type: str, model_category: str, input_type: str = 'text', output_type: str = None):
    if config_type == 'io':
        model_config = model_pipeline.io_config(model_category, input_type=input_type, output_type=output_type, default=None)
    elif config_type == 'model':
        model_config = model_pipeline.model_config(model_category)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'msg': 'Unsupported config type'})
    print("Fetching config")
    return JSONResponse(status_code=status.HTTP_200_OK, content=model_config)


@router.post('/run')
async def run_model(request_id:str, model_category: str, user_input: RequiredInput):
    print(f"User Input >> {user_input} for Request_id = {request_id}")
    print("-------------- User Config --------------")
    print(f"Model Name: {model_category}")
    print(f"User Input: {user_input.dict()}")
    user_input = user_input.dict()

    model_pipeline.model_category = model_category
    model_pipeline.request_id = request_id
    
    try:
        # Make prediction based on the input
        # async with model_pipeline as call_pipeline:
        results = await model_pipeline.run_pipeline(**user_input)
        print("================== PREDICTION ==================")
        print(results)

        return {
            'status': 'SUCCESS',
            'prediction': results
        }, 200
    except Exception as e:
        print(f"[!] Unable to predict. \n[Error] -> {e}")
        print(traceback.format_exc())
        
        return {
            'status': 'FAIL',
            'msg': 'Unable to predict. Please check the request parameters.'
        }, 500


# TODO:
# Find a better solution than repeating code for different input types.
# We can not process json and file in same request - http limitation, so we 
# have to create a separate endpoint to handle multipart/form-data.
@router.post('/run/img')
async def run_model_image_ip(request_id:str, model_category: str, image: UploadFile = File(...), user_input: RequiredInput = Depends(RequiredInput.as_form)):
    print("Request to run model with image input received.")
    user_input = user_input.dict()
    user_input['image'] = image

    model_pipeline.model_category = model_category 
    model_pipeline.request_id = request_id
    
    try:
        # Make prediction based on the input
        # async with model_pipeline as call_pipeline:
        results = await model_pipeline.run_pipeline(**user_input)
        print("================== PREDICTION ==================")
        print(results)

        return {
            'status': 'SUCCESS',
            'prediction': results
        }, 200
    except Exception as e:
        print(f"[!] Unable to predict. \n[Error] -> {e}")
        print(traceback.format_exc())
        
        return {
            'status': 'FAIL',
            'msg': 'Unable to predict. Please check the request parameters.'
        }, 500