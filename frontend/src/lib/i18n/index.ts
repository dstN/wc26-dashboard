import { writable, derived } from 'svelte/store';
import en from './en';
import de from './de';
import es from './es';
import pt from './pt';
import fr from './fr';
import ar from './ar';

export type Locale = 'en' | 'de' | 'es' | 'pt' | 'fr' | 'ar';

export const LOCALES: { code: Locale; label: string; dir: 'ltr' | 'rtl' }[] = [
	{ code: 'en', label: 'EN', dir: 'ltr' },
	{ code: 'de', label: 'DE', dir: 'ltr' },
	{ code: 'es', label: 'ES', dir: 'ltr' },
	{ code: 'pt', label: 'PT', dir: 'ltr' },
	{ code: 'fr', label: 'FR', dir: 'ltr' },
	{ code: 'ar', label: 'AR', dir: 'rtl' },
];

const translations = { en, de, es, pt, fr, ar } as const;

function getInitialLocale(): Locale {
	if (typeof localStorage === 'undefined') return 'en';
	const saved = localStorage.getItem('efi-locale') as Locale | null;
	if (saved && saved in translations) return saved;
	const browser = navigator.language.slice(0, 2) as Locale;
	return browser in translations ? browser : 'en';
}

export const locale = writable<Locale>('en');

export function setLocale(l: Locale) {
	locale.set(l);
	if (typeof localStorage !== 'undefined') localStorage.setItem('efi-locale', l);
	const dir = LOCALES.find((x) => x.code === l)?.dir ?? 'ltr';
	document.documentElement.setAttribute('dir', dir);
	document.documentElement.setAttribute('lang', l);
}

export function initLocale() {
	const l = getInitialLocale();
	setLocale(l);
}

export const t = derived(locale, ($locale) => translations[$locale]);
