# Finnish NHL Players - Design Tokens

## Overview

Design tokens are the single source of truth for all design decisions in the Finnish NHL Players application. They provide a consistent way to manage colors, typography, spacing, and other design properties while maintaining Finnish identity throughout the system.

## Table of Contents

1. [Color Tokens](#color-tokens)
2. [Typography Tokens](#typography-tokens)
3. [Spacing Tokens](#spacing-tokens)
4. [Shadow Tokens](#shadow-tokens)
5. [Border Radius Tokens](#border-radius-tokens)
6. [Motion Tokens](#motion-tokens)
7. [Semantic Tokens](#semantic-tokens)
8. [Theme Tokens](#theme-tokens)
9. [Custom Token Creation](#custom-token-creation)

## Color Tokens

### Finnish Brand Colors

Primary color palette inspired by Finnish flag and national hockey team.

```css
/* Finnish Blues */
--brand-blue-900: #001A4D;    /* Deep professional blue */
--brand-blue-800: #002F6C;    /* Standard Finnish blue */
--brand-blue-600: #0052CC;    /* Vibrant interactive blue */
--brand-blue-400: #4A90E2;    /* Light accent blue */

/* RGB Values for shadows and gradients */
--brand-blue-900-rgb: 0, 26, 77;
--brand-blue-800-rgb: 0, 47, 108;
--brand-blue-600-rgb: 0, 82, 204;
--brand-blue-400-rgb: 74, 144, 226;
```

### Finnish Gold Accents

Gold colors inspired by Finnish national hockey team (Leijonat).

```css
/* Finnish Golds */
--brand-gold-500: #FFB81C;    /* Vibrant gold (NHL-inspired) */
--brand-gold-450: #FFA000;    /* Deeper gold for contrast */
--brand-gold-300: #FFD54F;    /* Lighter gold for accents */

/* RGB Values */
--brand-gold-500-rgb: 255, 184, 28;
--brand-gold-450-rgb: 255, 160, 0;
--brand-gold-300-rgb: 255, 213, 79;
```

### Neutral Colors

Neutral foundation colors with Finnish silver influences.

```css
/* Finnish Silvers */
--brand-silver-300: #E0E0E0;    /* Lighter, modern silver */
--brand-silver-200: #F5F5F5;    /* Very light silver for backgrounds */

/* Base Colors */
--base-white: #FFFFFF;
--base-black: #0C0D0E;
--neutral-700: #7C878E;
```

### Accent Colors

Additional accent colors for specific use cases.

```css
/* Accent Colors */
--accent-coral: #FF6B6B;    /* For player highlights */
--accent-teal: #00BCD4;     /* For live indicators */
--accent-purple: #7C4DFF;   /* For special achievements */
```

### Semantic Colors

Colors with semantic meaning for status and feedback.

```css
/* Semantic Colors */
--success-green: #4CAF50;    /* Success states */
--warning-orange: #FF9800;   /* Warning states */
--error-red: #F44336;        /* Error states */
--info-blue: #2196F3;        /* Information states */
```

## Typography Tokens

### Font Families

Typography system optimized for Finnish character support.

```css
/* Font Stack */
--font-family-primary: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif;
--font-family-secondary: "Inter Tight", "SF Pro Text", system-ui, sans-serif;
--font-family-mono: "JetBrains Mono", "SF Mono", Consolas, monospace;
```

### Font Sizes

Responsive typographic scale for Finnish content.

```css
/* Display Typography */
--font-size-hero: 48px;
--line-height-hero: 56px;
--font-weight-hero: 800;

--font-size-display: 36px;
--line-height-display: 44px;
--font-weight-display: 700;

/* Heading Typography */
--font-size-h1: 28px;
--line-height-h1: 36px;
--font-weight-h1: 700;

--font-size-h2: 24px;
--line-height-h2: 32px;
--font-weight-h2: 600;

--font-size-h3: 20px;
--line-height-h3: 28px;
--font-weight-h3: 600;

/* Body Typography */
--font-size-body-large: 18px;
--line-height-body-large: 26px;
--font-weight-body-large: 400;

--font-size-body: 16px;
--line-height-body: 24px;
--font-weight-body: 400;

--font-size-caption: 14px;
--line-height-caption: 20px;
--font-weight-caption: 500;

--font-size-small: 12px;
--line-height-small: 16px;
--font-weight-small: 500;
```

### Font Weights

Consistent font weight scale.

```css
/* Font Weights */
--font-weight-light: 300;
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
--font-weight-black: 900;
```

### Letter Spacing

Optimized letter spacing for Finnish characters.

```css
/* Letter Spacing */
--letter-spacing-tight: -0.02em;
--letter-spacing-normal: 0;
--letter-spacing-wide: 0.02em;
--finnish-letter-spacing: 0.01em;    /* Optimized for Finnish */
```

## Spacing Tokens

Consistent spacing scale based on 4px grid system.

```css
/* Spacing Scale */
--space-1: 4px;      /* 0.25rem */
--space-2: 8px;      /* 0.5rem */
--space-3: 12px;     /* 0.75rem */
--space-4: 16px;     /* 1rem */
--space-5: 20px;     /* 1.25rem */
--space-6: 24px;     /* 1.5rem */
--space-8: 32px;     /* 2rem */
--space-10: 40px;    /* 2.5rem */
--space-12: 48px;    /* 3rem */
--space-16: 64px;    /* 4rem */
--space-20: 80px;    /* 5rem */
--space-24: 96px;    /* 6rem */
--space-32: 128px;   /* 8rem */
```

### Component Spacing

Specialized spacing for component layouts.

```css
/* Component Spacing */
--component-padding-xs: var(--space-2);
--component-padding-sm: var(--space-3);
--component-padding-md: var(--space-4);
--component-padding-lg: var(--space-6);
--component-padding-xl: var(--space-8);

--component-gap-xs: var(--space-1);
--component-gap-sm: var(--space-2);
--component-gap-md: var(--space-3);
--component-gap-lg: var(--space-4);
--component-gap-xl: var(--space-6);
```

## Shadow Tokens

Elevation system with Finnish-themed colored shadows.

```css
/* Base Shadows */
--shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
--shadow-md: 0 4px 16px rgba(0, 0, 0, 0.12);
--shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.16);
--shadow-xl: 0 16px 64px rgba(0, 0, 0, 0.20);

/* Colored Shadows */
--shadow-blue: 0 8px 32px rgba(0, 82, 204, 0.15);
--shadow-gold: 0 8px 32px rgba(255, 184, 28, 0.15);
--shadow-success: 0 8px 32px rgba(76, 175, 80, 0.15);
--shadow-teal: 0 8px 32px rgba(0, 188, 212, 0.15);

/* Inner Shadows */
--shadow-inset: inset 0 1px 2px rgba(0, 0, 0, 0.1);
--shadow-inset-reverse: inset 0 -1px 2px rgba(0, 0, 0, 0.1);
```

## Border Radius Tokens

Consistent border radius scale for rounded elements.

```css
/* Border Radius */
--radius-sm: 4px;      /* Small elements */
--radius-base: 8px;    /* Default radius */
--radius-md: 12px;     /* Medium elements */
--radius-lg: 16px;     /* Large elements */
--radius-xl: 24px;     /* Extra large elements */
--radius-2xl: 32px;    /* Very large elements */
--radius-full: 9999px;  /* Fully rounded */
```

## Motion Tokens

Animation and transition tokens for consistent motion.

```css
/* Durations */
--duration-fast: 120ms;      /* Quick interactions */
--duration-normal: 180ms;     /* Standard transitions */
--duration-slow: 240ms;      /* Slower animations */
--duration-slower: 300ms;    /* Complex animations */

/* Easing Functions */
--easing-standard: cubic-bezier(0.2, 0.7, 0.2, 1);    /* Standard easing */
--easing-enter: cubic-bezier(0, 0, 0.2, 1);           /* Enter animations */
--easing-exit: cubic-bezier(0.4, 0, 1, 1);            /* Exit animations */
```

## Semantic Tokens

High-level semantic tokens that abstract lower-level design decisions.

### Light Theme (Default)

```css
:root {
  /* Foreground Colors */
  --fg-primary: var(--brand-blue-900);
  --fg-secondary: var(--neutral-700);
  --fg-inverse: var(--base-white);
  
  /* Background Colors */
  --bg-canvas: var(--base-white);
  --bg-subtle: var(--brand-silver-200);
  --bg-elevated: var(--base-white);
  
  /* Border Colors */
  --border-subtle: #D5D9DE;
  --border-strong: var(--brand-silver-300);
  
  /* Accent Colors */
  --accent-primary: var(--brand-blue-900);
  --accent-interactive: var(--brand-blue-600);
  
  /* Status Colors */
  --status-live: var(--brand-gold-450);
  --status-upcoming: var(--brand-blue-600);
  --status-done: var(--brand-silver-300);
  
  /* Focus Ring */
  --focus-ring: #1453A8;
}
```

### Dark Theme

```css
[data-theme="dark"] {
  /* Foreground Colors */
  --fg-primary: #E6F0FA;
  --fg-secondary: #A9B3BD;
  --fg-inverse: var(--base-black);
  
  /* Background Colors */
  --bg-canvas: #0E1A29;
  --bg-subtle: #132339;
  --bg-elevated: #1A2A44;
  
  /* Border Colors */
  --border-subtle: #23415F;
  --border-strong: #2A4B70;
  
  /* Accent Colors */
  --accent-primary: #4A90E2;
  --accent-interactive: #64B5F6;
  
  /* Status Colors */
  --status-live: #FFA000;
  
  /* Focus Ring */
  --focus-ring: #4A90E2;
}
```

### Winter Theme

```css
[data-theme="winter"] {
  --bg-canvas: #F6FAFF;
  --bg-subtle: #E8F2FF;
  --fg-primary: var(--brand-blue-900);
  --fg-secondary: var(--neutral-700);
  --border-subtle: #D0E1FF;
  --border-strong: #B8D0FF;
}
```

### Summer Theme

```css
[data-theme="summer"] {
  --bg-canvas: #FAFBFF;
  --bg-subtle: var(--brand-silver-200);
  --fg-primary: var(--brand-blue-900);
  --fg-secondary: var(--neutral-700);
  --border-subtle: #E8E8E8;
  --border-strong: #D0D0D0;
}
```

### Playoffs Theme

```css
[data-theme="playoffs"] {
  --bg-canvas: var(--base-white);
  --bg-subtle: #FFF9E6;
  --fg-primary: var(--brand-blue-900);
  --fg-secondary: var(--neutral-700);
  --accent-primary: var(--brand-gold-500);
  --accent-interactive: var(--brand-gold-450);
  --border-subtle: #FFE4B5;
  --border-strong: #FFD700;
}
```

## Theme Tokens

### Dark Mode Enhancements

```css
/* Dark Mode Specific Colors */
--dark-surface: #0A0E27;
--dark-card: #151932;
--dark-border: #2A3F5F;
```

### Theme Implementation

Themes are implemented using data attributes:

```html
<html data-theme="dark">    <!-- Dark theme -->
<html data-theme="winter">  <!-- Winter theme -->
<html data-theme="summer">  <!-- Summer theme -->
<html data-theme="playoffs"> <!-- Playoffs theme -->
```

## Custom Token Creation

### Guidelines for Creating New Tokens

1. **Follow Naming Conventions**
   ```css
   --category-property-modifier: value;
   ```

2. **Use Semantic Names**
   ```css
   /* Good */
   --accent-primary: var(--brand-blue-900);
   
   /* Avoid */
   --blue-color: #001A4D;
   ```

3. **Provide RGB Values for Colors**
   ```css
   --brand-blue-900: #001A4D;
   --brand-blue-900-rgb: 0, 26, 77;
   ```

4. **Create Responsive Variants**
   ```css
   --font-size-h1: 28px;
   --font-size-h1-mobile: 24px;
   ```

### Token Categories

#### Color Tokens
```css
--category-color-name: #hex;
--category-color-name-rgb: r, g, b;
```

#### Typography Tokens
```css
--font-size-name: size;
--line-height-name: height;
--font-weight-name: weight;
```

#### Spacing Tokens
```css
--space-size: value;
--component-spacing-type: value;
```

#### Shadow Tokens
```css
--shadow-size: value;
--shadow-color: value;
```

### Token Usage Examples

#### Using Tokens in Components
```css
.component {
  background: var(--bg-elevated);
  color: var(--fg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--component-padding-md);
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-normal) var(--easing-standard);
}
```

#### Creating Theme-Aware Components
```css
.theme-aware-component {
  background: var(--bg-canvas);
  color: var(--fg-primary);
  border-color: var(--border-subtle);
}

.theme-aware-component:hover {
  background: var(--bg-subtle);
  border-color: var(--accent-interactive);
}
```

## Token Maintenance

### Version Control
- Document token changes in version history
- Use semantic versioning for breaking changes
- Maintain backward compatibility when possible

### Testing
- Test tokens across all themes
- Verify contrast ratios for accessibility
- Check responsive behavior
- Validate Finnish character rendering

### Performance
- Use CSS custom properties for dynamic values
- Avoid excessive token nesting
- Optimize token calculations

## Browser Support

Design tokens are supported in all modern browsers:
- Chrome 49+
- Firefox 31+
- Safari 9.1+
- Edge 16+

## Related Documentation

- [Style Guide](./STYLE_GUIDE.md) - Overall design system documentation
- [Components](./COMPONENTS.md) - Component-specific token usage
- [Accessibility](./ACCESSIBILITY.md) - Accessibility token considerations

## Contributing

When contributing new design tokens:

1. Follow established naming conventions
2. Provide RGB values for colors
3. Document semantic meaning
4. Test across all themes
5. Consider accessibility implications
6. Update documentation