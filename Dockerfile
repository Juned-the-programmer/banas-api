FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directories for media and static files
RUN mkdir -p /app/media /app/static 

# Add these lines near the top, after FROM
RUN addgroup --system celery && \
    adduser --system --group celery

# Add this at the end
RUN chown -R celery:celery /app