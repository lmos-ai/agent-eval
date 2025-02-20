# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache if they don't change
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# (Optional) Set the Flask application entry point if needed
# ENV FLASK_APP=app.py

# Expose the port that the Flask app runs on
EXPOSE 5000

# Note: the .env file is expected to be in the project root.
# For security reasons, you might prefer passing env variables at runtime:
#   docker run --env-file .env -p 5000:5000 <your-image>

# Run the Flask application with reload enabled and listening on all interfaces
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]
