"""
Django settings for blog_template project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os, environ
from ckeditor.configs import DEFAULT_CONFIG  # noqa

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGIN_REDIRECT_URL = "/home"
environ.Env.read_env(os.path.join(BASE_DIR + '/w3s-dynamic-storage', '.env'))
env = environ.Env()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')
RECAPTCHA_SECRET_KEY = env('RECAPTCHA_SECRET')
RECAPTCHA_SITE_KEY=env('RECAPTCHA_SITE_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
#True if env('DEBUG') == 'True' else False

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
  'https://*.w3spaces.com',
  'https://*.w3spaces-preview.com',
]
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True
CSRF_HEADER_NAME = 'CSRF_COOKIE'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SAMESITE = None
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_AGE=43200
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'wuleaders',
    'ckeditor',
    'ckeditor_uploader',
    'django_seed'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'wuleaders_template.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wuleaders_template.wsgi.application'

PASSWORD_HASHERS = [
  'django.contrib.auth.hashers.Argon2PasswordHasher',
]
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

def get_db_config(environ_var):
    """Get Database configuration."""
    options = env.db(var=environ_var, default='sqlite:///w3s-dynamic-storage/database.db')
    if options.get('ENGINE') != 'django.db.backends.sqlite3':
        return options

    # This will allow use a relative to the project root DB path
    # for SQLite like 'sqlite:///db.sqlite3'
    if not options['NAME'] == ':memory:' and not os.path.isabs(options['NAME']):
        options.update({'NAME': os.path.join(BASE_DIR, options['NAME'])})

    return options


DATABASES = {
    'default': get_db_config('DATABASE_URL'),
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'w3s-dynamic-storage', 'media')
STATICFILES_DIRS = []
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CKEditor
# https://github.com/django-ckeditor/django-ckeditor

CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
CKEDITOR_UPLOAD_PATH = 'uploads/'
# DummyBackend is required to redirect to the default database.
CKEDITOR_IMAGE_BACKEND = 'ckeditor_uploader.backends.DummyBackend'
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_RESTRICT_BY_DATE = False

WITH_IMAGE_TOOLBAR = [
    {
        "name": "content",
        "items": [
            "Font",
            "FontSize",
            "-",
            "Bold",
            "Italic",
            "Underline",
            "-",
            "JustifyLeft",
            "JustifyRight",
            "JustifyCenter",
            "JustifyBlock",
        ],
    },
    {
        "name": "widgets",
        "items": [
            "Image",
        ],
    },
]
WITHOUT_IMAGE_TOOLBAR = [
    {
        "name": "content",
        "items": [
            "Font",
            "FontSize",
            "-",
            "Bold",
            "Italic",
            "Underline",
            "-",
            "JustifyLeft",
            "JustifyRight",
            "JustifyCenter",
            "JustifyBlock",
        ],
    },
]

CKEDITOR_CONFIGS = {
  "default": DEFAULT_CONFIG,
  "content-editor": {
    "skin": "moono-lisa",
    "toolbar": WITH_IMAGE_TOOLBAR,
    "toolbarGroups": None,
    "extraPlugins": ",".join(["image2", "codesnippet", "sharedspace", "font", "editorplaceholder"]),
    "removePlugins": ",".join(["image", "floatingspace", "resize", "elementspath", "exportPdf_tokenUrl"]),
    "codeSnippet_theme": "xcode",
    "sharedSpaces": {
        'top': 'toolbar',
    },
    "editorplaceholder": 'Write content here...',
  },
  "title-about-editor": {
    "skin": "moono-lisa",
    "toolbar": WITH_IMAGE_TOOLBAR,
    "toolbarGroups": None,
    "extraPlugins": ",".join(["image2", "codesnippet", "sharedspace", "font", "editorplaceholder"]),
    "removePlugins": ",".join(["image", "floatingspace", "resize", "elementspath", "exportPdf_tokenUrl"]),
    "codeSnippet_theme": "xcode",
    "sharedSpaces": {
        'top': 'toolbar',
    },
    "editorplaceholder": 'Title...',
  },
  "title-article-editor": {
    "skin": "moono-lisa",
    "toolbar": WITHOUT_IMAGE_TOOLBAR,
    "toolbarGroups": None,
    "extraPlugins": ",".join(["image2", "codesnippet", "sharedspace", "font", "editorplaceholder"]),
    "removePlugins": ",".join(["image", "floatingspace", "resize", "elementspath", "exportPdf_tokenUrl"]),
    "codeSnippet_theme": "xcode",
    "sharedSpaces": {
        'top': 'toolbar',
    },
    "editorplaceholder": 'Title...',
    'disallowedContent': 'img'
  },
}