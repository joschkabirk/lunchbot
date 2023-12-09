from openai import OpenAI


def generate_images_with_dalle(prompt):
    client = OpenAI()

    response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size="256x256",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url

    return image_url


if __name__ == "__main__":
    # Replace the prompts with your actual list of menu entries
    menu_entries = [
        "Spaghetti Bolognese",
        # "Pizza Salami",
    ]

    # Convert the list of menu entries to a string
    prompt = "\n".join(menu_entries)

    # Generate an image with DALL-E based on the menu entries
    for menu_entry in menu_entries:
        generated_image_url = generate_images_with_dalle(prompt)
        # Print the URL of the generated image
        print(f"Generated Image URL: {generated_image_url}")
