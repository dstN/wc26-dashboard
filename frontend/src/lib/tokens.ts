/** Maps FIFA 3-letter short_code to ISO 3166-1 alpha-2 used by flag-icons */
const FIFA_TO_ISO2: Record<string, string> = {
	ALG: 'dz', ARG: 'ar', AUS: 'au', AUT: 'at', BEL: 'be', BIH: 'ba',
	BRA: 'br', CPV: 'cv', CAN: 'ca', COL: 'co', COD: 'cd', CIV: 'ci',
	CRO: 'hr', CZE: 'cz', ECU: 'ec', EGY: 'eg', ENG: 'gb-eng', FRA: 'fr',
	GHA: 'gh', HAI: 'ht', IRN: 'ir', IRQ: 'iq', JPN: 'jp', JOR: 'jo',
	KOR: 'kr', MEX: 'mx', MAR: 'ma', NED: 'nl', NZL: 'nz', NOR: 'no',
	PAN: 'pa', PAR: 'py', POR: 'pt', QAT: 'qa', KSA: 'sa', SCO: 'gb-sct',
	SEN: 'sn', RSA: 'za', ESP: 'es', SWE: 'se', SUI: 'ch', TUN: 'tn',
	TUR: 'tr', URU: 'uy', USA: 'us', UZB: 'uz', GER: 'de', CUR: 'cw',
	GER2: 'de'
};

/** Returns the ISO-2 code for flag-icons CSS class (fi fi-{code}), or empty string. */
export function flagCode(short_code: string): string {
	return FIFA_TO_ISO2[short_code] ?? '';
}

// Maps real DB phase_name values to CSS variable names (theme-agnostic)
const IN_POSSESSION_COLORS: Record<string, string> = {
	'Build Up Unopposed': '--c-teal',
	'Build Up Opposed':   '--c-indigo',
	'Progression':        '--c-blue',
	'Final Third':        '--c-lime',
	'Long Ball':          '--c-orange',
	'Attacking Transition': '--c-red',
	'Counter Attack':     '--c-pink',
	'Set Piece':          '--c-lavender'
};

const OUT_POSSESSION_COLORS: Record<string, string> = {
	'High Press':          '--c-red',
	'Mid Press':           '--c-orange',
	'Low Press':           '--c-yellow',
	'High Block':          '--c-teal',
	'Mid Block':           '--c-blue',
	'Low Block':           '--c-indigo',
	'Recovery':            '--c-lime',
	'Defensive Transition':'--c-lavender',
	'Counter-press':       '--c-pink'
};

export function phaseColor(name: string): string {
	const cssVar = IN_POSSESSION_COLORS[name] ?? OUT_POSSESSION_COLORS[name] ?? '--c-muted';
	return `var(${cssVar})`;
}

export function teamColorVar(color: string): string {
	if (color.startsWith('--')) return `var(${color})`;
	return color;
}

/** Colors that need dark text when used as a badge background */
const LIGHT_BG_COLORS = new Set(['--c-yellow', '--c-lime', '--c-teal', '--c-orange', '--c-lavender', '--c-pink']);

/** Returns the correct text color for a colored badge background */
export function badgeTextColor(color: string): string {
	return LIGHT_BG_COLORS.has(color) ? '#0c1a10' : '#ffffff';
}

/** Returns a version of the team color that is readable as text on both light and dark surfaces. */
export function teamTextColor(color: string): string {
	if (color === '--c-yellow')   return 'var(--c-yellow-ink)';
	if (color === '--c-lime')     return 'var(--c-lime-ink)';
	if (color === '--c-lavender') return 'var(--c-lavender-ink)';
	if (color === '--c-pink')     return 'var(--c-pink-ink)';
	if (color.startsWith('--'))   return `var(${color})`;
	return color;
}
