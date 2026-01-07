# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose the port (FastAPI/Uvicorn standard)
EXPOSE 8000

# Command to run the agent
CMD ["python", "demo_server.py"]
