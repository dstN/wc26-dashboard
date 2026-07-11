import type { PageLoad } from './$types';
import { apiBase } from '$lib/api-base';

export const load: PageLoad = async ({ fetch }) => {
	try {
		const base = apiBase();
		const res = await fetch(`${base}/api/v1/overview`);
		if (!res.ok) throw new Error(`${res.status}`);
		const overview = await res.json();
		return { overview };
	} catch (err) {
		return { overview: null, error: String(err) };
	}
};
