import { CookieJwtOptions, LoginCredentials } from '../types';

export declare function useAuth(axios: import('axios').AxiosInstance, options: Required<CookieJwtOptions>): {
    user: any;
    isAuthenticated: any;
    isLoading: any;
    error: any;
    login: (credentials: LoginCredentials) => Promise<void>;
    logout: () => Promise<void>;
    fetchUser: () => Promise<void>;
    refresh: () => Promise<void>;
};
