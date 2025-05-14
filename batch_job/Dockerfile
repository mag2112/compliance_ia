FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    chromium chromium-driver wget unzip curl gnupg2 \
    && apt-get clean

RUN pip install --no-cache-dir -r requirements.txt

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

COPY sistemas_antigo.py .

CMD ["python", "sistemas_antigo.py"]
