import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = str(os.getenv('DJANGO_SECRET_KEY'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', '') != 'False'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1').split()


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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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

if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=500,
        conn_health_checks=True,
    )


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [

]

LOGIN_REDIRECT_URL = '/'


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
STATIC_ROOT = BASE_DIR / 'staticfiles'

CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost').split()

SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_SAMESITE = 'Lax'

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

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

CURRENT_SEASON = 2026
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
DH = "DH"
INFIELD_OUTFIELD = "IF-OF"
PITCHER_OF = "OF-P"
PITCHER_IF = "IF-P"
PLAYER_POSITION_CHOICES = (
    (PITCHER, "Pitcher"),
    (INFIELD, "Infield"),
    (OUTFIELD, "Outfield"),
    (CATCHER, "Catcher"),
    (DH, "DH"),
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
    (DH, "Designated hitter"),
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
    "outs_bp_1": 3,     # first breakpoint (was 4)
    "outs_bp_2": 4,     # second breakpoint; 4th out gets a bonus
    "outs_max_1": 0.75, # per-out rate up to 3 outs
    "outs_max_2": 1.75, # per-out rate for the 4th out (+1 bonus)
    "outs_min_1": 1,    # kept for old migration compat
    "outs_min_2": 1.00, # per-out rate for 5th+ outs
    "BB":-.75,
    'triples':-3,
    'hits_bp_1': 1,
    'hits_bp_2': 2,
    'hits_max_1': -1.50,  # was -0.75
    'hits_max_2': -2.00,  # was -1.00
    'hits_min_2': -2.50,  # was -1.25
    'cycle':-40,
    'doubles':-2,
    'outfield_assists':-1,
    'cs':5,
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
    'rl2o':1,
    'rbi':-1,
    'k_looking':0.5,
    'k_bp_1':2,
    'k_bp_2':3,
    'k_bp_3':4,
    'k_max_1':0.5,
    'k_max_2':2,
    'k_max_3':4,
    'k_min_2':6,  # kept for old migration compat; superseded by 0036
    'k_min_3':6,
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
    'ip':-1.8,
    'h':1,
    'er':1,
    'bb':1,
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