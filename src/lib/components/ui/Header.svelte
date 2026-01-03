<script>
import { browser } from '$app/environment'
import { setDate } from '$lib/stores/gameData.js'

$: headerHeight = browser ? (window.innerWidth < 768 ? '60px' : '64px') : '64px'

let showMobileMenu = false
let isMenuOpen = false

function toggleMobileMenu() {
    showMobileMenu = !showMobileMenu
    isMenuOpen = !isMenuOpen
}

// Close mobile menu when clicking outside
function _handleClickOutside(event) {
    if (showMobileMenu && !event.target.closest('.mobile-menu-content')) {
        toggleMobileMenu()
    }
}

function _goToToday() {
    // Navigate to today's date
    const today = new Date().toISOString().split('T')[0]
    setDate(today)
    isMenuOpen = false // Close mobile menu after navigation
}
</script>

<svelte:window on:click={_handleClickOutside} />

<header class="noise-overlay-dark bg-finnish-blue-900 text-white py-4 shadow-lg transition-all duration-300 hover:shadow-xl">
	<nav class="container mx-auto px-4" aria-label="Päävalikko">
		<div class="flex items-center justify-between">
			<!-- Logo -->
			<div class="flex items-center space-x-3 group">
				<h1 class="text-xl font-bold font-sans transition-colors duration-300 group-hover:text-finnish-gold-300">Suomalaiset NHL-pelaajat</h1>
			</div>

			<!-- Controls -->
			<div class="hidden md:flex items-center space-x-3">
				<!-- Space for future controls -->
			</div>
			
			<!-- Mobile Menu Toggle -->
			<button
				class="md:hidden p-2 rounded-lg bg-white/10 backdrop-blur-sm border border-white/25 text-white hover:bg-white/20 transition-all duration-300 group"
				aria-label="Avaa valikko"
				aria-expanded={isMenuOpen}
				on:click={toggleMobileMenu}
			>
				{#if isMenuOpen}
					<svg class="w-6 h-6 transition-transform duration-300 group-hover:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				{:else}
					<svg class="w-6 h-6 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				{/if}
			</button>
		</div>

		<!-- Mobile Menu Content -->
		{#if showMobileMenu}
			<div class="md:hidden bg-finnish-blue-800 rounded-xl mt-4 p-6 shadow-2xl border-t border-finnish-gold-500/30 animate-fade-in-down">
				<div class="flex justify-between items-center mb-6 pb-4 border-b border-white/10">
					<div class="flex items-center space-x-3">
						<svg width="32" height="20" viewBox="0 0 18 12" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
							<rect width="18" height="12" fill="#FFFFFF"/>
							<rect x="5" y="0" width="3" height="12" fill="#003580"/>
							<rect x="0" y="4.5" width="18" height="3" fill="#003580"/>
						</svg>
						<h2 class="text-lg font-bold">Suomalaiset NHL-pelaajat</h2>
					</div>
				</div>

				<div class="py-4 space-y-4">
					<button
						class="w-full flex items-center space-x-3 p-4 bg-finnish-gold-500/10 rounded-lg border border-finnish-gold-500/30 text-finnish-gold-200 hover:bg-finnish-gold-500/20 transition-all duration-200 hover:scale-[1.02] hover:shadow-md"
						on:click={() => {
							toggleMobileMenu();
							_goToToday();
						}}
					>
						<span class="text-lg">📅</span>
						<span class="font-medium">Tänään</span>
					</button>

					<div class="pt-4 border-t border-white/10">
						<a href="/" class="block p-3 rounded-lg text-white hover:bg-white/5 transition-all duration-200 hover:pl-4">Koti</a>
						<a href="/about" class="block p-3 rounded-lg text-white hover:bg-white/5 transition-all duration-200 hover:pl-4">Tietoa</a>
						<a href="/stats" class="block p-3 rounded-lg text-white hover:bg-white/5 transition-all duration-200 hover:pl-4">Tilastot</a>
						<a href="/contact" class="block p-3 rounded-lg text-white hover:bg-white/5 transition-all duration-200 hover:pl-4">Yhteystiedot</a>
					</div>
				</div>

				<div class="pt-4 border-t border-white/10">
					<div class="text-center text-sm text-white/60">
						<p>© 2025 Suomalaiset NHL-pelaajat</p>
						<p class="text-finnish-gold-300 mt-1">Made with ❤️ and ☕ in Finland</p>
					</div>
				</div>
			</div>
		{/if}
	</nav>
</header>