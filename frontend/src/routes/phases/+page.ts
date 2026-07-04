import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	try {
		const base = import.meta.env.SSR
			? (process.env.INTERNAL_API_URL ?? 'http://localhost:8000')
			: (import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000');
		const res = await fetch(`${base}/api/v1/overview`);
		if (!res.ok) throw new Error(`${res.status}`);
		const overview = await res.json();
		return { overview };
	} catch (err) {
		return { overview: null, error: String(err) };
	}
};
