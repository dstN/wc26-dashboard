import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config';

export default mergeConfig(
	viteConfig,
	defineConfig({
		resolve: {
			conditions: ['browser']
		},
		test: {
			environment: 'happy-dom',
			globals: true,
			include: ['src/**/*.test.ts', 'src/**/*.svelte.test.ts'],
			exclude: ['e2e/**', 'node_modules/**'],
			setupFiles: ['src/vitest-setup-client.ts']
		}
	})
);
