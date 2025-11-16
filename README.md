# Finnish NHL Player Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Svelte](https://img.shields.io/badge/Svelte-4.2.8-orange)](https://svelte.dev/)
[![SvelteKit](https://img.shields.io/badge/SvelteKit-1.30.4-red)](https://kit.svelte.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3.2-blue)](https://www.typescriptlang.org/)

A modern web application that tracks and displays scoring statistics for Finnish NHL players on a daily basis. Built with SvelteKit, TypeScript, and Tailwind CSS for optimal performance and developer experience.

## ✨ Features

- **Daily Player Statistics**: View Finnish NHL players who scored points (goals/assists) on any selected date
- **Smart Data Sourcing**: Automatically uses pre-populated data when available, falls back to live NHL API
- **Real-time Data Integration**: Fetches live data from the official NHL API when pre-populated data isn't available
- **Direct API Integration**: Real-time data fetching with optimized HTTP requests
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Dark/Light Theme**: Automatic theme switching with system preferences
- **Finnish Identity**: Designed with Finnish colors, typography, and user experience in mind
- **Accessibility First**: WCAG compliant with keyboard navigation and screen reader support
- **Performance Optimized**: Lazy loading, efficient state management, and minimal bundle size

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd suomalaisetnhlssa

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`.

### Basic Usage

1. **View Today's Stats**: The app loads with the previous day's data by default
2. **Navigate Dates**: Use the date picker or Previous/Next buttons to browse different dates
3. **View Player Details**: Click on any player card to see detailed statistics
4. **Theme Switching**: Toggle between light and dark modes using the theme button

## 📊 Pre-populated Data

The application supports pre-populated data for development, testing, and offline scenarios:

### How It Works

- **Automatic Detection**: The app first checks for pre-populated data before making API calls
- **Seamless Fallback**: If no pre-populated data exists, it automatically fetches from the live NHL API
- **Performance**: Pre-populated data loads instantly without API requests
- **Offline Support**: Pre-populated data works without internet connection

### Generating Pre-populated Data

```bash
# Generate data for a specific date and make it web-available
./scripts/generate_prepopulated.sh 2025-11-09 --save

# Generate sample data for testing
./scripts/generate_prepopulated.sh 2025-11-09 --save --sample

# Check available pre-populated dates
./scripts/generate_prepopulated.sh
```

### Manual Data Generation

```bash
# Generate data (saves to data/prepopulated/)
python3 scripts/prepopulate_data.py --date 2025-11-09 --save

# Copy to static directory manually
cp data/prepopulated/finnish-players-2025-11-09.json static/data/prepopulated/
```

### Available Pre-populated Dates

The application currently includes pre-populated data for:
- `2025-11-08`: Sample data with 3 players (Mikko Rantanen, Sebastian Aho, Patrik Laine)
- `2025-11-09`: Real data with 1 player (Teuvo Teravainen)

## 🛠️ Development

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build

# Testing
npm run test         # Run tests
npm run test:watch   # Run tests in watch mode

# Code Quality
npm run lint         # Run Biome linter
npm run format       # Format code with Biome
npm run check        # Run Svelte type checking

# Data Management
npm run data:fetch         # Fetch current season data
npm run data:fetch:date    # Fetch data for specific date
npm run data:fetch:season  # Fetch entire season data
npm run players:update      # Update Finnish player database
npm run players:validate   # Validate Finnish player data
npm run players:stats      # Show player database statistics



# Testing
npm run test:simplified    # Run simplified system tests
```

### Project Structure

```
suomalaisetnhlssa/
├── src/
│   ├── lib/
│   │   ├── components/      # Reusable Svelte components
│   │   ├── services/        # Simplified business logic and API services
│   │   │   ├── simpleCacheService.js      # Simple key-value cache with TTL
│   │   │   ├── playerDetectionService.js  # Finnish player detection and management
│   │   │   └── dataService.js            # Main data service integration
│   │   ├── stores/          # Svelte stores for state management
│   │   ├── utils/           # Utility functions and helpers
│   │   └── types/           # TypeScript type definitions
│   ├── routes/              # SvelteKit pages and API routes
│   └── app.html            # Root HTML template
├── static/                  # Static assets
├── tests/                   # Test files
├── docs/                    # Detailed documentation
├── scripts/                 # Build and data scripts
│   ├── finnish-players-cli.js  # Simplified CLI for player management
│   ├── test-simplified-system.js # Comprehensive test suite
│   └── data-manager.js         # Legacy data manager (deprecated)
├── data/                    # Static data files
│   ├── players/               # Finnish player database
│   └── backups/              # Database backups
└── test-results/             # Test output and reports
```

## 🏗️ Architecture

### Simplified System Overview

The application has been simplified to improve maintainability and reduce complexity:

- **Direct Data Service**: Simplified data fetching without caching layers in [`dataService.js`](src/lib/services/dataService.js)
- **Direct Player Detection**: Replaced pattern matching with curated database in [`playerDetectionService.js`](src/lib/services/playerDetectionService.js)
- **Unified Data Service**: Consolidated data operations in [`dataService.js`](src/lib/services/dataService.js)
- **Streamlined CLI**: Simplified command-line interface with [`finnish-players-cli.js`](scripts/finnish-players-cli.js)

### Tech Stack

- **Framework**: Svelte 4 with SvelteKit 1.30.4
- **Language**: TypeScript 5.3.2
- **Styling**: Tailwind CSS 4.1.16 with PostCSS
- **Build Tool**: Vite 4.5.0
- **Testing**: Vitest 3.2.4 with jsdom
- **Code Quality**: Biome 2.2.5 for linting and formatting
- **Data**: NHL API integration with simplified caching

### Key Features

- **Component-based Architecture**: Modular, reusable Svelte components
- **State Management**: Svelte stores with derived values for reactive updates
- **Simplified API Integration**: Official NHL API endpoints with straightforward caching
- **Performance Optimization**: Lazy loading, code splitting, and efficient data fetching
- **Responsive Design**: Mobile-first approach with Finnish design principles
- **Accessibility**: Semantic HTML, ARIA attributes, and keyboard navigation

## 📊 Data Sources

- **NHL API**: Real-time game data, player statistics, and team information
- **Finnish Player Database**: Curated list of Finnish NHL players in [`data/players/finnish-players-db.json`](data/players/finnish-players-db.json)
- **Direct Data Fetching**: Real-time API integration without caching

## 🎨 Design System

The application follows Finnish design principles:

- **Colors**: Finnish flag colors (blue and white) with modern palette
- **Typography**: Optimized for Finnish language readability
- **Spacing**: Consistent spacing system following Finnish design standards
- **Components**: Finnish-themed UI components with accessibility features

## 🧪 Testing

The project includes comprehensive testing for the simplified system:

- **System Tests**: Comprehensive validation of simplified components with [`test-simplified-system.js`](scripts/test-simplified-system.js)
- **Unit Tests**: Store logic, utilities, and data services
- **Component Tests**: UI component behavior and accessibility
- **Integration Tests**: User workflows and API integration

```bash
# Run all tests
npm run test

# Run simplified system tests
npm run test:simplified

# Run tests with coverage
npm run test -- --coverage

# Run tests in watch mode during development
npm run test:watch
```

## 📚 Documentation

- [Migration Guide](./MIGRATION_GUIDE.md) - Guide for upgrading from old system
- [Caching Simplification](./CACHING_SIMPLIFICATION_MIGRATION_GUIDE.md) - Details on caching changes
- [Scripts Documentation](./scripts/README.md) - CLI tools and scripts documentation
- [Development Guide](./docs/DEVELOPMENT.md) - Development setup and workflow
- [Deployment Guide](./docs/DEPLOYMENT.md) - Deployment instructions

## 🚀 Deployment

### Static Site Deployment

The application is configured for static site deployment:

```bash
# Build for production
npm run build

# The build output is in the `build/` directory
# Deploy to any static hosting service (Vercel, Netlify, etc.)
```

### Environment Variables

Create a `.env` file for configuration:

```env
# NHL API Configuration
NHL_API_BASE_URL=https://api-web.nhle.com

# Cache Configuration
CACHE_TTL=3600000  # 1 hour in milliseconds
MAX_CACHE_SIZE=100

# Feature Flags
ENABLE_REAL_API=true
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./docs/CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and test thoroughly
4. Run linting and tests: `npm run lint && npm test`
5. Commit your changes: `git commit -m "Add new feature"`
6. Push to your fork: `git push origin feature/new-feature`
7. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- NHL for providing the official API
- Finnish hockey fans for inspiration and feedback
- Svelte and SvelteKit communities for excellent tools and documentation
- The Finnish design community for aesthetic guidance

## 📞 Support

For questions, issues, or suggestions:

- Open an issue on GitHub
- Check the [documentation](./docs/)
- Review the [FAQ](./docs/FAQ.md) (coming soon)

---

*Built with ❤️ for Finnish hockey fans everywhere*