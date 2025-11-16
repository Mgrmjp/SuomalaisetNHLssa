<script>
	export let count = 35
	export let delayRange = 6
	export let minDuration = 12

	const flakes = Array.from({ length: count }, (_, i) => ({
		index: i,
		delay: Math.random() * delayRange,
		duration: minDuration + Math.random() * 8,
		drift: (Math.random() - 0.5) * 18,
		size: 3 + Math.random() * 1.5,
		opacity: 0.35 + Math.random() * 0.25,
	}))
</script>

<div class="snowfall pointer-events-none" aria-hidden="true">
	{#each flakes as flake}
		<span
			class="snowflake"
			style={`--i:${flake.index};--delay:${flake.delay}s;--dur:${flake.duration}s;--drift:${flake.drift}px;--size:${flake.size}px;--op:${flake.opacity}`}
		/>
	{/each}
</div>

<style>
	.snowfall {
		position: fixed;
		inset: 0;
		overflow: hidden;
		z-index: 0;
	}

	.snowflake {
		position: absolute;
		left: calc(var(--i) * 3%);
		top: -10px;
		width: var(--size);
		height: var(--size);
		background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(226, 232, 240, 0.85));
		border: 1px solid rgba(148, 163, 184, 0.3);
		border-radius: 999px;
		box-shadow:
			0 0 6px rgba(148, 163, 184, 0.28),
			0 0 0 1px rgba(255, 255, 255, 0.6);
		opacity: var(--op);
		animation: snowfall var(--dur) linear infinite;
		animation-delay: var(--delay);
		filter: drop-shadow(0 2px 4px rgba(15, 23, 42, 0.12));
	}

	@keyframes snowfall {
		0% {
			transform: translate3d(0, -20px, 0);
			opacity: 0;
		}
		10% {
			opacity: var(--op);
		}
		90% {
			opacity: var(--op);
		}
		100% {
			transform: translate3d(var(--drift), 110vh, 0);
			opacity: 0;
		}
	}
</style>
