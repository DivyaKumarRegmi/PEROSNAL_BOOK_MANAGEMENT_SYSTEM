from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'backend', 'keycloak']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "myapp",

    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",

    "mozilla_django_oidc",  # <-- Use mozilla-django-oidc here
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "mozilla_django_oidc.middleware.SessionRefresh", # Handles token refresh
    "myapp.middleware.AttachRolesMiddleware", # Attaches roles from session to user
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                  "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": "3306",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp-relay.brevo.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="8fdab7001@smtp-brevo.com")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = "erdivyakumar@gmail.com"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = False
#SESSION_COOKIE_SAMESITE = "Lax"
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Authentication backends: use mozilla-django-oidc backend first
AUTHENTICATION_BACKENDS = [
    "myapp.backends.MyOIDCAuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Login URLs for OIDC (mozilla-django-oidc)
LOGIN_URL = "/oidc/authenticate/"
LOGIN_REDIRECT_URL = "/books/"
LOGOUT_REDIRECT_URL = "/"

# OIDC (Keycloak) settings
OIDC_RP_CLIENT_ID = config("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = config("OIDC_RP_CLIENT_SECRET")

# Define separate public and internal domains for Keycloak to handle Docker networking.
# The public domain is for browser redirects, the internal is for server-to-server communication.
KEYCLOAK_PUBLIC_DOMAIN = config("KEYCLOAK_PUBLIC_DOMAIN", default="http://localhost:8080")
KEYCLOAK_INTERNAL_DOMAIN = config("KEYCLOAK_INTERNAL_DOMAIN", default="http://keycloak:8080")
KEYCLOAK_REALM = config("KEYCLOAK_REALM")
OIDC_OP_ISSUER = "http://keycloak:8080/realms/my-app-realm"

# The authorization endpoint is for the user's browser, so it uses the public domain.
OIDC_OP_AUTHORIZATION_ENDPOINT = f"{KEYCLOAK_PUBLIC_DOMAIN}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"

# These endpoints are for server-to-server communication, so they use the internal Docker network domain.
OIDC_OP_TOKEN_ENDPOINT = f"{KEYCLOAK_INTERNAL_DOMAIN}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
OIDC_OP_USER_ENDPOINT = f"{KEYCLOAK_INTERNAL_DOMAIN}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
OIDC_OP_JWKS_ENDPOINT = f"{KEYCLOAK_INTERNAL_DOMAIN}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"

# Specify the algorithm Keycloak uses to sign ID tokens. Keycloak defaults to RS256.
OIDC_RP_SIGN_ALGO = "RS256"

# Define the scopes to request during the OIDC flow.
# 'openid' is required to access the userinfo endpoint.
OIDC_RP_SCOPES = "openid profile email"

# Disable SSL verification for local development against a non-HTTPS Keycloak instance.
# This should ALWAYS be True in production.
OIDC_VERIFY_SSL= False

# Map OIDC claims from Keycloak to Django User model fields.
# 'sub' is the unique subject identifier, 'preferred_username' is the human-readable username.
# 'given_name' and 'family_name' are standard OIDC claims for first and last names.
''''
import json  # Add this at the top of settings.py

def custom_extract_userinfo(claims):
    print("💥 Decoded ID token claims (pretty JSON):")
    print(json.dumps(claims, indent=4))  # <-- Pretty print to console

    resource_access = claims.get("resource_access", {})
    client_roles = resource_access.get("django-app", {})  # Replace with your client ID
    roles = client_roles.get("roles", []) if isinstance(client_roles, dict) else []

    userinfo = {
        "sub": claims.get("sub"),
        "email": claims.get("email"),
        "first_name": claims.get("given_name", ""),
        "last_name": claims.get("family_name", ""),
        "roles": roles,
    }
    return userinfo

OIDC_RP_USERINFO_CALLBACK = "myproject.settings.custom_extract_userinfo"
# This function will be called to extract user info from the OIDC claims.
'''

ALLOW_LOGOUT_GET_METHOD = True  # Allow GET requests for logout, useful for browser redirects

# The logout endpoint is for the user's browser, so it must use the public domain.
OIDC_OP_LOGOUT_ENDPOINT = f"{KEYCLOAK_PUBLIC_DOMAIN}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout"
# The OIDC logout URL is used to redirect the user after logging out.

# Point to the function that builds the full logout URL for Keycloak.
OIDC_OP_LOGOUT_URL_METHOD = "myproject.utils.build_keycloak_logout_url"
OIDC_STORE_ID_TOKEN = True  # Store the ID token in the session for logout
OIDC_STORE_ACCESS_TOKEN = True  # Store the access token in the session for logout