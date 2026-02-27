"""
Views prontas para autenticação via cookie JWT.
Compatíveis com simplejwt.
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import settings as cookie_settings
from .mixins import ClearAuthCookieMixin, SetAuthCookieMixin, set_auth_cookies


class CookieTokenObtainPairView(SetAuthCookieMixin, TokenObtainPairView):
    """
    Login: obtém access + refresh tokens e os define como cookies HTTP-only.
    O body da resposta não conterá os tokens — apenas uma confirmação.

    POST /auth/login/
    { "username": "...", "password": "..." }

    Resposta: 200 OK
    { "detail": "Login realizado com sucesso." }
    + Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Lax
    + Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=Lax
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.data["detail"] = "Login realizado com sucesso."
        return response


class CookieTokenRefreshView(APIView):
    """
    Refresh: lê o refresh_token do cookie e emite um novo access_token via cookie.

    POST /auth/refresh/
    (sem body — o refresh token vem do cookie)

    Resposta: 200 OK
    { "detail": "Token renovado com sucesso." }
    + Set-Cookie: access_token=...; HttpOnly
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(cookie_settings.REFRESH_COOKIE_NAME)

        if not refresh_token:
            return Response({"detail": "Refresh token ausente."}, status=401)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)

            response = Response({"detail": "Token renovado com sucesso."})
            set_auth_cookies(response, access_token)
            return response

        except Exception:
            return Response({"detail": "Refresh token inválido ou expirado."}, status=401)


class CookieTokenLogoutView(ClearAuthCookieMixin, APIView):
    """
    Logout: invalida o refresh token e limpa os cookies.

    POST /auth/logout/
    (sem body — o refresh token vem do cookie)

    Resposta: 200 OK
    { "detail": "Logout realizado com sucesso." }
    + Set-Cookie: access_token=; expires=Thu, 01 Jan 1970 ...
    + Set-Cookie: refresh_token=; expires=Thu, 01 Jan 1970 ...
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(cookie_settings.REFRESH_COOKIE_NAME)

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Requer simplejwt com blacklist habilitado
            except Exception:
                pass  # Token já expirado — tudo bem, limpa o cookie mesmo assim

        return Response({"detail": "Logout realizado com sucesso."})
