// Scopes below are this repo's own module names (seeded, edit freely). Everything else in
// `rules` comes from `commitlint.rules.mjs`, which is managed — do not edit it here; edit the
// scope list instead.
import rules from './commitlint.rules.mjs';

export default {
  extends: ['@commitlint/config-conventional'],
  plugins: rules.plugins,
  rules: {
    ...rules.rules,
    'scope-enum': [2, 'always', ['extension', 'hooks', 'config', 'deps', 'ci', 'docs']],
  },
};
