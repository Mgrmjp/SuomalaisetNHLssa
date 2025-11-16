# Finnish NHL Player Tracker - Component Documentation

## Overview

This document provides comprehensive documentation for all components in the Finnish NHL Player Tracker design system. Each component is built with Finnish identity, accessibility, and performance in mind using Svelte 4 and TypeScript.

## Component Architecture

### Design Principles

- **Finnish Identity**: Components reflect Finnish design aesthetics with blue and white color schemes
- **Accessibility First**: WCAG 2.1 AA compliance with semantic HTML and ARIA support
- **Mobile-First**: Responsive design optimized for all screen sizes
- **Performance**: Optimized for minimal bundle size and fast rendering
- **Type Safety**: Full TypeScript integration with comprehensive type definitions

### Component Structure

```
src/lib/components/
├── ui/                    # Base UI components
│   ├── Button.svelte
│   ├── Card.svelte
│   ├── Loading.svelte
│   ├── Modal.svelte
│   └── index.ts
├── layout/               # Layout components
│   ├── Header.svelte
│   ├── Footer.svelte
│   ├── Navigation.svelte
│   └── Container.svelte
├── features/             # Feature-specific components
│   ├── PlayerCard.svelte
│   ├── DateControls.svelte
│   ├── GameList.svelte
│   ├── PlayerStats.svelte
│   └── CacheMonitor.svelte
└── forms/               # Form components
    ├── DatePicker.svelte
    ├── SearchBox.svelte
    └── ThemeToggle.svelte
```

## Base UI Components

### Button (`Button.svelte`)

Versatile button component with multiple variants and states.

#### Props

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'accent' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  iconOnly?: boolean;
  type?: 'button' | 'submit' | 'reset';
}
```

#### Usage

```svelte
<script>
  import Button from '$lib/components/ui/Button.svelte';

  function handleClick() {
    console.log('Button clicked');
  }
</script>

<!-- Primary button -->
<Button variant="primary" on:click={handleClick}>
  Primary Action
</Button>

<!-- With loading state -->
<Button loading={true} disabled={true}>
  Processing...
</Button>

<!-- Icon only button -->
<Button iconOnly variant="ghost" on:click={handleClick}>
  <svg>...</svg>
</Button>
```

#### Features

- Multiple variants with Finnish color palette
- Loading states with spinner animation
- Full keyboard navigation support
- Focus management and ARIA attributes
- Ripple effect on click (optional)

### Card (`Card.svelte`)

Flexible card component for displaying content with multiple layout options.

#### Props

```typescript
interface CardProps {
  variant?: 'default' | 'elevated' | 'bordered' | 'interactive';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
  clickable?: boolean;
  accent?: boolean;
}
```

#### Usage

```svelte
<script>
  import Card from '$lib/components/ui/Card.svelte';
</script>

<!-- Default card -->
<Card padding="md">
  <h3>Card Title</h3>
  <p>Card content goes here.</p>
</Card>

<!-- Interactive card -->
<Card variant="interactive" clickable on:click={handleCardClick}>
  <h3>Clickable Card</h3>
  <p>Click me to trigger an action.</p>
</Card>

<!-- Accent card with Finnish blue -->
<Card variant="elevated" accent={true}>
  <h3>Featured Card</h3>
  <p>Important content with accent styling.</p>
</Card>
```

#### Features

- Multiple visual variants
- Responsive padding
- Hover and focus states
- Accessibility support
- Finnish themed accent colors

### Loading (`Loading.svelte`)

Animated loading indicator with customizable appearance and messaging.

#### Props

```typescript
interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  overlay?: boolean;
  spinner?: boolean;
  progress?: number;
}
```

#### Usage

```svelte
<script>
  import Loading from '$lib/components/ui/Loading.svelte';
</script>

<!-- Simple spinner -->
<Loading size="md" />

<!-- With message -->
<Loading message="Loading player data..." size="lg" />

