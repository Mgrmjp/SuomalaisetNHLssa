# Development Guide

This guide provides comprehensive instructions for setting up a development environment, understanding the project architecture, and following best practices for contributing to the Finnish NHL Player Tracker.

## Prerequisites

### Required Software

- **Node.js**: Version 18.0 or higher
- **npm**: Version 8.0 or higher (comes with Node.js)
- **Git**: Latest stable version
- **Code Editor**: VS Code (recommended) with extensions

### VS Code Extensions (Recommended)

```json
{
  "recommendations": [
    "svelte.svelte-vscode",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "biomejs.biome",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode.test-adapter-converter",
    "vitest.explorer"
  ]
}
```

## Quick Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd suomalaisetnhlssa

# Install dependencies
npm install

# Verify installation
npm run check
```

### 2. Start Development

```bash
# Start development server
npm run dev

# Open browser to http://localhost:5173
```

### 3. Verify Everything Works

```bash
# Run tests
npm test

# Check code quality
npm run lint

# Build project
npm run build
```

## Development Workflow

### Daily Development Routine

1. **Update Dependencies**
   ```bash
   git pull origin main
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Run Tests in Watch Mode**
   ```bash
   npm run test:watch
   ```

4. **Warm Up Cache (for faster development)
   ```bash
   npm run cache:warmup-recent
   ```

### Creating a New Feature

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Develop Your Feature**
   - Follow the component structure
   - Write tests for new functionality
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   npm run test
   npm run lint
   npm run check
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

## Project Architecture

### Directory Structure Deep Dive

```
src/
├── lib/
│   ├── components/
│   │   ├── ui/              # Base UI components (Button, Card, etc.)
│   │   │   ├── Button.svelte
│   │   │   ├── Card.svelte
│   │   │   ├── Loading.svelte
│   │   │   └── index.ts     # Barrel exports
│   │   ├── layout/          # Layout components
│   │   │   ├── Header.svelte
│   │   │   ├── Footer.svelte
│   │   │   └── Navigation.svelte
│   │   └── features/        # Feature-specific components
│   │       ├── PlayerCard.svelte
│   │       ├── DateControls.svelte
│   │       ├── GameList.svelte
│   │       └── CacheMonitor.svelte
│   ├── services/
│   │   ├── nhlApi.js        # NHL API client
│   │   ├── dataService.js   # Data abstraction layer
│   │   └── cacheManager.js  # Advanced caching system
│   ├── stores/
│   │   ├── gameData.js      # Game data state management
│   │   ├── theme.js         # Theme state
│   │   └── cache.js         # Cache state management
│   ├── utils/
│   │   ├── dateUtils.js     # Date manipulation
│   │   ├── formatters.js    # Data formatting
│   │   ├── constants.js     # App constants
│   │   └── validators.js    # Input validation
│   ├── types/
│   │   ├── nhl.ts          # NHL API types
│   │   ├── player.ts       # Player data types
│   │   ├── game.ts         # Game data types
│   │   └── cache.ts        # Cache system types
│   └── assets/
│       ├── icons/          # SVG icons
│       ├── images/         # Static images
│       └── fonts/          # Custom fonts
├── routes/
│   ├── +layout.svelte      # Root layout
│   ├── +page.svelte        # Home page
│   ├── +error.svelte       # Error page
│   └── api/               # API routes (if needed)
├── app.html               # HTML template
└── app.css                # Global styles
```

### Component Architecture

#### Component Naming Conventions

- **PascalCase** for component files: `PlayerCard.svelte`
- **kebab-case** for component props: `player-data`
- **BEM-like** CSS classes: `finnish-player-card__header`

#### Component Structure Template

```svelte
<script lang="ts">
  // Imports
  import type { Player } from '$lib/types/player';

  // Props interface
  export let player: Player;
  export let loading = false;

  // Reactive statements
  $: fullName = `${player.firstName} ${player.lastName}`;

  // Functions
  function handleCardClick() {
    // Handle interaction
  }
</script>

<div class="finnish-player-card" class:loading>
  <div class="finnish-player-card__header">
    <h3 class="finnish-player-card__name">{fullName}</h3>
  </div>

  <div class="finnish-player-card__body">
    <!-- Component content -->
  </div>
</div>

<style>
  .finnish-player-card {
    /* Component styles */
  }

  .finnish-player-card--loading {
    /* Loading state styles */
  }
</style>
```

### State Management

#### Store Patterns

