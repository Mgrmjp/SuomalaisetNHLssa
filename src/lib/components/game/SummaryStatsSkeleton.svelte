<script>
// Simple Summary Stats Skeleton
</script>

<div class="stats-grid">
	{#each Array(5) as _}
		<div class="stat-card">
			<div class="stat-value"></div>
			<div class="stat-label"></div>
		</div>
	{/each}
</div>

<style>
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 1rem;
		margin-bottom: 2rem;
	}

	@media (min-width: 768px) {
		.stats-grid {
			grid-template-columns: repeat(5, 1fr);
		}
	}

	.stat-card {
		background: white;
		padding: 1rem;
		border-radius: 0.5rem;
		border: 1px solid #e5e7eb;
		text-align: center;
	}

	.stat-value {
		width: 48px;
		height: 32px;
		background: #e5e7eb;
		border-radius: 4px;
		margin: 0 auto 0.5rem;
		animation: pulse 2s infinite;
	}

	.stat-label {
		width: 64px;
		height: 16px;
		background: #f3f4f6;
		border-radius: 4px;
		margin: 0 auto;
		animation: pulse 2s infinite 0.2s;
	}

	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}
</style>