# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml file into the container
COPY pyproject.toml ./

# Generate poetry.lock file if it doesn't exist and install dependencies
RUN poetry install --no-dev || poetry lock && poetry install --no-dev

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the Flask app runs on
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Command to run the Flask application
CMD ["poetry", "run", "flask", "run"]
