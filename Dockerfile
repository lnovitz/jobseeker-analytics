# Stage 1: Build dependencies in a full Python image
FROM python:3.11 as builder

WORKDIR /app

# Copy dependency files
COPY requirements.txt ./

# Create and activate virtual environment, then install dependencies
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Use slim image for runtime
FROM python:3.11-slim

WORKDIR /app

# Install necessary system libraries
RUN apt-get update && apt-get install -y \
    libpq-dev libssl-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from builder
COPY --from=builder /app/venv /app/venv

# Copy the application code
COPY . .

# Ensure the virtual environment is used
ENV PATH="/app/venv/bin:$PATH"

# Verify that Uvicorn is installed before running
RUN /app/venv/bin/uvicorn --version

# Expose the port (important for Uvicorn)
EXPOSE 8000

# Run the application
CMD ["/app/venv/bin/uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
