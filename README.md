# Neshaa Django Backend

A modern, production-ready Django backend for the Neshaa project.

## Overview

This project uses Django best practices, modular settings, and is ready for local development, staging, and production. It supports Docker, PostgreSQL, and secure deployment out of the box.

## Project Layout

```
backend/
├── neshaa/           # Main Django project & settings
│   └── settings/     # Modular settings: base, local, development, production
├── static/           # Static files (source)
├── staticfiles/      # Collected static files
├── media/            # User uploads
├── templates/        # Django templates
├── manage.py         # Django CLI
├── requirements.txt  # Python dependencies
└── Dockerfile        # Docker support
```

## System Requirements

Before setting up the project, install the required system dependencies:

### Ubuntu/Debian:
```bash
sudo apt-get install pkg-config python3-dev default-libmysqlclient-dev build-essential
```

### CentOS/RHEL/Fedora:
```bash
sudo yum install pkgconfig python3-devel mysql-devel gcc
# or for newer versions:
sudo dnf install pkgconfig python3-devel mysql-devel gcc
```


## Environment Setup

Settings are modular and selected via the `DJANGO_ENV` environment variable:

- `local` (default): Local dev, SQLite
- `development`: Dev server, PostgreSQL
- `production`: Hardened, PostgreSQL

Example:
```bash
export DJANGO_ENV=local         # or development, production
```

## Quick Start (Local)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
4. Start the server:
   ```bash
   python manage.py runserver
   ```

## Docker Usage

1. Build the image:
   ```bash
   docker build -t neshaa .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 -e DJANGO_ENV=production neshaa
   ```

## Required Environment Variables (Production)

- `SECRET_KEY`: Django secret key
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Database config
- `ALLOWED_HOSTS`: Comma-separated allowed hosts

## Features

- Modular, environment-based settings
- PostgreSQL support for dev/prod
- Static & media file handling
- Secure production defaults
- Docker-ready

## Development Notes

- Follows Django best practices
- Static/media files and security middleware configured
- Easy to extend for new apps or environments