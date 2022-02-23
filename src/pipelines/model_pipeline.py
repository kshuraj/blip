import sys
sys.path.append("BLIP")
import os
from datetime import datetime
from typing import overload

from src.pipelines.pipeline_base import PipelineBase

from io import BytesIO
from pydantic import BaseModel
from PIL import Image
import pathlib
import requests
import torch
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode
import gradio as gr
from models.blip import blip_decoder
from models.blip_vqa import blip_vqa


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ## IMPORTANT ##
# >>> Update this if your model expects inputs either in json format or as
#     additional parameters with file upload.
# Each filed should be declared with its appropriate input type
# Example:
# class RequiredInput(BaseModel):
#   name: str
#   last_name: str
#   age: int
class RequiredInput(BaseModel):
    model: str
    question: str
    # pass


class ModelPipelineException(Exception):
    pass


class ModelPipeline(PipelineBase):
    # ## Important ##
    # Define pipeline_config and components_config attributes
    pipeline_config = {
            'family': 'vision',
            'branch': [
                {
                    'name': 'BLIP',
                    'default': {
                        'input': 'image',
                        'output': 'text'
                    },
                    'request_body': {},
                    'input_types': ['image'],
                    'output_types': ['text']
                }
            ],
        }

    components_config = {
                'BLIP': {
                    'input': {
                        'image': 
                        [
                            {
                            'input_type': 'image',
                            'type': 'file', 
                            'label': 'UploadImage', 
                            'default': None,
                            'c_id':'image'
                            },
                            {
                            'input_type': 'radio', 
                            'default_args':[['Image Captioning',"Visual Question Answering"]], 
                            'default': 'Image Captioning', 
                            'label': 'Model',
                            'c_id':'model'
                            },
                            {
                            'input_type': 'text', 
                            'label': 'Question',
                            'default': None,
                            'c_id':'question'
                            }
                        ]
                    },
                    'output': {
                        'image': [
                            {
                                'output_type': 'image', 
                                'label': 'Output'
                            },
                        ]
                    }
                }
            }
    
    def __init__(self, *, model_category=None, request_id=None) -> None:
        self.model_category = model_category
        self.request_id = request_id
        self.transform = None
        self.transform_vq = None
        self.model_vq = None
        self.model=None

    def prepare_pipeline(self, save: bool = True, reload: bool = False) -> None:
        image_size = 384
        self.transform = transforms.Compose([
            transforms.Resize((image_size,image_size),interpolation=InterpolationMode.BICUBIC),
            transforms.ToTensor(),
            transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
            ]) 

        model_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model*_base_caption.pth'
            
        self.model = blip_decoder(pretrained=model_url, image_size=384, vit='base')
        self.model.eval()
        self.model = self.model.to(device)
        image_size_vq = 480
        self.transform_vq = transforms.Compose([
            transforms.Resize((image_size_vq,image_size_vq),interpolation=InterpolationMode.BICUBIC),
            transforms.ToTensor(),
            transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
            ]) 

        model_url_vq = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model*_vqa.pth'
            
        self.model_vq = blip_vqa(pretrained=model_url_vq, image_size=480, vit='base')
        self.model_vq.eval()
        self.model_vq = self.model_vq.to(device)
        # pass

    def read_imagefile(self, file) -> Image.Image:
        image = Image.open(BytesIO(file))
        return image

    async def run_pipeline(self, **kwargs) -> any:
        output_path = os.path.join(os.environ.get('MODEL_OUTPUT_CACHE', 'data/model_outputs'), 'BLIP', self.request_id)
        img = kwargs.get('image')
        img = self.read_imagefile(await img.read())
        img = img.convert('RGB')

        pathlib.Path(output_path).mkdir(parents=True, exist_ok=True) 
        temp_file = os.path.join(output_path, 'out.jpg')
        img.save(temp_file)

        model = kwargs.get('model')
        question = kwargs.get('question')

        if model == 'Image Captioning':
            timage = self.transform(Image.open(temp_file)).unsqueeze(0).to(device) 
            with torch.no_grad():
                caption = self.model.generate(timage, sample=False, num_beams=3, max_length=20, min_length=5)
                return 'caption: '+caption[0]

        else:
            image_vq = self.transform_vq(Image.open(temp_file)).unsqueeze(0).to(device)  
            with torch.no_grad():
                answer = self.model_vq(image_vq, question, train=False, inference='generate') 
            return  'answer: '+answer[0]
            # pass
