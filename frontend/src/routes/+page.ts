import type { PageLoad } from './$types';
import type { DashboardData } from '$lib/types/efi';

export const load: PageLoad = async ({ fetch }) => {
	try {
		// Use SvelteKit's fetch for SSR (handles INTERNAL_API_URL automatically via env)
		const baseUrl = import.meta.env.SSR
			? (process.env.INTERNAL_API_URL ?? 'http://localhost:8000')
			: (import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000');

		const response = await fetch(`${baseUrl}/api/v1/dashboard`);
		if (!response.ok) {
			throw new Error(`API responded with ${response.status}`);
		}
		const dashboard: DashboardData = await response.json();
		return { dashboard };
	} catch (err) {
		console.error('Failed to load dashboard:', err);
		// Return null so the page can show an error state
		return { dashboard: null as unknown as DashboardData, error: String(err) };
	}
};
