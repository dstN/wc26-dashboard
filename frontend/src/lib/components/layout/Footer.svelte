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
	<div class="d-inner">
		<div class="d-head">
			<div>
				<h2>{$t.footer.impressumTitle}</h2>
				<p class="d-sub">{$t.footer.impressumSubtitle}</p>
			</div>
			<button class="d-close" onclick={() => impressumDialog.close()} aria-label={$t.footer.close}>✕</button>
		</div>

		<section class="d-section">
			<h3>{$t.footer.impressumResponsible}</h3>
			<p>
				Dustin Tramm<br>
				c/o Impressumservice Dein-Impressum<br>
				Stettiner Str. 41<br>
				35410 Hungen<br>
				Germany
			</p>
		</section>

		<section class="d-section">
			<h3>{$t.footer.impressumContactHeading}</h3>
			<p><a href="mailto:dustin.tramm@yinside.de">dustin.tramm@yinside.de</a></p>
		</section>

		<section class="d-section">
			<h3>{$t.footer.impressumDataHeading}</h3>
			<p>{$t.footer.impressumDataText}</p>
			<p class="d-fine">{$t.footer.impressumTrademarkText}</p>
		</section>
	</div>
</dialog>

<!-- ── Privacy & Legal ────────────────────────────────────────── -->
<dialog bind:this={legalDialog} onclick={(e) => closeOnBackdrop(e, legalDialog)}>
	<div class="d-inner">
		<div class="d-head">
			<h2>{$t.footer.legalTitle}</h2>
			<button class="d-close" onclick={() => legalDialog.close()} aria-label={$t.footer.close}>✕</button>
		</div>

		<section class="d-section">
			<h3>{$t.footer.privacyHeading}</h3>
			<p>{$t.footer.privacyText1}</p>
			<p>{$t.footer.privacyText2}</p>
		</section>

		<section class="d-section">
			<h3>{$t.footer.dataHeading}</h3>
			<p>{$t.footer.dataText}</p>
			<p>
				<a href="https://www.fifatrainingcentre.com/en/fifa-world-cup-2026/match-report-hub.php"
					target="_blank" rel="noopener">{$t.footer.dataSource}</a>
			</p>
		</section>

		<section class="d-section">
			<h3>{$t.footer.disclaimerHeading}</h3>
			<p>{$t.footer.disclaimerText}</p>
		</section>

		<section class="d-section">
			<h3>{$t.footer.copyrightHeading}</h3>
			<p>{$t.footer.copyrightText}</p>
		</section>
	</div>
</dialog>

<!-- ── Contact ────────────────────────────────────────────────── -->
<dialog bind:this={contactDialog} onclick={(e) => closeOnBackdrop(e, contactDialog)}>
	<div class="d-inner">
		<div class="d-head">
			<h2>{$t.footer.contactTitle}</h2>
			<button class="d-close" onclick={() => { contactDialog.close(); resetContact(); }} aria-label={$t.footer.close}>✕</button>
		</div>

		{#if contactSent}
			<p class="d-success">{$t.footer.contactSuccess}</p>
			<button class="btn-sec" onclick={resetContact}>{$t.footer.contactNewMessage}</button>
		{:else}
			<form onsubmit={submitContact}>
				<label>
					{$t.footer.contactName}
					<input type="text" bind:value={contactName} required placeholder={$t.footer.contactNamePlaceholder} />
				</label>
				<label>
					{$t.footer.contactEmail}
					<input type="email" bind:value={contactEmail} required placeholder={$t.footer.contactEmailPlaceholder} />
				</label>
				<label>
					{$t.footer.contactMessage}
					<textarea bind:value={contactMessage} required rows="4" placeholder={$t.footer.contactMessagePlaceholder}></textarea>
				</label>
				<button type="submit" class="btn-pri">{$t.footer.contactSubmit}</button>
			</form>
			<p class="d-fine">{$t.footer.contactNote}</p>
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

	/* ── Dialog positioning & backdrop ──────────────────────── */
	dialog {
		position: fixed;
		inset: 0;
		margin: auto;
		height: fit-content;
		border: none;
		border-radius: var(--r-md);
		background: var(--surface);
		color: var(--ink);
		padding: 0;
		max-width: 540px;
		width: calc(100vw - var(--sp-8));
		max-height: 82vh;
		overflow-y: auto;
		box-shadow: 0 16px 48px rgba(0, 0, 0, 0.28), 0 2px 8px rgba(0, 0, 0, 0.12);
	}

	:global(dialog::backdrop) {
		background: rgba(0, 0, 0, 0.55);
		backdrop-filter: blur(3px);
		-webkit-backdrop-filter: blur(3px);
	}

	/* ── Dialog inner layout ─────────────────────────────────── */
	.d-inner {
		padding: var(--sp-6) var(--sp-7) var(--sp-7);
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
	}

	.d-head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: var(--sp-4);
	}

	.d-head h2 {
		font-size: var(--fs-h2);
		font-weight: 800;
		color: var(--ink);
		margin: 0;
		line-height: 1.1;
	}

	.d-sub {
		font-size: var(--fs-meta);
		color: var(--muted);
		margin: var(--sp-1) 0 0;
	}

	.d-close {
		flex-shrink: 0;
		background: none;
		border: none;
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: var(--r-sm);
		font-size: var(--fs-ui);
		color: var(--muted);
		cursor: pointer;
		transition: color 0.15s, background 0.15s;
		margin-top: 2px;
	}
	.d-close:hover { color: var(--ink); background: var(--border-soft); }

	/* ── Dialog sections ─────────────────────────────────────── */
	.d-section {
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
		padding-top: var(--sp-4);
		border-top: 1px solid var(--border-soft);
	}

	.d-section h3 {
		font-size: var(--fs-label);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
		margin: 0;
	}

	.d-section p {
		font-size: var(--fs-ui);
		color: var(--ink);
		line-height: 1.6;
		margin: 0;
	}

	.d-section a {
		color: var(--accent);
		text-decoration: none;
	}
	.d-section a:hover { text-decoration: underline; }

	.d-fine {
		font-size: var(--fs-meta) !important;
		color: var(--muted) !important;
	}

	.d-success {
		font-size: var(--fs-ui);
		color: var(--positive);
		font-weight: 600;
		line-height: 1.5;
	}

	/* ── Contact form ────────────────────────────────────────── */
	form {
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
	}

	label {
		display: flex;
		flex-direction: column;
		gap: var(--sp-1);
		font-size: var(--fs-meta);
		font-weight: 700;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.07em;
	}

	input, textarea {
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
	textarea { resize: vertical; }

	.btn-pri {
		align-self: flex-start;
		background: var(--accent);
		color: var(--bg);
		border: none;
		border-radius: var(--r-md);
		padding: var(--sp-2) var(--sp-5);
		font-size: var(--fs-ui);
		font-weight: 700;
		font-family: inherit;
		cursor: pointer;
		transition: opacity 0.15s;
	}
	.btn-pri:hover { opacity: 0.85; }

	.btn-sec {
		align-self: flex-start;
		background: var(--border-soft);
		color: var(--ink);
		border: none;
		border-radius: var(--r-md);
		padding: var(--sp-2) var(--sp-4);
		font-size: var(--fs-ui);
		font-weight: 600;
		font-family: inherit;
		cursor: pointer;
		transition: background 0.15s;
	}
	.btn-sec:hover { background: var(--border); }

	@media (max-width: 480px) {
		.d-inner { padding: var(--sp-5) var(--sp-5) var(--sp-6); }
	}
</style>
