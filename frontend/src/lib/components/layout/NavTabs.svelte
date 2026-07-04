<script lang="ts">
	import { page } from '$app/stores';
	import { Tabs } from 'bits-ui';

	let {
		tabs
	}: { tabs: Array<{ id: string; label: string; href: string }> } = $props();

	let activeTab = $derived(tabs.find((t) => $page.url.pathname === t.href)?.id ?? tabs[0]?.id);
</script>

<!-- Desktop: Tabs -->
<nav class="nav-tabs" aria-label="Main navigation">
	<Tabs.Root value={activeTab} class="tabs-root">
		<Tabs.List class="tabs-list">
			{#each tabs as tab (tab.id)}
				<Tabs.Trigger value={tab.id} class="tab-trigger" asChild>
					{#snippet child({ props })}
						<a
							{...props}
							href={tab.href}
							class="tab-link"
							class:tab-link--active={activeTab === tab.id}
							aria-current={activeTab === tab.id ? 'page' : undefined}
						>
							{tab.label}
						</a>
					{/snippet}
				</Tabs.Trigger>
			{/each}
		</Tabs.List>
	</Tabs.Root>
</nav>

<!-- Mobile: Select -->
<div class="nav-select">
	<label for="nav-select-input" class="sr-only">Navigate to section</label>
	<select
		id="nav-select-input"
		onchange={(e) => {
			const target = e.target as HTMLSelectElement;
			window.location.href = target.value;
		}}
	>
		{#each tabs as tab (tab.id)}
			<option value={tab.href} selected={activeTab === tab.id}>{tab.label}</option>
		{/each}
	</select>
</div>

<style>
	.nav-tabs {
		display: block;
		background: var(--surface);
		border-bottom: 1px solid var(--border);
		padding: 0 var(--sp-8);
	}
	@media (max-width: 720px) {
		.nav-tabs {
			display: none;
		}
	}
	:global(.tabs-root) {
		display: flex;
	}
	:global(.tabs-list) {
		display: flex;
		gap: 0;
	}
	.tab-link {
		display: inline-flex;
		align-items: center;
		padding: var(--sp-4) var(--sp-5);
		font-size: var(--fs-ui);
		font-weight: 500;
		color: var(--muted);
		text-decoration: none;
		border-bottom: 2px solid transparent;
		transition: color 0.15s, border-color 0.15s;
		white-space: nowrap;
		min-height: 44px;
	}
	.tab-link:hover {
		color: var(--ink);
	}
	.tab-link--active {
		color: var(--ink);
		font-weight: 700;
		border-bottom-color: var(--accent);
	}
	.nav-select {
		display: none;
		padding: var(--sp-3) var(--sp-4);
		background: var(--surface);
		border-bottom: 1px solid var(--border);
	}
	@media (max-width: 720px) {
		.nav-select {
			display: block;
		}
	}
	select {
		font-family: var(--font);
		font-size: var(--fs-ui);
		font-weight: 500;
		background: var(--surface);
		color: var(--ink);
		border: 1px solid var(--border);
		border-radius: var(--r-sm);
		padding: var(--sp-2) var(--sp-4);
		min-height: 44px;
		width: 100%;
		cursor: pointer;
	}
	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border: 0;
	}
</style>
