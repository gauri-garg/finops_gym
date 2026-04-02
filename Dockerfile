# Use a lightweight python image
FROM python:3.10-slim

# Set environment variables for non-interactive installs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies first (for faster rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose the HF Space default port
EXPOSE 7860

# Command to run the FastAPI server
# We use uvicorn to serve the 'app' from main.py (we will create this next)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]