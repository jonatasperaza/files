"""
Middleware que renova automaticamente o access token próximo do vencimento.
Usa o refresh token do cookie para emitir um novo access token transparentemente.
"""
import time

from django.utils.deprecation import MiddlewareMixin

from . import settings as cookie_settings


class AutoRefreshJWTMiddleware(MiddlewareMixin):
    """
    Renova automaticamente o access token quando ele está próximo de expirar.

    O refresh acontece silenciosamente: o cliente recebe a resposta normalmente
    com um novo cookie access_token já definido.

    Ativação no settings.py do projeto:
        MIDDLEWARE = [
            ...
            "django_cookie_jwt.middleware.AutoRefreshJWTMiddleware",
        ]

    Configuração opcional:
        # Renova o token se ele expira em menos de X segundos (padrão: 60)
        AUTH_COOKIE_REFRESH_THRESHOLD = 60
    """

    REFRESH_THRESHOLD_SETTING = "AUTH_COOKIE_REFRESH_THRESHOLD"
    DEFAULT_THRESHOLD = 60  # segundos antes de expirar para renovar

    def process_response(self, request, response):
        from django.conf import settings
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

        from .mixins import set_auth_cookies

        access_raw = request.COOKIES.get(cookie_settings.AUTH_COOKIE_NAME)
        refresh_raw = request.COOKIES.get(cookie_settings.REFRESH_COOKIE_NAME)

        if not access_raw or not refresh_raw:
            return response

        threshold = getattr(settings, self.REFRESH_THRESHOLD_SETTING, self.DEFAULT_THRESHOLD)

        try:
            token = AccessToken(access_raw)
            exp = token.payload.get("exp", 0)
            remaining = exp - time.time()

            if remaining > threshold:
                return response  # Token ainda tem vida suficiente

            # Token próximo de expirar — tenta renovar
            refresh = RefreshToken(refresh_raw)
            new_access = str(refresh.access_token)
            set_auth_cookies(response, new_access)

        except (InvalidToken, TokenError):
            pass  # Token inválido — deixa o fluxo normal de auth tratar

        return response
