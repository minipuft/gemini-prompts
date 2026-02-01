export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [
      2,
      'always',
      [
        'extension',
        'hooks',
        'config',
        'deps',
        'ci',
        'docs',
      ],
    ],
    'scope-empty': [0, 'never'],
    'header-max-length': [2, 'always', 100],
  },
};
