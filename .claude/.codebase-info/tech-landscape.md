# Tech Landscape

*Last Updated: 2026-07-13*

## Languages & runtimes

| Language | Version | Use |
|----------|---------|-----|
| Python | ≥3.11 | `expand_includes.py`, YAML→JSON conversion |
| TypeScript | via Node ≥18 | Astro components (`web/src/`) |
| LaTeX (XeLaTeX) | via Docker | PDF rendering |

## Frameworks & tools

| Tool | Version | Role |
|------|---------|------|
| Astro | ^7.0.3 | Static site framework for `web/` |
| Pandoc | Docker (`pandoc/extra`) | Markdown+YAML → PDF conversion |
| uv | latest | Python tool runner (`uv run --with pyyaml`) |
| pyyaml | ≥6 | YAML parsing in Python tooling |
| awesome-cv.cls | bundled | LaTeX document class for CV formatting |

## Infrastructure

| Platform | Use |
|----------|-----|
| Docker | Pandoc+XeLaTeX build environment; `ingy/yaml-to-json` for JSON conversion |
| GitHub Actions | CI (prettier check, PDF/JSON build), web deploy, release |
| GitHub Pages | Hosts the Astro SPA at `https://kornicameister.github.io/CV` |

## Source-of-truth files

| File | What it controls |
|------|-----------------|
| `cv.yml` | CV composition (section order, included entries) |
| `pyproject.toml` | Python project config + dependencies |
| `uv.lock` | Locked Python deps |
| `web/package.json` | Node/Astro deps for web frontend |
| `Dockerfile` | Pandoc container definition |
| `Makefile` | All build targets |
| `.prettierrc` | YAML formatting rules (checked in CI) |

## Fonts

Roboto (Light, Regular, Medium, Bold, Thin + Italic variants) + FontAwesome bundled in `fonts/`.
Loaded by XeLaTeX via the template.
