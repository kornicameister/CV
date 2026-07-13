# Directory Structure

*Last Updated: 2026-07-13*

```
CV/
├── cv.yml                   # Top-level composition file (uses !include)
├── cv.yml.backup            # Backup of original monolithic cv.yml
├── metadata.yml             # Pandoc metadata (passed alongside cv.yml)
├── Makefile                 # All build targets
├── Dockerfile               # Pandoc+XeLaTeX container
├── expand_includes.py       # !include resolver (uv run expand_includes.py cv.yml)
├── pyproject.toml           # Python project config
├── uv.lock                  # Locked Python deps
├── awesome-cv.cls           # LaTeX document class (bundled, don't modify)
│
├── data/                    # CV content — one file per logical unit
│   ├── basic.yml            # Name, position, photo URL
│   ├── contact.yml          # Address, email
│   ├── social.yml           # LinkedIn, GitHub, etc.
│   ├── rodo.yml             # GDPR compliance text (always keep in output)
│   ├── experience/          # One .yml per employer
│   ├── skills/              # One .yml per skill category
│   ├── education/           # One .yml per degree
│   ├── certifications/      # One .yml per cert
│   ├── presentations/       # Conference talks
│   ├── articles/            # Published articles
│   └── oss/                 # Open source contributions
│
├── template/                # LaTeX templates
│   ├── cv.tex               # Main Pandoc template (maps YAML vars → LaTeX)
│   ├── cv_before.tex        # Included before appendix body
│   └── cv_after.tex         # Included after appendix body
│
├── fonts/                   # Roboto + FontAwesome TTFs (used by XeLaTeX)
│
├── media/                   # Photos
│   ├── profile.png          # Used in PDF
│   └── avatar-dev.png       # Used in web
│
├── build/                   # Generated artifacts (gitignored)
│   ├── cv.yml               # Expanded (include-resolved) YAML
│   ├── cv.pdf               # Final PDF
│   └── cv.json              # JSON for web consumption
│
├── web/                     # Astro SPA frontend (separate Node project)
│   ├── astro.config.mjs     # Astro config (base: '/CV', GitHub Pages)
│   ├── package.json         # Node deps (Astro ^7)
│   ├── src/
│   │   ├── pages/index.astro    # Single page, imports all components
│   │   ├── layouts/             # BaseLayout.astro
│   │   ├── components/          # Hero, Experience, Skills, Education, etc.
│   │   ├── styles/global.css    # Global styles
│   │   └── data/cv.json         # Generated (gitignored), copied from build/
│   └── public/              # Static assets (favicon, media/)
│
├── .github/workflows/       # CI/CD
│   ├── ci.yml               # Prettier + PDF/JSON build
│   ├── release.yml          # Creates GitHub Release on v* tags
│   └── deploy-web.yml       # Deploys web/ to GitHub Pages
│
└── specs/                   # Design notes / architecture decisions
    └── yaml-include-solution.md
```

## Key invariant

`cv.yml` uses non-standard `!include` directives and **must** be processed through
`expand_includes.py` before any YAML parser sees it. Never pass `cv.yml` directly to
`yaml.safe_load` or similar.
