import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, url }) => {
	const stage = url.searchParams.get('stage'); // 'group' | 'knockout' | null (= all)
	const base = import.meta.env.SSR
		? (process.env.INTERNAL_API_URL ?? 'http://localhost:8000')
		: (import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000');
	const qs = stage ? `?stage=${stage}` : '';
	try {
		const lbRes = await fetch(`${base}/api/v1/stats/leaderboards${qs}`);
		if (!lbRes.ok) throw new Error(`${lbRes.status}`);
		const leaderboards = await lbRes.json();
		return { leaderboards, stage };
	} catch (err) {
		return { leaderboards: null, stage, error: String(err) };
	}
};
