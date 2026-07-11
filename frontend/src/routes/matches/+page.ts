import type { PageLoad } from './$types';
import { apiBase } from '$lib/api-base';

export const load: PageLoad = async ({ fetch }) => {
	try {
		const base = apiBase();
		const res = await fetch(`${base}/api/v1/matches`);
		if (!res.ok) throw new Error(`${res.status}`);
		const matches = await res.json();
		return { matches };
	} catch (err) {
		return { matches: [], error: String(err) };
	}
};