<!-- Overlay loading -->
<Loading overlay={true} message="Processing..." />

<!-- Progress indicator -->
<Loading progress={75} message="Loading... 75%" />
```

#### Features

- Finnish-themed spinner animations
- Configurable sizes and colors
- Message display with typewriter effect
- Progress bar support
- Accessibility announcements

### Modal (`Modal.svelte`)

Dialog component for displaying content overlays with proper focus management.

#### Props

```typescript
interface ModalProps {
  open?: boolean;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  closable?: boolean;
  backdrop?: boolean;
}
```

#### Usage

```svelte
<script>
  import Modal from '$lib/components/ui/Modal.svelte';

  let showModal = false;

  function openModal() {
    showModal = true;
  }

  function closeModal() {
    showModal = false;
  }
</script>

<Button on:click={openModal}>Open Modal</Button>

<Modal
  bind:open={showModal}
  title="Player Details"
  size="md"
  closable={true}
  on:close={closeModal}
>
  <p>Detailed player information goes here.</p>

  <svelte:fragment slot="actions">
    <Button variant="secondary" on:click={closeModal}>Close</Button>
  </svelte:fragment>
</Modal>
```

#### Features

- Focus trapping and restoration
- Escape key handling
- Click outside to close
- Backdrop blur effect
- Full accessibility support

## Layout Components

### Container (`Container.svelte`)

Responsive container with consistent padding and max-width across breakpoints.

#### Props

```typescript
interface ContainerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'fluid';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  centered?: boolean;
}
```

#### Usage

```svelte
<script>
  import Container from '$lib/components/layout/Container.svelte';
</script>

<!-- Default container -->
<Container>
  <h1>Main Content</h1>
  <p>Responsive content with proper spacing.</p>
</Container>

<!-- Large container for hero sections -->
<Container size="xl" padding="lg">
  <h1>Hero Section</h1>
  <p>Extra large container for important content.</p>
</Container>
```

#### Features

- Responsive max-width and padding
- Mobile-first approach
- Finnish spacing system
- Centered content option

### Header (`Header.svelte`)

Main application header with navigation, branding, and controls.

#### Props

```typescript
interface HeaderProps {
  sticky?: boolean;
  transparent?: boolean;
  showSearch?: boolean;
  showThemeToggle?: boolean;
}
```

#### Usage

```svelte
<script>
  import Header from '$lib/components/layout/Header.svelte';
</script>

<Header
  sticky={true}
  showSearch={true}
  showThemeToggle={true}
/>
```

#### Features

- Finnish flag branding
- Responsive navigation menu
- Search functionality
- Theme toggle integration
- Accessibility navigation

## Feature Components

### PlayerCard (`PlayerCard.svelte`)

Specialized card for displaying Finnish NHL player information with statistics.

#### Props

```typescript
interface PlayerCardProps {
  player: Player;
  loading?: boolean;
  compact?: boolean;
  showDetails?: boolean;
  interactive?: boolean;
}
```

#### Usage

```svelte
<script>
  import PlayerCard from '$lib/components/features/PlayerCard.svelte';

  export let player: Player;
</script>

<PlayerCard
  {player}
  interactive={true}
  showDetails={true}
  on:click={handlePlayerClick}
  on:favorite={handleFavorite}
/>
```

#### Features

- Finnish player information display
- Team logos and colors
- Live game indicators
- Performance statistics
- Finnish flag integration for top performers
- Leijonat badge for exceptional performances

#### Data Structure

```typescript
interface Player {
  id: number;
  firstName: string;
  lastName: string;
  team: string;
  position: string;
  goals: number;
  assists: number;
  points: number;
  gameDate: string;
  isLive?: boolean;
  isFinnish?: boolean;
}
```

### DateControls (`DateControls.svelte`)

Date navigation component with Finnish localization and keyboard support.

#### Props

```typescript
interface DateControlsProps {
  selectedDate?: Date;
  minDate?: Date;
  maxDate?: Date;
  showToday?: boolean;
  compact?: boolean;
}
```

#### Usage

```svelte
<script>
  import DateControls from '$lib/components/features/DateControls.svelte';

  let selectedDate = new Date();

  function handleDateChange(event: CustomEvent<Date>) {
    selectedDate = event.detail;
  }
