import os

from src.alsterfood_scraping import fetch_lunch_menu
from src.image_generation import generate_image
from src.mattermost_posting import send_message

DEBUG = True
ALSTERFOOD_WEBSITE_URL = os.getenv("ALSTERFOOD_WEBSITE_URL")
MATTERMOST_WEBHOOK_URL = os.getenv("MATTERMOST_WEBHOOK_URL")

debug_list_of_meals = [
    "Spaghetti Bolognese (Pork/Beef) with Gouda shavings",
    "Vegan Peanut Vegetable Curry with Coconut Milk and Basmati Rice",
]
debug_list_of_prices = [
    "€ 4.50",
    "€ 4.50",
]
debug_list_of_descriptions = [
    "This spaghetti bolognese is made with pork and beef and is served with gouda shavings. The first bite will make you feel like you're in Italy!",
    "This vegan peanut vegetable curry is made with coconut milk and basmati rice. The wide range of vegetables will make you feel like you're in a tropical paradise!",
]
debug_list_of_images = [
    "https://oaidalleapiprodscus.blob.core.windows.net/private/org-Q9Rj5vhxAlToLRKA1ArxsFPb/user-3wIkLqTRO6pY44iwB89vGS34/img-wEyVXCz1cdPfUjWI3T3he2Ek.png?st=2023-12-09T17%3A10%3A35Z&se=2023-12-09T19%3A10%3A35Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-12-08T23%3A13%3A43Z&ske=2023-12-09T23%3A13%3A43Z&sks=b&skv=2021-08-06&sig=7md/joH9I1tPhWzZ6f4YqmzXoY1FJHexuCIDUf0Z5d4%3D",
    "https://oaidalleapiprodscus.blob.core.windows.net/private/org-Q9Rj5vhxAlToLRKA1ArxsFPb/user-3wIkLqTRO6pY44iwB89vGS34/img-5Iz1SIavniWBEeGIDXGf9Wxu.png?st=2023-12-09T17%3A10%3A42Z&se=2023-12-09T19%3A10%3A42Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-12-08T23%3A12%3A49Z&ske=2023-12-09T23%3A12%3A49Z&sks=b&skv=2021-08-06&sig=BRIxAYciSC3TlzmgXfhMJ32XWV9Y1KjqoX2swR7gfwM%3D",
]


if __name__ == "__main__":
    url = ALSTERFOOD_WEBSITE_URL
    print(url)

    # Fetch the entire HTML source after rendering
    if DEBUG:
        list_of_meals = debug_list_of_meals
    else:
        list_of_meals, list_of_prices = fetch_lunch_menu(url)

    print(list_of_meals)

    if DEBUG:
        images = debug_list_of_images
    else:
        images = []
        # Generate an image with DALL-E based on the menu entries
        for menu_entry in list_of_meals:
            generated_image_url = generate_image(prompt=menu_entry)
            images.append(generated_image_url)
            # Print the URL of the generated image
            print(f"Generated Image URL: {generated_image_url}")

    # TODO: Replace this with the actual meals of the day and their descriptions
    # and images
    descriptions = debug_list_of_descriptions

    prefix = f"For today, we have the following meals ({ALSTERFOOD_WEBSITE_URL}):"

    # Generate markdown table
    table = "| Preview | Meal | Description | \n| --- | --- | --- |\n"
    for meal, desc, img_url in zip(list_of_meals, descriptions, images):
        table += f"| ![preview]({img_url}) | **{meal}**  | {desc}| \n"

    message = prefix + "\n\n" + table

    print(message)

    send_message(
        url=MATTERMOST_WEBHOOK_URL,
        message=message,
        username="Lunchbot (always hungry)",
    )
