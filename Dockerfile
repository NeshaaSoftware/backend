FROM python:3.11.9-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .

# Set environment to production by default in Docker
ENV DJANGO_ENV=production

# Collect static files
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "neshaa.wsgi:application", "--bind", "0.0.0.0:8000"]
