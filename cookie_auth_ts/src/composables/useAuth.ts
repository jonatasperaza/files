import { computed, ref } from "vue";
import type { CookieJwtOptions, LoginCredentials } from "../types";

// Estado reativo global — compartilhado entre todos os componentes
const user = ref<Record<string, unknown> | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);

const isAuthenticated = computed(() => user.value !== null);

export function useAuth(
  axios: import("axios").AxiosInstance,
  options: Required<CookieJwtOptions>,
) {
  /**
   * Realiza login enviando credenciais para o Django.
   * O cookie é definido automaticamente pela resposta do servidor.
   */
  async function login(credentials: LoginCredentials): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await axios.post(options.loginEndpoint, credentials);
      await fetchUser();
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Erro ao realizar login.";
      error.value = msg;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Realiza logout: invalida o token no servidor e limpa o estado local.
   */
  async function logout(): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await axios.post(options.logoutEndpoint);
    } catch {
      // Ignora erro — pode já ter expirado
    } finally {
      user.value = null;
      isLoading.value = false;
    }
  }

  /**
   * Busca os dados do usuário autenticado.
   * Útil para hidratar o estado após recarregar a página.
   */
  async function fetchUser(): Promise<void> {
    isLoading.value = true;

    try {
      const response = await axios.get(options.userEndpoint);
      user.value = response.data;
    } catch {
      user.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Renova manualmente o access token via cookie de refresh.
   */
  async function refresh(): Promise<void> {
    await axios.post(options.refreshEndpoint);
  }

  return {
    // Estado
    user,
    isAuthenticated,
    isLoading,
    error,

    // Ações
    login,
    logout,
    fetchUser,
    refresh,
  };
}
