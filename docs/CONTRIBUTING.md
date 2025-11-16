# Contributing to the Finnish NHL Player Tracker

Thank you for your interest in contributing to the Finnish NHL Player Tracker! This guide will help you understand how to contribute effectively to our project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)
- [Pull Request Process](#pull-request-process)
- [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Node.js 18+** and **npm** installed
- **Git** configured on your system
- A **code editor** (VS Code recommended)
- Basic knowledge of **Svelte**, **TypeScript**, and **JavaScript**
- Familiarity with **Git** workflow

### First-Time Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/suomalaisetnhlssa.git
   cd suomalaisetnhlssa
   ```

2. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/original-owner/suomalaisetnhlssa.git
   ```

3. **Install Dependencies**
   ```bash
   npm install
   ```

4. **Verify Setup**
   ```bash
   npm run dev
   npm test
   ```

## Development Setup

### Development Workflow

1. **Sync with Upstream**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

3. **Make Changes**
   - Follow coding standards
   - Write tests for new functionality
   - Update documentation

4. **Test Your Changes**
   ```bash
   npm run test:watch
   npm run lint
   npm run check
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create Pull Request on GitHub
   ```

### Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Configure for development
VITE_NHL_API_BASE_URL=https://api-web.nhle.com
VITE_CACHE_TTL=60000
VITE_ENABLE_CACHE_MONITORING=true
```

## How to Contribute

### Types of Contributions

We welcome the following types of contributions:

#### 🐛 Bug Fixes
- Fix reported issues
- Add test cases to prevent regressions
- Update documentation if needed

#### ✨ New Features
- Implement new functionality
- Follow existing patterns and architecture
- Include comprehensive tests

#### 📚 Documentation
- Improve existing documentation
- Add examples and tutorials
- Fix typos and grammatical errors

#### 🎨 UI/UX Improvements
- Enhance user interface
- Improve accessibility
- Optimize for different screen sizes

#### ⚡ Performance Improvements
- Optimize bundle size
- Improve loading times
- Enhance caching strategies

#### 🧪 Testing
- Add test coverage
- Improve test quality
- Add integration tests

### Finding Issues to Work On

1. **Good First Issues**
   - Look for issues labeled `good first issue`
   - These are great for newcomers

2. **Bug Reports**
   - Check issues labeled `bug`
   - Reproduce the issue before fixing

3. **Feature Requests**
   - Look for issues labeled `enhancement`
   - Discuss implementation approach first

4. **Documentation**
   - Check for `documentation` label
   - Improve READMEs and guides

## Coding Standards

### Code Style

We use **Biome** for code formatting and linting:

```bash
# Check code style
npm run lint

# Auto-fix issues
npm run format

# Type checking
npm run check
```

### TypeScript Standards

```typescript
// Use explicit types
const player: Player = {
  id: 1,
  name: 'Mikko Rantanen'
};

// Use interfaces for object shapes
interface Player {
  id: number;
  name: string;
  team?: string;
}

// Avoid 'any' type
function processPlayer(player: Player): void {
  // Implementation
}
```

### Component Standards

```svelte
<script lang="ts">
  // 1. Imports
  import type { Player } from '$lib/types/player';
  import { formatDate } from '$lib/utils/dateUtils';

  // 2. Props with types
  export let player: Player;
  export let loading = false;

  // 3. Reactive statements
  $: formattedDate = formatDate(player.gameDate);
  $: isTopPerformer = player.points > 2;

  // 4. Functions
  function handleCardClick(): void {
    // Handle interaction
  }
</script>

<!-- Use semantic HTML with accessibility attributes -->
<article class="player-card" role="button" tabindex="0" on:click={handleCardClick} on:keydown={handleCardClick}>
  <header class="player-card__header">
    <h3 class="player-card__name">{player.name}</h3>
  </header>

  <div class="player-card__body">
    <!-- Content -->
  </div>
</article>

<style>
  /* Use BEM-like naming convention */
  .player-card {
    /* Base styles */
  }

  .player-card--loading {
    /* Modifier styles */
  }

  .player-card__header {
    /* Element styles */
  }

  /* Use CSS custom properties for theming */
  .player-card {
    background: var(--color-surface);
    color: var(--color-text);
    border: 1px solid var(--color-border);
  }
</style>
```

### File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `PlayerCard.svelte` |
| Utilities | camelCase | `dateUtils.ts` |
| Types | PascalCase | `PlayerTypes.ts` |
| Constants | UPPER_SNAKE_CASE | `API_ENDPOINTS.ts` |
| Tests | kebab-case with .test.ts | `player-card.test.ts` |

### Import Organization

```typescript
// 1. External libraries
import { writable, derived } from 'svelte/store';
import { z } from 'zod';

// 2. Internal lib imports (absolute paths)
import type { Player } from '$lib/types/player';
import { formatDate } from '$lib/utils/dateUtils';
import { gameData } from '$lib/stores/gameData';

// 3. Relative imports
import './PlayerCard.css';
```

## Testing Guidelines

### Test Structure

```typescript
// tests/lib/components/PlayerCard.test.ts
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, beforeEach } from 'vitest';
import PlayerCard from '$lib/components/features/PlayerCard.svelte';
import type { Player } from '$lib/types/player';

describe('PlayerCard', () => {
  let mockPlayer: Player;

  beforeEach(() => {
    mockPlayer = {
      id: 1,
      name: 'Mikko Rantanen',
      team: 'COL',
      goals: 2,
      assists: 1,
      points: 3
    };
  });

  it('should render player information correctly', () => {
    render(PlayerCard, { props: { player: mockPlayer } });

    expect(screen.getByText('Mikko Rantanen')).toBeInTheDocument();
    expect(screen.getByText('COL')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument(); // Total points
  });

  it('should handle click events', async () => {
    const { component } = render(PlayerCard, { props: { player: mockPlayer } });

    const clickHandler = vi.fn();
    component.$on('click', clickHandler);

    const card = screen.getByRole('button');
    await fireEvent.click(card);

    expect(clickHandler).toHaveBeenCalledOnce();
  });

  it('should show loading state', () => {
    render(PlayerCard, { props: { player: mockPlayer, loading: true } });

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });
});
```

### Test Coverage Requirements

- **Unit Tests**: 100% coverage for business logic
- **Component Tests**: Cover all states and interactions
- **Integration Tests**: Critical user workflows
- **Accessibility Tests**: Screen reader and keyboard navigation

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

## Documentation Standards

### Code Documentation

```typescript
/**
 * Formats a date according to Finnish locale standards
 * @param date - The date to format
 * @param options - Formatting options
 * @returns Formatted date string in Finnish format
 *
 * @example
 * ```typescript
 * const date = new Date('2024-01-15');
 * const formatted = formatDate(date); // '15.1.2024'
 * ```
 */
export function formatDate(
  date: Date,
  options: { includeTime?: boolean } = {}
): string {
  // Implementation
}
```

### Component Documentation

```svelte
<!--
  @component
  PlayerCard - Displays Finnish NHL player information

  @prop {Player} player - Player data to display
  @prop {boolean} [loading=false] - Show loading state
  @prop {boolean} [compact=false] - Use compact layout

  @event {CustomEvent<Player>} click - Fired when card is clicked

  @example
  ```svelte
  <PlayerCard
    {player}
    loading={false}
    on:click={handlePlayerClick}
  />
  ```
-->
```

### README Documentation

When adding new features, update relevant documentation:

1. **Update Feature Lists** in README.md
2. **Add Component Documentation** to COMPONENTS.md
3. **Update API Documentation** if applicable
4. **Add Examples** to documentation

## Pull Request Process

### Before Creating a PR

1. **Ensure Tests Pass**
   ```bash
   npm test
   npm run lint
   npm run check
   ```

2. **Update Documentation**
   - README changes if needed
   - Component documentation
   - API documentation

3. **Test Your Changes**
   - Manual testing in browser
   - Accessibility testing
   - Performance testing

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changes tested in multiple browsers
- [ ] Accessibility considered

## Screenshots (if applicable)
Add screenshots for UI changes.

## Additional Notes
Any additional information for reviewers.
```

### PR Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code quality checks
   - Build verification

2. **Code Review**
   - At least one maintainer review required
   - Focus on code quality and functionality
   - Check for potential issues

3. **Approval and Merge**
   - Address all review comments
   - Maintain clean commit history
   - Merge to main branch

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and considerate
- Use inclusive language
- Focus on constructive feedback
- Welcome newcomers and help them learn

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For general questions and ideas
- **PR Comments**: For code-specific feedback

### Getting Help

1. **Check Documentation**
   - Read existing docs
   - Search for similar issues

2. **Ask Questions**
   - GitHub Discussions for general questions
   - Issues for specific problems

3. **Join Community**
   - Participate in discussions
   - Help others with their issues

## Recognition

### Contributors

All contributors are recognized in:

- README.md contributors section
- Release notes for significant contributions
- GitHub contributor statistics

### Types of Recognition

- **Code Contributions**: Features, bug fixes, improvements
- **Documentation**: Improving guides and examples
- **Community**: Helping others, reporting issues
- **Design**: UI/UX improvements, accessibility

## Development Resources

### Useful Links

- [Svelte Documentation](https://svelte.dev/docs)
- [SvelteKit Documentation](https://kit.svelte.dev/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Vitest Documentation](https://vitest.dev/guide/)

### Development Tools

- **VS Code Extensions**
  - Svelte for VS Code
  - Tailwind CSS IntelliSense
  - Biome
  - GitLens

- **Browser Tools**
  - Svelte DevTools
  - React Developer Tools (for state debugging)

## Troubleshooting

### Common Issues

#### Setup Problems

```bash
# Clear all caches
rm -rf node_modules build .svelte-kit
npm install

# Verify Node.js version
node --version  # Should be 18+
npm --version   # Should be 8+
```

#### Test Failures

```bash
# Update test snapshots
npm test -- --update-snapshots

# Run tests with verbose output
npm test -- --reporter=verbose
```

#### Build Issues

```bash
# Check TypeScript configuration
npm run check

# Analyze bundle size
npm run build
npx vite-bundle-analyzer build/
```

### Getting Help

1. **Search Existing Issues**
   - Check for similar problems
   - Look for closed issues

2. **Create Detailed Issue**
   - Include error messages
   - Provide reproduction steps
   - Include environment details

3. **Ask in Discussions**
   - For general questions
   - For design feedback
   - For implementation ideas

Thank you for contributing to the Finnish NHL Player Tracker! Your contributions help make this project better for everyone. 🏒🇫🇮