</script>

<DateControls
  bind:selectedDate={selectedDate}
  showToday={true}
  on:dateChange={handleDateChange}
/>
```

#### Features

- Finnish date formatting
- Previous/Next navigation
- Today button for quick access
- Keyboard shortcuts (arrow keys, T for today)
- Date picker integration
- Accessibility support

### GameList (`GameList.svelte`)

List component for displaying NHL games with Finnish player highlights.

#### Props

```typescript
interface GameListProps {
  games: Game[];
  loading?: boolean;
  showFinnishOnly?: boolean;
  compact?: boolean;
}
```

#### Usage

```svelte
<script>
  import GameList from '$lib/components/features/GameList.svelte';

  export let games: Game[];
</script>

<GameList
  {games}
  showFinnishOnly={true}
  compact={false}
  on:gameSelect={handleGameSelect}
/>
```

#### Features

- Game schedule display
- Finnish player highlighting
- Live score updates
- Team logos and colors
- Game status indicators
- Responsive layout

### CacheMonitor (`CacheMonitor.svelte`)

Development tool for monitoring cache performance and health.

#### Props

```typescript
interface CacheMonitorProps {
  visible?: boolean;
  compact?: boolean;
  showCharts?: boolean;
}
```

#### Usage

```svelte
<script>
  import CacheMonitor from '$lib/components/features/CacheMonitor.svelte';
</script>

