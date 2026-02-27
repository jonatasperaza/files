# django-cookie-jwt + vue-cookie-jwt

Autenticação JWT via cookies HTTP-only para projetos Django + Vue 3.

---

## 📦 django-cookie-jwt (PyPI)

### Instalação

```bash
pip install django-cookie-jwt
```

### Configuração (`settings.py`)

```python
INSTALLED_APPS = [
    ...
    "django_cookie_jwt",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "django_cookie_jwt.authentication.CookieJWTAuthentication",
    ],
}

# Opcional — todos têm defaults razoáveis
AUTH_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
AUTH_COOKIE_SECURE = True          # False automaticamente em DEBUG=True
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_SAMESITE = "Lax"       # "Strict" | "Lax" | "None"
AUTH_COOKIE_ACCESS_MAX_AGE = 300   # 5 minutos
AUTH_COOKIE_REFRESH_MAX_AGE = 86400  # 1 dia
```

### URLs (`urls.py`)

```python
from django_cookie_jwt.views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    CookieTokenLogoutView,
)

urlpatterns = [
    path("auth/login/",   CookieTokenObtainPairView.as_view()),
    path("auth/refresh/", CookieTokenRefreshView.as_view()),
    path("auth/logout/",  CookieTokenLogoutView.as_view()),
]
```

### Middleware de renovação automática (opcional)

```python
MIDDLEWARE = [
    ...
    "django_cookie_jwt.middleware.AutoRefreshJWTMiddleware",
]

# Renova se o token expira em menos de 60 segundos (padrão)
AUTH_COOKIE_REFRESH_THRESHOLD = 60
```

### Usando os mixins em views customizadas

```python
from django_cookie_jwt.mixins import SetAuthCookieMixin, ClearAuthCookieMixin
from rest_framework_simplejwt.views import TokenObtainPairView

class MeuLoginView(SetAuthCookieMixin, TokenObtainPairView):
    pass  # Cookies são definidos automaticamente

class MeuLogoutView(ClearAuthCookieMixin, APIView):
    def post(self, request):
        return Response({"detail": "Tchau!"})
```

### Usando os helpers diretamente

```python
from django_cookie_jwt.mixins import set_auth_cookies, clear_auth_cookies

def minha_view(request):
    response = Response(...)
    set_auth_cookies(response, access_token="...", refresh_token="...")
    return response
```

---

## 📦 vue-cookie-jwt (npm)

### Instalação

```bash
npm install vue-cookie-jwt
```

### Configuração (`main.ts`)

```typescript
import { createApp } from "vue"
import axios from "axios"
import { createCookieJwt } from "vue-cookie-jwt"
import App from "./App.vue"

const app = createApp(App)

app.use(createCookieJwt(axios, {
  baseURL: "https://api.meusite.com",
  // Endpoints opcionais (abaixo estão os defaults)
  loginEndpoint:   "/auth/login/",
  logoutEndpoint:  "/auth/logout/",
  refreshEndpoint: "/auth/refresh/",
  userEndpoint:    "/auth/me/",
  loginRoute:      "/login",   // rota de redirect após 401 irrecuperável
}))

app.mount("#app")
```

### Uso nos componentes (`LoginPage.vue`)

```vue
<script setup lang="ts">
import axios from "axios"
import { useAuth } from "vue-cookie-jwt"

const { login, logout, user, isAuthenticated, isLoading, error } = useAuth(axios, {
  baseURL: "https://api.meusite.com"
})

async function handleLogin() {
  await login({ username: "admin", password: "123" })
}
</script>

<template>
  <div v-if="isAuthenticated">
    Olá, {{ user?.username }}!
    <button @click="logout">Sair</button>
  </div>
  <form v-else @submit.prevent="handleLogin">
    <p v-if="error">{{ error }}</p>
    <button :disabled="isLoading">Entrar</button>
  </form>
</template>
```

### Hidratar o estado após recarregar a página

```typescript
// App.vue ou router guard
const { fetchUser } = useAuth(axios, options)
await fetchUser()  // tenta buscar /auth/me/ — se 401, user fica null
```

### Route guard com vue-router

```typescript
// router/index.ts
router.beforeEach(async (to) => {
  if (to.meta.requiresAuth) {
    const { isAuthenticated, fetchUser } = useAuth(axios, options)
    if (!isAuthenticated.value) {
      await fetchUser()
    }
    if (!isAuthenticated.value) {
      return "/login"
    }
  }
})
```

---

## Como funciona o refresh automático

```
Cliente                     Vue interceptor                Django
  │                               │                           │
  │──── GET /api/dados/ ─────────▶│──── GET /api/dados/ ─────▶│
  │                               │◀─── 401 Unauthorized ─────│
  │                               │──── POST /auth/refresh/ ──▶│
  │                               │◀─── 200 + novo cookie ────│
  │                               │──── GET /api/dados/ ─────▶│  (retry)
  │◀─── 200 + dados ─────────────│◀─── 200 + dados ──────────│
```

Requests simultâneos que chegam durante o refresh ficam em fila e são reexecutados automaticamente após a renovação.

---

## Segurança

- Cookies `HttpOnly` → JavaScript não consegue ler os tokens
- Cookies `Secure` → só trafegam via HTTPS em produção
- `SameSite=Lax` → proteção contra CSRF na maioria dos casos
- Tokens não aparecem no body das respostas nem em `localStorage`
- Refresh token é invalidado no servidor ao fazer logout (blacklist)