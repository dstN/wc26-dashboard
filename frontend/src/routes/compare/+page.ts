import type { PageLoad } from './$types';
import { apiBase } from '$lib/api-base';

export const load: PageLoad = async ({ fetch, url }) => {
	const type = url.searchParams.get('type') as 'teams' | 'players' | 'matches' | null;
	const idsRaw = url.searchParams.get('ids') ?? '';
	const ids = idsRaw
		.split(',')
		.map((s) => parseInt(s, 10))
		.filter((n) => !isNaN(n) && n > 0);

	const base = apiBase();

	const get = (path: string) =>
		fetch(`${base}${path}`)
			.then((r) => (r.ok ? r.json() : null))
			.catch(() => null);

	const searchOptions = await loadSearchOptions(type, get);

	if (!type || ids.length < 2) {
		return { type, ids, entities: [], error: null, searchOptions };
	}

	try {
		const entities = await Promise.all(
			ids.map((id) => {
				if (type === 'teams') {
					return Promise.all([
						get(`/api/v1/teams/${id}/general`),
						get(`/api/v1/teams/${id}/avg-stats`),
					]).then(([gen, avg]) => (gen ? { ...gen, avgStats: avg } : null));
				} else if (type === 'matches') {
					return Promise.all([
						get(`/api/v1/matches/${id}`),
						get(`/api/v1/matches/${id}/possession`),
					]).then(([meta, poss]) => (meta ? { ...meta, possession: poss } : null));
				} else {
					return get(`/api/v1/players/${id}`);
				}
			})
		);
		return { type, ids, entities: entities.filter(Boolean), error: null, searchOptions };
	} catch (err) {
		return { type, ids, entities: [], error: String(err), searchOptions };
	}
};

async function loadSearchOptions(
	type: string | null,
	get: (path: string) => Promise<any>
): Promise<Array<{ id: number; name: string; sub: string; color?: string }>> {
	if (type === 'teams') {
		const lb = await get('/api/v1/stats/leaderboards');
		return (lb?.team_rankings ?? []).map((r: any) => ({
			id: r.team.id,
			name: r.team.name,
			sub: r.team.short_code,
			color: r.team.color,
		}));
	}
	if (type === 'players') {
		const players = await get('/api/v1/players/');
		return (players ?? []).map((p: any) => ({
			id: p.id,
			name: p.name,
			sub: `${p.position ?? ''} · ${p.team?.short_code ?? ''}`,
		}));
	}
	if (type === 'matches') {
		const matches = await get('/api/v1/matches/');
		return (matches ?? []).map((m: any) => ({
			id: m.id,
			name: `${m.team_a?.short_code ?? '?'} ${m.score_a ?? '–'}–${m.score_b ?? '–'} ${m.team_b?.short_code ?? '?'}`,
			sub: `Match ${m.match_no}`,
		}));
	}
	return [];
}
