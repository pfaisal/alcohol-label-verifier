# Use a small Python image
FROM python:3.11-slim

# Install system packages, including Tesseract OCR
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency list and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose port (Render will still use $PORT)
EXPOSE 8000

# Start the FastAPI app using uvicorn
# $PORT is provided by Render
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
