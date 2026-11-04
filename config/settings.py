"""Development-first settings for RedaWay Academy."""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("REDAWAY_SECRET_KEY", "dev-only-change-me-before-deploy")
DEBUG = os.environ.get("REDAWAY_DEBUG", "1") == "1"
if not DEBUG and SECRET_KEY == "dev-only-change-me-before-deploy":
    raise ImproperlyConfigured("Defina REDAWAY_SECRET_KEY antes de executar em produção.")
if not DEBUG and len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("REDAWAY_SECRET_KEY precisa ter ao menos 50 caracteres em produção.")
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("REDAWAY_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if host.strip()]
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])
REDAWAY_REGISTRATION_ENABLED = os.environ.get("REDAWAY_REGISTRATION_ENABLED", "1" if DEBUG else "0") == "1"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "academy.apps.AcademyConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASE_URL = os.environ.get("DATABASE_URL")
DB_ENGINE = os.environ.get("REDAWAY_DB_ENGINE", "django.db.backends.sqlite3")
if DATABASE_URL:
    import dj_database_url

    DATABASES = {"default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=int(os.environ.get("REDAWAY_DB_CONN_MAX_AGE", "60")),
        ssl_require=not DEBUG,
    )}
    if not DEBUG and DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
        raise ImproperlyConfigured("DATABASE_URL precisa apontar para PostgreSQL em produção.")
elif DB_ENGINE == "django.db.backends.postgresql":
    DB_NAME = os.environ.get("REDAWAY_DB_NAME")
    if not DB_NAME:
        raise ImproperlyConfigured("Defina REDAWAY_DB_NAME para usar PostgreSQL.")
    DATABASES = {"default": {
        "ENGINE": DB_ENGINE,
        "NAME": DB_NAME,
        "USER": os.environ.get("REDAWAY_DB_USER", ""),
        "PASSWORD": os.environ.get("REDAWAY_DB_PASSWORD", ""),
        "HOST": os.environ.get("REDAWAY_DB_HOST", "localhost"),
        "PORT": os.environ.get("REDAWAY_DB_PORT", "5432"),
        "CONN_MAX_AGE": int(os.environ.get("REDAWAY_DB_CONN_MAX_AGE", "60")),
        "OPTIONS": ({"sslmode": os.environ["REDAWAY_DB_SSLMODE"]} if os.environ.get("REDAWAY_DB_SSLMODE") else {}),
    }}
elif DB_ENGINE == "django.db.backends.sqlite3":
    if not DEBUG:
        raise ImproperlyConfigured("SQLite é reservado ao desenvolvimento; configure PostgreSQL antes da produção.")
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }}
else:
    raise ImproperlyConfigured("REDAWAY_DB_ENGINE precisa ser sqlite3 ou postgresql.")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "academy.User"
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_STORAGE_BACKEND = os.environ.get("REDAWAY_STORAGE_BACKEND", "filesystem")
if not DEBUG:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
if MEDIA_STORAGE_BACKEND == "supabase_s3":
    s3_storage_settings = {
        "access_key": os.environ.get("SUPABASE_STORAGE_ACCESS_KEY_ID", ""),
        "secret_key": os.environ.get("SUPABASE_STORAGE_SECRET_ACCESS_KEY", ""),
        "bucket_name": os.environ.get("SUPABASE_STORAGE_BUCKET", ""),
        "endpoint_url": os.environ.get("SUPABASE_STORAGE_ENDPOINT", ""),
        "region_name": os.environ.get("SUPABASE_STORAGE_REGION", ""),
    }
    missing_storage_settings = [key for key, value in s3_storage_settings.items() if not value]
    if missing_storage_settings:
        raise ImproperlyConfigured("Configure as credenciais do Supabase Storage no ambiente do servidor.")
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            **s3_storage_settings,
            "addressing_style": "path",
            "signature_version": "s3v4",
            "querystring_auth": True,
            "default_acl": None,
            "file_overwrite": False,
        },
    }
elif MEDIA_STORAGE_BACKEND != "filesystem":
    raise ImproperlyConfigured("REDAWAY_STORAGE_BACKEND precisa ser filesystem ou supabase_s3.")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
EMAIL_BACKEND = os.environ.get(
    "REDAWAY_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend" if DEBUG else "django.core.mail.backends.smtp.EmailBackend",
)
DEFAULT_FROM_EMAIL = os.environ.get("REDAWAY_DEFAULT_FROM_EMAIL", "RedaWay Academy <nao-responda@redaway.local>")
EMAIL_HOST = os.environ.get("REDAWAY_EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("REDAWAY_EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.environ.get("REDAWAY_EMAIL_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("REDAWAY_EMAIL_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("REDAWAY_EMAIL_USE_TLS", "0") == "1"
EMAIL_USE_SSL = os.environ.get("REDAWAY_EMAIL_USE_SSL", "0") == "1"
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    # Subdomains/preload stay off until the final domain and its other hosts are reviewed.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
