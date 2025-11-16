<div class="skeleton-card">
	<div class="skeleton-border-outer"></div>
	<div class="skeleton-border-inner"></div>

	<div class="skeleton-content">
		<div class="skeleton-top">
			<div class="skeleton-avatar"></div>
			<div class="skeleton-headings">
				<div class="skeleton-line skeleton-line--wide"></div>
				<div class="skeleton-pill"></div>
				<div class="skeleton-line skeleton-line--narrow"></div>
			</div>
			<div class="skeleton-logo"></div>
		</div>

		<div class="skeleton-divider"></div>

		<div class="skeleton-stats">
			{#each Array(4) as _}
				<div class="skeleton-stat">
					<div class="skeleton-chip"></div>
					<div class="skeleton-line skeleton-line--compact"></div>
				</div>
			{/each}
		</div>

		<div class="skeleton-game">
			<div class="skeleton-team">
				<div class="skeleton-dot"></div>
				<div class="skeleton-line skeleton-line--compact"></div>
			</div>
			<div class="skeleton-score"></div>
			<div class="skeleton-team skeleton-team--right">
				<div class="skeleton-line skeleton-line--compact"></div>
				<div class="skeleton-dot"></div>
			</div>
		</div>
	</div>
</div>

<style>
	:global(:root) {
		--skeleton-surface: linear-gradient(145deg, rgba(255, 255, 255, 0.92), rgba(248, 250, 252, 0.95));
		--skeleton-border: rgba(226, 232, 240, 0.7);
		--skeleton-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
		--skeleton-highlight: rgba(59, 130, 246, 0.12);
		--skeleton-muted: #e5e7eb;
		--skeleton-muted-2: #f1f5f9;
		--skeleton-accent: #cbd5e1;
	}

	.skeleton-card {
		position: relative;
		height: 280px;
		border-radius: 12px;
		overflow: hidden;
	}

	.skeleton-border-outer,
	.skeleton-border-inner {
		position: absolute;
		inset: 0;
		border-radius: 12px;
		pointer-events: none;
	}

	.skeleton-border-outer {
		border: 1px solid var(--skeleton-border);
		box-shadow: var(--skeleton-shadow);
		background: radial-gradient(120% 80% at 0% 0%, rgba(59, 130, 246, 0.08), transparent 55%),
			radial-gradient(120% 80% at 100% 0%, rgba(99, 102, 241, 0.08), transparent 55%);
	}

	.skeleton-border-inner {
		inset: 6px;
		border-radius: 10px;
		background: var(--skeleton-surface);
		border: 1px solid rgba(255, 255, 255, 0.7);
	}

	.skeleton-content {
		position: relative;
		z-index: 1;
		height: 100%;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.skeleton-top {
		display: grid;
		grid-template-columns: auto 1fr auto;
		align-items: center;
		gap: 0.75rem;
	}

	.skeleton-avatar {
		width: 52px;
		height: 52px;
		border-radius: 12px;
		background: linear-gradient(135deg, var(--skeleton-muted), var(--skeleton-muted-2));
		position: relative;
		overflow: hidden;
	}

	.skeleton-headings {
		display: grid;
		gap: 0.4rem;
	}

	.skeleton-logo {
		width: 44px;
		height: 44px;
		border-radius: 12px;
		background: linear-gradient(135deg, var(--skeleton-muted-2), var(--skeleton-muted));
		position: relative;
		overflow: hidden;
	}

	.skeleton-line,
	.skeleton-pill,
	.skeleton-chip,
	.skeleton-dot,
	.skeleton-score {
		position: relative;
		overflow: hidden;
		border-radius: 999px;
		background: var(--skeleton-muted);
	}

	.skeleton-line {
		height: 10px;
		border-radius: 6px;
	}

	.skeleton-line--wide {
		width: 70%;
	}

	.skeleton-line--narrow {
		width: 40%;
	}

	.skeleton-line--compact {
		width: 46px;
		height: 8px;
	}

	.skeleton-pill {
		width: 96px;
		height: 14px;
		border-radius: 999px;
		background: var(--skeleton-muted-2);
	}

	.skeleton-stats {
		display: grid;
		grid-template-columns: repeat(4, minmax(0, 1fr));
		gap: 0.75rem;
	}

	.skeleton-stat {
		display: grid;
		gap: 0.4rem;
		justify-items: center;
		padding: 0.65rem 0.5rem;
		border-radius: 10px;
		background: linear-gradient(145deg, rgba(255, 255, 255, 0.9), rgba(248, 250, 252, 0.95));
		box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6), 0 1px 0 rgba(226, 232, 240, 0.6);
	}

	.skeleton-chip {
		width: 34px;
		height: 18px;
		border-radius: 8px;
		background: var(--skeleton-accent);
	}

	.skeleton-game {
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem;
		border-radius: 10px;
		background: linear-gradient(145deg, rgba(226, 232, 240, 0.45), rgba(241, 245, 249, 0.7));
		border: 1px solid rgba(226, 232, 240, 0.8);
		box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
	}

	.skeleton-team {
		display: flex;
		align-items: center;
		gap: 0.45rem;
	}

	.skeleton-team--right {
		justify-content: flex-end;
	}

	.skeleton-dot {
		width: 10px;
		height: 10px;
		border-radius: 999px;
		background: var(--skeleton-accent);
	}

	.skeleton-divider {
		height: 1px;
		background: linear-gradient(90deg, transparent, rgba(226, 232, 240, 0.9), transparent);
	}

	.skeleton-score {
		width: 64px;
		height: 24px;
		border-radius: 10px;
		background: var(--skeleton-accent);
	}

	/* Shimmer effect */
	.skeleton-card :global(.shimmer)::after,
	.skeleton-line::after,
	.skeleton-pill::after,
	.skeleton-chip::after,
	.skeleton-dot::after,
	.skeleton-score::after,
	.skeleton-avatar::after,
	.skeleton-logo::after {
		content: '';
		position: absolute;
		inset: 0;
		transform: translateX(-100%);
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.65), transparent);
		animation: shimmer 1.8s infinite;
	}

	@keyframes shimmer {
		100% {
			transform: translateX(100%);
		}
	}
</style>
