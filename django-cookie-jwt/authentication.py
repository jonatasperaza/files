from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from . import settings as cookie_settings


class CookieJWTAuthentication(JWTAuthentication):
    """
    Autenticação JWT que lê o access token de um cookie HTTP-only.

    Ordem de prioridade:
      1. Header Authorization: Bearer <token>  (compatibilidade com clientes API)
      2. Cookie definido em AUTH_COOKIE_NAME

    Uso no settings.py do projeto:
        REST_FRAMEWORK = {
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "django_cookie_jwt.authentication.CookieJWTAuthentication",
            ],
        }
    """

    def authenticate(self, request):
        # 1. Tenta header Authorization (prioridade para clientes API/mobile)
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
            if raw_token is not None:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token

        # 2. Tenta cookie HTTP-only
        raw_token = request.COOKIES.get(cookie_settings.AUTH_COOKIE_NAME)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except InvalidToken:
            return None

        return self.get_user(validated_token), validated_token
