import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
	const id = params.id;
	const base = import.meta.env.SSR
		? (process.env.INTERNAL_API_URL ?? 'http://localhost:8000')
		: (import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000');

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
