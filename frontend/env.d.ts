/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_USE_API_MOCK?: 'true' | 'false';
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
