from rest_framework.throttling import SimpleRateThrottle


class APIKeyRateThrottle(SimpleRateThrottle):
    scope = 'apikey'

    def get_cache_key(self, request, view):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': api_key
        }
