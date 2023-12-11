"""Image generation with DALL-E."""
import hashlib

from openai import OpenAI


def generate_hash(input_string: str):
    """Get the first 20 characters of the SHA256 hash of a string."""
    return hashlib.sha256(input_string.encode()).hexdigest()[:20]


def generate_image(
    prompt,
    model="dall-e-2",
    size="256x256",
    quality="standard",
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
    quality : str
        The quality of the generated image. Defaults to "standard".
    """
    client = OpenAI()

    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
    )
    image_url = response.data[0].url

    return image_url
