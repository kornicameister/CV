# CV Website

Modern single-page application (SPA) for displaying CV content online.

## Tech Stack

- **Framework:** Astro 6.x
- **Styling:** CSS (vanilla, CSS variables for theming)
- **JavaScript:** Vanilla JS for scroll-spy navigation (~2KB)
- **Deployment:** GitHub Pages

## Features

- 📱 Fully responsive (mobile, tablet, desktop)
- 🌓 Auto dark/light mode (system preference detection)
- 🔗 URL routing with scroll-spy navigation
- ⚡ Fast load times (< 3s on 3G)
- 🎨 Modern design with gradients and animations
- ♿ Accessible navigation

## Development

### Prerequisites

- Node.js 18+
- Data generated from root: `make cv.json`

### Commands

```bash
# Start dev server
make web-dev

# Production build
make web

# Clean build artifacts
make clean-web
```

### Dev Server

```bash
cd web
npm run dev
```

Visit: `http://localhost:4321`

## Build Process

1. Root Makefile generates `build/cv.json` from YAML data
2. JSON + media files copied to `web/src/data/` and `web/public/media/`
3. Astro builds static site to `web/dist/`
4. Deploy `web/dist/` to hosting

## Project Structure

```
web/
├── src/
│   ├── pages/
│   │   └── index.astro           # Main page
│   ├── components/
│   │   ├── Hero.astro            # Hero section
│   │   ├── Experience.astro      # Experience timeline
│   │   ├── Certifications.astro  # Certs grid
│   │   ├── Skills.astro          # Skills by category
│   │   ├── Education.astro       # Education timeline
│   │   └── NavIndicator.astro    # Scroll-spy nav
│   ├── layouts/
│   │   └── BaseLayout.astro      # Base HTML wrapper
│   ├── styles/
│   │   └── global.css            # Global styles & theme
│   └── data/
│       └── cv.json               # CV data (generated)
└── public/
    └── media/                     # Images (copied)
```

## Deployment

### GitHub Pages

1. Build: `make web`
2. Deploy `web/dist/` to `gh-pages` branch
3. GitHub Actions handles this automatically on push to `master`

### Manual Deploy

```bash
make web
cd web/dist
# Deploy these files to any static hosting
```

## Browser Support

Modern browsers (last 2 versions):
- Chrome 111+
- Firefox
- Safari 18+
- Edge

## Performance

- **FCP:** < 1.5s
- **TTI:** < 3.0s
- **JS bundle:** < 10KB
- **CSS bundle:** < 50KB

## Customization

### Theme

Edit `web/src/styles/global.css` CSS variables:

```css
:root {
  --accent-from: #3b82f6;
  --accent-to: #8b5cf6;
  /* ... */
}
```

### Sections

Add/remove sections in `web/src/pages/index.astro`.
