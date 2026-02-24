import { AxiosInstance } from 'axios';
import { CookieJwtOptions } from '../types';

export declare function setupAxiosInterceptors(axios: AxiosInstance, options: Required<CookieJwtOptions>, onAuthFailure: () => void): void;
