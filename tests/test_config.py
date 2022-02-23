from src.pipelines.model_pipeline import ModelPipeline
from src.pipelines.schemas import ModelConfigSchema, ModelIOConfigSchema

def test_model_config():
    print("Validating model config schema...")
    schema_passed: bool = False

    try:
        ModelConfigSchema(**ModelPipeline.pipeline_config)
        schema_passed = True
    except Exception as e:
        raise Exception(e)

    assert schema_passed == True


def test_model_io_config():
    print("Validating model io components config schema...")
    schema_passed: bool = False

    # We will get the mdel config and test the io schema for each branch.
    branches = ModelPipeline.pipeline_config['branch']

    for branch in branches:
        model_name = branch['name']
        schema_passed = False
        try:
            print(f"\tChecking for branch: {model_name}")
            ModelIOConfigSchema(**ModelPipeline.components_config[model_name])
            schema_passed = True
        except Exception as e:
            raise Exception(e)

        assert schema_passed == True