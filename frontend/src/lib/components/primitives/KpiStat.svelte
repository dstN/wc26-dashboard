<script lang="ts">
	let {
		label,
		value,
		unit = '',
		color = ''
	}: { label: string; value: string | number; unit?: string; color?: string } = $props();
</script>

<div class="kpi">
	<p class="kpi__label">{label}</p>
	<p class="kpi__value" style={color ? `color: ${color}` : ''}>
		<span class="tabular">{value}</span>{#if unit}<span class="kpi__unit">{unit}</span>{/if}
	</p>
</div>

<style>
	.kpi {
		display: flex;
		flex-direction: column;
		gap: var(--sp-1);
	}
	.kpi__label {
		font-size: var(--fs-label);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--muted);
	}
	.kpi__value {
		font-size: var(--fs-stat);
		font-weight: 800;
		color: var(--ink);
		line-height: 1;
	}
	.tabular {
		font-variant-numeric: tabular-nums;
	}
	.kpi__unit {
		font-size: var(--fs-h2);
		font-weight: 600;
		color: var(--muted);
		margin-left: 2px;
	}
</style>
