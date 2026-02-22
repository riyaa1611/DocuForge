

# Add Smooth Theme Transition Animations

## Overview
Add CSS transitions to create a smooth, polished experience when users switch between light and dark modes. The transition will animate background colors, text colors, and border colors across the entire application.

## Implementation Details

### 1. Update `src/index.css`
Add a global CSS transition rule that applies to all elements when the theme changes:

- Add a new utility class and base styles that apply `transition-colors` behavior to the HTML element
- Target `background-color`, `color`, `border-color`, and `fill` properties
- Use a 200-300ms duration for a smooth but responsive feel
- Apply `ease-out` timing function for natural deceleration

The transition will be applied to the `html` element so it cascades to all children, ensuring consistent animation across the entire interface.

### 2. Optional Enhancement: Disable Transitions on Initial Load
To prevent a flash of transition on page load, we can add a small script that adds a "no-transition" class initially and removes it after the page loads. However, `next-themes` handles this well with its `disableTransitionOnChange` prop set to `false` (the default), so we may not need this.

---

## Technical Notes

The implementation uses CSS custom properties (CSS variables) which naturally support transitions. By adding `transition` properties to colors that reference these variables, the browser will smoothly interpolate between the light and dark values.

Key CSS properties that will transition:
- `background-color` - for backgrounds, cards, buttons
- `color` - for text content
- `border-color` - for borders and dividers
- `fill` and `stroke` - for SVG icons

