# Patterns & Conventions

*Last Updated: 2026-07-13*

## YAML composition pattern

`cv.yml` is the only file Pandoc or the build pipeline ever reads. It composes data via
non-standard `!include` directives:

```yaml
basic: !include data/basic.yml
experience:
  - !include data/experience/lcloud.yml
```

`expand_includes.py` resolves these recursively before any downstream tool sees the YAML.
**Never run a YAML parser on `cv.yml` directly.**

## Data entry schema

### Experience entry (`data/experience/<company>.yml`)
```yaml
start: MM.YYYY
end: MM.YYYY  # or "now"
position: Job Title
company: Company Name
city: Location
tasks:
  - project: Project Name
    entries:
      - bullet point
```

### Skill category (`data/skills/<name>.yml`)
```yaml
name: Category Name
items: [skill1, skill2]
```

## Build determinism

- Prettier enforced on `cv.yml` in CI (`--check` only, no autofix)
- Python deps locked via `uv.lock` — always use `uv run` to ensure reproducibility
- Docker image tag `pandoc:latest` is local; rebuilt with `make build_docker`

## JSON date handling

The YAML→JSON conversion uses a Python one-liner that serializes `datetime.date`/`datetime.datetime`
to ISO strings via `default=lambda o: o.isoformat()`. YAML date values (e.g. `2024-01-01`) become
JSON strings.

## Web data flow

`make web` does:
1. Copies `build/cv.json` → `web/src/data/cv.json`
2. Copies `media/*` → `web/public/media/`
3. Writes a `content-seed.txt` (SHA of all `data/` files) for cache-busting
4. Runs `npm run build` in `web/`

`web/src/data/cv.json` and `web/public/media/` are both gitignored — always generated.

## Astro component pattern

Components are pure Astro (`.astro`), typed with TypeScript interfaces in the frontmatter.
No framework (React/Vue/Svelte) is used — just Astro's island architecture with `<ClientRouter>`
for view transitions. Client-side JS lives in `<script>` blocks in `index.astro`.

## Error handling

`expand_includes.py` prints a warning to stderr for missing includes and returns the raw
`!include` directive unchanged — allowing the build to continue but making the output incorrect.
Treat any warning from this script as a build failure.

## CI/CD

- All jobs on `ubuntu-latest`
- `uv` installed via `astral-sh/setup-uv@v6`
- Docker via `docker/setup-buildx-action@v3`
- Artifacts uploaded with `actions/upload-artifact@v4` (named `cv_<sha>_build`)
