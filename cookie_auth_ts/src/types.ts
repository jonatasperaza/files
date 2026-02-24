export interface CookieJwtOptions {
  /** URL base da API Django (ex: "https://api.meusite.com") */
  baseURL: string

  /** Endpoint de login. Padrão: "/auth/login/" */
  loginEndpoint?: string

  /** Endpoint de logout. Padrão: "/auth/logout/" */
  logoutEndpoint?: string

  /** Endpoint de refresh. Padrão: "/auth/refresh/" */
  refreshEndpoint?: string

  /** Endpoint para buscar dados do usuário logado. Padrão: "/auth/me/" */
  userEndpoint?: string

  /**
   * Rota para redirecionar após logout ou 401 não recuperável.
   * Padrão: "/login"
   */
  loginRoute?: string
}

export interface LoginCredentials {
  username: string
  password: string
  [key: string]: unknown
}

export interface AuthState {
  user: Record<string, unknown> | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}
