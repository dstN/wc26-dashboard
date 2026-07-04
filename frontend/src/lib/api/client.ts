import { browser } from '$app/environment';
import { env } from '$env/dynamic/public';

function getBaseUrl(): string {
	if (browser) {
		return env.PUBLIC_API_URL ?? 'http://localhost:8000';
	}
	// Server-side: use INTERNAL_API_URL via process.env (set in Docker)
	return process.env.INTERNAL_API_URL ?? env.PUBLIC_API_URL ?? 'http://localhost:8000';
}

export async function apiFetch<T>(path: string, fetchFn: typeof fetch = fetch): Promise<T> {
	const url = `${getBaseUrl()}${path}`;
	const response = await fetchFn(url);
	if (!response.ok) {
		throw new Error(`API error ${response.status}: ${url}`);
	}
	return response.json() as Promise<T>;
}
