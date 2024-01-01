import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = str(os.getenv('DJANGO_SECRET_KEY'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'statsdb.apps.StatsdbConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ballgame.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'ballgame.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD':os.getenv('POSTGRES_PASSWORD'),
        'HOST':os.getenv('POSTGRES_HOST','localhost'),
        'PORT':'5432'
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [

]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ROSTER_TEAM_IDS = [
    ("1", "LAA", "Los Angeles Angels"),
    ("2", "BAL", "Baltimore Orioles"),
    ("3", "BOS", "Boston Red Sox"),
    ("4", "CHW", "Chicago White Sox"),
    ("5", "CLE", "Cleveland Guardians"),
    ("6", "DET", "Detroit Tigers"),
    ("7", "KCR", "Kansas City Royals"),
    ("8", "MIN", "Minnesota Twins"),
    ("9", "NYY", "New York Yankees"),
    ("10", "OAK", "Oakland Athletics"),
    ("11", "SEA", "Seattle Mariners"),
    ("12", "TBR", "Tampa Bay Rays"),
    ("13", "TEX", "Texas Rangers"),
    ("14", "TOR", "Toronto Blue Jays"),
    ("15", "ARI", "Arizona Diamondbacks"),
    ("16", "ATL", "Atlanta Braves"),
    ("17", "CHC", "Chicago Cubs"),
    ("18", "CIN", "Cincinatti Reds"),
    ("19", "COL", "Colorado Rockies"),
    ("20", "MIA", "Miami Marlins"),
    ("21", "HOU", "Houston Astros"),
    ("22", "LAD", "Los Angeles Dodgers"),
    ("23", "MIL", "Milwaukee Brewers"),
    ("24", "WAS", "Washington Nationals"),
    ("24", "WSN", "Washington Nationals"),
    ("25", "NYM", "New York Mets"),
    ("26", "PHI", "Philadelphia Phillies"),
    ("27", "PIT", "Pittsburgh Pirates"),
    ("28", "STL", "St. Louis Cardinals"),
    ("29", "SDP", "San Diego Padres"),
    ("30", "SFG", "San Francisco Giants"),
]

MLB_URL_TO_ORG_NAME = {
    "orioles": "BAL",
    "whitesox": "CWS",
    "astros": "HOU",
    "redsox": "BOS",
    "guardians": "CLE",
    "indians": "CLE",
    "angels": "LAA",
    "athletics": "OAK",
    "yankees": "NYY",
    "tigers": "DET",
    "rays": "TB",
    "royals": "KC",
    "mariners": "SEA",
    "bluejays": "TOR",
    "twins": "MIN",
    "rangers": "TEX",
    "braves": "ATL",
    "cubs": "CHC",
    "dbacks": "AZ",
    "marlins": "MIA",
    "reds": "CIN",
    "rockies": "COL",
    "mets": "NYM",
    "brewers": "MIL",
    "dodgers": "LAD",
    "phillies": "PHI",
    "pirates": "PIT",
    "padres": "SD",
    "nationals": "WSH",
    "cardinals": "STL",
    "giants": "SF"
}

LEVELS = [
    (16,"R"),
    (14,"A"),
    (13,"A+"),
    (12,'AA'),
    (11,"AAA"),
    (1,"MLB"),
]

CURRENT_SEASON = 2024
CURRENT_SEASON_TYPE = "offseason"

DATEFORMAT = "%Y-%m-%d"