# Design System Quick Reference
*For Daily Development Use*

---

## 🎨 Essential Classes

### Colors
```css
/* Text */
.text-gray-900  /* Primary text, headings */
.text-gray-600  /* Secondary text */
.text-gray-500  /* Captions */

/* Backgrounds */
.bg-white       /* Cards */
.bg-gray-50     /* Page background */
.bg-finnish-blue /* Brand color (#003580) */

/* Borders */
.border-gray-200 /* Default borders */
.border-gray-300 /* Active borders */
```

### Spacing (Most Common)
```css
/* Padding */
.p-4   /* 1rem - Standard card padding */
.p-6   /* 1.5rem - Large containers */
.px-4  /* 1rem left/right */
.py-8  /* 2rem top/bottom */

/* Margins */
.m-4   /* 1rem */
.mb-6  /* 1.5rem bottom */
.mt-8  /* 2rem top */
.gap-6 /* 1.5rem flex/grid gaps */
```

### Borders
```css
.rounded-lg    /* 0.5rem - Standard radius */
.rounded-xl    /* 0.75rem - Large radius */
.rounded-full  /* 999px - Circles */
.border        /* 1px border */
.border-2      /* 2px border */
```

### Shadows
```css
.shadow-md     /* Standard card shadow */
.shadow-lg     /* Elevated elements */
.shadow-sm     /* Subtle shadows */
```

---

## 🔘 Buttons

### Gradient Buttons (Primary)
```html
<button class="gradient-button-primary">
  Button Text
</button>

<!-- Sizes -->
<button class="gradient-button-primary gradient-button-primary--sm">Small</button>
<button class="gradient-button-primary gradient-button-primary--lg">Large</button>

<!-- Hover Effects -->
<button class="gradient-button-primary scale">Scale</button>
<button class="gradient-button-primary elevate">Elevate</button>
<button class="gradient-button-primary glow">Glow</button>
```

### Button Variants
```html
<!-- Secondary (Gray) -->
<button class="gradient-button-secondary">Secondary</button>

<!-- Success (Green) -->
<button class="gradient-button-success">Success</button>

<!-- Danger (Red) -->
<button class="gradient-button-danger">Delete</button>

<!-- Ghost (Light) -->
<button class="gradient-button-ghost">Cancel</button>
```

---

## 📴 Cards

### Player Card Structure
```html
<div class="bg-white rounded-lg border border-gray-200 shadow-md p-4">
  <!-- Content -->
</div>
```

### Enhanced Card (Double Border)
```html
<div class="relative">
  <!-- Outer Border -->
  <div class="absolute inset-0 border border-gray-200/20 rounded-xl shadow-lg"></div>

  <!-- Middle Border -->
  <div class="absolute inset-[2px] bg-gradient-to-br from-slate-50 to-slate-100 border border-gray-200/18 rounded-lg"></div>

  <!-- Inner Content -->
  <div class="relative bg-white rounded-lg shadow-inner border border-gray-200/40">
    <!-- Your content here -->
  </div>
</div>
```

---

## 📊 Grid Layouts

### Responsive Card Grid
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  <!-- Cards -->
</div>
```

### Stats Grid
```html
<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
  <!-- Stat items -->
</div>
```

---

## 🎯 Indicators

### Result Dot (Win/Loss)
```html
<div class="w-2.5 h-2.5 rounded-full ring-2 ring-gray-300 bg-green-500 shadow-md" title="W"></div>

<!-- Colors -->
bg-green-500   /* Win */
bg-red-500     /* Loss */
bg-amber-500   /* Overtime */
bg-gray-400    /* No result */
```

### Live Badge
```html
<span class="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">
  LIVE
</span>
```

---

## 🔄 Loading States

### Loading Spinner
```html
<LoadingSpinner message="Loading..." size="medium" />

