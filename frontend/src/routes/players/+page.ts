import type { PageLoad } from './$types';
import { apiBase } from '$lib/api-base';

export const load: PageLoad = async ({ fetch, url }) => {
	const stage = url.searchParams.get('stage'); // 'group' | 'knockout' | null (= all)
	const base = apiBase();
	const qs = stage ? `?stage=${stage}` : '';
	try {
		// Player identities (roster) never change by stage — only the stats do.
		const [plRes, psRes, gkRes] = await Promise.all([
			fetch(`${base}/api/v1/players/`),
			fetch(`${base}/api/v1/stats/player-stats-summary${qs}`),
			fetch(`${base}/api/v1/stats/goalkeeper-rankings${qs}`),
		]);
		if (!plRes.ok) throw new Error(`${plRes.status}`);
		const players = await plRes.json();
		const playerStats: Record<string, { appearances: number; goals: number; yellow_cards: number; red_cards: number; minutes_played: number }> =
			psRes.ok ? await psRes.json() : {};
		const goalkeepers = gkRes.ok ? await gkRes.json() : [];
		return { players, playerStats, goalkeepers, stage };
	} catch (err) {
		return { players: [], playerStats: {}, goalkeepers: [], stage, error: String(err) };
	}
};
