import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
	const id = params.id;
	const base = import.meta.env.SSR
		? (process.env.INTERNAL_API_URL ?? 'http://localhost:8000')
		: (import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000');

	const get = (path: string) =>
		fetch(`${base}${path}`)
			.then((r) => (r.ok ? r.json() : null))
			.catch(() => null);

	try {
		const [general, matches, players, phases, playerStats, avgStats] = await Promise.all([
			get(`/api/v1/teams/${id}/general`),
			get(`/api/v1/teams/${id}/matches`),
			get(`/api/v1/teams/${id}/players`),
			get(`/api/v1/teams/${id}/phases`),
			get(`/api/v1/stats/player-stats-summary?team_id=${id}`),
			get(`/api/v1/teams/${id}/avg-stats`),
		]);

		if (!general) return { error: 'Team not found', team: null };
		return {
			team: general.team,
			stats: general.stats,
			matches: matches ?? [],
			players: players ?? [],
			phases: phases ?? [],
			playerStats: playerStats ?? {},
			avgStats: avgStats ?? null,
		};
	} catch (err) {
		return { error: String(err), team: null };
	}
};
