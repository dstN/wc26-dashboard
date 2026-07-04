let theme = $state<'light' | 'dark'>(
	typeof document !== 'undefined'
		? ((document.documentElement.getAttribute('data-theme') as 'light' | 'dark') ?? 'light')
		: 'light'
);

export function getTheme(): 'light' | 'dark' {
	return theme;
}

export function toggleTheme() {
	theme = theme === 'light' ? 'dark' : 'light';
	if (typeof document !== 'undefined') {
		document.documentElement.setAttribute('data-theme', theme);
		localStorage.setItem('efi-theme', theme);
	}
}
