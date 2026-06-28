<script lang="ts">
	import { t } from '$lib/i18n';

	let impressumDialog: HTMLDialogElement;
	let legalDialog: HTMLDialogElement;
	let contactDialog: HTMLDialogElement;

	let contactName = $state('');
	let contactEmail = $state('');
	let contactMessage = $state('');
	let contactSent = $state(false);

	function closeOnBackdrop(e: MouseEvent, dialog: HTMLDialogElement) {
		if (e.target === dialog) dialog.close();
	}

	function submitContact(e: SubmitEvent) {
		e.preventDefault();
		const subject = encodeURIComponent('EFI Dashboard — Contact');
		const body = encodeURIComponent(`Name: ${contactName}\nEmail: ${contactEmail}\n\n${contactMessage}`);
		window.location.href = `mailto:dustin.tramm@yinside.de?subject=${subject}&body=${body}`;
		contactSent = true;
	}

	function resetContact() {
		contactSent = false;
		contactName = '';
		contactEmail = '';
		contactMessage = '';
	}
</script>

<footer>
	<button onclick={() => impressumDialog.showModal()}>{$t.footer.impressum}</button>
	<span class="sep">·</span>
	<button onclick={() => legalDialog.showModal()}>{$t.footer.legal}</button>
	<span class="sep">·</span>
	<button onclick={() => contactDialog.showModal()}>{$t.footer.contact}</button>
</footer>

<!-- ── Impressum ──────────────────────────────────────────────── -->
<dialog bind:this={impressumDialog} onclick={(e) => closeOnBackdrop(e, impressumDialog)}>
	<div class="modal">
		<button class="modal__close" onclick={() => impressumDialog.close()} aria-label={$t.footer.close}>
			<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
				<path d="M1 1l12 12M13 1L1 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
			</svg>
		</button>

		<h2 class="modal__title">{$t.footer.impressumTitle}</h2>
		<p class="modal__subtitle">{$t.footer.impressumSubtitle}</p>

		<div class="modal__section">
			<p class="modal__label">{$t.footer.impressumResponsible}</p>
			<p class="modal__body">
				Dustin Tramm<br>
				c/o Impressumservice Dein-Impressum<br>
				Stettiner Str. 41<br>
				35410 Hungen<br>
				Germany
			</p>
		</div>

		<div class="modal__section">
			<p class="modal__label">{$t.footer.impressumContactHeading}</p>
			<p class="modal__body">
				<a href="mailto:dustin.tramm@yinside.de">dustin.tramm@yinside.de</a>
			</p>
		</div>

		<div class="modal__section">
			<p class="modal__label">{$t.footer.impressumDataHeading}</p>
			<p class="modal__body">{$t.footer.impressumDataText}</p>
			<p class="modal__fine">{$t.footer.impressumTrademarkText}</p>
		</div>
	</div>
</dialog>

<!-- ── Privacy & Legal ────────────────────────────────────────── -->
<dialog bind:this={legalDialog} onclick={(e) => closeOnBackdrop(e, legalDialog)}>
	<div class="modal">
		<button class="modal__close" onclick={() => legalDialog.close()} aria-label={$t.footer.close}>
			<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
				<path d="M1 1l12 12M13 1L1 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
			</svg>
		</button>

		<h2 class="modal__title">{$t.footer.legalTitle}</h2>

		<div class="modal__section">
			<p class="modal__label">{$t.footer.privacyHeading}</p>
			<p class="modal__body">{$t.footer.privacyText1}</p>
			<p class="modal__body">{$t.footer.privacyText2}</p>
		</div>

		<div class="modal__section">
			<p class="modal__label">{$t.footer.dataHeading}</p>
			<p class="modal__body">{$t.footer.dataText}</p>
			<p class="modal__body">
				<a href="https://www.fifatrainingcentre.com/en/fifa-world-cup-2026/match-report-hub.php"
					target="_blank" rel="noopener">{$t.footer.dataSource} ↗</a>
			</p>
		</div>

		<div class="modal__section">
			<p class="modal__label">{$t.footer.disclaimerHeading}</p>
			<p class="modal__body">{$t.footer.disclaimerText}</p>
		</div>

		<div class="modal__section">
			<p class="modal__label">{$t.footer.copyrightHeading}</p>
			<p class="modal__body">{$t.footer.copyrightText}</p>
		</div>
	</div>
</dialog>