<!-- Props -->
message: string    /* Default: "Loading..." */
size: small|medium|large
showProgress: boolean
progress: number   /* 0-100 */
```

### Skeleton Loader
```html
<!-- In component -->
{#if isLoading}
  <PlayerCardSkeleton />
{/if}
```

---

## 📱 Responsive Breakpoints

```css
sm:  640px   /* Mobile landscape */
md:  768px   /* Tablet */
lg:  1024px  /* Desktop */
xl:  1280px  /* Large desktop */
```

### Usage Examples
```html
<!-- Text sizing -->
<h1 class="text-2xl md:text-3xl">Responsive Heading</h1>

<!-- Grid columns -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  <!-- Content -->
</div>

<!-- Spacing -->
<div class="p-4 md:p-6 lg:p-8">
  <!-- Content -->
</div>
```

---

## 🎨 Common Patterns

### Card with Hover Effect
```html
<div class="bg-white rounded-lg border border-gray-200 shadow-md hover:shadow-lg transition-shadow duration-200">
  <!-- Content -->
</div>
```

### Centered Content
```html
<div class="flex items-center justify-center">
  <!-- Centered content -->
</div>
```

### Space Between
```html
<div class="flex items-center justify-between">
  <!-- Left and right content -->
</div>
```

### Divider Line
```html
<div class="h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent"></div>
```

---

## 🎭 Animations

### Hover Elevation
```css
/* On hover */
transform: translateY(-2px);
transition: transform 0.4s cubic-bezier(0.23, 1, 0.32, 1);
```

### Button Pulse
```css
/* Active state */
transform: translateY(0) scale(0.98);
```

### Fade In
```css
opacity: 0;
animation: fadeIn 0.4s ease-in-out forwards;

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
```

---

## 📝 Typography Examples

### Headings
```html
<h1 class="text-3xl font-bold text-gray-900">Page Title</h1>
<h2 class="text-2xl font-bold text-gray-900">Section Title</h3>
<h3 class="text-lg font-semibold text-gray-900">Card Title</h4>
```

### Body Text
```html
<p class="text-base text-gray-900">Primary text</p>
<p class="text-sm text-gray-600">Secondary text</p>
<p class="text-xs text-gray-500">Caption</p>
```

### Labels
```html
<span class="text-sm font-medium text-gray-700">Label</span>
<span class="text-xs font-bold text-gray-900">Badge</span>
```

---

## ✅ CSS Grid Classes

### Column Counts
```css
grid-cols-1   /* 1 column (mobile) */
grid-cols-2   /* 2 columns */
grid-cols-3   /* 3 columns */
grid-cols-4   /* 4 columns */
```

### Gap Sizes
```css
gap-1   /* 0.25rem (4px) */
gap-3   /* 0.75rem (12px) */
gap-4   /* 1rem (16px) */
gap-6   /* 1.5rem (24px) */
gap-8   /* 2rem (32px) */
```

---

## 🔧 Utility Classes

### Positioning
```css
.relative  /* Position relative */
.absolute  /* Position absolute */
.fixed     /* Position fixed */
.sticky    /* Position sticky */
```

### Display
```css
.block     /* Display block */
.inline    /* Display inline */
.flex      /* Display flex */
.grid      /* Display grid */
.hidden    /* Display none */
```

### Flexbox
```css
.flex          /* Display flex */
.items-center  /* Align items center */
.justify-center/* Justify center */
.justify-between /* Space between */
.flex-col     /* Flex direction column */
.flex-wrap    /* Flex wrap */
```

### Text
```css
.text-center   /* Text align center */
.text-left     /* Text align left */
.text-right    /* Text align right */
.font-bold     /* Font weight bold */
.font-semibold /* Font weight semibold */
```

---

## 📋 Checklists

### New Component Checklist
- [ ] Uses established color palette
- [ ] Follows spacing system (4px base)
- [ ] Has responsive design
- [ ] Includes hover states
- [ ] Has focus states for accessibility
- [ ] Uses semantic HTML
- [ ] Meets WCAG AA contrast ratios
- [ ] Tested on mobile and desktop

### Button Checklist
- [ ] Uses gradient-button-* classes
- [ ] Has appropriate size variant
- [ ] Includes hover effect
- [ ] Has focus state
- [ ] Icon (if applicable) is centered
- [ ] Minimum 44px touch target

### Card Checklist
- [ ] White background
- [ ] Gray border (border-gray-200)
- [ ] Rounded corners (rounded-lg)
- [ ] Shadow (shadow-md)
- [ ] Proper padding (p-4 or p-6)
- [ ] Hover state defined

---

## 🚀 Quick Start Template

### Basic Card
```html
<div class="bg-white rounded-lg border border-gray-200 shadow-md p-4">
  <h3 class="text-lg font-semibold text-gray-900 mb-2">Title</h3>
  <p class="text-sm text-gray-600">Content</p>
</div>
```

### Button with Icon
```html
<button class="gradient-button-primary flex items-center gap-2">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <!-- Icon path -->
  </svg>
  <span>Button Text</span>
</button>
```

### Grid of Cards
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  <!-- Repeat card component -->
</div>
```

---

## 💡 Pro Tips

1. **Use Tailwind's spacing scale** - It follows a consistent 4px base unit
2. **Prefer utility classes** - Don't write custom CSS unless necessary
3. **Mobile first** - Design for mobile, then enhance for larger screens
4. **Consistent borders** - Use border-gray-200 for cards, border-gray-300 for active states
5. **Semantic HTML first** - Use `<button>` for buttons, `<a>` for links
6. **Test keyboard navigation** - Ensure all interactive elements are focusable
7. **Use design tokens** - Reference DESIGN_SYSTEM.md for values

---

*Last Updated: November 29, 2025*
