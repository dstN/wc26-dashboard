<script lang="ts">
	let { label, color = 'var(--muted)' }: { label: string; color?: string } = $props();
</script>

<p class="label" style="color: {color}">{label}</p>

<style>
	.label {
		font-size: var(--fs-label);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}
</style>
