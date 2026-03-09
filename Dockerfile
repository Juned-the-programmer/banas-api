# Stage 1: Builder
FROM python:3.12-slim as builder

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
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Copy Python packages AND binaries
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=builder /usr/local/bin/newrelic-admin /usr/local/bin/newrelic-admin

# Copy app code
COPY . .

# New Relic Environment Variables
ENV NEW_RELIC_CONFIG_FILE=/app/newrelic.ini
ENV PORT=8000

# Create non-root user
RUN addgroup --system appuser && \
    adduser --system --ingroup appuser appuser && \
    chown -R appuser:appuser /app

RUN mkdir -p /media/qr_codes && chmod -R 777 /media/qr_codes

USER appuser

# Verify installations
RUN python -c "import django; print(f'Django {django.__version__}')" && \
    gunicorn --version

CMD ["newrelic-admin", "run-program", "gunicorn", "banas.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=2"]