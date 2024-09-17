"""Utils for lunchbot."""

import logging

from openai import OpenAI
import hashlib

logger = logging.getLogger(__name__)


def translate_german_food_description_to_english(
    meal_name: str,
    return_prompt_answer: bool = False,
    system_content: str = None,
):
    """Translate a German food description to English.

    Parameters
    ----------
    meal_name : str
        The name of the meal in German.
    return_prompt_answer : bool, optional
        Whether to return the prompt and the answer, by default False
    system_content : str, optional
        The system content to use for the prompt, by default None

    Returns
    -------
    str or tuple
        The answer or a tuple of the prompt and the answer (if return_prompt_answer=True).
    """

    client = OpenAI()

    if system_content is None:
        system_content = (
            "You are a translator. Be sure to keep the meaning of the text. "
        )

    prompt = meal_name + " - please translate this from german to english."

    logger.info(f"Prompt: {prompt}")
    logger.info(f"System Content: {system_content}")

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ],
    )

    response = completion.choices[0].message.content

    if return_prompt_answer:
        return prompt, response

    return response


def generate_hash(input_string: str):
    """Get the first 20 characters of the SHA256 hash of a string."""
    return hashlib.sha256(input_string.encode()).hexdigest()[:20]