<!-- Development only -->
{#if import.meta.env.DEV}
  <CacheMonitor visible={true} showCharts={true} />
{/if}
```

#### Features

- Real-time cache statistics
- Performance metrics
- Health recommendations
- Cache warming controls
- Debug information display
- Development-only visibility

## Form Components

### DatePicker (`DatePicker.svelte`)

Finnish-localized date picker with calendar interface.

#### Props

```typescript
interface DatePickerProps {
  value?: Date;
  min?: Date;
  max?: Date;
  disabled?: boolean;
  placeholder?: string;
  format?: string;
}
```

#### Usage

```svelte
<script>
  import DatePicker from '$lib/components/forms/DatePicker.svelte';

  let selectedDate: Date;
</script>

<DatePicker
  bind:value={selectedDate}
  placeholder="Valitse päivämäärä"
  format="dd.MM.yyyy"
/>
```

#### Features

- Finnish day and month names
- Calendar popup interface
- Keyboard navigation
- Min/max date constraints
- Mobile-friendly touch interface

### ThemeToggle (`ThemeToggle.svelte`)

Theme switching component with smooth transitions and system preference detection.

#### Props

```typescript
interface ThemeToggleProps {
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  animated?: boolean;
}
```

#### Usage

```svelte
<script>
  import ThemeToggle from '$lib/components/forms/ThemeToggle.svelte';
</script>

<ThemeToggle
  size="md"
  showLabel={true}
  animated={true}
/>
```

#### Features

- Light/dark mode switching
- System preference detection
- Smooth color transitions
- Finnish-themed icons
- Accessibility support
- Local storage persistence

## Styling System

### CSS Custom Properties

Components use a comprehensive design token system:

```css
:root {
  /* Finnish Color Palette */
  --color-primary: #003580;        /* Finnish blue */
  --color-secondary: #ffffff;      /* White */
  --color-accent: #0052cc;         /* Bright blue */

  /* Semantic Colors */
  --color-success: #007e3f;        /* Green */
  --color-warning: #ff6b35;        /* Orange */
  --color-error: #dc2626;          /* Red */

  /* Neutral Colors */
  --color-gray-50: #f8fafc;
  --color-gray-900: #0f172a;

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Spacing (Finnish design system) */
  --space-1: 0.25rem;   /* 4px */
  --space-4: 1rem;      /* 16px */
  --space-8: 2rem;      /* 32px */

  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px rgb(0 0 0 / 0.1);
}
```

### Component Class Naming

Components follow a BEM-like naming convention with Finnish prefixes:

```css
/* Block */
.finnish-player-card { }

/* Element */
.finnish-player-card__header { }
.finnish-player-card__name { }
.finnish-player-card__stats { }

/* Modifier */
.finnish-player-card--loading { }
.finnish-player-card--compact { }
.finnish-player-card--featured { }
```

## Accessibility Features

### ARIA Support

All components include comprehensive ARIA attributes:

```svelte
<button
  type="button"
  aria-label="Toggle theme"
  aria-expanded={isExpanded}
  aria-controls="theme-menu"
  aria-describedby="theme-description"
>
  Theme
</button>
```

### Keyboard Navigation

- Tab order follows logical content flow
- Custom keyboard shortcuts (arrow keys, Enter, Escape)
- Focus indicators with high contrast
- Skip links for navigation

### Screen Reader Support

- Semantic HTML structure
- Descriptive alt text for images
- Live regions for dynamic content
- Context announcements for actions

## Performance Optimizations

### Component Optimization

- **Lazy Loading**: Components loaded on demand
- **Tree Shaking**: Unused code eliminated
- **Code Splitting**: Separate bundles for features
- **CSS Optimization**: Minimal CSS with critical path loading

### Bundle Size Management

```typescript
// Dynamic imports for heavy components
const ChartComponent = lazy(() => import('$lib/components/charts/PlayerChart.svelte'));

// Conditional loading
{#if showAdvancedStats}
  <ChartComponent data={playerStats} />
{/if}
```

## Testing Guidelines

### Component Testing Structure

```typescript
// PlayerCard.test.ts
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, beforeEach } from 'vitest';
import PlayerCard from '$lib/components/features/PlayerCard.svelte';

describe('PlayerCard', () => {
  const mockPlayer = {
    id: 1,
    name: 'Mikko Rantanen',
    team: 'COL',
    goals: 2,
    assists: 1,
    points: 3
  };

  it('renders player information correctly', () => {
    render(PlayerCard, { props: { player: mockPlayer } });

    expect(screen.getByText('Mikko Rantanen')).toBeInTheDocument();
    expect(screen.getByText('COL')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('handles click events', async () => {
    const { component } = render(PlayerCard, { props: { player: mockPlayer } });

    const clickHandler = vi.fn();
    component.$on('click', clickHandler);

    await fireEvent.click(screen.getByRole('button'));
    expect(clickHandler).toHaveBeenCalled();
  });
});
```

## Usage Examples

### Complete Page Example

```svelte
<script>
  import Container from '$lib/components/layout/Container.svelte';
  import Header from '$lib/components/layout/Header.svelte';
  import PlayerCard from '$lib/components/features/PlayerCard.svelte';
  import DateControls from '$lib/components/features/DateControls.svelte';
  import Loading from '$lib/components/ui/Loading.svelte';

  export let players = [];
  export let loading = false;
  export let selectedDate = new Date();
</script>

<Header sticky={true} showThemeToggle={true} />

<Container size="lg" padding="md">
  <DateControls bind:selectedDate />

  {#if loading}
    <Loading message="Loading player data..." size="lg" />
  {:else if players.length === 0}
    <p>No Finnish players scored on this date.</p>
  {:else}
    <div class="player-grid">
      {#each players as player (player.id)}
        <PlayerCard
          {player}
          interactive={true}
          on:click={() => handlePlayerSelect(player)}
        />
      {/each}
    </div>
  {/if}
</Container>

<style>
  .player-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--space-6);
    margin-top: var(--space-8);
  }
</style>
```

This component documentation provides a comprehensive guide to the Finnish NHL Player Tracker's design system, ensuring consistency, accessibility, and performance across all components while maintaining Finnish identity and user experience excellence.