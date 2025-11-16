<script>
import '../app.css'
// import Header from '$lib/components/ui/Header.svelte'
import ErrorBoundary from '$lib/components/ui/ErrorBoundary.svelte'
import PlayerPatternBackground from '$lib/components/ui/PlayerPatternBackground.svelte'
// import Footer from '$lib/components/ui/Footer.svelte'
</script>

<svelte:head>
	<meta name="description" content="Seuraa suomalaisten NHL-pelaajien pistetilastoja päivittäin" />
	<meta name="keywords" content="NHL, suomalaiset pelaajat, jääkiekko, pistet, maalit, syötöt, Leijonat" />
	<meta name="language" content="fi" />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
	<link
		href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div class="min-h-screen flex flex-col relative bg-gray-50" style="color-scheme: light;">
	<PlayerPatternBackground />
	<!-- <Header /> -->
	<main class="flex-1 w-full relative z-10">
		<ErrorBoundary>
			<slot />
		</ErrorBoundary>
	</main>
	<!-- <Footer /> -->
</div>
