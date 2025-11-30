# Design System
## NHL Finnish Players Application

### Version 1.0
### Last Updated: November 29, 2025

---

## 🎨 Design Philosophy

The NHL Finnish Players application follows a **minimal, professional, and user-friendly** design approach focused on clarity and readability. The design emphasizes data visualization, card-based layouts, and subtle interactive feedback.

**Core Principles:**
- ✅ **Minimal**: Clean, uncluttered interfaces with purposeful elements
- ✅ **Professional**: Business-appropriate colors and spacing
- ✅ **Readable**: High contrast, clear typography hierarchy
- ✅ **Responsive**: Seamless experience across all devices
- ✅ **Accessible**: WCAG compliant with proper contrast ratios
- ✅ **Finnish Heritage**: Subtle incorporation of Finnish blue (#003580)

---

## 🌈 Color Palette

### Primary Colors

#### Finnish Blue (Brand)
```css
--color-finnish-blue: #003580;
```
- **Usage**: Brand elements, highlights, important accents
- **Examples**: Team logo overlays, key statistics

#### Gray Scale
```css
Gray 900: #111827  /* Primary text, headings */
Gray 600: #4b5563  /* Secondary text, labels */
Gray 500: #6b7280  /* Placeholder text, captions */
Gray 50:  #f9fafb  /* Page background */
White:   #ffffff   /* Card backgrounds */
```

#### Border Colors
```css
Border 200: #e5e7eb  /* Default borders */
Border 300: #d1d5db  /* Active borders, dividers */
```

#### Semantic Colors

**Success (Green)**
- Background: `rgba(236, 252, 245, 0.9)`
- Border: `rgba(209, 250, 229, 0.7)`
- Text: `#22c55e` → `#16a34a`

**Error (Red)**
- Background: `rgba(239, 68, 68, 1)`
- Shadows: `rgba(239, 68, 68, 0.35)`

**Warning (Amber)**
- Used for overtime indicators
- Background: `rgba(245, 158, 11, 1)`

### Color Usage Guidelines

| Color | Primary Use | Secondary Use | Do's |
|-------|-------------|---------------|------|
| Finnish Blue (#003580) | Brand elements | Accents | Use for team logos, key stats |
| Gray 900 | Headings | Important text | Use for primary information |
| Gray 600 | Body text | Labels | Use for descriptions |
| Gray 500 | Captions | Metadata | Use for timestamps, counts |
| White | Cards | Backgrounds | Base color for all cards |
| Success Green | Wins | Positive stats | Use for wins, positive values |
| Red | Losses | Errors | Use for losses, negative stats |

---

## 📝 Typography

### Font Stack
- **Primary**: System font stack (Inter, -apple-system, BlinkMacSystemFont, "Segoe UI")
- **Monospace**: System monospace for code and data

### Font Sizes

#### Heading Scale
```css
Text 3xl: 1.875rem (30px)  /* Main page title */
Text 2xl: 1.5rem (24px)    /* Section titles */
Text xl:  1.25rem (20px)   /* Card titles */
Text lg:  1.125rem (18px)  /* Subsections */
Text base: 1rem (16px)     /* Body text */
```

#### Label Scale
```css
Text sm:  0.875rem (14px)  /* Small labels */
Text xs:  0.75rem (12px)   /* Captions, badges */
```

### Font Weights
```css
Font Bold: 700    /* Headings */
Font Semibold: 600 /* Labels, emphasis */
Font Medium: 500   /* Buttons */
Font Normal: 400   /* Body text */
Font ExtraBold: 800 /* Player names, stats */
```

### Text Colors
```css
.text-gray-900    /* Primary text, player names */
.text-gray-600    /* Secondary text, positions */
.text-gray-500    /* Captions, metadata */
.text-gray-400    /* Placeholder text */
```

### Letter Spacing
```css
Normal:  0        /* Body text */
Wide:    0.025em  /* Buttons */
Wider:   0.04em   /* Player initials */
```

---

## 📐 Spacing System

### Scale (Based on 4px base unit)
```css
0.25rem: 4px     /* Tight spacing */
0.5rem:  8px     /* Small gaps */
0.75rem: 12px    /* Medium gaps */
1rem:    16px    /* Standard padding */
1.25rem: 20px    /* Large padding */
1.5rem:  24px    /* Section spacing */
```

### Component Spacing Patterns

#### Card Padding
```css
Standard: 1rem (16px)
Large: 1.25rem (20px)
Modal: 1.5rem (24px)
```

#### Grid Gaps
```css
Small: 0.75rem (12px)
Medium: 1rem (16px)
Large: 1.5rem (24px)
```

#### Container Spacing
```css
Page: 2rem (32px) max-width padding
Section: 2rem (32px) vertical spacing
Component: 1rem (16px) internal spacing
```

---

## 📏 Layout & Grid

### Breakpoints
```css
sm:  640px   /* Small devices */
md:  768px   /* Medium devices */
lg:  1024px  /* Large devices */
xl:  1280px  /* Extra large */
```

### Grid System
- **Card Grid**: 1 column (mobile) → 2 columns (md) → 3 columns (lg) → 4 columns (xl)
- **Stat Grid**: 2-5 columns based on content
- **Container**: Max-width 6xl (1152px), centered

### Responsive Patterns

#### Player Cards
```css
Mobile (< 768px):   1 column
Tablet (768-1024px): 2-3 columns
Desktop (> 1024px):  3-4 columns
```

#### Hero Stats
```css
Mobile: Stack vertically
Desktop: Horizontal flex row
```

---

## 🎴 Card System

### Card Variants

#### Primary Player Card
```css
Background: white
Border: 1px solid #e5e7eb
Radius: 0.5rem (8px)
Shadow: 0 8px 18px rgba(15, 23, 42, 0.08)
Padding: 1rem
```

#### Enhanced Double Border Effect
```css
Outer Border:
  - Border: 1px solid rgba(148, 163, 184, 0.2)
  - Shadow: 0 8px 18px rgba(15, 23, 42, 0.08)
  - Radius: 12px

Middle Border:
  - Background: linear-gradient(135deg, #f8fafc, #e2e8f0)
  - Border: 1px solid rgba(148, 163, 184, 0.18)
  - Radius: 10px

Inner Border:
  - Background: white
  - Box Shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6)
  - Border: 1px solid rgba(226, 232, 240, 0.4)
  - Radius: 9px
```

#### Stat Card
```css
Background: linear-gradient(145deg, rgba(255, 255, 255, 0.9), rgba(248, 250, 252, 0.95))
Border: 1px solid rgba(226, 232, 240, 0.6)
Shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6), 0 1px 0 rgba(226, 232, 240, 0.6)
Radius: 10px
```

### Card Content Structure
```css
Header: Player name, position, team
Divider: 1px gradient line
Content: Stats grid
Footer: Result indicator, actions
```

---

## 🔘 Button System

### Button Variants

#### Primary Gradient Button
```css
Background: linear-gradient(135deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%)
Color: white
Border: 1px solid rgba(255, 255, 255, 0.2)
Radius: 8px
Padding: 10px 20px
Font-weight: 500
```

**Hover State:**
- Background: `linear-gradient(135deg, #2563eb 0%, #4f46e5 50%, #7c3aed 100%)`
- Transform: `translateY(-1px)`
- Shadow: Enhanced elevation

**Active State:**
- Transform: `translateY(0) scale(0.98)`
- Shadow: Reduced elevation

#### Secondary Gray Button
```css
Background: linear-gradient(135deg, #6b7280 0%, #9ca3af 50%, #d1d5db 100%)
Color: white
```

#### Success Green Button
```css
Background: linear-gradient(135deg, #10b981 0%, #34d399 50%, #6ee7b7 100%)
Color: white
```

#### Danger Red Button
```css
Background: linear-gradient(135deg, #ef4444 0%, #f87171 50%, #fca5a5 100%)
Color: white
```

#### Ghost Button
```css
Background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%)
Color: #475569
Border: 1px solid rgba(148, 163, 184, 0.3)
```

### Button Sizes
```css
Small:  padding: 6px 12px;  font-size: 0.875rem
Medium: padding: 10px 20px; font-size: 14px (default)
Large:  padding: 12px 32px; font-size: 1.125rem
```

### Interactive Effects

#### Shimmer Effect (All Gradient Buttons)
```css
::before pseudo-element:
  Position: absolute
  Content: ''
  Transform: rotate(45deg) translateX(-100%)
  Background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.2) 50%, transparent 70%)
  Transition: transform 0.6s ease
  Opacity: 0

:hover::before:
  Opacity: 1
  Transform: rotate(45deg) translateX(100%)
```

---

## 🎭 Loading States

### Loading Spinner
```css
Box: bg-white rounded-lg border border-gray-200 shadow-md
Padding: 1.5rem (default)
Spinner:
  - 3 rotating rings
  - Colors: gray-400, white, gray-300
  - Different speeds and delays
  - Reverse animation on second ring
```

### Skeleton Loader
```css
Background: linear-gradient(145deg, rgba(255, 255, 255, 0.92), rgba(248, 250, 252, 0.95))
Animation: pulse (1.5s ease-in-out infinite)
  - Background-position: 200% 0 → -200% 0
  - Creates shimmer effect

Staggered Delays:
  nth-child(1): 0.1s
  nth-child(2): 0.15s
  nth-child(3): 0.2s
  nth-child(4): 0.25s
```

#### Skeleton Variants
- **Avatar**: 52x52px, radius 12px
- **Logo**: 44x44px, radius 12px
- **Line Wide**: 70% width, 10px height
- **Line Narrow**: 40% width, 10px height
- **Line Compact**: 46px width, 8px height
- **Pill**: 96x14px
- **Chip**: 34x18px
- **Dot**: 10x10px
- **Score**: 64x24px

---

## 🔳 Visual Effects

### Shadows

#### Shadow Scale
```css
Light:   0 1px 3px rgba(0, 0, 0, 0.1)
Medium:  0 4px 6px rgba(0, 0, 0, 0.1)
Card:    0 8px 18px rgba(15, 23, 42, 0.08)
Modal:   0 10px 24px rgba(15, 23, 42, 0.08)
```

#### Shadow Variants by Component

**Player Card:**
```css
Outer:  0 8px 18px rgba(15, 23, 42, 0.08)
Inner:  inset 0 1px 0 rgba(255, 255, 255, 0.6)
```

**Button (Default):**
```css
Box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3),
            0 2px 4px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.2)
```

**Button (Hover):**
```css
Box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4),
            0 4px 8px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.3)
```

**Button (Active):**
```css
Box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35),
            0 2px 4px rgba(0, 0, 0, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.25)
```

### Gradients

#### Card Backgrounds
```css
Standard: linear-gradient(145deg, rgba(255, 255, 255, 0.86), rgba(248, 250, 252, 0.92))
Stat Panel: linear-gradient(140deg, rgba(236, 252, 245, 0.9), rgba(232, 247, 255, 0.9))
Overlay: radial-gradient(120% 80% at 0% 0%, rgba(59, 130, 246, 0.08), transparent 50%)
```

#### Button Backgrounds
```css
Primary: linear-gradient(135deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%)
Secondary: linear-gradient(135deg, #6b7280 0%, #9ca3af 50%, #d1d5db 100%)
Success: linear-gradient(135deg, #10b981 0%, #34d399 50%, #6ee7b7 100%)
Danger: linear-gradient(135deg, #ef4444 0%, #f87171 50%, #fca5a5 100%)
```

---

## 🎯 Indicators & Badges

### Result Dot Indicator
```css
Size: 10px × 10px
Radius: 999px (circle)
Double Border:
  - Outer: 2px ring-gray-300
  - Inner: bg-[color] (green/red/amber)
Shadow: shadow-md
Position: Card footer, left side
```

#### Result Dot Colors
```css
Win (W, SOW):    bg-green-500
Loss (L, SOL):   bg-red-500
Overtime (OTW, OTL): bg-amber-500
No Result:       bg-gray-400
```

### Live Badge
```css
Background: #ef4444
Color: white
Font-size: 0.65rem
Font-weight: 800
Padding: 2px 6px
Radius: 999px
Shadow: 0 6px 14px rgba(239, 68, 68, 0.35)
```

---

## 🔄 Transitions & Animations

### Timing Functions
```css
Standard: cubic-bezier(0.4, 0.0, 0.2, 1)
Button Hover: cubic-bezier(0.23, 1, 0.32, 1)
Smooth: ease-in-out
Quick: ease
```

### Duration Scale
```css
Fast: 0.12s    /* Hover states */
Normal: 0.3s   /* Standard transitions */
Medium: 0.4s   /* Button interactions */
Slow: 0.6s     /* Complex animations */
```

### Common Animations

#### Button Hover
```css
Transform: translateY(-1px) scale(1.02)
Transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1)
```

#### Card Hover
```css
Box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15)
Transition: box-shadow 0.2s ease
```

#### Image Loading
```css
Filter: blur → clear
Transition: filter 0.3s ease, opacity 0.3s ease
```

#### Skeleton Pulse
```css
Animation: pulse 1.5s ease-in-out infinite
Background-position: 200% 0 → -200% 0
```

---

## 📱 Responsive Design

### Mobile First Approach
- Start with mobile styles
- Add complexity at larger breakpoints
- Touch-friendly sizing (minimum 44px touch targets)

### Key Responsive Patterns

#### Player Cards
```css
< 768px: 1 column, stacked
768-1024px: 2-3 columns
> 1024px: 3-4 columns
```

#### Text Scaling
```css
Mobile: Text base (16px) minimum
Desktop: Can use smaller text (14px) if needed
```

#### Spacing
```css
Mobile: 1rem padding
Desktop: 1.5rem padding
```

---

## ✅ Accessibility

### Color Contrast
- All text meets WCAG AA standards (4.5:1 minimum)
- Interactive elements have visible focus states
- Color is never the only indicator of meaning

### Focus States
```css
Button Focus:
  Box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3),
              0 2px 4px rgba(0, 0, 0, 0.1),
              inset 0 1px 0 rgba(255, 255, 255, 0.2),
              0 0 0 3px rgba(59, 130, 246, 0.4)
```

### Semantic HTML
- Proper heading hierarchy (h1 → h2 → h3)
- Landmarks (main, nav, section)
- Alt text for images
- ARIA labels where needed

### Touch Targets
- Minimum 44px × 44px for interactive elements
- Adequate spacing between targets

---

## 🧩 Component Library

### Core Components

#### 1. PlayerCard
- **Props**: player data object
- **Variants**: Skater, Goalie
- **States**: Default, Loading (skeleton), Hover
- **Features**: Flippable, Color-coded result dot

#### 2. PlayerCardSkeleton
- **Props**: None
- **Animation**: Pulse with staggered delays
- **Usage**: Loading state placeholder

#### 3. LoadingSpinner
- **Props**: message, size (small/medium/large)
- **Animation**: Multi-ring rotation
- **Usage**: Data loading states

#### 4. TeamLogo
- **Props**: team (string), size (number)
- **Types**: Team abbreviation lookup
- **Fallback**: Generic NHL logo

#### 5. DateControls
- **Props**: selectedDate, onDateChange
- **Features**: Previous/Next, Today, Calendar picker
- **Responsive**: Collapsible on mobile

### Composite Components

#### 6. PlayerList
- **Composition**: PlayerCard + filters + sorting
- **States**: Loading, Empty, Error, Populated
- **Features**: Position grouping (Forwards/Defense/Goalies)

#### 7. HeroStats
- **Composition**: Stats cards in flex layout
- **Data**: Total goals, assists, points, PIMs
- **Animation**: Number counting on mount

---

## 🎨 Design Tokens

### CSS Custom Properties
```css
:root {
  /* Colors */
  --color-finnish-blue: #003580;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Border Radius */
  --radius-sm: 0.375rem;  /* 6px */
  --radius-md: 0.5rem;    /* 8px */
  --radius-lg: 0.75rem;   /* 12px */
  --radius-xl: 1rem;      /* 16px */
  --radius-full: 999px;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 8px 18px rgba(15, 23, 42, 0.08);
  --shadow-xl: 0 10px 24px rgba(15, 23, 42, 0.08);

  /* Transitions */
  --transition-fast: 0.12s ease;
  --transition-normal: 0.3s ease;
  --transition-slow: 0.4s cubic-bezier(0.23, 1, 0.32, 1);
}
```

---

## 📚 Usage Guidelines

### Do's ✅

1. **Use established patterns** - Reuse existing components
2. **Maintain consistency** - Follow spacing, colors, typography
3. **Ensure accessibility** - Test with keyboard and screen readers
4. **Responsive first** - Design mobile, enhance for desktop
5. **Use semantic HTML** - Proper tags for better accessibility
6. **Test contrast ratios** - Maintain WCAG AA standards
7. **Document changes** - Update this design system

### Don'ts ❌

1. **Don't invent new colors** - Use established palette
2. **Don't ignore spacing** - Follow 4px base unit
3. **Don't skip focus states** - Always include keyboard navigation
4. **Don't use magic numbers** - Use design tokens
5. **Don't forget responsive** - Test on all breakpoints
6. **Don't hardcode values** - Use CSS variables
7. **Don't break consistency** - New components should match existing patterns

---

## 🔄 Change Log

### v1.0 (November 29, 2025)
- Initial design system documentation
- Color palette established
- Component library defined
- Typography scale documented
- Spacing system defined
- Button system created
- Card system established
- Loading states designed
- Animation patterns documented

---

## 📞 Contact & Resources

**Design System Maintainer**: Development Team
**Last Reviewed**: November 29, 2025
**Next Review**: Quarterly

### Resources
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Finnish Blue Color Guide](https://www.suomi.fi/colors)

---

*This design system is a living document and should be updated as the application evolves. When making design decisions, refer to this document and update it accordingly.*
