import { browser } from '$app/environment';
import { env as publicEnv } from '$env/dynamic/public';

const FALLBACK = 'http://localhost:8000';

/**
 * Resolve the API base URL for the current execution context.
 *
 * - **Browser:** `PUBLIC_API_URL` via `$env/dynamic/public` (runtime-resolved by
 *   adapter-node from the process env). This MUST go through `$env` — Vite only
 *   exposes `VITE_`-prefixed vars on `import.meta.env`, so `import.meta.env.PUBLIC_API_URL`
 *   is always `undefined` in the client bundle and would silently fall back to localhost.
 * - **SSR:** `INTERNAL_API_URL` — the server-only, internal-network backend URL.
 *
 * Centralized here so the base-URL resolution lives in exactly one place
 * (used by every `+page.ts` load and the admin upload form).
 */
export function apiBase(): string {
	if (browser) {
		return publicEnv.PUBLIC_API_URL ?? FALLBACK;
	}
	return process.env.INTERNAL_API_URL ?? FALLBACK;
}
