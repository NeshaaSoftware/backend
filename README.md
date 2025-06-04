# Neshaa Django Project

A Django web application built with modern practices and production-ready configuration.

## Project Structure

```
backend/
├── neshaa/                 # Main Django project
│   ├── settings/          # Split settings configuration
│   │   ├── base.py       # Shared settings
│   │   ├── local.py      # Local development
│   │   ├── development.py # Development environment
│   │   └── production.py  # Production environment
│   ├── wsgi.py
│   └── urls.py
├── static/                # Static files source
├── staticfiles/           # Collected static files
├── media/                 # User uploaded files
├── templates/             # Django templates
├── manage.py
├── requirements.txt
└── Dockerfile
```

## Environment Configuration

The project uses Django's recommended split settings pattern:

- **Base settings** (`base.py`): Shared configuration
- **Local settings** (`local.py`): Local development with SQLite
- **Development settings** (`development.py`): Development server with PostgreSQL
- **Production settings** (`production.py`): Production server with security settings

Settings are automatically loaded based on the `DJANGO_ENV` environment variable:

```bash
# Local development (default)
export DJANGO_ENV=local

# Development server
export DJANGO_ENV=development

# Production server
export DJANGO_ENV=production
```

## Quick Start

### Local Development

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

4. Run the development server:
```bash
python manage.py runserver
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t neshaa .
```

2. Run the container:
```bash
docker run -p 8000:8000 -e DJANGO_ENV=production neshaa
```

## Environment Variables

For production deployment, set these environment variables:

- `SECRET_KEY`: Django secret key
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Features

- Split settings configuration for different environments
- PostgreSQL support for development and production
- Static files handling
- Security settings for production
- Docker support
- Comprehensive gitignore and dockerignore files

## Development

The project follows Django best practices:

- Settings are split by environment
- Static files are properly configured
- Media files handling is set up
- Security middleware is enabled
- CSRF and session security are configured for production