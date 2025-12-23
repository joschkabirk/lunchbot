FROM python:3.11.14-trixie

USER root

RUN apt update && apt install -y python3 python3-pip zsh git curl wget vim

WORKDIR /lunchbot
COPY requirements.txt .

# Create venv, activate it, and install requirements
ENV VIRTUAL_ENV=/lunchbot_venv
RUN pip install --upgrade pip
RUN python3 -m venv $VIRTUAL_ENV && \
    . $VIRTUAL_ENV/bin/activate && \
    pip install -r requirements.txt

# Add the virtual environment's bin directory to the PATH
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
