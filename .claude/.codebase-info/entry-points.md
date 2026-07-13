# Entry Points

*Last Updated: 2026-07-13*

## Build entry points

| Target | Command | What it does |
|--------|---------|-------------|
| PDF | `make cv.pdf` | Full PDF build: expand → pandoc+xelatex → `build/cv.pdf` |
| JSON only | `make cv.json` | YAML → JSON → `build/cv.json` |
| Web | `make web` | JSON + Astro build → `web/dist/` |
| Full CV with appendix | `make cv_full.pdf` | PDF + appendix.md joined with pdfunite |
| Docker image | `make build_docker` | Builds `pandoc:latest` from `Dockerfile` |
| Clean | `make clean` | Removes `build/`, `web/dist/`, `web/src/data/cv.json`, `web/public/media/` |

## Python entry point

`expand_includes.py` — called as `uv run expand_includes.py cv.yml > build/cv.yml`.
Recursively resolves `!include <path>` directives. No arguments beyond the input file.

## Web entry point

`web/src/pages/index.astro` — the single page of the SPA.
- Imports `cv.json` at build time
- Renders: `Hero` → `Experience` → `Certifications` → `Skills` → `Education` + `NavIndicator`
- Client-side scroll-spy updates URL hash and nav dots

## CI/CD entry points

| Trigger | Workflow | Result |
|---------|----------|--------|
| Push/PR to `master` | `.github/workflows/ci.yml` | Prettier check → PDF/JSON build → artifact upload |
| `v*` tag push | `.github/workflows/release.yml` | GitHub Release with PDF/JSON attached |
| Push to `master` | `.github/workflows/deploy-web.yml` | Web SPA deployed to GitHub Pages |
