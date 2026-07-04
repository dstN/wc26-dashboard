<div class="motif-clip" aria-hidden="true">
	<div class="motif"></div>
	<span class="numeral">26</span>
</div>

<style>
	.motif-clip {
		position: relative;
		overflow: hidden;
		width: 100%;
		height: 100%;
		background: #0b0b0f;
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 200px;
	}
	.motif {
		width: 190px;
		height: 104px;
		border-radius: var(--r-pill);
		background: var(--c-red);
		box-shadow:
			0 0 0 28px #ff5b1e,
			0 0 0 56px #ffd23f,
			0 0 0 84px #b6e62e,
			0 0 0 112px #16c5a8,
			0 0 0 140px #2a57e8,
			0 0 0 168px #6a2ee0,
			0 0 0 196px #a78bfa,
			0 0 0 224px #ff7e9d,
			0 0 0 252px #da1e37,
			0 0 0 280px #ff5b1e,
			0 0 0 308px #ffd23f,
			0 0 0 336px #b6e62e;
		position: relative;
		z-index: 1;
	}
	.numeral {
		position: absolute;
		bottom: 22px;
		left: 28px;
		font-size: var(--fs-numeral);
		font-weight: 900;
		color: white;
		z-index: 2;
		pointer-events: none;
		user-select: none;
		line-height: 0.8;
		letter-spacing: -0.04em;
	}
</style>
