import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from django.utils.crypto import get_random_string
from redis import ConnectionPool

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("MONOSTAT_DATA_DIR", BASE_DIR / "data"))
LOG_DIR = DATA_DIR / "logs"
MEDIA_ROOT = DATA_DIR / "media"
STATIC_ROOT = os.path.join(os.path.dirname(__file__), "static.dist")

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
if not os.path.exists(MEDIA_ROOT):
    os.mkdir(MEDIA_ROOT)

SECRET_FILE = os.path.join(DATA_DIR, ".secret")
if os.path.exists(SECRET_FILE):
    with open(SECRET_FILE, "r") as f:
        SECRET_KEY = f.read().strip()
else:
    chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    SECRET_KEY = get_random_string(50, chars)
    with open(SECRET_FILE, "w") as f:
        os.chmod(SECRET_FILE, 0o600)
        try:
            os.chown(SECRET_FILE, os.getuid(), os.getgid())
        except AttributeError:
            pass  # os.chown is not available on Windows
        f.write(SECRET_KEY)

debug_default = (
    "runserver" in sys.argv or "runserver_plus" in sys.argv or "manage.py" in sys.argv
)
DEBUG = os.environ.get("MONOSTAT_DEBUG", str(debug_default)) == "True"

SITE_URL = os.getenv("MONOSTAT_SITE_URL", "http://localhost")
if SITE_URL == "http://localhost" or DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = [urlparse(SITE_URL).netloc]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_NAME = "monostat_session"
CSRF_COOKIE_NAME = "monostat_csrftoken"
SESSION_COOKIE_HTTPONLY = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "huey.contrib.djhuey",
    "solo",
    "compressor",
    "monostat.core",
    "monostat.public",
    "monostat.opsgenie",
    "monostat.slack",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
]

ROOT_URLCONF = "monostat.urls"

template_loaders = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)
if not DEBUG:
    template_loaders = (("django.template.loaders.cached.Loader", template_loaders),)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            DATA_DIR / "templates",
        ],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "monostat.public.context.contextprocessor",
            ],
            "loaders": template_loaders,
        },
    },
]

WSGI_APPLICATION = "monostat.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends." + os.getenv("MONOSTAT_DB_TYPE", "sqlite3"),
        "NAME": os.getenv("MONOSTAT_DB_NAME", DATA_DIR / "db.sqlite3"),
        "USER": os.getenv("MONOSTAT_DB_USER", ""),
        "PASSWORD": os.getenv("MONOSTAT_DB_PASS", ""),
        "HOST": os.getenv("MONOSTAT_DB_HOST", ""),
        "PORT": os.getenv("MONOSTAT_DB_PORT", ""),
        "CONN_MAX_AGE": 0,
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/admin/"

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

STATICFILES_DIRS = (
    [os.path.join(DATA_DIR, "static")]
    if os.path.exists(os.path.join(DATA_DIR, "static"))
    else []
)

STATICFILES_DIRS += (
    [os.path.join(BASE_DIR, "monostat/static")]
    if os.path.exists(os.path.join(BASE_DIR, "monostat/static"))
    else []
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging

loglevel = "DEBUG" if DEBUG else "INFO"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s %(asctime)s %(name)s %(module)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": loglevel,
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "level": loglevel,
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "monostat.log"),
            "formatter": "default",
        },
    },
    "loggers": {
        "": {
            "handlers": ["file", "console"],
            "level": loglevel,
            "propagate": True,
        },
        "django.request": {
            "handlers": ["file", "console"],
            "level": loglevel,
            "propagate": True,
        },
        "django.security": {
            "handlers": ["file", "console"],
            "level": loglevel,
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["file", "console"],
            "level": "INFO",  # Do not output all the queries
            "propagate": True,
        },
    },
}

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = not debug_default

COMPRESS_FILTERS = {
    "css": (
        "compressor.filters.css_default.CssAbsoluteFilter",
        "compressor.filters.cssmin.rCSSMinFilter",
    ),
    "js": ("compressor.filters.jsmin.JSMinFilter",),
}

CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'self'",)
CSP_INCLUDE_NONCE_IN = ["style-src"]


pool = ConnectionPool(
    **{
        "host": os.getenv("MONOSTAT_REDIS_HOST", "localhost"),
        "port": int(os.getenv("MONOSTAT_REDIS_PORT", "6379")),
        "db": int(os.getenv("MONOSTAT_REDIS_DB", "0")),
        "max_connections": 20,
    }
)
HUEY = {
    "huey_class": "huey.PriorityRedisExpireHuey",
    "name": "monostat",
    "results": True,
    "store_none": False,
    "immediate": False,
    "utc": True,
    "blocking": True,
    "connection": {
        "connection_pool": pool,
    },
    "consumer": {
        "workers": 2,
        "worker_type": "thread",
        "check_worker_health": True,
        "health_check_interval": 1,
    },
}
