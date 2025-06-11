FROM python:3.10-slim

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    unzip \
    curl \
    gnupg2 \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxtst6 \
    libappindicator3-1 \
    xdg-utils \
    build-essential \
    git \
    && apt-get clean

# Variáveis para Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o script unificado
WORKDIR /app
COPY main.py .

CMD ["python", "main.py"]
