FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy your application code to the container
COPY . .

# Expose port for FastAPI (default port is 8000)
EXPOSE 8000

# Run FastAPI app with uvicorn
CMD ["uvicorn", "entrypoint:app", "--host", "0.0.0.0", "--reload"]

