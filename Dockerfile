FROM python:3.11-slim

# Use modern ENV syntax
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workdir to where manage.py is
WORKDIR /auth

# Install system dependencies (use netcat-openbsd instead of netcat)
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Prepare static folder and make entrypoint executable
RUN mkdir -p /vol/web/static
RUN chmod +x /auth/entrypoint.sh

# Expose port
EXPOSE 8000

# Entrypoint
ENTRYPOINT ["/auth/entrypoint.sh"]
