import os

import requests

MATTERMOST_WEBHOOK_URL = os.getenv("MATTERMOST_WEBHOOK_URL")
ALSTERFOOD_WEBSITE_URL = os.getenv("ALSTERFOOD_WEBSITE_URL")
IMAGE_URL = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-Q9Rj5vhxAlToLRKA1ArxsFPb/user-3wIkLqTRO6pY44iwB89vGS34/img-5Z3RFrZgJwdENFP2Za33DoAl.png?st=2023-12-09T15%3A41%3A53Z&se=2023-12-09T17%3A41%3A53Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-12-08T23%3A13%3A02Z&ske=2023-12-09T23%3A13%3A02Z&sks=b&skv=2021-08-06&sig=bqSjVm52XHAoMzcDEbiqvjd1enrdVSzJewY/Iz6vSE4%3D"


def send_message(
    url: str,
    message: str,
    props: dict = None,
    username: str = "Lunchbot (always hungry)",
):
    r = requests.post(
        url,
        json={
            "username": username,
            "text": message,
            "props": props,
        },
    )
    assert r.status_code == 200
    return r


if __name__ == "__main__":
    # TODO: Replace this with the actual meals of the day and their descriptions
    # and images
    meals_of_the_day = [
        "Spaghetti Bolognese (Pork/Beef) with Gouda shavings",
        "Vegan Peanut Vegetable Curry with Coconut Milk and Basmati Rice",
    ]
    descriptions = [
        "This spaghetti bolognese is made with pork and beef and is served with gouda shavings. The first bite will make you feel like you're in Italy!",
        "This vegan peanut vegetable curry is made with coconut milk and basmati rice. The wide range of vegetables will make you feel like you're in a tropical paradise!",
    ]
    images = [
        IMAGE_URL,
        IMAGE_URL,
    ]

    prefix = f"For today, we have the following meals ({ALSTERFOOD_WEBSITE_URL}):"

    # Generate markdown table
    table = "| Preview | Meal | Description | \n| --- | --- | --- |\n"
    for meal, desc, img_url in zip(meals_of_the_day, descriptions, images):
        table += f"| ![preview]({img_url}) | **{meal}**  | {desc}| \n"

    message = prefix + "\n\n" + table

    print(message)

    send_message(
        url=MATTERMOST_WEBHOOK_URL,
        message=message,
        props=None,
        username="Lunchbot (always hungry)",
    )
