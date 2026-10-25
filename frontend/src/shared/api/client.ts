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

export async function apiRequest<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);
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
