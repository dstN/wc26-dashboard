import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const base = import.meta.env.SSR
		? (process.env.INTERNAL_API_URL ?? 'http://localhost:8000')
		: (import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000');
	try {
		const [plRes, psRes, gkRes] = await Promise.all([
			fetch(`${base}/api/v1/players/`),
			fetch(`${base}/api/v1/stats/player-stats-summary`),
			fetch(`${base}/api/v1/stats/goalkeeper-rankings`),
		]);
		if (!plRes.ok) throw new Error(`${plRes.status}`);
		const players = await plRes.json();
		const playerStats: Record<string, { appearances: number; goals: number; yellow_cards: number; red_cards: number; minutes_played: number }> =
			psRes.ok ? await psRes.json() : {};
		const goalkeepers = gkRes.ok ? await gkRes.json() : [];
		return { players, playerStats, goalkeepers };
	} catch (err) {
		return { players: [], playerStats: {}, goalkeepers: [], error: String(err) };
	}
};
