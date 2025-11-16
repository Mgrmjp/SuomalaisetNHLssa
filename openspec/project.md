# Project Context

## Purpose
Finnish NHL Player Tracker is a web application that displays daily performance statistics for Finnish NHL players. The app provides a user-friendly interface for browsing player data including goals, assists, points, and game information across different dates. Currently implemented as a static site with mock data, with plans for future NHL API integration.

## Tech Stack
- **Frontend Framework**: SvelteKit 1.30.4 with static adapter
- **Language**: Mixed JavaScript/TypeScript with TypeScript configuration
- **UI Styling**: Tailwind-style utility classes with custom CSS
- **State Management**: Svelte stores with reactive patterns
- **Build Tool**: Vite 4.5.0 with optimized configuration
- **Testing**: Vitest 3.2.4 with jsdom environment
- **Code Quality**: Biome 2.2.5 for linting and formatting
- **Date Handling**: date-fns 2.30.0 for date manipulation
- **Minification**: Terser 5.44.0 for production builds

## Project Conventions

### Code Style
- **Indentation**: 2 spaces (Biome configured)
- **Quotes**: Single quotes for strings
- **Semicolons**: As needed (Biome configured)
- **Line Width**: 100 characters maximum
- **File Extensions**: Mixed (.js for data, .ts for typed code, .svelte for components)
- **Component Naming**: PascalCase for Svelte components
- **Store Pattern**: Writable stores for state, derived stores for computed values
- **Type Safety**: Optional TypeScript, interfaces defined for core data structures

### Architecture Patterns
- **Static Site Generation**: Using SvelteKit static adapter for deployable HTML files
- **Component-Based Architecture**: Reusable UI components in `src/lib/components/`
- **Store-Based State Management**: Centralized state in `src/lib/stores/gameData.ts`
- **Data Caching**: In-memory caching for performance optimization
- **Responsive Design**: Mobile-first approach with utility classes
- **Theme System**: Dark/light mode with system preference detection and localStorage persistence

### Testing Strategy
- **Test Runner**: Vitest with jsdom environment
- **Test Files**: Located in `src/lib/tests/` with `.test.js` extension
- **Mock Setup**: Comprehensive browser API mocking in setup.js
- **Coverage**: Unit tests for store logic and component behavior
- **CI/CD**: Build validation through `npm run check` and `npm run test`

### Git Workflow
- **Branching**: Feature branches for development
- **Commits**: Conventional commit messages
- **Code Review**: Automated linting with Biome before commits

## Domain Context

### NHL Data Structure
- **Player Information**: Name, team, position, opponent team
- **Performance Metrics**: Goals, assists, points per game
- **Game Details**: Game score, result (W/L/OT), date played
- **Team Abbreviations**: Standard 3-letter NHL team codes
- **Position Codes**: RW (Right Wing), C (Center), D (Defenseman)

### Finnish Player Tracking
- Focus on Finnish-born NHL players and their daily performance
- Mock data includes notable players like Mikko Rantanen, Sebastian Aho, Roope Hintz
- Game statistics tracked on a daily basis with historical browsing capability

## Important Constraints
- **Static Site Limitation**: All player data must be available at build time
- **Mock Data Dependency**: Currently uses hardcoded data for October 9, 2025
- **Browser Compatibility**: Supports modern browsers with ES6+ features
- **Performance Focus**: Optimized for fast loading and smooth interactions
- **Accessibility**: Semantic HTML structure with proper ARIA support

## External Dependencies
- **NHL API**: Planned integration for real-time game data (not implemented)
- **Date Operations**: date-fns library for reliable date manipulation
- **Static Hosting**: Compatible with Netlify, Vercel, or any static hosting service
- **CDN Assets**: No external CDN dependencies for core functionality

## Data Scripts
- **fetchGameData.js**: Scripts for fetching NHL game data
- **findFinnishPlayers.js**: Identifies Finnish players from NHL rosters
- **updateFinnishPlayers.js**: Updates player database with latest information
- **exploreRosters.js**: Tools for exploring team roster data

## Build Configuration
- **Development**: `vite dev` on port 3000 with HMR
- **Production**: Static build to `build/` directory with source maps
- **Preview**: `vite preview` on port 4173 for local testing
- **Optimization**: Terser minification, CSS code splitting, asset optimization
