from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth.models import AnonymousUser  # ✅ нэмнэ

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY') or request.GET.get('api_key')
        expected_key = getattr(settings, 'CUSTOM_API_KEY', None)

        if not api_key or api_key != expected_key:
            raise AuthenticationFailed('Invalid or missing API key')

        return (AnonymousUser(), None)  # ✅ None биш