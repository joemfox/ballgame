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
    'django_extensions',
    'corsheaders',
    'django_filters',
    'ninja_extra',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'statsdb.urls'

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:5174',
    'http://0.0.0.0:5173'
]

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

WSGI_APPLICATION = 'statsdb.wsgi.application'


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

PITCHER = "P"
STARTER = "SP"
RELIEVER = "RP"
CATCHER = "C"
INFIELD = "IF"
OUTFIELD = "OF"
FIRSTBASE = "1B"
SECONDBASE = "2B"
SHORTSTOP = "SS"
THIRDBASE = "3B"
LEFTFIELD = "LF"
CENTERFIELD = "CF"
RIGHTFIELD = "RF"
INFIELD_OUTFIELD = "IF-OF"
PITCHER_OF = "OF-P"
PITCHER_IF = "IF-P"
PLAYER_POSITION_CHOICES = (
    (PITCHER, "Pitcher"),
    (INFIELD, "Infield"),
    (OUTFIELD, "Outfield"),
    (INFIELD_OUTFIELD, "IF-OF"),
    (PITCHER_OF, "OF-P"),
    (PITCHER_IF, "IF-P"),
)
POSITIONS_CHOICES = (
    (STARTER, "Starter"),
    (RELIEVER, "Reliever"),
    (CATCHER, "Catcher"),
    (FIRSTBASE, "First base"),
    (SECONDBASE, "Second base"),
    (SHORTSTOP, "Shortstop"),
    (THIRDBASE, "Third base"),
    (LEFTFIELD, "Left field"),
    (CENTERFIELD, "Center field"),
    (RIGHTFIELD, "Right field"),
)

# all categories should be listed here
# and have point assignments in the object below
FAN_CATEGORIES_HIT = [
    "outs",
    "bb",
    "triples",
    "h",
    "cycle",
    "doubles",
    "outfield_assists",
    "cs",
    "e",
    "gidp",
    "hr",
    "r",
    "lob",
    "po",
    "rl2o",
    "rbi",
    "k_looking",
    "k",
    "sb"
]

POINT_VALUES_HIT = {
    "outs_bp_1":4,  # breakpoint
    "outs_max_1": 0.75, # lower value
    "outs_min_1":1, # higher value
    "BB":-1,
    'triples':-3,
    'hits_bp_1': 1,
    'hits_bp_2': 2,
    'hits_max_1':-1,
    'hits_max_2':-1.25,
    'hits_min_2':-1.5,
    'cycle':-40,
    'doubles':-2,
    'outfield_assists':-1,
    'cs':2,
    'e':2,
    'gidp':2,
    'hr_bp_1':1,
    'hr_bp_2':2,
    'hr_bp_3':3,
    'hr_bp_4':4,
    'hr_max_1':-3,
    'hr_max_2':-4,
    'hr_max_3':-5,
    'hr_max_4':-100,
    'hr_min_4':-1000,
    'r':-1,
    'lob':0.5,
    'po':4,
    'rl2o':2,
    'rbi':-1,
    'k_looking':0.5,
    'k_bp_1':2,
    'k_bp_2':3,
    'k_max_1':0.5,
    'k_max_2':1,
    'k_min_2':4,
    'sb':-3,
}

FAN_CATEGORIES_PITCH = [
    "ip",
    "h",
    "er",
    "bb",
    "k",
    "hr",
    "bs",
    "balks",
    "hb",
    "bra",
    "dpi",
    "e",
    "wp",
    "ir",
    "irs",
    "perfect_game",
    "no_hitter",
    "relief_loss"
]

POINT_VALUES_PITCH = {
    'ip':-1.5,
    'h':0.5,
    'er':1,
    'bb':0.5,
    'k_bp_1':7,
    'k_bp_2':9,
    'k_max_1':-0.5,
    'k_max_2':-1,
    'k_min_2':-2,
    'hr_bp_1':1,
    'hr_bp_2':2,
    'hr_max_1':3,
    'hr_max_2':3.5,
    'hr_min_2':4,
    'bs':5,
    'balks':5,
    'hb':1,
    'bra':1,
    'dpi':-1,
    'e':1,
    'wp':2,
    'ir':5,
    'irs':-5,
    'perfect_game':-1000,
    'no_hitter':-100,
    'relief_loss':3
}