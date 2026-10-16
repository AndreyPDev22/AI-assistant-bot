export default {
  '*.{js,ts,vue}': ['eslint --fix', 'prettier --write'],
  '*.{json,css,scss,md}': ['prettier --write'],
  '*.{vue,ts}': [
    () => {
      return `vue-tsc --build`;
    },
  ],
};
