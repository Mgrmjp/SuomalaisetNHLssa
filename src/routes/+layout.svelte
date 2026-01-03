<script>
import ErrorBoundary from '$lib/components/ui/ErrorBoundary.svelte'
import { base } from '$app/paths'
import '../app.css'
// import PlayerPatternBackground from '$lib/components/ui/PlayerPatternBackground.svelte'
// import Footer from '$lib/components/ui/Footer.svelte'
</script>

<svelte:head>
	<meta name="description" content="Miten suomalaisilla kulkee NHL:ssä? Tutki päivän ottelut, pisteet ja onnistumiset." />
	<meta name="keywords" content="NHL, suomalaiset pelaajat, jääkiekko, pistet, maalit, syötöt, Leijonat" />
	<meta name="language" content="fi" />
	<link rel="icon" type="image/svg+xml" href={base + "/logo.svg"} />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
	<link
		href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div class="min-h-screen flex flex-col relative bg-gray-50" style="color-scheme: light;">
	<!-- <Header /> -->
	<main class="flex-1 w-full relative z-10">
		<ErrorBoundary>
			<slot />
		</ErrorBoundary>
	</main>
	<!-- <Footer /> -->
</div>
