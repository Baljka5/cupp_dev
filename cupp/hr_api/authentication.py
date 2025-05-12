from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-KEY') or request.GET.get('api_key')
        expected_key = getattr(settings, 'CUSTOM_API_KEY', None)

        if not api_key or api_key != expected_key:
            raise AuthenticationFailed('Invalid or missing API key')

        return (None, None)
