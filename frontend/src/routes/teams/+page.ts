import type { PageLoad } from './$types';
import { apiBase } from '$lib/api-base';

export const load: PageLoad = async ({ fetch, url }) => {
	const stage = url.searchParams.get('stage'); // 'group' | 'knockout' | null (= all)
	const base = apiBase();
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
