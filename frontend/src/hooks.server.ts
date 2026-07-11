import type { Handle } from '@sveltejs/kit';

// Locales the app ships; ar is the only RTL one. Kept in sync with
// $lib/i18n (LOCALES) but duplicated here to avoid importing client store code
// into the server hook.
const KNOWN = new Set(['en', 'de', 'es', 'pt', 'fr', 'ar']);
const RTL = new Set(['ar']);

/**
 * Server-side locale resolution: read the `efi-locale` cookie and stamp the
 * correct `lang`/`dir` into the served HTML (WCAG 3.1.1 Language of Page,
 * 1.3.2). Previously `<html lang="en">` was hardcoded and only corrected after
 * hydration, so a DE/AR user (or a no-JS/SEO/screen-reader client) always saw
 * English LTR. Falls back to en/ltr for first-time visitors.
 */
export const handle: Handle = async ({ event, resolve }) => {
	const cookie = event.cookies.get('efi-locale');
	const locale = cookie && KNOWN.has(cookie) ? cookie : 'en';
	const dir = RTL.has(locale) ? 'rtl' : 'ltr';

	return resolve(event, {
		transformPageChunk: ({ html }) =>
			html.replace('%lang%', locale).replace('%dir%', dir)
	});
};
