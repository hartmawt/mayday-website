# Use the official Python image from the Docker Hub, specifying version 3.11-slim
FROM python:3.11-slim

# Install UV, a fast Python package installer and resolver
RUN pip install uv

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the UV configuration files to the working directory
COPY pyproject.toml uv.lock README.md ./

# Install system dependencies if necessary
# Here we install git as it is required by the Python code
RUN apt-get update && apt-get install -y pandoc && apt-get install -y chromium

# Install the project dependencies using UV
RUN uv sync --frozen

# Install chromium dependencies
RUN uv run python -m playwright install chromium

# Copy the rest of the application code to the working directory
COPY /static static
COPY /templates templates
COPY /mayday mayday
COPY app.py app.py

# Ensure the static directory has proper permissions for file uploads
RUN chmod -R 755 /app/static

# Run the application
CMD ["uv", "run", "python", "app.py"]