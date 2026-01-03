# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the port (Render/Railway use the PORT env var, but 8000 is default)
EXPOSE 8000

# Run the application
CMD ["python", "demo_server.py"]
