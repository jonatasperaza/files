import type { AxiosInstance } from "axios";
import type { CookieJwtOptions } from "../types";

export function setupAxiosInterceptors(
  axios: AxiosInstance,
  options: Required<CookieJwtOptions>,
  onAuthFailure: () => void,
): void {
  // Garante que todos os requests enviam cookies
  axios.defaults.withCredentials = true;
  axios.defaults.baseURL = options.baseURL;

  let isRefreshing = false;
  // Fila de requests que chegaram enquanto o refresh estava em andamento
  let pendingRequests: Array<{
    resolve: () => void;
    reject: (err: unknown) => void;
  }> = [];

  const flushQueue = (success: boolean, error?: unknown) => {
    pendingRequests.forEach(({ resolve, reject }) =>
      success ? resolve() : reject(error),
    );
    pendingRequests = [];
  };

  axios.interceptors.response.use(
    // Resposta OK — passa direto
    (response) => response,

    async (error) => {
      const originalRequest = error.config;

      // Só tenta refresh em 401, e apenas uma vez por request
      if (error.response?.status !== 401 || originalRequest._retried) {
        return Promise.reject(error);
      }

      // Se já está em refresh, coloca o request na fila
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingRequests.push({
            resolve: () => resolve(axios(originalRequest)),
            reject,
          });
        });
      }

      originalRequest._retried = true;
      isRefreshing = true;

      try {
        await axios.post(options.refreshEndpoint);
        flushQueue(true);
        return axios(originalRequest);
      } catch (refreshError) {
        flushQueue(false, refreshError);
        onAuthFailure();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    },
  );
}
