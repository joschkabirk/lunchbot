# lunchbot

Bot that scrapes the daily lunch menus from the DESY canteen (Alsterfood) and
Cafe CFEL, generates AI preview images for each dish, and posts everything as a
formatted table to a Mattermost channel.

**Example**:

<img src="https://syncandshare.desy.de/public.php/dav/files/EbaHq5W8zof5SPH/?accept=zip">

Each execution scrapes the menu, generates images (skipping dishes that already
have a cached image in the cloud), uploads them, and posts a single message.
To run the bot periodically, use e.g. `cron`.

<img width=600px src=assets/lunchbot.excalidraw.svg>

## Usage

### Requirements

Install [uv](https://docs.astral.sh/uv/getting-started/installation/):

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Configuration

Create a `.env` file in the project root. All variables are listed below:

#### Image generation

| Variable                | Required        | Description                                                                                                                   |
| ----------------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `API_TO_USE`            | yes             | Which image generation backend to use: `"openai"` or `"huggingface"`                                                          |
| `OPENAI_API_KEY`        | if using OpenAI | Your OpenAI API key                                                                                                           |
| `HUGGINGFACE_API_URL`   | if using HF     | HF Inference API endpoint, e.g. `https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell`          |
| `HUGGINGFACE_API_TOKEN` | if using HF     | Your Hugging Face API token                                                                                                   |
| `IMAGE_PROMPT_PREFIX`   | no              | Style prefix prepended to every image prompt for consistent visuals (e.g. `"Professional food photography, overhead shot: "`) |
| `USE_OPENAI_IMAGE_URL`  | no              | If `"true"`, use the temporary OpenAI image URL directly instead of uploading to the cloud (expires after 1 hour)             |

#### Menu sources

| Variable                 | Required | Description                                  |
| ------------------------ | -------- | -------------------------------------------- |
| `ALSTERFOOD_WEBSITE_URL` | yes      | URL of the DESY Alsterfood canteen menu page |
| `CFEL_WEBSITE_URL`       | no       | URL of the Cafe CFEL menu page (iMensa)      |

#### Image cloud storage

Images are uploaded to a WebDAV-compatible cloud so they remain available
indefinitely. Not needed if `USE_OPENAI_IMAGE_URL="true"`.

| Variable                   | Required | Description                                      |
| -------------------------- | -------- | ------------------------------------------------ |
| `IMAGE_CLOUD_UPLOAD_URL`   | yes\*    | WebDAV upload base URL                           |
| `IMAGE_CLOUD_UPLOAD_TOKEN` | yes\*    | Credentials for the upload (`user:password`)     |
| `IMAGE_CLOUD_DOWNLOAD_URL` | yes\*    | Public download base URL for the uploaded images |

#### Mattermost

| Variable                       | Required | Description                                                       |
| ------------------------------ | -------- | ----------------------------------------------------------------- |
| `MATTERMOST_WEBHOOK_URL`       | yes      | Incoming webhook URL for posting the daily menu                   |
| `MATTERMOST_WEBHOOK_URL_ALERT` | no       | Separate webhook URL for error alerts                             |
| `MATTERMOST_USERNAME`          | no       | Display name for the bot (default: `"Lunchbot"`)                  |
| `ALERT_PREFIX`                 | no       | Text prepended to error alert messages (e.g. `"ALERT @someone "`) |

#### Message content

| Variable                                    | Required | Description                                             |
| ------------------------------------------- | -------- | ------------------------------------------------------- |
| `MESSAGE_PREFIX`                            | no       | Text prepended to the daily message                     |
| `MESSAGE_SUFFIX_MON` … `MESSAGE_SUFFIX_SUN` | no       | Day-specific suffix appended to the message             |
| `SYSTEM_CONTENT`                            | no       | System prompt used for AI-generated dish descriptions   |
| `DESCRIPTION_SUFFIX`                        | no       | Suffix appended after "Description" in the table header |

For different messages in even/odd weeks, use `MESSAGE_SUFFIX_MON_EVEN`,
`MESSAGE_SUFFIX_MON_ODD`, etc. These take precedence over the base day suffix
when set.

#### Other

| Variable   | Required | Description                                              |
| ---------- | -------- | -------------------------------------------------------- |
| `HOSTNAME` | no       | Identifier logged at startup (default: `"unknown_host"`) |

### Run the bot

```shell
uv run scripts/run_lunchbot.py
```

This runs the bot once. Use `cron` or a similar scheduler to run it daily.

### Run with Docker

```shell
docker build -t lunchbot .
docker run -it --env-file .env lunchbot uv run scripts/run_lunchbot.py
```

### Development

```shell
uv sync --dev
uv run pre-commit install
```
