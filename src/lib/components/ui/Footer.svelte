<script>
const _currentYear = new Date().getFullYear()
</script>

<footer class="bg-blue-900 text-white py-12">
  <div class="container mx-auto px-4">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
      <div class="text-center md:text-left">
        <h3 class="text-xl font-bold text-yellow-500 mb-4">Tietoa</h3>
        <ul class="space-y-2">
          <li>
            <a 
              href="https://github.com/miikka-dev/suomalaiset-nhl-ssa" 
              target="_blank" 
              rel="noopener noreferrer"
              class="text-white/80 hover:text-yellow-400 transition-colors duration-200"
            >
              GitHub
            </a>
          </li>
          <li>
            <a 
              href="#api" 
              class="text-white/80 hover:text-yellow-400 transition-colors duration-200"
            >
              API
            </a>
          </li>
          <li>
            <a 
              href="#contact" 
              class="text-white/80 hover:text-yellow-400 transition-colors duration-200"
            >
              Yhteystiedot
            </a>
          </li>
        </ul>
      </div>
      
      <div class="text-center">
        <h3 class="text-xl font-bold text-yellow-500 mb-4">Ominaisuudet</h3>
        <ul class="space-y-2">
          <li>
            <a 
              href="#players" 
              class="text-white/80 hover:text-yellow-400 transition-colors duration-200"
            >
              Pelaajahaku
            </a>
          </li>
          <li>
            <a 
              href="#stats" 
              class="text-white/80 hover:text-yellow-400 transition-colors duration-200"
            >
              Tilastot
            </a>
          </li>
          <li>
            <a 
              href="#calendar" 
              class="text-white/80 hover:text-yellow-400 transition-colors duration-200"
            >
              Kalenteri
            </a>
          </li>
        </ul>
      </div>
      
      <div class="text-center md:text-right">
        <h3 class="text-xl font-bold text-yellow-500 mb-4">Seuraa</h3>
        <div class="flex justify-center md:justify-end space-x-4">
          <a 
            href="https://github.com/miikka-dev/suomalaiset-nhl-ssa" 
            target="_blank" 
            rel="noopener noreferrer" 
            aria-label="GitHub"
            class="p-3 bg-white/10 rounded-full text-white hover:bg-yellow-500/20 hover:text-yellow-300 transition-colors duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
            </svg>
          </a>
        </div>
      </div>
    </div>
    
    <div class="border-t border-white/10 pt-8 text-center">
      <p class="text-white/60">
        © {_currentYear} Suomalaiset NHL-pelaajat •
        Built with ❤️ and ☕ in Finland
      </p>
    </div>
  </div>
</footer>
