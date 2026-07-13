# CV — Codebase Map

*Last Updated: 2026-07-13*

A CV/resume generation system for Tomasz Trębski (Lead Software Developer). Produces a PDF via
Pandoc + XeLaTeX and a static Astro web SPA from the same YAML source data.

## Docs

| Doc | What it covers |
|-----|---------------|
| [architecture.md](architecture.md) | System overview, components, data flow |
| [tech-landscape.md](tech-landscape.md) | Languages, frameworks, runtimes, tooling |
| [directory-structure.md](directory-structure.md) | Annotated folder tree |
| [entry-points.md](entry-points.md) | Where builds and the web app begin |
| [patterns.md](patterns.md) | Build patterns, YAML conventions, CI/CD |
| [onboarding.md](onboarding.md) | Quick start, common tasks |

## Quick orientation

- Source data: `data/**/*.yml` composed via `cv.yml` with `!include` directives
- PDF build: `make cv.pdf` (Docker + Pandoc + XeLaTeX, no local LaTeX needed)
- Web build: `make web` → `cd web && npm run build` (Astro SPA)
- Python tooling: `uv run expand_includes.py cv.yml` resolves `!include` before Pandoc

## How to use this map

Read `INDEX.md` for orientation. Open specific docs when working in that area. The
`codebase-mapper` plugin injects this file on every prompt.

## How to maintain this map

Update the relevant doc when you change an area. Run `/codebase-mapper:update-codebase-map` after
significant changes. Commit `.claude/.codebase-info/` so the whole team shares it.
