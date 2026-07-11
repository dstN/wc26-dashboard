import type { PageLoad } from './$types';
import { apiBase } from '$lib/api-base';

export const load: PageLoad = async ({ fetch, params }) => {
	const id = params.id;
	const base = apiBase();

	const get = (path: string) =>
		fetch(`${base}${path}`)
			.then((r) => (r.ok ? r.json() : null))
			.catch(() => null);

	try {
		const [
			match, possession, phases, spatial, lineBreaks, finalThird,
			defensive, keyStats, shots, passingNetwork, crosses, offerings, movement, pressure, gkStats,
			playerNameMap, lineup
		] = await Promise.all([
			get(`/api/v1/matches/${id}`),
			get(`/api/v1/matches/${id}/possession`),
			get(`/api/v1/matches/${id}/phases`),
			get(`/api/v1/matches/${id}/spatial`),
			get(`/api/v1/matches/${id}/line-breaks`),
			get(`/api/v1/matches/${id}/final-third`),
			get(`/api/v1/matches/${id}/defensive`),
			get(`/api/v1/matches/${id}/key-stats`),
			get(`/api/v1/matches/${id}/shots`),
			get(`/api/v1/matches/${id}/passing-network`),
			get(`/api/v1/matches/${id}/crosses`),
			get(`/api/v1/matches/${id}/offerings`),
			get(`/api/v1/matches/${id}/movement`),
			get(`/api/v1/matches/${id}/pressure`),
			get(`/api/v1/matches/${id}/gk-stats`),
			get(`/api/v1/matches/${id}/player-name-map`),
			get(`/api/v1/matches/${id}/lineup`),
		]);

		if (!match) {
			return { error: 'Match not found', match: null };
		}

		return {
			match, possession, phases, spatial, lineBreaks, finalThird,
			defensive, keyStats, shots, passingNetwork, crosses, offerings, movement, pressure, gkStats,
			playerNameMap: (playerNameMap ?? {}) as Record<string, number>,
			lineup: lineup ?? null,
		};
	} catch (err) {
		return { error: String(err), match: null };
	}
};
