# Dynamically load settings in the correct order
import os

DJANGO_ENV = os.getenv("DJANGO_ENV", "development")
if DJANGO_ENV == "production":
    from .production import *
elif DJANGO_ENV == "development":
    from .development import *
else:
    from .local import * # Doesn't work
