FROM python:3.11-slim

RUN mkdir /walk-chat

WORKDIR /walk-chat

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x /walk-chat/docker/*.sh
