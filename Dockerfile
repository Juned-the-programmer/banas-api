# Stage 1: Builder
FROM python:3.9-slim as builder

WORKDIR /app

# Install system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==20.1.*

# Stage 2: Runtime
FROM python:3.9-slim

WORKDIR /app

# Copy Python packages AND binaries
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=builder /usr/local/bin/celery /usr/local/bin/celery

# Copy app code
COPY . .

ENV PORT=8000
# Create non-root user
RUN addgroup --system celery && \
    adduser --system --ingroup celery celery && \
    chown -R celery:celery /app

RUN mkdir -p /media/qr_codes && chmod -R 777 /media/qr_codes

USER celery

# Verify installations
RUN python -c "import django; print(f'Django {django.__version__}')" && \
    gunicorn --version && \
    /usr/local/bin/celery --version  # Use full path for verification

CMD gunicorn banas.wsgi:application --bind 0.0.0.0:$PORT --workers=4