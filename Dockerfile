FROM python:3.12-slim

WORKDIR /app

# Install system tools needed to download and extract the ML model
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create model directory
RUN mkdir -p /app/data/models

# Download trained Random Forest model
RUN curl -L \
    -o /tmp/trained-pm25-model.zip \
    https://github.com/mayankmajoka2000-tech/india-air-pollution-intelligence-api/releases/download/v5.1.0-model/trained-pm25-model.zip \
    && unzip -o /tmp/trained-pm25-model.zip \
    -d /app/data/models \
    && rm /tmp/trained-pm25-model.zip

# API port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
