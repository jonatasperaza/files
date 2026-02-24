"""
Mixins e helpers para set/clear dos cookies JWT nas views Django.
"""
from django.http import HttpResponse

from . import settings as cookie_settings


def set_auth_cookies(response: HttpResponse, access_token: str, refresh_token: str = None) -> None:
    """
    Define os cookies de autenticação na resposta HTTP.

    Args:
        response: Objeto HttpResponse do Django.
        access_token: JWT access token.
        refresh_token: JWT refresh token (opcional).
    """
    common = dict(
        httponly=cookie_settings.AUTH_COOKIE_HTTP_ONLY(),
        secure=cookie_settings.AUTH_COOKIE_SECURE(),
        samesite=cookie_settings.AUTH_COOKIE_SAMESITE(),
        path=cookie_settings.AUTH_COOKIE_PATH(),
        domain=cookie_settings.AUTH_COOKIE_DOMAIN(),
    )

    response.set_cookie(
        cookie_settings.AUTH_COOKIE_NAME(),
        access_token,
        max_age=cookie_settings.AUTH_COOKIE_ACCESS_MAX_AGE(),
        **common,
    )

    if refresh_token is not None:
        response.set_cookie(
            cookie_settings.REFRESH_COOKIE_NAME(),
            refresh_token,
            max_age=cookie_settings.AUTH_COOKIE_REFRESH_MAX_AGE(),
            **common,
        )


def clear_auth_cookies(response: HttpResponse) -> None:
    """
    Remove os cookies de autenticação da resposta HTTP.
    Usado tipicamente na view de logout.
    """
    path = cookie_settings.AUTH_COOKIE_PATH()
    domain = cookie_settings.AUTH_COOKIE_DOMAIN()

    response.delete_cookie(cookie_settings.AUTH_COOKIE_NAME(), path=path, domain=domain)
    response.delete_cookie(cookie_settings.REFRESH_COOKIE_NAME(), path=path, domain=domain)


class SetAuthCookieMixin:
    """
    Mixin para views que precisam definir cookies JWT automaticamente
    ao retornar tokens (ex: LoginView).

    Detecta os campos `access` e `refresh` no corpo da resposta
    e os move para cookies HTTP-only.
    """

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)

        if response.status_code == 200 and hasattr(response, "data"):
            access = response.data.get("access")
            refresh = response.data.get("refresh")

            if access:
                set_auth_cookies(response, access, refresh)
                # Remove tokens do body JSON por segurança
                response.data.pop("access", None)
                response.data.pop("refresh", None)

        return response


class ClearAuthCookieMixin:
    """
    Mixin para views de logout que limpam os cookies JWT.
    """

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        clear_auth_cookies(response)
        return response
