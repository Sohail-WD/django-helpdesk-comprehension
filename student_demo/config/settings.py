from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "student-demo-only-not-for-production"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
    "rest_framework",
    "django_cleanup.apps.CleanupConfig",
    "helpdesk",
    "demo",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "demo.context_processors.company",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
SITE_ID = 1

# The demo deliberately prints mail to the terminal. No SMTP setup is required.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "support@northstar.example"
SERVER_EMAIL = "support@northstar.example"

LOGIN_URL = "helpdesk:login"
LOGIN_REDIRECT_URL = "/"

# Keep the first classroom experience focused on the core support workflow.
HELPDESK_TEAMS_MODE_ENABLED = False
HELPDESK_UI_ENABLED = True
HELPDESK_API_ENABLED = True  # "My Tickets" uses the user-tickets API.
HELPDESK_NAVIGATION_ENABLED = True

HELPDESK_VIEW_A_TICKET_PUBLIC = True
HELPDESK_SUBMIT_A_TICKET_PUBLIC = True
HELPDESK_REDIRECT_TO_LOGIN_BY_DEFAULT = False

HELPDESK_KB_ENABLED = True # Upstream needs it which should be fixed there. 
HELPDESK_KANBAN_ENABLED = False
HELPDESK_TICKETS_TIMELINE_ENABLED = False
HELPDESK_ENABLE_DEPENDENCIES_ON_TICKET = False
HELPDESK_ENABLE_TIME_SPENT_ON_TICKET = False

HELPDESK_ENABLE_ATTACHMENTS = True
HELPDESK_STAFF_ONLY_TICKET_OWNERS = True
HELPDESK_SHOW_MY_TICKETS_IN_NAV_FOR_STAFF = False

HELPDESK_DEFAULT_SETTINGS = {
    "use_email_as_submitter": True,
    "email_on_ticket_assign": False,
    "email_on_ticket_change": False,
    "login_view_ticketlist": False,
    "tickets_per_page": 25,
}
