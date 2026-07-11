<script lang="ts">
	import { page } from '$app/state';
	import { t } from '$lib/i18n';
	import SectionLabel from '$lib/components/primitives/SectionLabel.svelte';
</script>

<svelte:head>
	<title>{$t.a11y.errorTitle} — EFI Data Engine</title>
</svelte:head>

<section class="error-page">
	<SectionLabel label="{$t.a11y.errorTitle} {page.status}" color="var(--c-red)" />
	<h1 class="error-title">{$t.a11y.errorHeading}</h1>
	<p class="error-msg">{page.error?.message ?? $t.a11y.errorGeneric}</p>
	<a href="/" class="back-link">← {$t.a11y.backToHome}</a>
</section>

<style>
	.error-page {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: var(--sp-6);
		padding: var(--sp-10);
		text-align: center;
		min-height: 60vh;
	}
	.error-title {
		font-size: var(--fs-h2);
		font-weight: 800;
		color: var(--ink);
	}
	.error-msg {
		font-size: var(--fs-body);
		color: var(--muted);
		max-width: 480px;
	}
	.back-link {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--accent);
		text-decoration: none;
	}
	.back-link:hover {
		text-decoration: underline;
	}
</style>
