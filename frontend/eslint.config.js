import js from '@eslint/js';
import ts from 'typescript-eslint';
import svelte from 'eslint-plugin-svelte';
import globals from 'globals';

/**
 * Flat ESLint config (ESLint 9). Lints JS/TS and Svelte 5 components.
 * svelte-check remains the type-authoritative gate; this catches lint-class
 * issues (unused vars, unsafe patterns) that svelte-check does not.
 */
export default ts.config(
	js.configs.recommended,
	...ts.configs.recommended,
	...svelte.configs['flat/recommended'],
	{
		languageOptions: {
			globals: { ...globals.browser, ...globals.node }
		}
	},
	{
		files: ['**/*.svelte', '**/*.svelte.ts'],
		languageOptions: {
			parserOptions: { parser: ts.parser }
		}
	},
	{
		rules: {
			// The codebase leans on `any` at the API boundary (untyped list
			// endpoints); flagged in the audit as a tracked cleanup, not a gate.
			'@typescript-eslint/no-explicit-any': 'off',
			// SvelteKit's generated app.d.ts uses empty `interface` extensions
			// (App.Locals/PageData/…) by design.
			'@typescript-eslint/no-empty-object-type': 'off',
			// Bare expressions in $effect/$derived are the idiomatic Svelte 5
			// dependency-tracking pattern, not dead statements.
			'@typescript-eslint/no-unused-expressions': 'off',
			'@typescript-eslint/no-unused-vars': [
				'warn',
				{ argsIgnorePattern: '^_', varsIgnorePattern: '^_' }
			]
		}
	},
	{
		ignores: [
			'.svelte-kit/',
			'build/',
			'node_modules/',
			'src/lib/types/openapi.ts',
			'src/lib/types/openapi-raw.json'
		]
	}
);
