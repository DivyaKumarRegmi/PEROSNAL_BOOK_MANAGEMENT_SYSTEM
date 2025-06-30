class AttachRolesMiddleware:
    """
    Middleware to attach roles from the session to the user object for each request.
    This must be placed AFTER Django's AuthenticationMiddleware.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Get roles from the session, which were stored by the auth backend
            setattr(request.user, 'roles', request.session.get('oidc_roles', []))

        response = self.get_response(request)
        return response