```javascript
// stores/gameData.js
import { writable, derived } from 'svelte/store';
import type { GameData, Player } from '$lib/types';

function createGameDataStore() {
  const { subscribe, set, update } = writable<GameData>({
    selectedDate: new Date(),
    players: [],
    loading: false,
    error: null
  });

  return {
    subscribe,
    setSelectedDate: (date: Date) => update(state => ({
      ...state,
      selectedDate: date,
      loading: true
    })),
    setPlayers: (players: Player[]) => update(state => ({
      ...state,
      players,
      loading: false
    })),
    setError: (error: string) => update(state => ({
      ...state,
      error,
      loading: false
    })),
    reset: () => set({
      selectedDate: new Date(),
      players: [],
      loading: false,
      error: null
    })
  };
}

export const gameData = createGameDataStore();

// Derived stores
export const displayDate = derived(
  gameData,
  $gameData => $gameData.selectedDate.toLocaleDateString('fi-FI')
);

export const hasPlayers = derived(
  gameData,
  $gameData => $gameData.players.length > 0
);
```

## Code Style and Standards

### TypeScript Configuration

The project uses strict TypeScript settings:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

### Biome Configuration

Code formatting and linting with Biome:

```json
{
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "suspicious": {
        "noExplicitAny": "error"
      }
    }
  },
  "formatter": {
    "enabled": true,
    "formatWithErrors": false
  }
}
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Files | kebab-case | `player-card.svelte` |
| Components | PascalCase | `PlayerCard` |
| Variables | camelCase | `playerData` |
| Constants | UPPER_SNAKE_CASE | `API_BASE_URL` |
| Functions | camelCase | `fetchPlayerData` |
| Types | PascalCase | `PlayerData` |
| Interfaces | PascalCase with I prefix | `IPlayerService` |

### Import Organization

```typescript
// 1. External libraries
import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';

// 2. Internal lib imports (absolute)
import type { Player } from '$lib/types/player';
import { formatDate } from '$lib/utils/dateUtils';

// 3. Relative imports
import './PlayerCard.css';
```

## Testing Guide

### Test Structure

```
tests/
├── setup.ts              # Test configuration
├── mocks/                # Mock implementations
│   ├── browser.ts       # Browser API mocks
│   └── nhlApi.ts        # NHL API mocks
├── lib/
│   ├── stores/          # Store tests
│   │   └── gameData.test.ts
│   ├── utils/           # Utility tests
│   │   └── dateUtils.test.ts
│   └── services/        # Service tests
│       └── nhlApi.test.ts
└── components/          # Component tests (future)
    └── PlayerCard.test.ts
```

### Writing Tests

#### Unit Test Example

```typescript
// tests/lib/utils/dateUtils.test.ts
import { describe, it, expect } from 'vitest';
import { formatDate, getPreviousDay, getNextDay } from '$lib/utils/dateUtils';

describe('dateUtils', () => {
  describe('formatDate', () => {
    it('should format date correctly', () => {
      const date = new Date('2024-01-15');
      expect(formatDate(date)).toBe('15.1.2024');
    });

    it('should handle Finnish locale formatting', () => {
      const date = new Date('2024-12-25');
      expect(formatDate(date)).toBe('25.12.2024');
    });
  });

  describe('getPreviousDay', () => {
    it('should return previous day', () => {
      const date = new Date('2024-01-15');
      const previous = getPreviousDay(date);
      expect(previous.getDate()).toBe(14);
    });

    it('should handle month boundaries', () => {
      const date = new Date('2024-03-01');
      const previous = getPreviousDay(date);
      expect(previous.getMonth()).toBe(1); // February
      expect(previous.getDate()).toBe(29); // Leap year
    });
  });
});
```

#### Component Test Example

```typescript
// tests/lib/components/PlayerCard.test.ts
import { render, screen } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import PlayerCard from '$lib/components/features/PlayerCard.svelte';
import type { Player } from '$lib/types/player';

const mockPlayer: Player = {
  id: 1,
  firstName: 'Mikko',
  lastName: 'Rantanen',
  team: 'COL',
  position: 'RW',
  goals: 2,
  assists: 1,
  points: 3,
  gameDate: '2024-01-15'
};

