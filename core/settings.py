from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "2zdo-&at%(_q!axzbo@74ng*47gy_o5y3g9fej*0@5s-12wa7a"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'account',
    'cart',
    'store',
    'payment'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.categories',
                'store.context_processors.balance',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "URL":"postgres://default:mZD8bG1afhJS@ep-dark-cloud-16772177-pooler.us-east-1.postgres.vercel-storage.com:5432/verceldb",
        "PRISMA_URL":"postgres://default:mZD8bG1afhJS@ep-dark-cloud-16772177-pooler.us-east-1.postgres.vercel-storage.com:5432/verceldb?pgbouncer=true&connect_timeout=15",
        "URL_NON_POOLING":"postgres://default:mZD8bG1afhJS@ep-dark-cloud-16772177.us-east-1.postgres.vercel-storage.com:5432/verceldb",
        "USER":"default",
        "HOST":"ep-dark-cloud-16772177-pooler.us-east-1.postgres.vercel-storage.com",
        "PASSWORD":"mZD8bG1afhJS",
        "NAME":"verceldb",
    }
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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR/'static'
]
STATIC_ROOT = BASE_DIR / "static_root"
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "staticfiles-cdn" / "uploads"
#from .cdn.conf import * # noqa
LOGIN_URL = 'account:login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'account:login'
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "account.Customer"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"