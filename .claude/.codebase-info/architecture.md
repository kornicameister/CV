# Architecture

*Last Updated: 2026-07-13*

## Overview

Two independent output pipelines share one YAML source:

```
data/**/*.yml
     │
     └─ cv.yml (!include composition)
          │
          ├─ expand_includes.py ──► build/cv.yml
          │                              │
          │               ┌─────────────┴──────────────┐
          │               │                            │
          │     Pandoc+XeLaTeX (Docker)      Python yaml→json
          │               │                            │
          │          build/cv.pdf              build/cv.json
          │                                         │
          │                                  web/src/data/cv.json
          │                                         │
          │                                  Astro SPA (web/)
          │                                         │
          │                              web/dist/ (static site)
          │
          └─ (also produces build/cv.json for web)
```

## Components

| Component | Path | Role |
|-----------|------|------|
| Data layer | `data/` | YAML source-of-truth for all CV content |
| Composition file | `cv.yml` | Assembles sections via `!include`; the only file Pandoc/build sees |
| Include expander | `expand_includes.py` | Resolves non-standard `!include` YAML directives recursively |
| LaTeX template | `template/cv.tex` | Awesome-CV template; maps YAML keys to LaTeX macros |
| Pandoc container | `Dockerfile` | `pandoc/extra` base + fontawesome6, roboto, xelatex |
| Web frontend | `web/` | Astro SPA; reads `cv.json` at build time, no server-side rendering |

## Data flow — PDF

1. `make cv.pdf` triggers `build/cv.yml` target
2. `uv run expand_includes.py cv.yml > build/cv.yml` — all `!include` directives resolved
3. Docker runs `pandoc` with `--pdf-engine=xelatex --template=template/cv.tex`
4. Output: `build/cv.pdf`

## Data flow — Web

1. `make web` triggers `build/cv.json` target first
2. Python one-liner converts `build/cv.yml` → `build/cv.json` (handles `date` → ISO string)
3. `cp build/cv.json web/src/data/cv.json` (also copies `media/` → `web/public/media/`)
4. `cd web && npm run build` — Astro static build → `web/dist/`

## Deployment

- PDF: GitHub Release artifact (on `v*` tags)
- Web: GitHub Pages via `deploy-web.yml` workflow, published at `https://kornicameister.github.io/CV`
