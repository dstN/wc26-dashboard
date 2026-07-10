<script lang="ts">
	import { browser } from '$app/environment';
	import { t } from '$lib/i18n';

	const KEY_STORAGE = 'efi_ingest_key';

	let apiKey = $state(browser ? (localStorage.getItem(KEY_STORAGE) ?? '') : '');
	let rememberKey = $state(browser ? !!localStorage.getItem(KEY_STORAGE) : false);
	let file: File | null = $state(null);
	let status: 'idle' | 'uploading' | 'ok' | 'error' = $state('idle');
	let log = $state('');
	let errorMsg = $state('');

	const apiBase = browser
		? (import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000')
		: '';

	function onFileChange(e: Event) {
		const input = e.currentTarget as HTMLInputElement;
		file = input.files?.[0] ?? null;
		status = 'idle';
		log = '';
		errorMsg = '';
	}

	async function upload() {
		if (!file || !apiKey) return;

		if (rememberKey) {
			localStorage.setItem(KEY_STORAGE, apiKey);
		} else {
			localStorage.removeItem(KEY_STORAGE);
		}

		status = 'uploading';
		log = '';
		errorMsg = '';

		const form = new FormData();
		form.append('file', file);

		try {
			const res = await fetch(`${apiBase}/api/v1/ingest/upload`, {
				method: 'POST',
				headers: { Authorization: `Bearer ${apiKey}` },
				body: form,
			});

			const data = await res.json().catch(() => null);

			if (res.ok) {
				status = 'ok';
				log = data?.log ?? '';
			} else {
				status = 'error';
				const detail = data?.detail;
				if (typeof detail === 'object' && detail !== null) {
					errorMsg = detail.message ?? $t.admin.unknownError;
					log = detail.log ?? '';
				} else {
					errorMsg = detail ?? `HTTP ${res.status}`;
				}
			}
		} catch (err) {
			status = 'error';
			errorMsg = `${$t.admin.networkError}: ${err}`;
		}
	}
</script>

<svelte:head>
	<title>{$t.admin.pageTitle}</title>
</svelte:head>

<div class="admin-page">
	<div class="admin-card">
		<div class="admin-header">
			<span class="admin-lock" aria-hidden="true">🔒</span>
			<div>
				<h1 class="admin-title">{$t.admin.title}</h1>
				<p class="admin-sub">{$t.admin.subtitle}</p>
			</div>
		</div>

		<form class="upload-form" onsubmit={(e) => { e.preventDefault(); upload(); }}>
			<!-- API Key -->
			<div class="field">
				<label class="field__label" for="apikey">{$t.admin.apiKey}</label>
				<input
					id="apikey"
					type="password"
					class="field__input"
					placeholder={$t.admin.apiKeyPlaceholder}
					bind:value={apiKey}
					autocomplete="current-password"
				/>
				<label class="field__check">
					<input type="checkbox" bind:checked={rememberKey} />
					{$t.admin.rememberKey}
				</label>
			</div>

			<!-- File picker -->
			<div class="field">
				<label class="field__label" for="pdffile">{$t.admin.pdfFile}</label>
				<div class="file-drop" class:file-drop--selected={!!file}>
					<input
						id="pdffile"
						type="file"
						accept=".pdf,application/pdf"
						class="file-drop__input"
						onchange={onFileChange}
					/>
					{#if file}
						<span class="file-drop__name">{file.name}</span>
						<span class="file-drop__size">{(file.size / 1024).toFixed(0)} KB</span>
					{:else}
						<span class="file-drop__hint">{$t.admin.dropHint}</span>
					{/if}
				</div>
			</div>

			<!-- Submit -->
			<button
				type="submit"
				class="btn-upload"
				disabled={!file || !apiKey || status === 'uploading'}
			>
				{#if status === 'uploading'}
					<span class="spinner" aria-hidden="true"></span>
					{$t.admin.uploading}
				{:else}
					{$t.admin.submit}
				{/if}
			</button>
		</form>

		<!-- Result -->
		{#if status === 'ok'}
			<div class="result result--ok">
				<p class="result__title">✓ {$t.admin.successTitle}</p>
				{#if log}<pre class="result__log">{log}</pre>{/if}
			</div>
		{:else if status === 'error'}
			<div class="result result--error">
				<p class="result__title">✗ {$t.admin.errorTitle}: {errorMsg}</p>
				{#if log}<pre class="result__log">{log}</pre>{/if}
			</div>
		{/if}

		<p class="admin-cron-hint">
			{$t.admin.cronHint} <code>PDF_WATCH_DIR</code>
		</p>
	</div>
</div>

<style>
	.admin-page {
		min-height: 100vh;
		display: flex;
		align-items: flex-start;
		justify-content: center;
		padding: var(--sp-10) var(--sp-4);
		background: var(--bg);
	}

	.admin-card {
		width: 100%;
		max-width: 560px;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--r-lg);
		padding: var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-6);
	}

	.admin-header {
		display: flex;
		align-items: flex-start;
		gap: var(--sp-4);
	}
	.admin-lock {
		font-size: 2rem;
		line-height: 1;
		flex-shrink: 0;
	}
	.admin-title {
		font-size: var(--fs-h1);
		font-weight: 800;
		color: var(--ink);
		margin: 0;
	}
	.admin-sub {
		font-size: var(--fs-ui);
		color: var(--muted);
		margin: var(--sp-1) 0 0;
	}

	/* Form */
	.upload-form {
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
	}
	.field__label {
		font-size: var(--fs-ui);
		font-weight: 700;
		color: var(--ink);
	}
	.field__input {
		padding: var(--sp-3) var(--sp-4);
		border: 1px solid var(--border);
		border-radius: var(--r-sm);
		background: var(--bg);
		color: var(--ink);
		font-size: var(--fs-ui);
		font-family: inherit;
		outline: none;
		transition: border-color 0.15s;
	}
	.field__input:focus {
		border-color: var(--accent);
	}
	.field__check {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		font-size: var(--fs-meta);
		color: var(--muted);
		cursor: pointer;
	}

	/* File drop zone */
	.file-drop {
		position: relative;
		border: 2px dashed var(--border);
		border-radius: var(--r-md);
		padding: var(--sp-6) var(--sp-4);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--sp-2);
		cursor: pointer;
		transition: border-color 0.15s, background 0.15s;
	}
	.file-drop:hover,
	.file-drop--selected {
		border-color: var(--accent);
		background: color-mix(in srgb, var(--accent) 4%, transparent);
	}
	.file-drop__input {
		position: absolute;
		inset: 0;
		opacity: 0;
		cursor: pointer;
		width: 100%;
		height: 100%;
	}
	.file-drop__hint {
		font-size: var(--fs-ui);
		color: var(--muted);
	}
	.file-drop__name {
		font-size: var(--fs-ui);
		font-weight: 700;
		color: var(--ink);
		word-break: break-all;
		text-align: center;
	}
	.file-drop__size {
		font-size: var(--fs-meta);
		color: var(--muted);
	}

	/* Submit button */
	.btn-upload {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--sp-3);
		padding: var(--sp-4) var(--sp-6);
		background: var(--accent);
		color: var(--accent-fg);
		border: none;
		border-radius: var(--r-md);
		font-size: var(--fs-ui);
		font-weight: 700;
		font-family: inherit;
		cursor: pointer;
		transition: opacity 0.15s;
	}
	.btn-upload:disabled {
		opacity: 0.45;
		cursor: not-allowed;
	}
	.btn-upload:not(:disabled):hover {
		opacity: 0.85;
	}

	/* Spinner */
	.spinner {
		width: 16px;
		height: 16px;
		border: 2px solid rgba(255, 255, 255, 0.35);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 0.7s linear infinite;
		flex-shrink: 0;
	}
	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	/* Result */
	.result {
		border-radius: var(--r-md);
		padding: var(--sp-4) var(--sp-5);
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
	}
	.result--ok {
		background: color-mix(in srgb, var(--positive) 10%, transparent);
		border: 1px solid color-mix(in srgb, var(--positive) 30%, transparent);
	}
	.result--error {
		background: color-mix(in srgb, var(--c-red) 10%, transparent);
		border: 1px solid color-mix(in srgb, var(--c-red) 30%, transparent);
	}
	.result__title {
		font-size: var(--fs-ui);
		font-weight: 700;
		color: var(--ink);
		margin: 0;
	}
	.result__log {
		font-size: 12px;
		font-family: var(--font-mono, monospace);
		color: var(--muted);
		white-space: pre-wrap;
		word-break: break-word;
		margin: 0;
		max-height: 300px;
		overflow-y: auto;
		background: var(--bg);
		border: 1px solid var(--border);
		border-radius: var(--r-sm);
		padding: var(--sp-3);
	}

	/* Cron hint */
	.admin-cron-hint {
		font-size: var(--fs-meta);
		color: var(--muted);
		border-top: 1px solid var(--border);
		padding-top: var(--sp-4);
		margin: 0;
		line-height: 1.5;
	}
	.admin-cron-hint code {
		background: color-mix(in srgb, var(--ink) 8%, transparent);
		border-radius: var(--r-sm);
		padding: 1px 5px;
		font-size: 11px;
	}
</style>
