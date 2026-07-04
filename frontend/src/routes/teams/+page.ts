import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	try {
		const base = import.meta.env.SSR
			? (process.env.INTERNAL_API_URL ?? 'http://localhost:8000')
			: (import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000');
		const [teamsRes, lbRes] = await Promise.all([
			fetch(`${base}/api/v1/teams/`),
			fetch(`${base}/api/v1/stats/leaderboards`),
		]);
		if (!teamsRes.ok) throw new Error(`${teamsRes.status}`);
		const teams = await teamsRes.json();
		const leaderboards = lbRes.ok ? await lbRes.json() : null;
		return { teams, leaderboards };
	} catch (err) {
		return { teams: [], leaderboards: null, error: String(err) };
	}
};
