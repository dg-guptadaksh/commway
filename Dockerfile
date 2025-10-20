# Dockerfile

# 1. Base Image: Use a slim Python image for a smaller final container size
FROM python:3.11-slim

# 2. Set environment variables
# Disables buffering for easier logging in containers
ENV PYTHONUNBUFFERED 1 
# Set the working directory
WORKDIR /app

# 3. Install dependencies
# Copy requirements first to leverage Docker layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application code
COPY . /app/

# 5. Expose the port Uvicorn runs on
EXPOSE 8000

# 6. Define the command to run the application
# This command initializes the DB (via the init_db() call in api.py) and starts the server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]