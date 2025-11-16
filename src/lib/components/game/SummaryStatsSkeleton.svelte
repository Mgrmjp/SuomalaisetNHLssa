<div class="stats-grid">
	{#each Array(5) as _}
		<div class="stat-card">
			<div class="stat-icon"></div>
			<div class="stat-value"></div>
			<div class="stat-label"></div>
		</div>
	{/each}
</div>

<style>
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 1rem;
		margin-bottom: 2rem;
	}

	@media (min-width: 768px) {
		.stats-grid {
			grid-template-columns: repeat(5, minmax(0, 1fr));
		}
	}

	.stat-card {
		position: relative;
		text-align: center;
		padding: 1rem;
		border-radius: 14px;
		border: 1px solid rgba(226, 232, 240, 0.9);
		background: linear-gradient(145deg, rgba(255, 255, 255, 0.92), rgba(241, 245, 249, 0.96));
		box-shadow:
			0 10px 24px rgba(15, 23, 42, 0.08),
			inset 0 1px 0 rgba(255, 255, 255, 0.65);
		overflow: hidden;
	}

	.stat-card::before {
		content: '';
		position: absolute;
		inset: 0;
		background: radial-gradient(90% 70% at 0 0, rgba(59, 130, 246, 0.08), transparent 55%),
			radial-gradient(90% 70% at 100% 0, rgba(99, 102, 241, 0.08), transparent 55%);
		pointer-events: none;
	}

	.stat-icon,
	.stat-value,
	.stat-label {
		position: relative;
		overflow: hidden;
		background: #e5e7eb;
		border-radius: 12px;
	}

	.stat-icon {
		width: 36px;
		height: 36px;
		margin: 0 auto 0.55rem;
		border-radius: 999px;
		background: linear-gradient(135deg, #e5e7eb, #f1f5f9);
	}

	.stat-value {
		width: 52px;
		height: 26px;
		margin: 0 auto 0.4rem;
	}

	.stat-label {
		width: 70px;
		height: 12px;
		border-radius: 999px;
		background: #f1f5f9;
		margin: 0 auto;
	}

	/* Shimmer */
	.stat-icon::after,
	.stat-value::after,
	.stat-label::after {
		content: '';
		position: absolute;
		inset: 0;
		transform: translateX(-100%);
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.75), transparent);
		animation: shimmer 1.8s infinite;
	}

	@keyframes shimmer {
		100% {
			transform: translateX(100%);
		}
	}
</style>
