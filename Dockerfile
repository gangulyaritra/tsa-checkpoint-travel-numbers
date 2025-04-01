FROM python:3.11.11-slim-bullseye
RUN apt-get update -y && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
RUN pip install --upgrade pip && pip install .
CMD ["/bin/sh"]