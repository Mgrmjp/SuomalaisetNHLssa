# Finnish NHL Players - Accessibility Guidelines

## Overview

This document outlines the accessibility standards and implementation guidelines for the Finnish NHL Players application. We are committed to WCAG 2.1 AA compliance as a minimum standard, with many components exceeding these requirements.

## Table of Contents

1. [Accessibility Standards](#accessibility-standards)
2. [Focus Management](#focus-management)
3. [Screen Reader Support](#screen-reader-support)
4. [Keyboard Navigation](#keyboard-navigation)
5. [Color Contrast](#color-contrast)
6. [Reduced Motion](#reduced-motion)
7. [High Contrast Mode](#high-contrast-mode)
8. [Finnish Language Support](#finnish-language-support)
9. [Testing Guidelines](#testing-guidelines)
10. [Implementation Examples](#implementation-examples)

## Accessibility Standards

### WCAG 2.1 Compliance

We aim to meet WCAG 2.1 AA standards across all components:

- **Level A**: Essential accessibility features
- **Level AA**: Enhanced accessibility features
- **Level AAA**: Advanced features where applicable

### Target Audience

Our accessibility features support users with:
- Visual impairments
- Hearing impairments
- Motor disabilities
- Cognitive disabilities
- Finnish language requirements

## Focus Management

### Focus Indicators

All interactive elements have clear focus indicators:

```css
/* Standard Focus Indicator */
*:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}

/* Component-specific Focus */
.finnish-component:focus-within {
  box-shadow: 0 0 0 3px var(--focus-ring);
}
```

### Focus Trapping

Modal and overlay components trap focus within their content:

```javascript
// Focus trap implementation
function trapFocus(element) {
  const focusableElements = element.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];
  
  element.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          lastFocusable.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          firstFocusable.focus();
          e.preventDefault();
        }
      }
    }
  });
}
```

### Skip Links

Skip navigation links for keyboard users:

```html
<a href="#main-content" class="skip-to-content">
  Siirry pääsisältöön
</a>
```

```css
.skip-to-content {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--accent-primary);
  color: var(--fg-inverse);
  padding: 8px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 1000;
  transition: top 0.3s;
}

.skip-to-content:focus {
  top: 6px;
}
```

## Screen Reader Support

### Semantic HTML

Use semantic HTML elements for proper structure:

```html
<header class="finnish-header">
  <nav aria-label="Päävalikko">
    <ul role="menubar">
      <li role="none">
        <button role="menuitem" aria-expanded="false">
          Valikko
        </button>
      </li>
    </ul>
  </nav>
</header>

<main id="main-content" role="main">
  <section aria-labelledby="section-title">
    <h2 id="section-title">Otsikko</h2>
    <!-- Content -->
  </section>
</main>
```

### ARIA Attributes

Proper ARIA attributes for enhanced screen reader support:

```html
<!-- Live Regions -->
<div role="status" aria-live="polite" aria-atomic="true">
  <span>Peli päättyi: 5-3</span>
</div>

<!-- Descriptive Labels -->
<button aria-label="Sulje modal" aria-describedby="modal-description">
  ✕
</button>

<div id="modal-description" class="sr-only">
  Sulkee tämän ikkunan ja palaa edelliseen näkymään
</div>

<!-- Form Labels -->
<label for="player-search">Etsi pelaajaa:</label>
<input 
  type="search" 
  id="player-search"
  aria-describedby="search-help"
  aria-required="true"
>
<div id="search-help" class="sr-only">
  Kirjoita pelaajan nimi etsiäksesi tietoja
</div>
```

### Screen Reader Announcements

Dynamic content changes are announced to screen readers:

```javascript
// Announce content changes
function announceToScreenReader(message, priority = 'polite') {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

// Usage
announceToScreenReader('Uusi peli alkaa');
announceToScreenReader('Pelaajan tilastot päivitetty', 'assertive');
```

## Keyboard Navigation

### Tab Order

Logical tab order for all interactive elements:

```html
<!-- Proper tab order -->
<div class="finnish-player-card">
  <h3 tabindex="0" role="button" aria-expanded="false">
    Pelaajan Nimi
  </h3>
  <div class="player-details" hidden>
    <!-- Expandable content -->
  </div>
</div>
```

### Keyboard Shortcuts

Common keyboard shortcuts for enhanced usability:

```javascript
// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
  // Alt + S: Focus search
  if (e.altKey && e.key === 's') {
    e.preventDefault();
    document.getElementById('player-search').focus();
  }
  
  // Escape: Close modal
  if (e.key === 'Escape') {
    closeModal();
  }
  
  // Arrow keys: Navigate list
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    navigateList(e.key === 'ArrowDown' ? 1 : -1);
  }
});
```

### Accessible Menus

Keyboard-accessible dropdown menus:

```html
<nav aria-label="Päävalikko">
  <button 
    aria-haspopup="true" 
    aria-expanded="false"
    aria-controls="menu-dropdown"
  >
    Valikko
  </button>
  <ul id="menu-dropdown" role="menu" hidden>
    <li role="none">
      <a href="#" role="menuitem">Koti</a>
    </li>
    <li role="none">
      <a href="#" role="menuitem">Tilastot</a>
    </li>
  </ul>
</nav>
```

## Color Contrast

### Contrast Ratios

All text meets WCAG AA contrast requirements:

- **Normal text**: 4.5:1 minimum
- **Large text**: 3:1 minimum
- **Interactive elements**: 3:1 minimum

### Contrast Testing

Regular contrast testing across all themes:

```css
/* High contrast testing */
@media (prefers-contrast: high) {
  .finnish-component {
    border-width: 2px;
    color: var(--fg-primary);
    background: var(--bg-canvas);
  }
}
```

### Color Independence

Information not conveyed through color alone:

```html
<!-- Good: Multiple indicators -->
<span class="finnish-status-pill finnish-status-pill--live">
  <span class="status-indicator" aria-hidden="true">●</span>
  <span>LIVE</span>
</span>

<!-- Bad: Color only -->
<span class="live-indicator">LIVE</span>
```

## Reduced Motion

### Motion Preferences

Respect user's motion preferences:

```css
/* Respect reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Alternative for reduced motion */
@media (prefers-reduced-motion: reduce) {
  .finnish-loading-spinner {
    animation: none;
  }
  
  .finnish-loading-spinner::before {
    content: 'Ladataan...';
    display: block;
    text-align: center;
  }
}
```

### Accessible Animations

Animations that don't cause vestibular issues:

```css
/* Safe animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { 
    transform: translateY(10px);
    opacity: 0;
  }
  to { 
    transform: translateY(0);
    opacity: 1;
  }
}

/* Avoid problematic animations */
/* Avoid: rapid flashing, spinning, parallax */
```

## High Contrast Mode

### High Contrast Support

Enhanced visibility for high contrast mode:

```css
@media (prefers-contrast: high) {
  .finnish-card {
    border-width: 2px;
    border-color: var(--fg-primary);
  }
  
  .finnish-btn {
    border-width: 2px;
    background: var(--bg-canvas);
    color: var(--fg-primary);
  }
  
  .finnish-player-card__accent {
    height: 6px;
  }
  
  .finnish-status-pill {
    border-width: 2px;
  }
}
```

### Focus Enhancement

Enhanced focus indicators in high contrast mode:

```css
@media (prefers-contrast: high) {
  *:focus-visible {
    outline: 3px solid var(--focus-ring);
    outline-offset: 2px;
  }
}
```

## Finnish Language Support

### Finnish Typography

Optimized typography for Finnish characters:

```css
/* Finnish character support */
.finnish-text {
  font-family: var(--font-family-primary);
  letter-spacing: var(--finnish-letter-spacing);
  line-height: 1.5;
}

/* Support for Finnish vowels and consonants */
.finnish-heading {
  letter-spacing: 0.01em;
  word-spacing: 0.05em;
}
```

### Finnish Labels

Proper Finnish labels and descriptions:

```html
<!-- Finnish labels -->
<button aria-label="Avaa haku">
  <span aria-hidden="true">🔍</span>
</button>

<div aria-label="Pelaajan tilastot" role="region">
  <!-- Player statistics -->
</div>

<!-- Finnish descriptions -->
<span class="finnish-caption" aria-label="Kotipelissä">
  Kotona
</span>
```

### Language Attributes

Proper language attributes for screen readers:

```html
<html lang="fi">
<head>
  <meta charset="UTF-8">
  <title>Suomalaiset NHL-pelaajat</title>
</head>
<body>
  <!-- Content -->
</body>
</html>
```

## Testing Guidelines

### Accessibility Testing Tools

Recommended tools for accessibility testing:

1. **Automated Testing**
   - axe-core for automated accessibility testing
   - Lighthouse accessibility audit
   - WAVE browser extension

2. **Manual Testing**
   - Keyboard navigation testing
   - Screen reader testing (NVDA, JAWS, VoiceOver)
   - Color contrast analysis

3. **User Testing**
   - Test with actual assistive technology users
   - Test with Finnish language users
   - Test across different disabilities

### Testing Checklist

#### Keyboard Navigation
- [ ] All interactive elements reachable by keyboard
- [ ] Logical tab order
- [ ] Visible focus indicators
- [ ] Escape key functionality
- [ ] Enter/Space key activation

#### Screen Reader Support
- [ ] Semantic HTML structure
- [ ] Proper ARIA labels
- [ ] Live region announcements
- [ ] Form labels and descriptions
- [ ] Table headers and captions

#### Visual Accessibility
- [ ] Sufficient color contrast
- [ ] Text resizing support
- [ ] High contrast mode support
- [ ] Reduced motion support
- [ ] Focus indicators visible

#### Finnish Language Support
- [ ] Proper language attributes
- [ ] Finnish labels and descriptions
- [ ] Character support
- [ ] Text direction

## Implementation Examples

### Accessible Button

```html
<button 
  class="finnish-btn finnish-btn--primary"
  aria-label="Hae pelaajia"
  aria-describedby="search-help"
>
  <span aria-hidden="true">🔍</span>
  Hae
</button>
<div id="search-help" class="sr-only">
  Etsii suomalaisia NHL-pelaajia nimen perusteella
</div>
```

### Accessible Form

```html
<form aria-labelledby="search-form-title">
  <h2 id="search-form-title">Etsi pelaajaa</h2>
  
  <div class="form-group">
    <label for="player-name">Pelaajan nimi:</label>
    <input 
      type="text" 
      id="player-name"
      name="player-name"
      aria-required="true"
      aria-describedby="name-help name-error"
      autocomplete="name"
    >
    <div id="name-help" class="form-help">
      Kirjoita pelaajan koko nimi
    </div>
    <div id="name-error" class="form-error" role="alert" hidden>
      Nimi on pakollinen
    </div>
  </div>
  
  <button type="submit" class="finnish-btn finnish-btn--primary">
    Hae
  </button>
</form>
```

### Accessible Data Table

```html
<table 
  class="finnish-table"
  aria-labelledby="table-title"
  aria-describedby="table-description"
>
  <caption id="table-description">
    Suomalaisten NHL-pelaajien tilastot kaudelle 2024-2025
  </caption>
  
  <thead>
    <tr>
      <th scope="col" id="name-header">Pelaaja</th>
      <th scope="col" id="team-header">Joukkue</th>
      <th scope="col" id="goals-header">Maalit</th>
      <th scope="col" id="assists-header">Syötöt</th>
      <th scope="col" id="points-header">Pisteet</th>
    </tr>
  </thead>
  
  <tbody>
    <tr>
      <th scope="row" headers="name-header">
        <a href="/player/1" aria-describedby="player-1-details">
          Mikko Rantanen
        </a>
      </th>
      <td headers="team-header">Colorado Avalanche</td>
      <td headers="goals-header" aria-label="25 maalia">25</td>
      <td headers="assists-header" aria-label="35 syöttöä">35</td>
      <td headers="points-header" aria-label="60 pistettä">60</td>
    </tr>
  </tbody>
</table>
```

### Accessible Modal

```html
<div 
  class="finnish-modal"
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
  hidden
>
  <div class="finnish-modal__overlay" onclick="closeModal()"></div>
  <div class="finnish-modal__content">
    <div class="finnish-modal__card">
      <header>
        <h2 id="modal-title">Pelaajan tiedot</h2>
        <button 
          class="finnish-btn finnish-btn--icon-only"
          aria-label="Sulje ikkuna"
          onclick="closeModal()"
        >
          ✕
        </button>
      </header>
      
      <div id="modal-description">
        <!-- Modal content -->
      </div>
      
      <footer>
        <button class="finnish-btn finnish-btn--secondary" onclick="closeModal()">
          Sulje
        </button>
      </footer>
    </div>
  </div>
</div>
```

## Browser Support

### Accessibility Features Support

Our accessibility features work across:

- **Chrome**: Full support for all features
- **Firefox**: Full support for all features
- **Safari**: Full support for all features
- **Edge**: Full support for all features

### Screen Reader Support

Tested with:

- **NVDA** (Windows)
- **JAWS** (Windows)
- **VoiceOver** (macOS/iOS)
- **TalkBack** (Android)

## Related Documentation

- [Style Guide](./STYLE_GUIDE.md) - Overall design system
- [Components](./COMPONENTS.md) - Component-specific accessibility
- [Design Tokens](./DESIGN_TOKENS.md) - Accessibility tokens

## Contributing

When contributing to accessibility:

1. Test with keyboard navigation
2. Verify screen reader compatibility
3. Check color contrast ratios
4. Test with reduced motion
5. Ensure Finnish language support
6. Document accessibility features
7. Update this guide as needed

## Resources

### Accessibility Guidelines
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/TR/wai-aria-practices-1.1/)
- [Finnish Web Accessibility Guidelines](https://www.vaestorekisteri.fi/)

### Testing Tools
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE Web Accessibility Evaluation](https://wave.webaim.org/)
- [Colour Contrast Analyser](https://www.tpgi.com/color-contrast-checker/)

### Screen Readers
- [NVDA](https://www.nvaccess.org/)
- [JAWS](https://www.freedomscientific.com/products/software/jaws/)
- [VoiceOver](https://www.apple.com/accessibility/vision/)