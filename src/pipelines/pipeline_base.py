import abc
import inspect
import os

from fastapi import Form
from pydantic import BaseModel
from typing import Type

"""
To use same request model for json and multipart/form-data, we override the
model class to generate a Form equvialent.
The following code is copied from the reference link.
Ref: https://github.com/tiangolo/fastapi/issues/2387#issuecomment-731662551
"""
def as_form(cls: Type[BaseModel]):
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...))
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        print(f"[DATA]: {data}")
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls


class PipelineBase(metaclass=abc.ABCMeta):
    asset_base_path = os.environ.get('MODEL_OUTPUT_CACHE', 'data/model_output')
    
    @property
    @abc.abstractmethod
    def pipeline_config(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def components_config(self):
        raise NotImplementedError

    @property
    def base_path(self):
        return os.path.join(self.asset_base_path, self.pipeline_config['branch'][0]['name'])

    @abc.abstractmethod
    def prepare_pipeline(self, save: bool, reload: bool) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def run_pipeline(self, *kwargs) -> any:
        raise NotImplementedError

    @classmethod
    def model_config(cls, model_category: str) -> dict:
        for branch_conf in cls.pipeline_config['branch']:
            if branch_conf['name'] == model_category:
                return branch_conf
            
        return {}

    @classmethod
    def io_config(cls, model_category: str, input_type: str, output_type: str, default: bool) -> dict:
        """
        Define properties for input and output fields for each category
        supported by the pipeline.
        """
        return {
            'input': cls.components_config[model_category]['input'][input_type],
            'output': cls.components_config[model_category]['output'][output_type]
        }

    def __await__(self, **kwargs):
        return self.run_pipeline(kwargs).__await__()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return self