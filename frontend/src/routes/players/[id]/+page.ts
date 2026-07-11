import type { PageLoad } from './$types';
import { apiBase } from '$lib/api-base';

export const load: PageLoad = async ({ fetch, params }) => {
	const id = params.id;
	const base = apiBase();

	try {
		const [res, lbRes] = await Promise.all([
			fetch(`${base}/api/v1/players/${id}`),
			fetch(`${base}/api/v1/players/${id}/line-breaks`),
		]);
		if (!res.ok) return { player: null, error: `${res.status}` };
		const data = await res.json();
		const lineBreaks = lbRes.ok ? ((await lbRes.json()).line_breaks ?? []) : [];
		return { ...data, lineBreaks, error: null };
	} catch (err) {
		return { player: null, error: String(err) };
	}
};
