import js from '@eslint/js';
import pluginVue from 'eslint-plugin-vue';
import tseslint from 'typescript-eslint';
import prettier from 'eslint-config-prettier';
import globals from 'globals';

export default tseslint.config(
  { ignores: ['dist/**', 'node_modules/**', 'public/**', 'src/mocks/mockServiceWorker.js'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.vue'],
    languageOptions: { parserOptions: { parser: tseslint.parser } },
  },
  {
    files: ['src/**/ui/*.vue'],
    rules: { 'vue/multi-word-component-names': 'off' },
  },
  {
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
  },
  prettier,
);
