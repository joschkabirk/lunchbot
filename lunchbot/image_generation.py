"""Image generation stuff."""

import base64
import io
import logging

import requests
from openai import OpenAI
from PIL import Image

logger = logging.getLogger(__name__)

FALLBACK_IMAGE_URL = "https://syncandshare.desy.de/index.php/s/QRHbNjEPB39FF55/download?path=lunchbot_assets&files=technical_difficulties.JPG"


def generate_image_openai(
    prompt,
    save_path,
    model="gpt-image-1-mini",
    size="1024x1024",
    quality="medium",
    resize_to=512,
):
    """Generate an image based on a prompt and save it to disk.

    The gpt-image-1 model returns base64-encoded image data (not a URL like
    DALL-E did), so the image is decoded, optionally downscaled, and written
    to ``save_path``.

    Parameters
    ----------
    prompt : str
        The prompt to generate an image for.
    save_path : str
        Path the generated image will be written to.
    model : str
        The model to use for generating the image. Defaults to "gpt-image-1-mini".
    size : str
        The size requested from the API. Defaults to "1024x1024".
    quality : str
        Rendering quality for gpt-image-1 models. One of "low", "medium",
        "high", or "auto". Defaults to "medium".
    resize_to : int or None
        If set, downscale the saved image to this many pixels on the longer
        edge (preserving aspect ratio). Set to None to keep the original size.
        Defaults to 512.
    """
    client = OpenAI()

    logger.info(f"Generating image (with OpenAI-API) with prompt: {prompt}")

    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )
        image_bytes = base64.b64decode(response.data[0].b64_json)
        image = Image.open(io.BytesIO(image_bytes))
        if resize_to is not None:
            image.thumbnail((resize_to, resize_to), Image.LANCZOS)
        image.convert("RGB").save(save_path, format="JPEG", quality=85, optimize=True)
        logger.info(f"Image generated successfully. Saved to {save_path}.")
    except Exception as e:
        logger.error(f"Exception raised during image generation: {e}")
        logger.info(f"Falling back to default image at {FALLBACK_IMAGE_URL}")
        fallback = requests.get(FALLBACK_IMAGE_URL, timeout=60)
        with open(save_path, "wb") as f:
            f.write(fallback.content)


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
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        return response.content

    add_prompt = "Generate a realistic looking image based on the following prompt: "

    image_bytes = query({"inputs": add_prompt + prompt})
    image = Image.open(io.BytesIO(image_bytes))
    logger.info(f"Image generated successfully. Saving to {save_path}.")
    image.save(save_path)
