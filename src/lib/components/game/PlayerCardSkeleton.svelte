<script>
// Simple Player Card Skeleton
</script>

<div class="skeleton-card">
	<div class="skeleton-header">
		<div class="skeleton-name"></div>
		<div class="skeleton-details"></div>
	</div>

	<div class="skeleton-logo"></div>

	<div class="skeleton-stats">
		<div class="skeleton-stat"></div>
		<div class="skeleton-stat"></div>
		<div class="skeleton-stat"></div>
	</div>

	<div class="skeleton-game">
		<div class="skeleton-score"></div>
	</div>
</div>

<style>
	.skeleton-card {
		background: white;
		border-radius: 0.5rem;
		padding: 1rem;
		height: 280px;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
		position: relative;
		display: flex;
		flex-direction: column;
	}

	.skeleton-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 3rem;
	}

	.skeleton-name {
		width: 120px;
		height: 24px;
		background: #e5e7eb;
		border-radius: 4px;
		animation: pulse 2s infinite;
	}

	.skeleton-details {
		width: 160px;
		height: 16px;
		background: #f3f4f6;
		border-radius: 4px;
		margin-top: 8px;
		animation: pulse 2s infinite 0.2s;
	}

	.skeleton-logo {
		width: 48px;
		height: 48px;
		background: #f3f4f6;
		border-radius: 50%;
		animation: pulse 2s infinite 0.1s;
	}

	.skeleton-stats {
		display: flex;
		justify-content: space-around;
		margin-bottom: 2rem;
		flex: 1;
	}

	.skeleton-stat {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 4px;
	}

	.skeleton-stat::before {
		content: '';
		width: 32px;
		height: 20px;
		background: #d1d5db;
		border-radius: 4px;
		animation: pulse 2s infinite;
	}

	.skeleton-stat::after {
		content: '';
		width: 48px;
		height: 12px;
		background: #e5e7eb;
		border-radius: 4px;
		animation: pulse 2s infinite 0.3s;
	}

	.skeleton-game {
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 1rem;
		background: #f9fafb;
		border-radius: 0.25rem;
	}

	.skeleton-score {
		width: 60px;
		height: 24px;
		background: #d1d5db;
		border-radius: 4px;
		animation: pulse 2s infinite 0.4s;
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