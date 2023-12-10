# lunchbot

Bot that extracts the lunch menu from the DESY canteen website and posts a message in
a dedicated Mattermost channel.

## Usage

### Requirements

The easiest way to run this bot is to use the dedicated Docker image.
The image is available on [Docker Hub at jobirk/lunchbot](https://hub.docker.com/r/jobirk/lunchbot).

Furthermore, you have to set the following environment variables in a `.env` file:

```shell
ALSTERFOOD_WEBSITE_URL="https://desy.myalsterfood.de/"
OPENAI_API_KEY="<your OpenAI API key>"
MATTERMOST_WEBHOOK_URL="<your Mattermost webhook URL>"
IMAGE_CLOUD_UPLOAD_URL="<your image cloud upload URL>"
IMAGE_CLOUD_UPLOAD_TOKEN="<your image cloud upload token>"
IMAGE_CLOUD_DOWNLOAD_URL="<your image cloud download URL>"
```

### Run the bot

Inside the container (and repo), just run:

```shell
python scripts/run_lunchbot.py
```

This will run the bot once. To run it periodically, just use e.g. `cron` to run the script
every day at a specific time.
