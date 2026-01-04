# Suomalaiset NHL:ssä — Finnish NHL Player Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Svelte](https://img.shields.io/badge/Svelte-5.0.0-orange)](https://svelte.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0-blue)](https://tailwindcss.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue)](https://www.typescriptlang.org/)
[![Status](https://img.shields.io/badge/Status-Automated-brightgreen)](https://github.com/miikka/suomalaisetnhlssa/actions)

A high-performance web application tracking scoring statistics for Finnish NHL players. Automatically updated daily to ensure you never miss a point from your favorite players.

## ✨ Features

- **🎯 Finnish Focus**: Specifically optimized for Finnish players (30-35 players), making data processing 10x faster than general trackers.
- **🔄 Automated Updates**: Daily and real-time data sync via GitHub Actions.
- **⚡ Performance First**: Built with Svelte 5 and Tailwind CSS 4 for a lightning-fast user experience.
- **📱 Responsive & Accessible**: Premium UI designed with Finnish aesthetics, fully responsive and WCAG compliant.
- **🌓 Adaptive Theme**: Sleek dark and light modes that follow your system preferences.
- **📅 Historical Browsing**: Integrated calendar to view highlights and scores from any date in the season.

## 🚀 Quick Start

### Prerequisites

- **Node.js**: 20+
- **npm**: Latest version recommended
- **Python**: 3.9+ (for internal data collection scripts)

### Installation

```bash
# Clone the repository
git clone https://github.com/miikka/suomalaisetnhlssa.git
cd suomalaisetnhlssa

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`.

## 🛠️ Development

### Project Structure

```text
suomalaisetnhlssa/
├── src/                # Svelte 5 frontend
│   ├── lib/            # Shared components and services
│   └── routes/         # SvelteKit pages
├── scripts/            # Data collection and management tools
├── static/             # Static assets and cached data
└── tests/              # Vitest & Playwright tests
```

### Key Commands

```bash
npm run dev      # Start dev server
npm run build    # Build for production (Static Adapter)
npm run lint     # Lint check with Biome
npm run format   # Format code
npm run test     # Run unit tests
npm run check    # Type-check Svelte files
```

## 📊 Data & Automation

The project uses a hybrid data approach:
1. **GitHub Actions**: Periodically runs Python scripts in `.venv` to fetch and commit the latest NHL data.
2. **NHL API**: Dynamic fallback for dates not yet cached in the repository.
3. **Curated Database**: A dedicated database of Finnish player IDs ensures 100% accuracy and high speed.

## 🎨 Design Principles

Inspired by Finnish minimalism and the blue-and-white identity, the UI focuses on clarity, premium micro-animations, and a "Finnish-first" user experience.

## 🤝 Contributing

Contributions are welcome! Please ensure you run `npm run validate` before submitting a pull request to check linting, types, and tests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ for Finnish hockey fans everywhere*