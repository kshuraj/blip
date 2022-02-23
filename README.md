# Z2AI Model Service Boilerplate
A boilerplate for implementing model service

### Pre-requisites
1. Python3.7+
2. Python virtual env (app should be developed inside virtual env)
3. Docker 19+

### How to create your service
##### Defining model service
Your code will go inside `src/pipelines/model_pipeline.py`. Split your code in two methods,
1. `prepare_pipeline()`
2. `run_pipeline()`<br>
Both these methods are required and so are enforced by the boilerplate.<br>
`prepare_pipeline()` method should define instructions that setups the model before the model inference. Meaning the method definition should consist of instructions that takes long time and are required only once during the lifetime of the service.

##### Define configuration
Define your model's basic details by setting the `pipeline_config` variable inside `src/pipelines/model_pipeline.py` (instructions provided in the py file).<br>
Your `pipeline_config` variable should be consist of following details,
```py3
pipeline_config = {
            'family': '<language|vision|...>',
            'branch': [
                {
                    'name': '<MODEL_NAME>',
                    'default': {
                        'input': '<DEFAULT_INPUT_TYPE (text|image|voice|...)>',
                        'output': '<DEFAULT_OUTPUT_TYPE (text|image|voice|...)>'
                    },
                    'request_body': {},
                    'input_types': ['<LIST_OF_SUPPORTED_INPUT_TYPES>'],
                    'output_types': ['<LIST_OF_SUPPORTED_OUTPUT_TYPES>']
                }
            ],
        }

# Example config
# pipeline_config = {
#             'family': 'vision',
#             'branch': [
#                 {
#                     'name': 'DallEmini',
#                     'default': {
#                         'input': 'text',
#                         'output': 'image'
#                     },
#                     'request_body': {},
#                     'input_types': ['text'],
#                     'output_types': ['image']
#                 }
#             ],
#         }
```
<br>
Same goes for the input/output components. You need to define your input output components for our interface to work with your model service.<br>
To define i/o components config, set `components_config` variable in 
`src/pipelines/model_pipeline.py` (instructions provided in the py file).

```py3
components_config = {
            '<MODEL_NAME_SAME_AS_ABOVE>': {
                'input': {
                    '<text|image|voice|...>': [
                        { 
                            'input_type': '<text|image|voice|...>', 
                            'label': 'Input',  
                            'default': None,
                            'c_id': 'input_1'   # Same as RequiredInput for each input
                        },
                        ... # Any additional input types
                    ]
                },
                'output': {
                    '<text|image|voice|...>': [
                        {
                            'output_type': '<text|image|voice|...>', 
                            'label': 'Output'
                        },
                        ... # Any additional output types
                    ]
                }
            }
        }

# Example
# components_config = {
#             'DallEmini': {
#                 'input': {
#                     'text': [
#                         { 'input_type': 'text', 'label': 'Input',  'default': None, 'c_id': 'input' },
#                         { 'input_type': 'slider', 'minimum': 0, 'maximum':  10, 'step': 1, 'default': 3, 'label': 'Quality', 'c_id': 'quality' }
#                     ]
#                 },
#                 'output': {
#                     'image': [
#                         { 'output_type': 'image', 'type': 'auto', 'label': 'Output' }
#                     ]
#                 }
#             }
#         }
```
For input and output config, additional key value pairs can be reference from [Gradio Docs](https://gradio.app/docs/).
Some parameters for input and output components are required as stated in the Gradio's doc or should comply with what your service requires for input and output.


### Start the app
From app's root directory
```sh
$ uvicorn run:app --reload 
```

### Test
After implemetation of model service, make sure it passes unit tests. To start tests run the following commands
```sh
$ pytest
```
Note: Make sure the app is running.


### Add dependencies
To add any dependencies or artefacts, create a `install.sh` inside `assets/scripts` folder.<br>
Add instructions to setup dependencies or download artefacts required by your service.

### Build
To package your code into a docker image run the following command
```sh
# For local
docker build -t dev/z2ai:ms_<MODEL_NAME_WITH_NO_SPACES>_<VERSION> .
```
If you have any files or directories that will be created on runtime and are not supposed to be included in the image, list them in the `.dockerignore` file.

### Deploy
`Note` Before you deploy make sure the application passes all the tests.<br>
The application's docker image is required to be deployed to make the model available on the app. `The image should be pushed on Z2AI's hosted repository only.`

```sh
# Instructions will be updated soon
```