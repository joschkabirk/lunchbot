FROM selenium/standalone-chrome

USER root

RUN apt update && apt install -y python3 python3-pip zsh git curl wget vim

WORKDIR /app
COPY requirements.txt .

# create venv, activate it, and install requirements
RUN apt-get update && apt-get install -y python3-venv
RUN python3 -m venv venv_container && \
    . venv_container/bin/activate && \
    pip install -r requirements.txt

COPY . .
RUN chmod +x ./scripts/run_website.sh

CMD ["./scripts/run_website.sh"]
