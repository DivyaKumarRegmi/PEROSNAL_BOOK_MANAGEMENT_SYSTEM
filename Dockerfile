# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for mysqlclient
# python:3.11-slim is Debian-based
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc pkg-config default-libmysqlclient-dev && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy all project files
COPY . .

# Expose port
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
