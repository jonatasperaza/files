"""
Configurações centralizadas para django-cookie-jwt.
Todos os valores podem ser sobrescritos via settings.py do projeto Django.
"""
from django.conf import settings


def get_setting(name, default):
    return getattr(settings, name, default)


# Nome do cookie que carrega o access token
AUTH_COOKIE_NAME = lambda: get_setting("AUTH_COOKIE_NAME", "access_token")

# Nome do cookie que carrega o refresh token
REFRESH_COOKIE_NAME = lambda: get_setting("REFRESH_COOKIE_NAME", "refresh_token")

# Cookie HttpOnly (nunca acessível via JS)
AUTH_COOKIE_HTTP_ONLY = lambda: get_setting("AUTH_COOKIE_HTTP_ONLY", True)

# Cookie Secure (apenas HTTPS). Use False só em dev.
AUTH_COOKIE_SECURE = lambda: get_setting("AUTH_COOKIE_SECURE", not settings.DEBUG)

# SameSite policy: "Lax" | "Strict" | "None"
AUTH_COOKIE_SAMESITE = lambda: get_setting("AUTH_COOKIE_SAMESITE", "Lax")

# Path do cookie
AUTH_COOKIE_PATH = lambda: get_setting("AUTH_COOKIE_PATH", "/")

# Domain do cookie (None = domínio atual)
AUTH_COOKIE_DOMAIN = lambda: get_setting("AUTH_COOKIE_DOMAIN", None)

# Tempo de vida do access token em segundos (padrão: 5 minutos)
AUTH_COOKIE_ACCESS_MAX_AGE = lambda: get_setting("AUTH_COOKIE_ACCESS_MAX_AGE", 60 * 5)

# Tempo de vida do refresh token em segundos (padrão: 1 dia)
AUTH_COOKIE_REFRESH_MAX_AGE = lambda: get_setting("AUTH_COOKIE_REFRESH_MAX_AGE", 60 * 60 * 24)
