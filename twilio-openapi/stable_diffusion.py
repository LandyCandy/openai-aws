import os
import io
import warnings
import datetime
import boto3
from botocore.exceptions import ClientError
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

def generate_image(prompt, clip_flag):
    # Our Host URL should not be prepended with "https" nor should it have a trailing slash.
    os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'

    # Sign up for an account at the following link to get an API Key.
    # https://beta.dreamstudio.ai/membership

    # Click on the following link once you have created an account to be taken to your API Key.
    # https://beta.dreamstudio.ai/membership?tab=apiKeys

    s3 = boto3.client('s3')

    # Set up our connection to the API.
    stability_api = client.StabilityInference(
        key=os.environ['STABILITY_KEY'], # API Key reference.
        verbose=True, # Print debug messages.
        engine="stable-diffusion-v1-5", # Set the engine to use for generation. 
        # Available engines: stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0 
        # stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-inpainting-v1-0 stable-inpainting-512-v2-0
    )

    input_clip = {
        'prompt': prompt,
        'steps': 30, # Amount of inference steps performed on image generation. Defaults to 30. 
        'cfg_scale' :8.0, # Influences how strongly your generation is guided to match your prompt.
                    # Setting this value higher increases the strength in which it tries to match your prompt.
                    # Defaults to 7.0 if not specified.
        'width': 512, # Generation width, defaults to 512 if not included.
        'height': 512, # Generation height, defaults to 512 if not included.
        'samples': 1, # Number of images to generate, defaults to 1 if not included.
        # sampler=generation.SAMPLER_K_DPMPP_2M,
        'sampler': generation.SAMPLER_K_DPMPP_2S_ANCESTRAL, 
                                                    # Choose which sampler we want to denoise our generation with.
                                                    # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
                                                    # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m)
        'guidance_preset': generation.GUIDANCE_PRESET_FAST_GREEN
    }

    input_sampler = {
        'prompt': prompt,
        'steps': 30, # Amount of inference steps performed on image generation. Defaults to 30. 
        'cfg_scale' :8.0, # Influences how strongly your generation is guided to match your prompt.
                    # Setting this value higher increases the strength in which it tries to match your prompt.
                    # Defaults to 7.0 if not specified.
        'width': 512, # Generation width, defaults to 512 if not included.
        'height': 512, # Generation height, defaults to 512 if not included.
        'samples': 1, # Number of images to generate, defaults to 1 if not included.
        'sampler' : generation.SAMPLER_K_DPMPP_2M
        # 'sampler': generation.SAMPLER_K_DPMPP_2S_ANCESTRAL, 
                                                    # Choose which sampler we want to denoise our generation with.
                                                    # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
                                                    # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m)
        # 'guidance_preset': generation.GUIDANCE_PRESET_FAST_GREEN
    }

    # Set up our initial generation parameters.
    if clip_flag:
        answers = stability_api.generate(**input_clip)
    else:
        answers = stability_api.generate(**input_sampler)

    # Set up our warning to print to the console if the adult content classifier is tripped.
    # If adult content classifier is not tripped, save generated images.
    for resp in answers:
        for artifact in resp.artifacts:
            key = "stable-diffusion-images/" + str(artifact.seed) + "-" + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + ".png"
            if artifact.finish_reason == generation.FILTER:
                raise Exception("Your request activated the API's safety filters and could not be processed.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                # Upload image to s3
                img = io.BytesIO(artifact.binary)
                out = s3.upload_fileobj(
                    img,
                    "myshitbucket",
                    key,
                    ExtraArgs={
                        'ACL': 'public-read',
                        'ContentType': 'image/png'
                    }
                )

                return "https://%s.s3.amazonaws.com/%s" % ("myshitbucket", key)

if __name__ == "__main__":
    generate_image("expansive nightscape of an advanced city with many warmachines fighting brutally in the foreground, artstation, masterful, dali")