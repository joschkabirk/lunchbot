"""Image generation stuff."""

import io
import logging

import requests
from openai import OpenAI
from PIL import Image

logger = logging.getLogger(__name__)


def generate_image_huggingface(
    prompt,
    api_token,
    api_url,
    save_path="image.jpg",
):
    """Generate an image using the huggingface api.

    Parameters
    ----------
    prompt : str
        The prompt to generate an image for.
    api_token : str
        The API token to use for the request.
    api_url : str
        The URL of the API to use for the request.
    save_path : str
        The path to save the generated image to. Defaults to "image.jpg".
    """
    headers = {"Authorization": f"Bearer {api_token}"}

    logger.info(f"Generating image (with huggingface-api) with prompt: {prompt}")

    def query(payload):
        response = requests.post(api_url, headers=headers, json=payload)
        return response.content

    add_prompt = "Generate a realistic looking image based on the following prompt: "

    image_bytes = query({"inputs": add_prompt + prompt})
    image = Image.open(io.BytesIO(image_bytes))
    logger.info(f"Image generated successfully. Saving to {save_path}.")
    image.save(save_path)


def generate_image_openai(
    prompt,
    model="dall-e-2",
    size="256x256",
):
    """Generate images with DALL-E based on a prompt.

    Parameters
    ----------
    prompt : str
        The prompt to generate an image for.
    model : str
        The model to use for generating the image. Defaults to "dall-e-2".
    size : str
        The size of the generated image. Defaults to "256x256".

    Returns
    -------
    str
        The URL of the generated image. If an error occurs, a default image URL is returned.
    """
    client = OpenAI()

    logger.info(f"Generating image (with OpenAI-API) with prompt: {prompt}")

    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            n=1,
        )
        image_url = response.data[0].url
    except Exception as e:
        print(f"Exception raised during image generation: {e}")
        image_url = "https://syncandshare.desy.de/index.php/s/QRHbNjEPB39FF55/download?path=lunchbot_assets&files=technical_difficulties.JPG"

    return image_url
