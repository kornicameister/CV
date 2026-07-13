# Project structure — CV

## Purpose

A CV/resume generation system that maintains source data in modular YAML files and produces:
- PDF output via Pandoc + XeLaTeX in Docker (the primary artifact)
- JSON output for the web frontend
- An Astro-based static site (`web/`) that renders the CV as a SPA

## Organizing principle

**Data lives in `data/`, presentation lives in `template/`, web in `web/`, build artifacts in `build/`.**
Nothing generated belongs in the root or `data/` directories.

## Where things go

| What | Where |
|------|-------|
| CV content (jobs, skills, education, etc.) | `data/<section>/<entry>.yml` |
| Top-level YAML composition | `cv.yml` (uses `!include` directives) |
| LaTeX template | `template/cv.tex` + `awesome-cv.cls` |
| Fonts for PDF | `fonts/` |
| Astro frontend source | `web/src/` |
| Web data (generated JSON) | `web/src/data/cv.json` (generated, gitignored) |
| Build artifacts (PDF, JSON) | `build/` (gitignored) |
| Media/photos | `media/` |
| GitHub Actions workflows | `.github/workflows/` |
| Python tooling (`expand_includes.py`) | repo root |

## Build pipeline

1. `expand_includes.py` resolves `!include` in `cv.yml` → `build/cv.yml`
2. Pandoc (Docker) + XeLaTeX → `build/cv.pdf`
3. `yaml-to-json` (Docker) → `build/cv.json` → copied to `web/src/data/cv.json`
4. Astro (`web/`) builds the SPA from `cv.json`

All builds go through `make`. No local LaTeX installation needed.

## Key constraints

- `cv.yml` uses a non-standard `!include` YAML directive — never pass it raw to a YAML parser without
  running `expand_includes.py` first.
- The Astro site at `web/` is a separate Node project (`web/package.json`) but lives in the same repo.
- GDPR compliance text is in `data/rodo.yml` — always keep it in the output.
