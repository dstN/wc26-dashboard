<script lang="ts">
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
		const subject = encodeURIComponent('EFI Dashboard — Kontaktanfrage');
		const body = encodeURIComponent(`Name: ${contactName}\nE-Mail: ${contactEmail}\n\n${contactMessage}`);
		window.location.href = `mailto:dustin.tramm@yinside.de?subject=${subject}&body=${body}`;
		contactSent = true;
	}
</script>

<footer>
	<button onclick={() => impressumDialog.showModal()}>Impressum</button>
	<span class="sep">·</span>
	<button onclick={() => legalDialog.showModal()}>Datenschutz & Legal</button>
	<span class="sep">·</span>
	<button onclick={() => contactDialog.showModal()}>Kontakt</button>
</footer>

<!-- ── Impressum ──────────────────────────────────────────────── -->
<dialog bind:this={impressumDialog} onclick={(e) => closeOnBackdrop(e, impressumDialog)}>
	<div class="dialog-inner">
		<button class="dialog-close" onclick={() => impressumDialog.close()} aria-label="Schließen">✕</button>
		<h2>Impressum</h2>
		<p class="dialog-hint">Angaben gemäß § 5 DDG</p>

		<h3>Verantwortlich</h3>
		<p>
			Dustin Tramm<br>
			c/o Impressumservice Dein-Impressum<br>
			Stettiner Str. 41<br>
			35410 Hungen<br>
			Germany
		</p>

		<h3>Kontakt</h3>
		<p>
			E-Mail: <a href="mailto:dustin.tramm@yinside.de">dustin.tramm@yinside.de</a>
		</p>

		<h3>Hinweis zu Datenmaterial</h3>
		<p>
			Dieses Dashboard ist ein nicht-kommerzielles Forschungs- und Demonstrationsprojekt.
			Die dargestellten Statistiken basieren auf offiziellen FIFA Match Performance Stats Reports
			(PMSR) der FIFA WC 2026 Gruppenphase. Dieses Projekt steht in keiner Verbindung zur FIFA
			oder einem ihrer Partner. Alle Daten werden ohne Gewähr bereitgestellt.
		</p>

		<p class="dialog-small">
			&quot;FIFA&quot; und damit verbundene Marken sind eingetragene Markenzeichen der
			Fédération Internationale de Football Association. Die Verwendung erfolgt ausschließlich
			zu nicht-kommerziellen, informativen Zwecken.
		</p>
	</div>
</dialog>

<!-- ── Datenschutz & Legal ────────────────────────────────────── -->
<dialog bind:this={legalDialog} onclick={(e) => closeOnBackdrop(e, legalDialog)}>
	<div class="dialog-inner">
		<button class="dialog-close" onclick={() => legalDialog.close()} aria-label="Schließen">✕</button>
		<h2>Datenschutz &amp; Legal</h2>

		<h3>Datenschutzerklärung</h3>
		<p>
			Dieses Dashboard erhebt keine personenbezogenen Daten. Es werden keine Cookies gesetzt,
			kein Tracking durchgeführt und keine Nutzerdaten gespeichert oder weitergegeben.
		</p>
		<p>
			Das Kontaktformular öffnet Ihren lokalen E-Mail-Client — es werden keine Daten an
			unsere Server übertragen.
		</p>

		<h3>Datenmaterial</h3>
		<p>
			Die dargestellten Statistiken basieren auf den offiziellen EFI Match Performance Stats
			Reports (PMSR) zur WC 2026 Gruppenphase, die von der FIFA öffentlich und ohne
			Zugangsbeschränkung zum freien Download bereitgestellt werden.
		</p>
		<p>
			Quelle: <a href="https://www.fifatrainingcentre.com/en/fifa-world-cup-2026/match-report-hub.php" target="_blank" rel="noopener">FIFA Training Centre — Match Report Hub</a>
		</p>

		<h3>Haftungsausschluss</h3>
		<p>
			Alle Inhalte werden ohne Gewähr bereitgestellt. Für die Richtigkeit, Vollständigkeit
			und Aktualität der Daten übernehmen wir keine Haftung. Dieses Projekt ist weder von
			der FIFA autorisiert noch mit ihr verbunden.
		</p>

		<h3>Urheberrecht</h3>
		<p>
			Der Quellcode dieses Dashboards ist urheberrechtlich geschützt.
			Die zugrundeliegenden Statistikdaten sind Eigentum der FIFA.
		</p>
	</div>
</dialog>

