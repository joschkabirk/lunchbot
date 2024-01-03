# lunchbot

Bot that extracts the lunch menu from the DESY canteen website and posts a message in
a dedicated Mattermost channel.

**Example**:

<img src="https://syncandshare.desy.de/index.php/s/QRHbNjEPB39FF55/download?path=lunchbot_assets&files=lunchbot_message_example.png" width=600px style="border-radius:10px">

At the moment, this implementation is designed to represent only one execution of
the bot. To run it periodically, use e.g. `cron`.

Overall, the whole setup is kinda DESY-specific due to the fact that the
DESY Sync&Share is used to store the menu preview images.

<img src=assets/lunchbot.excalidraw.svg width=500px style="border-radius:10px">

## Usage

### Requirements

The easiest way to run this bot is to use the dedicated Docker image.
The image is available on [Docker Hub at `jobirk/lunchbot`](https://hub.docker.com/r/jobirk/lunchbot).

Furthermore, you have to set the following environment variables in a `.env` file:

```shell
ALSTERFOOD_WEBSITE_URL="https://desy.myalsterfood.de/"
OPENAI_API_KEY="<your OpenAI API key>"
MATTERMOST_WEBHOOK_URL="<your Mattermost webhook URL>"
USE_OPENAI_IMAGES_URL="<if set to 'true', the bot will use the OpenAI image API to generate images (which expire after 1 hour)>"
IMAGE_CLOUD_UPLOAD_URL="<your image cloud upload URL>"
IMAGE_CLOUD_UPLOAD_TOKEN="<your image cloud upload token>"
IMAGE_CLOUD_DOWNLOAD_URL="<your image cloud download URL>"
MESSAGE_PREFIX="<your message prefix>"
MESSAGE_SUFFIX="<your message suffix>"
MATTERMOST_USERNAME="<username displayed for the bot>"
SYSTEM_CONTENT="<description of the system that describes the food>"
DESCRIPTION_SUFFIX="<suffix to put after "Description" in the table header>"
```

### Run the bot

Inside the container (and repo), just run:

```shell
python scripts/run_lunchbot.py
```

This will run the bot once. To run it periodically, just use e.g. `cron` to run the script
every day at a specific time.
