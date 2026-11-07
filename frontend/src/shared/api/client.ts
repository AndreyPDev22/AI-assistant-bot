import camelcaseKeys from 'camelcase-keys';

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
  input?: unknown;
  ctx?: object;
}

export interface ErrorResponse {
  code: number;
  message: string;
}

export interface Envelope<T> {
  data: T | null;
  error: ErrorResponse | null;
  detail?: ValidationError[];
}

export enum APIResponseStatus {
  SUCCESS = 200,
  CREATED = 201,
  NO_CONTENT = 204,
  NOT_AUTHORIZED = 401,
  NOT_FOUND = 404,
  CONFLICT = 409,
  UNPROCESSABLE_ENTITY = 422,
  INTERNAL_SERVER_ERROR = 500,
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public error: ErrorResponse | null,
    public detail?: ValidationError[],
  ) {
    super(error?.message ?? `Request failed with status ${status}`);
  }
}

let refreshRequest: Promise<boolean> | null = null;
let authVersion = 0;

function requestRefresh(): Promise<boolean> {
  return fetch('/api/auth/refresh', {
    method: 'POST',
    credentials: 'include',
    headers: { 'X-CSRF-Protection': '1' },
  }).then((response) => response.ok);
}

function refreshSession(): Promise<boolean> {
  if (!refreshRequest) {
    const update =
      typeof navigator !== 'undefined' && navigator.locks
        ? navigator.locks.request('ai-assistant-auth-refresh', async () => {
            const current = await fetch('/api/auth/me', { credentials: 'include' });
            return current.ok || requestRefresh();
          })
        : requestRefresh();
    refreshRequest = update
      .then((success) => {
        if (success) authVersion += 1;
        return success;
      })
      .catch(() => false)
      .finally(() => {
        refreshRequest = null;
      });
  }
  return refreshRequest;
}

export async function apiRequest<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  const method = (init?.method ?? 'GET').toUpperCase();
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    headers.set('X-CSRF-Protection', '1');
  }
  const request = new Request(input, { credentials: 'include', ...init, headers });
  const retry = request.clone();
  const requestAuthVersion = authVersion;
  let response = await fetch(request);
  const excludedPaths = [
    '/api/auth/login',
    '/api/auth/logout',
    '/api/auth/refresh',
    '/api/users/register',
  ];
  if (
    response.status === APIResponseStatus.NOT_AUTHORIZED &&
    !excludedPaths.includes(new URL(request.url).pathname) &&
    (requestAuthVersion !== authVersion || (await refreshSession()))
  ) {
    response = await fetch(retry);
  }
  const body = await response.json().catch(() => null);
  const { data, error, detail } = camelcaseKeys((body ?? {}) as Envelope<T>, { deep: true });

  if (!response.ok || error) {
    throw new ApiError(response.status, error ?? null, detail);
  }

  return data as T;
}

export function getErrorMessage(error: unknown, fallback: string) {
  return error instanceof ApiError ? error.message : fallback;
}