<!-- ── Contact ────────────────────────────────────────────────── -->
<dialog bind:this={contactDialog} onclick={(e) => closeOnBackdrop(e, contactDialog)}>
	<div class="modal">
		<button class="modal__close" onclick={() => { contactDialog.close(); resetContact(); }} aria-label={$t.footer.close}>
			<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
				<path d="M1 1l12 12M13 1L1 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
			</svg>
		</button>

		<h2 class="modal__title">{$t.footer.contactTitle}</h2>

		{#if contactSent}
			<div class="modal__section">
				<p class="modal__success">{$t.footer.contactSuccess}</p>
				<button class="btn-sec" onclick={resetContact}>{$t.footer.contactNewMessage}</button>
			</div>
		{:else}
			<div class="modal__section">
				<form onsubmit={submitContact}>
					<div class="field">
						<label for="cf-name">{$t.footer.contactName}</label>
						<input id="cf-name" type="text" bind:value={contactName} required placeholder={$t.footer.contactNamePlaceholder} />
					</div>
					<div class="field">
						<label for="cf-email">{$t.footer.contactEmail}</label>
						<input id="cf-email" type="email" bind:value={contactEmail} required placeholder={$t.footer.contactEmailPlaceholder} />
					</div>
					<div class="field">
						<label for="cf-msg">{$t.footer.contactMessage}</label>
						<textarea id="cf-msg" bind:value={contactMessage} required rows="4" placeholder={$t.footer.contactMessagePlaceholder}></textarea>
					</div>
					<div class="form-footer">
						<button type="submit" class="btn-pri">{$t.footer.contactSubmit}</button>
						<p class="modal__fine">{$t.footer.contactNote}</p>
					</div>
				</form>
			</div>
		{/if}
	</div>
</dialog>

<style>
	/* ── Footer bar ──────────────────────────────────────────── */
	footer {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--sp-2);
		padding: var(--sp-5) var(--sp-4);
		border-top: 1px solid var(--border-soft);
	}

	footer button {
		background: none;
		border: none;
		padding: 0;
		font-size: var(--fs-meta);
		color: var(--muted);
		cursor: pointer;
		font-family: inherit;
		transition: color 0.15s;
	}
	footer button:hover { color: var(--ink); }

	.sep {
		font-size: var(--fs-meta);
		color: var(--border);
		user-select: none;
	}

	/* ── Dialog shell ────────────────────────────────────────── */
	:global(dialog::backdrop) {
		background: rgba(0, 0, 0, 0.6);
		backdrop-filter: blur(4px);
		-webkit-backdrop-filter: blur(4px);
	}

	dialog {
		position: fixed;
		inset: 0;
		margin: auto;
		height: fit-content;
		border: 1px solid var(--border);
		border-radius: var(--r-md);
		background: var(--surface);
		padding: 0;
		max-width: 520px;
		width: calc(100vw - var(--sp-8));
		max-height: 82vh;
		overflow-y: auto;
		box-shadow: 0 24px 64px rgba(0, 0, 0, 0.35), 0 4px 16px rgba(0, 0, 0, 0.15);
	}

	/* ── Modal inner ─────────────────────────────────────────── */
	.modal {
		position: relative;
		padding: var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-6);
	}

	.modal__close {
		position: absolute;
		top: var(--sp-5);
		right: var(--sp-5);
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: none;
		border: none;
		border-radius: var(--r-sm);
		color: var(--muted);
		cursor: pointer;
		transition: color 0.15s, background 0.15s;
		flex-shrink: 0;
	}
	.modal__close:hover {
		color: var(--ink);
		background: var(--border-soft);
	}

	.modal__title {
		font-size: var(--fs-h2);
		font-weight: 800;
		color: var(--ink);
		margin: 0;
		padding-right: var(--sp-8);
		line-height: 1.1;
	}

	.modal__subtitle {
		margin: calc(-1 * var(--sp-4)) 0 0;
		font-size: var(--fs-meta);
		color: var(--muted);
	}

	/* ── Sections ────────────────────────────────────────────── */
	.modal__section {
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
		padding-top: var(--sp-5);
		border-top: 1px solid var(--border-soft);
	}

	.modal__label {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--muted);
		margin: 0;
	}

	.modal__body {
		font-size: var(--fs-ui);
		color: var(--ink);
		line-height: 1.65;
		margin: 0;
	}

	.modal__body a {
		color: var(--accent);
		text-decoration: none;
	}
	.modal__body a:hover { text-decoration: underline; }

	.modal__fine {
		font-size: var(--fs-meta);
		color: var(--muted);
		line-height: 1.5;
		margin: 0;
	}

	.modal__success {
		font-size: var(--fs-ui);
		color: var(--positive);
		font-weight: 600;
		line-height: 1.5;
		margin: 0;
	}

	/* ── Contact form ────────────────────────────────────────── */
	form {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: var(--sp-1);
	}

	.field label {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}

	input, textarea {
		width: 100%;
		box-sizing: border-box;
		background: var(--bg);
		border: 1px solid var(--border);
		border-radius: var(--r-sm);
		padding: var(--sp-2) var(--sp-3);
		font-size: var(--fs-ui);
		font-family: inherit;
		color: var(--ink);
		transition: border-color 0.15s, box-shadow 0.15s;
	}
	input:focus, textarea:focus {
		outline: none;
		border-color: var(--accent);
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 20%, transparent);
	}
	textarea { resize: vertical; min-height: 100px; }

	.form-footer {
		display: flex;
		align-items: center;
		gap: var(--sp-4);
		flex-wrap: wrap;
		padding-top: var(--sp-2);
	}

	.btn-pri {
		flex-shrink: 0;
		background: var(--accent);
		color: var(--bg);
		border: none;
		border-radius: var(--r-sm);
		padding: var(--sp-2) var(--sp-5);
		font-size: var(--fs-ui);
		font-weight: 700;
		font-family: inherit;
		cursor: pointer;
		transition: opacity 0.15s;
		white-space: nowrap;
	}
	.btn-pri:hover { opacity: 0.85; }

	.btn-sec {
		background: var(--border-soft);
		color: var(--ink);
		border: none;
		border-radius: var(--r-sm);
		padding: var(--sp-2) var(--sp-4);
		font-size: var(--fs-ui);
		font-weight: 600;
		font-family: inherit;
		cursor: pointer;
		transition: background 0.15s;
		align-self: flex-start;
	}
	.btn-sec:hover { background: var(--border); }

	@media (max-width: 480px) {
		.modal { padding: var(--sp-6); }
	}
</style>
