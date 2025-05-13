FROM python:3.12-slim

# Install OS-level dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port Railway expects
EXPOSE 8080

# Start Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
