# CV SPA - Claude Instructions

This is a modern single-page application (SPA) built with Astro 7.x for displaying CV content online.

## Architecture

- **Framework:** Astro 7.x with View Transitions (ClientRouter)
- **Styling:** Vanilla CSS with CSS custom properties for theming
- **JavaScript:** Minimal (~16KB total) - scroll-spy navigation + accordion interactions
- **Data Source:** Static JSON (`src/data/cv.json`) copied from root `build/cv.json`
- **Deployment Target:** GitHub Pages (base path: `/CV`)

## Key Features

1. **Auto Dark/Light Theme** - Detects system preference via `prefers-color-scheme`
2. **Hero Section** - Profile photo with hover effect (swaps to developer avatar)
3. **Experience Accordion** - Collapsible job entries, only one expanded at a time
4. **Scroll-Spy Navigation** - Fixed right-side nav with IntersectionObserver, updates URL hash
5. **Responsive Design** - Breakpoints at 640px (mobile) and 1024px (tablet)
6. **FontAwesome Icons** - Loaded via CDN for skill categories

## Development Workflow

### Setup & Build
```bash
# From root directory
make web-dev    # Build JSON, copy assets, start dev server
make web        # Production build to web/dist/
make clean-web  # Clean generated files
```

### Data Updates
When CV data (YAML in `data/`) changes:
1. Run `make cv.json` from root (generates `build/cv.json`)
2. Run `make web-dev` or `make web` (copies to `web/src/data/cv.json`)

## Global Constraints

- **JavaScript budget:** < 10KB custom code (Astro router excluded)
- **CSS budget:** < 50KB
- **No runtime data fetching:** 100% static generation
- **Browser support:** Last 2 versions (Chrome, Firefox, Safari, Edge)

## Common Tasks

### Add a New Component
1. Create `src/components/NewComponent.astro`
2. Define TypeScript interface for props
3. Add component to `src/pages/index.astro`
4. If section: add to NavIndicator with unique ID

### Update Theme Colors
Edit `src/styles/global.css`:
```css
:root {
  --accent-from: #3b82f6;  /* Light mode accent start */
  --accent-to: #8b5cf6;    /* Light mode accent end */
}

@media (prefers-color-scheme: dark) {
  :root {
    --accent-from: #60a5fa;  /* Dark mode accent start */
    --accent-to: #a78bfa;    /* Dark mode accent end */
  }
}
```

## Troubleshooting

**Dev server won't start:**
```bash
cd web
npm install
rm -rf node_modules/.astro
```

**JavaScript not working:**
- Open Console (F12) for errors
- Verify script uses `astro:page-load` event

**Images not showing:**
- Run `make web-dev` to copy media files
- Check `public/media/` directory

## References

- [Astro Documentation](https://docs.astro.build)
- [FontAwesome 6 Icons](https://fontawesome.com/icons)
