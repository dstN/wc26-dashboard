import type { LayoutLoad } from './$types';
import { apiBase } from '$lib/api-base';

export const load: LayoutLoad = async ({ fetch }) => {
	const base = apiBase();

	try {
		const r = await fetch(`${base}/api/v1/matches/`);
		const matches = r.ok ? await r.json() : [];
		return { matchCount: Array.isArray(matches) ? matches.length : 0 };
	} catch {
		return { matchCount: 0 };
	}
};
