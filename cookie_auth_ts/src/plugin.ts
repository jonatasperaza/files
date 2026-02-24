/**
 * Plugin Vue 3 para autenticação via cookie JWT.
 *
 * Uso:
 *   import { createCookieJwt } from "vue-cookie-jwt"
 *   import axios from "axios"
 *
 *   app.use(createCookieJwt(axios, {
 *     baseURL: "https://api.meusite.com",
 *   }))
 *
 * Depois nos componentes:
 *   const { login, logout, user, isAuthenticated } = useAuth()
 */
import type { App } from "vue"
import type { AxiosInstance } from "axios"
import { useRouter } from "vue-router"
import { setupAxiosInterceptors } from "./axios/interceptor"
import { useAuth } from "./composables/useAuth"
import type { CookieJwtOptions } from "./types"

const DEFAULT_OPTIONS: Omit<Required<CookieJwtOptions>, "baseURL"> = {
  loginEndpoint: "/auth/login/",
  logoutEndpoint: "/auth/logout/",
  refreshEndpoint: "/auth/refresh/",
  userEndpoint: "/auth/me/",
  loginRoute: "/login",
}

export function createCookieJwt(axiosInstance: AxiosInstance, options: CookieJwtOptions) {
  const resolved: Required<CookieJwtOptions> = { ...DEFAULT_OPTIONS, ...options }

  return {
    install(app: App) {
      // Registra os interceptors no axios fornecido
      // O router pode não estar disponível no install, então usamos uma flag lazy
      let router: ReturnType<typeof useRouter> | null = null

      const onAuthFailure = () => {
        if (router) {
          router.push(resolved.loginRoute)
        } else {
          window.location.href = resolved.loginRoute
        }
      }

      setupAxiosInterceptors(axiosInstance, resolved, onAuthFailure)

      // Torna useAuth disponível via provide/inject como conveniência
      app.provide("cookieJwtAxios", axiosInstance)
      app.provide("cookieJwtOptions", resolved)

      // Captura o router quando disponível
      app.mixin({
        beforeCreate() {
          if (!router && this.$router) {
            router = this.$router
          }
        },
      })
    },
  }
}

// Re-exporta composable e tipos para o consumidor
export { useAuth } from "./composables/useAuth"
export type { CookieJwtOptions, LoginCredentials, AuthState } from "./types"
