# Finnish NHL Players - Style Guide

## Overview

This comprehensive style guide documents the design system, components, and best practices for the Finnish NHL Players application. The design system is built with Finnish identity at its core, featuring a blue and gold color scheme inspired by the Finnish flag and national hockey team (Leijonat).

## Table of Contents

1. [Design Principles](#design-principles)
2. [Finnish Design Identity](#finnish-design-identity)
3. [Naming Conventions](#naming-conventions)
4. [Component Architecture](#component-architecture)
5. [Performance Optimization](#performance-optimization)
6. [Accessibility Guidelines](#accessibility-guidelines)
7. [Responsive Design](#responsive-design)
8. [Theme System](#theme-system)
9. [Usage Examples](#usage-examples)

## Design Principles

### Finnish Identity First
- All components use the `finnish-` prefix to maintain brand consistency
- Color palette inspired by Finnish flag (blue and white) with gold accents
- Finnish language support with proper typography and spacing
- Cultural references to Finnish hockey heritage (Leijonat)

### Performance Optimized
- CSS containment for better rendering performance
- Hardware acceleration with `will-change` properties
- Optimized animations with reduced motion support
- Efficient component structure with minimal re-renders

### Accessibility Compliant
- WCAG 2.1 AA compliance as minimum standard
- Semantic HTML with proper ARIA attributes
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support

### Mobile First Responsive
- Progressive enhancement approach
- Touch-friendly interaction targets
- Optimized layouts for all screen sizes
- Performance considerations for mobile devices

## Finnish Design Identity

### Color Palette
The color system is inspired by Finnish national colors and hockey heritage:

```css
/* Primary Finnish Colors */
--brand-blue-900: #001A4D;    /* Deep Finnish blue */
--brand-blue-800: #002F6C;    /* Standard Finnish blue */
--brand-blue-600: #0052CC;    /* Interactive blue */
--brand-blue-400: #4A90E2;    /* Light accent blue */

/* Finnish Gold Accents */
--brand-gold-500: #FFB81C;    /* Leijonat gold */
--brand-gold-450: #FFA000;    /* Darker gold */
--brand-gold-300: #FFD54F;    /* Light gold */

/* Neutral Foundation */
--brand-silver-300: #E0E0E0;  /* Finnish silver */
--brand-silver-200: #F5F5F5;  /* Light silver */
```

### Typography
Finnish-optimized typography with proper character support:

```css
/* Font Stack with Finnish Support */
--font-family-primary: "Inter", "SF Pro Display", -apple-system, sans-serif;
--font-family-secondary: "Inter Tight", "SF Pro Text", system-ui, sans-serif;

/* Finnish Character Spacing */
--finnish-letter-spacing: 0.01em;
```

### Visual Elements
- Subtle gradients inspired by Finnish landscapes
- Clean, minimalist aesthetic
- Hockey-inspired visual metaphors
- Performance-optimized animations

## Naming Conventions

### BEM Methodology
All components follow BEM (Block, Element, Modifier) methodology:

```css
.finnish-block-name                    /* Block */
.finnish-block-name__element          /* Element */
.finnish-block-name--modifier         /* Modifier */
```

### Component Structure
```html
<div class="finnish-player-card">
  <div class="finnish-player-card__header">
    <span class="finnish-stat-chip finnish-stat-chip--goals">5</span>
  </div>
</div>
```

### Utility Classes
Utilities use the `finnish-` prefix with semantic naming:

```css
.finnish-flex--center        /* Flexbox utility */
.finnish-mt-4               /* Margin top utility */
.finnish-text-center        /* Text alignment utility */
```

## Component Architecture

### Component Categories

1. **Layout Components**
   - Container, Grid, Flex utilities
   - Responsive layout helpers
   - Spacing and positioning utilities

2. **Interactive Components**
   - Buttons, Forms, Inputs
   - Modals, Dropdowns
   - Navigation elements

3. **Display Components**
   - Cards, Badges, Pills
   - Status indicators
   - Data visualization

4. **Feedback Components**
   - Loading states, Spinners
   - Error boundaries, Messages
   - Progress indicators

### Component Structure
Each component follows this structure:
```svelte
<script>
  // Component logic
</script>

<!-- Component markup with semantic HTML -->
<div class="finnish-component-name">
  <!-- Content -->
</div>

<style>
  /* Component-specific styles that extend shared styles */
</style>
```

## Performance Optimization

### CSS Containment
```css
.finnish-component {
  contain: layout style paint;
  will-change: transform, opacity;
}
```

### Hardware Acceleration
```css
.finnish-interactive {
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
}
```

### Optimized Animations
```css
.finnish-animated {
  animation: var(--duration-normal) var(--easing-standard);
}

@media (prefers-reduced-motion: reduce) {
  .finnish-animated {
    animation: none;
  }
}
```

### Image Optimization
- WebP format with fallbacks
- Lazy loading for off-screen images
- Responsive images with proper sizing
- SVG icons for scalability

## Accessibility Guidelines

### Semantic HTML
```html
<!-- Use semantic elements -->
<header class="finnish-header">
  <nav aria-label="Päävalikko">
    <button aria-label="Avaa valikko" aria-expanded="false">
  </nav>
</header>
```

### ARIA Attributes
```html
<div role="status" aria-live="polite">
  <span aria-label="Pelaajan tilastot">Stats</span>
</div>
```

### Keyboard Navigation
```css
.finnish-focusable:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}
```

### Screen Reader Support
```html
<span class="sr-only">Visually hidden text for screen readers</span>
```

## Responsive Design

### Breakpoint System
```css
/* Mobile First Approach */
@media (min-width: 640px)   { /* Small tablets */ }
@media (min-width: 768px)   { /* Tablets */ }
@media (min-width: 1024px)  { /* Desktop */ }
@media (min-width: 1280px)  { /* Large desktop */ }
```

### Mobile Optimizations
```css
@media (max-width: 767px) {
  .finnish-component {
    padding: var(--space-4);
    font-size: var(--font-size-body);
  }
}
```

### Touch Targets
```css
.finnish-touch-target {
  min-height: 44px;
  min-width: 44px;
}
```

## Theme System

### Available Themes
1. **Light Theme** - Default bright theme
2. **Dark Theme** - Dark mode for low-light environments
3. **Winter Theme** - Cool blue tones for winter season
4. **Summer Theme** - Bright, warm tones for summer
5. **Playoffs Theme** - Special theme for playoff season

### Theme Implementation
```html
<html data-theme="dark">
```

### Semantic Color Tokens
```css
:root {
  --fg-primary: var(--brand-blue-900);
  --bg-canvas: var(--base-white);
  --accent-primary: var(--brand-blue-900);
}
```

## Usage Examples

### Basic Card Component
```html
<div class="finnish-card finnish-card--interactive">
  <div class="finnish-card__header">
    <h3 class="finnish-heading">Card Title</h3>
  </div>
  <div class="finnish-card__body">
    <p>Card content goes here.</p>
  </div>
</div>
```

### Button Variants
```html
<!-- Primary Button -->
<button class="finnish-btn finnish-btn--primary">
  Primary Action
</button>

<!-- Secondary Button -->
<button class="finnish-btn finnish-btn--secondary">
  Secondary Action
</button>

<!-- Icon Button -->
<button class="finnish-btn finnish-btn--icon-only">
  <span>🔍</span>
</button>
```

### Layout Utilities
```html
<!-- Flex Container -->
<div class="finnish-flex finnish-flex--center finnish-flex--gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Grid Layout -->
<div class="finnish-grid finnish-grid--cols-3 finnish-grid--gap-6">
  <div>Grid Item 1</div>
  <div>Grid Item 2</div>
  <div>Grid Item 3</div>
</div>
```

### Responsive Design
```html
<div class="finnish-container">
  <div class="finnish-grid finnish-grid--cols-auto">
    <!-- Responsive grid items -->
  </div>
</div>
```

## Related Documentation

- [Components Documentation](./COMPONENTS.md) - Detailed component reference
- [Design Tokens](./DESIGN_TOKENS.md) - Complete token system
- [Accessibility Guidelines](./ACCESSIBILITY.md) - Accessibility implementation details

## Contributing

When contributing to the design system:

1. Follow the established naming conventions
2. Ensure accessibility compliance
3. Test across all themes and breakpoints
4. Document new components and utilities
5. Maintain Finnish design identity
6. Consider performance implications

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Version History

- v2.0 - Complete design system overhaul with Finnish identity
- v1.5 - Added theme system and accessibility improvements
- v1.0 - Initial implementation