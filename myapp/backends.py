import json
import logging

from django.core.exceptions import SuspiciousOperation
from django.urls import reverse
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from mozilla_django_oidc.utils import absolutify

LOGGER = logging.getLogger(__name__)
class MyOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super().create_user(claims)
        self._attach_roles(user, claims)
        return user

    def update_user(self, user, claims):
        self._attach_roles(user, claims)
        return super().update_user(user, claims)

    def _attach_roles(self, user, claims):
        # Get client ID from settings for better configuration management
        client_id = self.get_settings("OIDC_RP_CLIENT_ID")

        resource_access = claims.get("resource_access", {})
        client_roles = resource_access.get(client_id, {})
        roles = client_roles.get("roles", []) if isinstance(client_roles, dict) else []

        # Attach roles to user instance in memory (not stored in DB by default)
        setattr(user, "roles", roles)
        print(f"✅ Attached roles to user: {roles}")

        # Also, store the roles in the session for subsequent requests
        if hasattr(self, 'request') and self.request:
            self.request.session['oidc_roles'] = roles

    def _debug_print_oidc_flow(self, code, token_payload, token_info):
        """Prints a formatted summary of the OIDC token exchange for debugging."""
        print("\n" + "="*80)
        print("🔄 OIDC Authorization Code Flow - Token Exchange")
        print("="*80 + "\n")

        # 1. Authorization Code
        print("✅ 1. Authorization Code Received from Keycloak")
        print("-" * 50)
        print(f"   A temporary, one-time-use code was received from the user's browser.")
        print(f"   Code: {code[:20]}...\n")

        # 2. Token Request Payload (Client ID + Secret)
        print("✅ 2. Exchanging Code for Tokens (Server-to-Server Request)")
        print("-" * 50)
        print("   Django is sending this payload to Keycloak's token endpoint:")
        # Create a copy to safely remove the secret for printing
        payload_to_print = token_payload.copy()
        if 'client_secret' in payload_to_print:
            payload_to_print['client_secret'] = '********' # Mask the secret for security
        print(json.dumps(payload_to_print, indent=4))
        print("\n")

        # 3. Token Response (ID, Access, Refresh Tokens)
        print("✅ 3. Tokens Received from Keycloak")
        print("-" * 50)
        print("   Keycloak responded with this JSON payload containing the tokens:")
        print(json.dumps(token_info, indent=4))
        print("\n")

        print("="*80)
        print("✅ OIDC Flow Debug Print Complete.")
        print("="*80 + "\n")

    def get_token(self, payload):
        """
        Overrides the original get_token method to intercept and print the
        token exchange details for debugging purposes.
        """
        # First, get the tokens from the parent class as usual.
        token_info = super().get_token(payload)

        # Now, call our dedicated printing function with all the necessary info.
        # This keeps the debugging logic separate and clean.
        code = payload.get('code')
        self._debug_print_oidc_flow(code, payload, token_info)

        # Return the original token_info to allow the auth process to continue.
        return token_info
