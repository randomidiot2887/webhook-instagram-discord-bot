FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY instabot.py discordbot.py webhook_server.py ./

EXPOSE 5000

CMD ["python", "webhook_server.py"]