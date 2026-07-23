# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Fact Verification — CV Content

**NEVER state facts about CV content from memory. ALWAYS verify first.**

When writing about CV content (LinkedIn posts, summaries, examples):

1. **Read the actual CV data files first** — `data/experience/*.yml`, `data/skills/*.yml`, etc.
2. **Use exact quotes or paraphrases** from those files — never invent examples
3. **If creating examples** — pull from real bullets in the CV, not from imagination

Making up facts about CV content is **absolutely forbidden**. If you catch yourself about to state a CV fact without having read the files — STOP. Read the files first.

Wrong:
- "Reduced MTTR from 45 to 15 minutes" (invented metric)
- "Freed 2 engineers" (invented outcome)

Right:
- Read `data/**/*.yml` first, this is source of truth !!!
- Quote: "founded the AI agent platform with first cross-account access proof-of-concept, contributing 45% of all commits"
- Quote: "gave every developer on the 7-person team the ability to deploy independently"

This applies to ALL CV-related content: blog posts, LinkedIn messages, summaries, examples.

## Overview

This is a CV/Resume generation system that:

- Maintains CV data in modular YAML files (`data/` directory)
- Uses a custom `!include` directive for composable YAML structure
- Generates PDF output via Pandoc + XeLaTeX in Docker
- Produces JSON output for web consumption
- Uses the Awesome-CV LaTeX template for professional formatting

## Python

All Python scripts and tools are run via `uv`. Never use `python` or
`pip` directly.

- Run scripts: `uv run script.py`
- Run with ad-hoc deps: `uv run --with <package> script.py`
- Never create virtualenvs manually — `uv` manages them automatically

## Build Commands

All builds run through Make + Docker (no local LaTeX dependencies required):

```bash
# Build the CV PDF (most common)
make cv.pdf

# Build JSON output for web
make cv.json

# Build full CV with appendix (if appendix.md exists)
make cv_full.pdf

# Build Docker image (pandoc container)
make build_docker

# Clean build artifacts
make clean
```

Build artifacts go to `build/` directory.

## Architecture

### Data Structure

CV data is split across `data/` subdirectories:

- `basic.yml` - name, position, photo
- `contact.yml` - address, email
- `social.yml` - LinkedIn, GitHub, etc.
- `experience/` - job history entries
- `skills/` - technical skills by category
- `education/` - degrees
- `certifications/` - professional certs
- `presentations/` - conference talks
- `articles/` - published articles
- `oss/` - open source contributions
- `rodo.yml` - GDPR compliance text

### Include Expansion

`cv.yml` uses custom `!include` directives (not standard YAML):

```yaml
experience:
  - !include data/experience/lcloud.yml
```

The `expand_includes.py` script recursively resolves these before passing to Pandoc:

```bash
uv run --with pyyaml expand_includes.py cv.yml > build/cv.yml
```

This happens automatically in the Makefile target `build/cv.yml`.

### PDF Generation Pipeline

1. `expand_includes.py` resolves all `!include` directives → `build/cv.yml`
2. Pandoc runs in Docker with custom template `template/cv.tex`
3. XeLaTeX renders using `awesome-cv.cls` document class
4. Fonts loaded from `fonts/` directory
5. Output: `build/cv.pdf`

The Pandoc Docker image is built from `Dockerfile` (based on `pandoc/extra`) with additional LaTeX packages (fontawesome6, roboto, etc.).

### JSON Generation

YAML → JSON conversion uses `ingy/yaml-to-json` Docker image. Output is used for website rendering.

## Working with CV Data

### Adding a New Experience Entry

1. Create `data/experience/company-name.yml` with structure:

```yaml
start: MM.YYYY
end: MM.YYYY # or "now"
position: Job Title
company: Company Name
city: Location
tasks:
  - project: Project Name
    entries:
      - bullet point description
      - another bullet point
```

2. Add `!include data/experience/company-name.yml` to `cv.yml` under `experience:`

### Adding a New Skill Category

1. Create `data/skills/category-name.yml`:

```yaml
name: Category Name
items:
  - skill 1
  - skill 2
```

2. Add `!include data/skills/category-name.yml` to `cv.yml` under `skill:`

## Git Workflow

**Always use a PR for any change with 2+ commits.** Single-line hotfixes may go directly to master, but feature work MUST go through a branch + PR. Never push a feature branch directly to master.

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

- **CI**: Runs on push/PR to master. Prettier checks `cv.yml`, builds PDF and JSON, uploads artifacts.
- **Release**: Runs on version tags (`v*`). Creates GitHub release with PDF/JSON.

## Dependencies

- **Docker**: Required for Pandoc + LaTeX environment
- **uv**: Python tool used to run `expand_includes.py` (installed via `uv run --with pyyaml`)
- **pdfunite**: Used for combining CV + appendix (if appendix exists)

No local Python virtualenv or LaTeX installation needed — everything runs in containers.

## Debugging Build Issues

If PDF build fails:

1. Check `build/cv.yml` was generated correctly (includes expanded)
2. Verify Docker image built: `make build_docker`
3. Check Pandoc command in Makefile targets (line 43)
4. LaTeX errors will appear in Pandoc output (usually missing packages or template syntax)

The custom LaTeX template (`template/cv.tex`) uses the `awesome-cv.cls` document class with variables like `$basic.firstName$`, `$contact.email$`, etc. mapped from YAML structure.
