from urllib.parse import urlencode
from django.conf import settings

def build_keycloak_logout_url(request, id_token_hint=None):
    """
    Constructs the full Keycloak logout URL.

    This function is used by mozilla-django-oidc to perform a single sign-out.
    It builds the URL to which the user will be redirected to terminate their
    Keycloak session.
    """
    # The base logout endpoint from settings
    logout_endpoint = settings.OIDC_OP_LOGOUT_ENDPOINT

    # The URL to redirect back to after Keycloak logout is complete
    post_logout_redirect_uri = request.build_absolute_uri(settings.LOGOUT_REDIRECT_URL)

    params = {'post_logout_redirect_uri': post_logout_redirect_uri}

    if id_token_hint:
        params['id_token_hint'] = id_token_hint

    return f"{logout_endpoint}?{urlencode(params)}"
