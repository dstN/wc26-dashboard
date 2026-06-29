<script lang="ts">
	import { page } from '$app/stores';
	import ThemeSwitch from './ThemeSwitch.svelte';
	import { t, locale, setLocale, LOCALES, type Locale } from '$lib/i18n';

	let { matchCount = 0 }: { matchCount?: number } = $props();
	let menuOpen = $state(false);

	$effect(() => {
		$page.url.pathname;
		menuOpen = false;
	});

	const navItems = $derived([
		{ label: $t.nav.overview, href: '/' },
		{ label: $t.nav.matches, href: '/matches' },
		{ label: $t.nav.teams, href: '/teams' },
		{ label: $t.nav.players, href: '/players' },
		{ label: $t.nav.tournament, href: '/phases' }
	]);
</script>

<header class="topbar">
	<a href="/" class="topbar__brand" aria-label="EFI Data Engine — Home">
		<span class="efi-dot" aria-hidden="true"></span>
		<span class="topbar__efi">EFI</span>
		<span class="topbar__sub">DATA ENGINE</span>
	</a>
	<nav class="topbar__nav" aria-label="Main navigation">
		{#each navItems as item}
			<a
				href={item.href}
				class="topbar__link"
				class:active={$page.url.pathname === item.href}
				aria-current={$page.url.pathname === item.href ? 'page' : undefined}
			>{item.label}</a>
		{/each}
	</nav>
	<div class="topbar__right">
		<div class="lang-switcher" role="group" aria-label="Language">
			{#each LOCALES as loc}
				<button
					class="lang-btn"
					class:lang-btn--active={$locale === loc.code}
					onclick={() => setLocale(loc.code as Locale)}
					aria-label={loc.label}
					aria-pressed={$locale === loc.code}
				>{loc.label}</button>
			{/each}
		</div>
		<ThemeSwitch />
		{#if matchCount > 0}
			<span class="reports-pill" aria-label="{matchCount} match reports available">{matchCount} Reports</span>
		{/if}
		<button
			class="topbar__burger"
			aria-label={menuOpen ? 'Close menu' : 'Open menu'}
			aria-expanded={menuOpen}
			onclick={() => (menuOpen = !menuOpen)}
		>
			<span class="burger-line"></span>
			<span class="burger-line"></span>
			<span class="burger-line"></span>
		</button>
	</div>
</header>

{#if menuOpen}
	<nav class="mobile-menu" aria-label="Mobile navigation">
		{#each navItems as item}
			<a
				href={item.href}
				class="mobile-menu__link"
				class:active={$page.url.pathname === item.href}
			>{item.label}</a>
		{/each}
		<div class="mobile-menu__controls">
			<div class="lang-switcher" role="group" aria-label="Language">
				{#each LOCALES as loc}
					<button
						class="lang-btn"
						class:lang-btn--active={$locale === loc.code}
						onclick={() => { setLocale(loc.code as Locale); menuOpen = false; }}
						aria-label={loc.label}
						aria-pressed={$locale === loc.code}
					>{loc.label}</button>
				{/each}
			</div>
			<ThemeSwitch />
		</div>
	</nav>
{/if}

<style>
	.topbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0 40px;
		height: 56px;
		background: var(--surface);
		border-bottom: 1px solid var(--border);
	}
	.topbar__brand {
		display: flex;
		align-items: center;
		gap: 12px;
		flex: none;
		text-decoration: none;
	}
	.efi-dot {
		width: 22px;
		height: 22px;
		border-radius: 50%;
		background: var(--c-red);
		box-shadow:
			0 0 0 3px var(--c-orange),
			0 0 0 6px var(--c-teal),
			0 0 0 9px var(--c-blue);
		flex-shrink: 0;
	}
	.topbar__efi {
		font-size: var(--fs-ui);
		font-weight: 800;
		letter-spacing: 0.12em;
		color: var(--ink);
	}
	.topbar__sub {
		font-size: var(--fs-label);
		font-weight: 500;
		letter-spacing: 0.12em;
		color: var(--muted);
	}
	.topbar__nav {
		display: flex;
		gap: 30px;
		align-items: center;
	}
	.topbar__link {
		font-size: var(--fs-ui);
		font-weight: 500;
		color: var(--muted);
		text-decoration: none;
		padding-bottom: 2px;
		border-bottom: 2px solid transparent;
		transition: color 0.15s;
		white-space: nowrap;
	}
	.topbar__link:hover {
		color: var(--ink);
	}
	.topbar__link.active {
		color: var(--ink);
		font-weight: 700;
		border-bottom-color: var(--accent);
	}
	.topbar__right {
		display: flex;
		align-items: center;
		gap: 16px;
		flex: none;
	}
	/* ── Language switcher ───────────────────────────────────────────── */
	.lang-switcher {
		display: flex;
		align-items: center;
		border: 1px solid var(--border);
		border-radius: var(--r-pill);
		overflow: hidden;
	}
	.lang-btn {
		padding: 4px 8px;
		background: transparent;
		border: none;
		font-size: 11px;
		font-weight: 600;
		letter-spacing: 0.04em;
		color: var(--muted);
		cursor: pointer;
		transition: background 0.1s, color 0.1s;
		font-family: inherit;
		line-height: 1;
	}
	.lang-btn:hover {
		background: color-mix(in srgb, var(--ink) 6%, transparent);
		color: var(--ink);
	}
	.lang-btn--active {
		background: var(--ink);
		color: var(--bg);
	}

	.reports-pill {
		font-size: var(--fs-label);
		font-weight: 600;
		letter-spacing: 0.04em;
		padding: 6px 12px;
		border-radius: var(--r-pill);
		background: color-mix(in srgb, var(--accent) 14%, transparent);
		color: var(--accent);
	}
	/* ── Hamburger button ────────────────────────────────────────────── */
	.topbar__burger {
		display: none;
		flex-direction: column;
		justify-content: center;
		gap: 5px;
		width: 32px;
		height: 32px;
		background: transparent;
		border: none;
		cursor: pointer;
		padding: 4px;
		border-radius: var(--r-sm);
	}
	.topbar__burger:hover {
		background: color-mix(in srgb, var(--ink) 8%, transparent);
	}
	.burger-line {
		display: block;
		width: 100%;
		height: 2px;
		background: var(--ink);
		border-radius: 2px;
		transition: opacity 0.15s;
	}

	/* ── Mobile menu ─────────────────────────────────────────────────── */
	:global(.mobile-menu) {
		display: flex;
		flex-direction: column;
		background: var(--surface);
		border-bottom: 1px solid var(--border);
		padding: var(--sp-2) 0;
	}
	:global(.mobile-menu__link) {
		padding: var(--sp-4) var(--sp-6);
		font-size: var(--fs-ui);
		font-weight: 500;
		color: var(--muted);
		text-decoration: none;
		border-inline-start: 3px solid transparent;
		transition: color 0.12s, background 0.12s;
	}
	:global(.mobile-menu__link:hover) {
		color: var(--ink);
		background: color-mix(in srgb, var(--ink) 4%, transparent);
	}
	:global(.mobile-menu__link.active) {
		color: var(--ink);
		font-weight: 700;
		border-inline-start-color: var(--accent);
		background: color-mix(in srgb, var(--accent) 6%, transparent);
	}

	@media (max-width: 960px) {
		.topbar__nav { display: none; }
		.topbar__burger { display: flex; }
		/* Hide these from the topbar only — they reappear inside the mobile menu */
		.topbar__right .lang-switcher,
		.reports-pill { display: none; }
	}

	/* ── Mobile menu controls row ─────────────────────────────────────── */
	:global(.mobile-menu__controls) {
		display: flex;
		align-items: center;
		gap: var(--sp-4);
		padding: var(--sp-3) var(--sp-6);
		border-top: 1px solid var(--border);
		margin-top: var(--sp-1);
	}
</style>