describe('PlayerCard', () => {
  it('should render player information correctly', () => {
    render(PlayerCard, { props: { player: mockPlayer } });

    expect(screen.getByText('Mikko Rantanen')).toBeInTheDocument();
    expect(screen.getByText('COL')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument(); // Goals
    expect(screen.getByText('1')).toBeInTheDocument(); // Assists
    expect(screen.getByText('3')).toBeInTheDocument(); // Points
  });

  it('should show loading state', () => {
    render(PlayerCard, { props: { player: mockPlayer, loading: true } });

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });
});
```

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test -- --coverage

# Run specific test file
npm test PlayerCard.test.ts
```

## Debugging

### Browser DevTools

1. **Svelte DevTools**: Install browser extension for component inspection
2. **Redux DevTools**: Works with Svelte stores for state inspection
3. **Console Debugging**: Use `console.log` with descriptive messages

### Debugging Techniques

```typescript
// Store debugging
import { gameData } from '$lib/stores/gameData';

// Log store changes
gameData.subscribe(value => {
  console.log('GameData changed:', value);
});

// Component debugging
<script>
  export let player;

  // Debug prop changes
  $: {
    console.log('Player prop changed:', player);
  }
</script>
```

### Cache Debugging

```bash
# Check cache status
npm run cache:status

# Monitor cache in real-time
npm run cache:monitor

# Clear cache for testing
npm run cache:clear
```

## Performance Optimization

### Development Performance

1. **Use Development Mode**
   ```bash
   npm run dev -- --mode development
   ```

2. **Enable Source Maps**
   ```javascript
   // vite.config.js
   export default {
     server: {
       fs: {
         allow: ['..']
       }
     },
     build: {
       sourcemap: true
     }
   };
   ```

3. **Bundle Analysis**
   ```bash
   npm run build
   npx vite-bundle-analyzer build/
   ```

### Code Splitting

```typescript
// Lazy load components
const PlayerCard = lazy(() => import('$lib/components/features/PlayerCard.svelte'));

// Dynamic imports for heavy utilities
const loadChart = () => import('$lib/utils/chartUtils.js');
```

## API Development

### Local API Testing

```typescript
// Mock API responses for development
const USE_MOCK_API = import.meta.env.DEV;

if (USE_MOCK_API) {
  // Use mock data
}
```

### Environment Variables

```env
# .env.development
VITE_NHL_API_BASE_URL=https://api-web.nhle.com
VITE_CACHE_TTL=60000
VITE_ENABLE_CACHE_MONITORING=true

# .env.production
VITE_NHL_API_BASE_URL=https://api-web.nhle.com
VITE_CACHE_TTL=300000
VITE_ENABLE_CACHE_MONITORING=false
```

## Common Development Tasks

### Adding a New Component

1. **Create Component File**
   ```bash
   touch src/lib/components/features/NewComponent.svelte
   ```

2. **Create Test File**
   ```bash
   touch tests/lib/components/NewComponent.test.ts
   ```

3. **Export from Index**
   ```typescript
   // src/lib/components/features/index.ts
   export { default as NewComponent } from './NewComponent.svelte';
   ```

4. **Add to Documentation**
   - Update COMPONENTS.md
   - Add usage examples

### Adding a New Store

1. **Create Store File**
   ```bash
   touch src/lib/stores/newStore.ts
   ```

2. **Create Test File**
   ```bash
   touch tests/lib/stores/newStore.test.ts
   ```

3. **Implement Store Pattern**
   - Use writable/readable from Svelte
   - Add derived stores if needed
   - Include TypeScript types

### Adding New API Endpoints

1. **Update API Service**
   ```typescript
   // src/lib/services/nhlApi.js
   export async function getNewEndpoint(params) {
     // Implementation
   }
   ```

2. **Add Types**
   ```typescript
   // src/lib/types/api.ts
   export interface NewResponseType {
     // Type definition
   }
   ```

3. **Add Tests**
   ```typescript
   // tests/lib/services/nhlApi.test.ts
   describe('getNewEndpoint', () => {
     // Test implementation
   });
   ```

## Troubleshooting

### Common Issues

#### Build Errors

```bash
# Clear build cache
rm -rf build/ .svelte-kit/

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check TypeScript configuration
npm run check
```

#### Development Server Issues

```bash
# Check port availability
lsof -i :5173

# Clear Vite cache
npm run dev -- --force
```

#### Test Failures

```bash
# Update test snapshots
npm test -- --update-snapshots

# Run tests with verbose output
npm test -- --reporter=verbose
```

#### Cache Issues

```bash
# Clear all caches
npm run cache:clear

# Reset cache statistics
npm run cache:warmup-all
```

### Getting Help

1. **Check Documentation**
   - Read relevant docs in `/docs/` folder
   - Check Svelte and SvelteKit documentation

2. **Console Logging**
   ```typescript
   // Add debug logging
   console.log('Debug info:', { data, state });
   ```

3. **Network Tab**
   - Check API calls in browser dev tools
   - Verify cache behavior

4. **Ask for Help**
   - Create detailed issue description
   - Include error messages and steps to reproduce

## Best Practices

### Code Organization

1. **Keep Components Small**
   - Single responsibility principle
   - Maximum 200-300 lines per component

2. **Use TypeScript Strictly**
   - Avoid `any` types
   - Use proper interfaces

3. **Test Everything**
   - Unit tests for logic
   - Component tests for UI
   - Integration tests for workflows

### Performance

1. **Optimize Images**
   - Use modern formats (WebP, AVIF)
   - Implement lazy loading

2. **Cache Effectively**
   - Use browser caching
   - Implement service worker if needed

3. **Bundle Optimization**
   - Dynamic imports for code splitting
   - Tree shaking for unused code

### Accessibility

1. **Semantic HTML**
   - Use proper HTML5 elements
   - Include ARIA attributes

2. **Keyboard Navigation**
   - Test tab order
   - Include focus indicators

3. **Screen Reader Support**
   - Use alt text for images
   - Announce dynamic content changes

This development guide provides a comprehensive foundation for contributing to the Finnish NHL Player Tracker. Follow these guidelines to ensure high-quality, maintainable code that aligns with the project's standards and goals.