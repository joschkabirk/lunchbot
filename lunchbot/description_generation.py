from openai import OpenAI


def get_food_description(meal_name, verbose=False):
    """Generate a description for a meal based on a prompt.

    Parameters
    ----------
    meal_name : str
        The name of the meal to generate a description for.
    """

    client = OpenAI()

    prompt = meal_name + " - please describe this meal in two sentences."

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a five star chef. You know how to describe food. But don't start always with 'Indulge in ...'",
            },
            {"role": "user", "content": prompt},
        ],
    )

    response = completion.choices[0].message.content

    if verbose:
        print("Prompt:", prompt)
        print("Response:", response)

    return response
