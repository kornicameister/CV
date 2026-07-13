# Onboarding

*Last Updated: 2026-07-13*

## Prerequisites

- Docker (for Pandoc/XeLaTeX and yaml-to-json)
- `uv` (Python tool runner — no virtualenv needed)
- Node.js ≥18 + npm (for the Astro web frontend)

No local LaTeX installation required.

## Quick start

```bash
# 1. Build the PDF (most common)
make cv.pdf               # → build/cv.pdf

# 2. Build just the JSON
make cv.json              # → build/cv.json

# 3. Build the web frontend
make web                  # → web/dist/

# 4. (Re)build the Docker image if dependencies changed
make build_docker

# 5. Preview the web locally
cd web && npm run dev     # → http://localhost:4321/CV
```

## Common tasks

### Add a new experience entry

1. Create `data/experience/<company-slug>.yml` with the schema in `patterns.md`
2. Add `  - !include data/experience/<company-slug>.yml` to `cv.yml` under `experience:`
3. Run `make cv.pdf` to verify it renders

### Add a new skill category

1. Create `data/skills/<name>.yml` with `name:` and `items:` keys
2. Add `  - !include data/skills/<name>.yml` to `cv.yml` under `skill:`

### Edit existing content

Edit the relevant file in `data/`. Changes propagate on next `make` invocation.

### Update the web frontend

Components live in `web/src/components/`. The page is `web/src/pages/index.astro`.
Run `cd web && npm run dev` for hot-reload during development.

### Debug a broken PDF build

1. Check `build/cv.yml` was generated: `make build/cv.yml`
2. Inspect it — if `!include` directives are still present, `expand_includes.py` failed
3. Verify Docker image exists: `docker images pandoc`
4. LaTeX errors appear in Pandoc stdout

## CI

Push to `master` or open a PR → CI checks prettier on `cv.yml`, builds PDF + JSON, uploads as artifact.
Tag `v*` → Release workflow creates a GitHub Release with PDF and JSON.
Push to `master` (after merge) → Astro site deployed to GitHub Pages.
