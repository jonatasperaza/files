import { App } from 'vue';
import { AxiosInstance } from 'axios';
import { CookieJwtOptions } from './types';

export declare function createCookieJwt(axiosInstance: AxiosInstance, options: CookieJwtOptions): {
    install(app: App): void;
};
export { useAuth } from './composables/useAuth';
export type { CookieJwtOptions, LoginCredentials, AuthState } from './types';
