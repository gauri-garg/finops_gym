# 1. Use Python 3.10 as it's the most stable for openenv-core and Pydantic V2
FROM python:3.10-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 3. Create a non-root user (Hugging Face requirement for many advanced features)
RUN useradd -m -u 1000 user
USER user
WORKDIR /app

# 4. Copy and install requirements first (to leverage Docker cache)
# We use --user to install in the user's home directory
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 5. Copy the rest of the application files
# The --chown=user ensures your code has permission to write logs if needed
COPY --chown=user . .

# 6. Expose the standard HF port
EXPOSE 7860

# 7. Start the application
# We use the full path to uvicorn to ensure the 'user' can find it
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]