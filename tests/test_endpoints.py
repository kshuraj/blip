from src.pipelines.schemas import ModelBranchSchema, ModelIOConfigSchema, ModelInputParametersSchema, ModelOutputParametersSchema
from src.pipelines.model_pipeline import ModelPipeline
from run import app
from fastapi.testclient import TestClient

client = TestClient(app)

pipeline_config = ModelPipeline.pipeline_config

def test_config_model():
    branches = pipeline_config['branch']
    schema_passed: bool = False
    for branch in branches:
        model_name = branch['name']
        print(f"\tChecking model config response for {model_name}")
        response = client.get(f'/api/v1/config/model?model_category={model_name}')
        print(f"Response: {response.text}")
        assert response.status_code == 200

        schema_passed = False
        try:
            ModelBranchSchema(**response.json())
            schema_passed = True
        except Exception as e:
            print(f"[E] -> {e}")
        assert schema_passed == True


def test_config_io():
    branches = pipeline_config['branch']
    schema_passed: bool = False
    for branch in branches:
        model_name = branch['name']
        default_input_type = branch['default']['input']
        default_output_type = branch['default']['output']
        print(f"\tChecking model config response for {model_name}")
        response = client.get(f'/api/v1/config/io?model_category={model_name}&input_type={default_input_type}&output_type={default_output_type}')
        print(f"Response: {response.text}")
        assert response.status_code == 200

        schema_passed = False
        try:
            io_config = response.json()
            # check input and output config in response
            print("\t\tChecking all the (input) parameters...")
            for input_config in io_config['input']:
                ModelInputParametersSchema(**input_config)

            print("\t\tChecking all the (output) parameters...")
            for output_config in io_config['output']:
                ModelOutputParametersSchema(**output_config)
            schema_passed = True
        except Exception as e:
            print(f"[E] -> {e}")
        assert schema_passed == True