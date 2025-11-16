<script>
// Pull names from prepopulated game JSON files
const gameFiles = import.meta.glob('../../../data/prepopulated/games/*.json', {
	eager: true,
	import: 'default'
})

const weightSteps = [500, 600, 700, 800]

function hashString(input) {
	let hash = 0
	for (let i = 0; i < input.length; i++) {
		hash = (hash << 5) - hash + input.charCodeAt(i)
		hash |= 0
	}
	return hash
}

const nameSet = new Set()
Object.values(gameFiles).forEach((file) => {
	const players = Array.isArray(file?.players) ? file.players : []
	players.forEach((p) => {
		if (p?.name) {
			nameSet.add(p.name)
		}
	})
})

const playerNames = Array.from(nameSet).slice(0, 120)

// Build lightweight entries with deterministic weight per name
const patternEntries = [...playerNames, ...playerNames].map((name, idx) => {
	const weight = weightSteps[Math.abs(hashString(name)) % weightSteps.length]
	return {
		name,
		offset: (idx % 3) * 6,
		rotation: -6,
		weight
	}
})
</script>

<div class="player-pattern" aria-hidden="true">
	{#each patternEntries as entry}
		<span
			class="player-pattern__name"
			style={`--pat-offset:${entry.offset}px;--pat-rot:${entry.rotation}deg;--pat-weight:${entry.weight};`}
		>
			{entry.name}
		</span>
	{/each}
</div>

<style>
	.player-pattern {
		position: fixed;
		inset: 0;
		pointer-events: none;
		z-index: 0;
		opacity: 0.08;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
		gap: 28px 24px;
		padding: 48px 32px;
		background: radial-gradient(circle at 10% 10%, rgba(255, 255, 255, 0.4), transparent 35%),
			radial-gradient(circle at 90% 30%, rgba(255, 255, 255, 0.25), transparent 30%),
			linear-gradient(135deg, rgba(15, 23, 42, 0.06), rgba(15, 23, 42, 0.12));
	}

	.player-pattern__name {
		font-size: 0.85rem;
		font-weight: var(--pat-weight, 700);
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: #0f172a;
		mix-blend-mode: multiply;
		transform: translateY(var(--pat-offset)) rotate(var(--pat-rot, -6deg));
	}

	@media (max-width: 640px) {
		.player-pattern {
			grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
			gap: 16px;
			padding: 28px 16px;
		}

		.player-pattern__name {
			font-size: 0.75rem;
			letter-spacing: 0.06em;
			transform: translateY(calc(var(--pat-offset) * 0.66)) rotate(calc(var(--pat-rot, -6deg) * 0.66));
		}
	}
</style>
