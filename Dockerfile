FROM python:3.11.9-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    pkg-config \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
ENV DJANGO_ENV=production
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["/bin/sh", "-c", "python manage.py migrate --noinput && gunicorn neshaa.wsgi:application --bind 0.0.0.0:8000 --timeout 120"]
