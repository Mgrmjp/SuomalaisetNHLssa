<script>
export const count = 50
export const delayRange = 15
export const minDuration = 8
export const maxDuration = 20

const _flakes = Array.from({ length: count }, (_, i) => ({
    index: i,
    delay: Math.random() * delayRange,
    duration: minDuration + Math.random() * (maxDuration - minDuration),
    horizontalDrift: (Math.random() - 0.5) * 100, // More natural horizontal drift
    size: 2 + Math.random() * 4, // More size variation
    opacity: 0.2 + Math.random() * 0.5, // More opacity variation
    amplitude: 10 + Math.random() * 20, // Sway amplitude
    frequency: 0.5 + Math.random() * 1, // Sway frequency
    rotationSpeed: (Math.random() - 0.5) * 2, // Gentle rotation
}))
</script>

<div class="snowfall pointer-events-none" aria-hidden="true">
	{#each _flakes as flake}
		<span
			class="snowflake"
			style={`
				--i:${flake.index};
				--delay:${flake.delay}s;
				--dur:${flake.duration}s;
				--drift:${flake.horizontalDrift}px;
				--size:${flake.size}px;
				--op:${flake.opacity};
				--amp:${flake.amplitude}px;
				--freq:${flake.frequency}s;
				--rot:${flake.rotationSpeed}s;
				--start-x:${(flake.index * 137.5) % 100}%; // Better distribution
			`}
		></span>
	{/each}
</div>

<style>
	.snowfall {
		position: fixed;
		inset: 0;
		overflow: hidden;
		z-index: -1; /* Behind all content */
		pointer-events: none;
	}

	.snowflake {
		position: absolute;
		left: var(--start-x);
		top: -20px;
		width: var(--size);
		height: var(--size);
		background: radial-gradient(circle at 30% 30%,
			rgba(255, 255, 255, 0.9) 0%,
			rgba(245, 248, 255, 0.8) 40%,
			rgba(220, 230, 240, 0.6) 100%);
		border: none;
		border-radius: 50%;
		box-shadow:
			0 0 3px rgba(255, 255, 255, 0.4),
			0 0 6px rgba(200, 210, 220, 0.2);
		opacity: 0;
		will-change: transform, opacity;
		backface-visibility: hidden;
	}

	/* Complex realistic snowfall animation */
	@keyframes snowfall-fall {
		0% {
			transform:
				translate3d(0, -20px, 0)
				rotate(0deg);
			opacity: 0;
		}
		5% {
			opacity: var(--op);
		}
		10% {
			transform:
				translate3d(
					calc(sin(0s) * var(--amp)),
					10vh,
					0
				)
				rotate(calc(var(--rot) * 36deg));
		}
		25% {
			transform:
				translate3d(
					calc(sin(0.25s / var(--freq)) * var(--amp)),
					25vh,
					0
				)
				rotate(calc(var(--rot) * 90deg));
		}
		50% {
			transform:
				translate3d(
					calc(sin(0.5s / var(--freq)) * var(--amp)),
					50vh,
					0
				)
				rotate(calc(var(--rot) * 180deg));
		}
		75% {
			transform:
				translate3d(
					calc(sin(0.75s / var(--freq)) * var(--amp)),
					75vh,
					0
				)
				rotate(calc(var(--rot) * 270deg));
		}
		95% {
			transform:
				translate3d(
					calc(sin(1s / var(--freq)) * var(--amp)),
					95vh,
					0
				)
				rotate(calc(var(--rot) * 360deg));
			opacity: var(--op);
		}
		100% {
			transform:
				translate3d(
					calc(sin(1s / var(--freq)) * var(--amp) + var(--drift)),
					110vh,
					0
				)
				rotate(calc(var(--rot) * 400deg));
			opacity: 0;
		}
	}

	/* Apply animation with realistic timing */
	.snowflake {
		animation: snowfall-fall var(--dur) ease-in-out infinite;
		animation-delay: var(--delay);
	}

	/* Vary snowflake sizes */
	.snowflake:nth-child(3n) {
		--size: 1px;
		opacity: 0.3;
	}

	.snowflake:nth-child(3n+1) {
		--size: 2px;
		opacity: 0.5;
	}

	.snowflake:nth-child(3n+2) {
		--size: 3px;
		opacity: 0.7;
	}

	/* Subtle glow effect */
	.snowflake::after {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: radial-gradient(circle at 30% 30%,
			rgba(255, 255, 255, 0.6) 0%,
			transparent 70%);
		border-radius: 50%;
		opacity: 0.5;
	}

	
	/* Performance optimization for mobile */
	@media (max-width: 768px) {
		.snowflake {
			will-change: transform;
		}
	}
</style>