<!-- ── Kontakt ────────────────────────────────────────────────── -->
<dialog bind:this={contactDialog} onclick={(e) => closeOnBackdrop(e, contactDialog)}>
	<div class="dialog-inner">
		<button class="dialog-close" onclick={() => { contactDialog.close(); contactSent = false; }} aria-label="Schließen">✕</button>
		<h2>Kontakt</h2>

		{#if contactSent}
			<p class="dialog-success">
				Ihr E-Mail-Client wurde geöffnet. Vielen Dank für Ihre Nachricht.
			</p>
			<button class="btn-secondary" onclick={() => { contactSent = false; contactName = ''; contactEmail = ''; contactMessage = ''; }}>
				Neue Nachricht
			</button>
		{:else}
			<form onsubmit={submitContact}>
				<label>
					Name
					<input type="text" bind:value={contactName} required placeholder="Ihr Name" />
				</label>
				<label>
					E-Mail
					<input type="email" bind:value={contactEmail} required placeholder="ihre@email.de" />
				</label>
				<label>
					Nachricht
					<textarea bind:value={contactMessage} required rows="4" placeholder="Ihre Nachricht…"></textarea>
				</label>
				<button type="submit" class="btn-primary">Nachricht senden</button>
			</form>
			<p class="dialog-small">Öffnet Ihren lokalen E-Mail-Client. Es werden keine Daten an Server übertragen.</p>
		{/if}
	</div>
</dialog>

<style>
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

	/* ── Dialog base ─────────────────────────────────────────── */
	dialog {
		border: none;
		border-radius: var(--r-md);
		background: var(--surface);
		color: var(--ink);
		padding: 0;
		max-width: 520px;
		width: calc(100vw - var(--sp-8));
		max-height: 80vh;
		overflow-y: auto;
		box-shadow: 0 8px 40px rgba(0,0,0,0.18);
	}
	dialog::backdrop {
		background: rgba(0,0,0,0.45);
		backdrop-filter: blur(2px);
	}

	.dialog-inner {
		padding: var(--sp-7) var(--sp-7) var(--sp-6);
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
		position: relative;
	}

	.dialog-close {
		position: absolute;
		top: var(--sp-4);
		right: var(--sp-4);
		background: none;
		border: none;
		font-size: var(--fs-ui);
		color: var(--muted);
		cursor: pointer;
		line-height: 1;
		padding: var(--sp-1);
		border-radius: var(--r-sm);
		transition: color 0.15s, background 0.15s;
	}
	.dialog-close:hover { color: var(--ink); background: var(--border-soft); }

	.dialog-inner h2 {
		font-size: var(--fs-h2);
		font-weight: 800;
		color: var(--ink);
		margin: 0;
		padding-right: var(--sp-8);
	}
	.dialog-inner h3 {
		font-size: var(--fs-ui);
		font-weight: 700;
		color: var(--ink);
		margin: var(--sp-2) 0 0;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		font-size: var(--fs-label);
	}
	.dialog-inner p {
		font-size: var(--fs-ui);
		color: var(--muted);
		line-height: 1.6;
		margin: 0;
	}
	.dialog-inner a {
		color: var(--accent);
		text-decoration: none;
	}
	.dialog-inner a:hover { text-decoration: underline; }

	.dialog-hint {
		font-size: var(--fs-meta);
		color: var(--muted);
		margin-top: calc(-1 * var(--sp-2));
	}
	.dialog-small {
		font-size: var(--fs-meta) !important;
	}
	.dialog-success {
		color: var(--positive) !important;
		font-weight: 600;
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
		font-weight: 600;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	input, textarea {
		background: var(--bg);
		border: 1px solid var(--border);
		border-radius: var(--r-sm);
		padding: var(--sp-2) var(--sp-3);
		font-size: var(--fs-ui);
		font-family: inherit;
		color: var(--ink);
		transition: border-color 0.15s;
	}
	input:focus, textarea:focus {
		outline: none;
		border-color: var(--accent);
	}
	textarea { resize: vertical; }

	.btn-primary {
		background: var(--accent);
		color: var(--bg);
		border: none;
		border-radius: var(--r-md);
		padding: var(--sp-3) var(--sp-5);
		font-size: var(--fs-ui);
		font-weight: 700;
		font-family: inherit;
		cursor: pointer;
		align-self: flex-start;
		transition: opacity 0.15s;
	}
	.btn-primary:hover { opacity: 0.85; }

	.btn-secondary {
		background: var(--border-soft);
		color: var(--ink);
		border: none;
		border-radius: var(--r-md);
		padding: var(--sp-2) var(--sp-4);
		font-size: var(--fs-ui);
		font-weight: 600;
		font-family: inherit;
		cursor: pointer;
		align-self: flex-start;
		transition: background 0.15s;
	}
	.btn-secondary:hover { background: var(--border); }
</style>
