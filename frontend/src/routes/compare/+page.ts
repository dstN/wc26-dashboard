import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, url }) => {
	const type = url.searchParams.get('type') as 'teams' | 'players' | null;
	const idsRaw = url.searchParams.get('ids') ?? '';
	const ids = idsRaw
		.split(',')
		.map((s) => parseInt(s, 10))
		.filter((n) => !isNaN(n) && n > 0);

	const base = import.meta.env.SSR
		? (process.env.INTERNAL_API_URL ?? 'http://localhost:8000')
		: (import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000');

	const get = (path: string) =>
		fetch(`${base}${path}`)
			.then((r) => (r.ok ? r.json() : null))
			.catch(() => null);

	if (!type || ids.length < 2) {
		return { type, ids, entities: [], error: null };
	}

	try {
		const entities = await Promise.all(
			ids.map((id) =>
				type === 'teams'
					? Promise.all([get(`/api/v1/teams/${id}/general`), get(`/api/v1/teams/${id}/avg-stats`)]).then(
							([gen, avg]) => (gen ? { ...gen, avgStats: avg } : null)
					  )
					: get(`/api/v1/players/${id}`)
			)
		);
		return { type, ids, entities: entities.filter(Boolean), error: null };
	} catch (err) {
		return { type, ids, entities: [], error: String(err) };
	}
};
