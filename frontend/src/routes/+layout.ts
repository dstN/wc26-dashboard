import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ fetch }) => {
	const base = import.meta.env.SSR
		? (process.env.INTERNAL_API_URL ?? 'http://localhost:8000')
		: (import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000');

	try {
		const r = await fetch(`${base}/api/v1/matches/`);
		const matches = r.ok ? await r.json() : [];
		return { matchCount: Array.isArray(matches) ? matches.length : 0 };
	} catch {
		return { matchCount: 0 };
	}
};
