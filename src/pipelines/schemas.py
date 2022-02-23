"""
Define and validate schemas.
"""
from typing import Dict, List
from typing_extensions import TypedDict
from pydantic import BaseModel


class ModelBranchDefaults(TypedDict):
    input: str
    output: str

class ModelBranchSchema(BaseModel):
    name: str
    default: ModelBranchDefaults
    request_body: dict
    input_types: List[str]
    output_types: List[str]

class ModelConfigSchema(BaseModel):
    """
    For basic information of the model.
    """
    family: str
    branch: List[ModelBranchSchema]


class ModelInputParametersSchema(TypedDict):
    input_type: str
    label: str


class ModelOutputParametersSchema(TypedDict):
    output_type: str
    label: str


class ModelInputSchema(TypedDict):
    __root__: List[ModelInputParametersSchema]


class ModelOutputSchema(TypedDict):
    __root__: List[ModelOutputParametersSchema]


class ModelIOConfigSchema(BaseModel):
    """
    For i/o components of the model.
    """
    input: Dict[str, List[ModelInputParametersSchema]]
    output: Dict[str, List[ModelOutputParametersSchema]]