---
name: cv-inference-update
description: Analyze recent git commits for CV updates. Filters by blacklist, infers achievements, anonymizes client/project names, outputs YAML ready for data/experience/*.yml. Use after completing work to update CV from commit history.
---

# CV Inference: Update CV from Commits

Analyzes recent git commits, infers CV-worthy achievements, outputs anonymized YAML.

## When to Use

- After completing significant work on a project
- When git hook notifies about new commits
- Quarterly CV update routine
- Before job applications / promotions

## What It Does

1. Loads blacklist from `.claude/skills/cv-inference/config.json`
2. Gets commits since last run (by your git email)
3. Filters blacklisted commits (privacy > CV completeness)
4. Analyzes remaining commits for high/medium value achievements
5. Groups related commits into single achievements
6. Anonymizes client/project names consistently
7. Outputs YAML matching `data/experience/*.yml` structure
8. Updates `last_run` date in config

## Prerequisites

- Config exists: `.claude/skills/cv-inference/config.json`
- If NOT: run `/cv-inference-init` first

## Workflow

**Delegate to subagent** (preserves main context):

```javascript
Agent({
  description: "Analyze commits for CV updates",
  prompt: `You are updating CV from recent git commit history.

**Steps:**

1. Load config from \`.claude/skills/cv-inference/config.json\`:
   - blacklist: terms to filter
   - author_email: whose commits to analyze
   - last_run: start date for analysis
   - anonymization_map: client name → replacement

2. Get commits since last run:
   \`\`\`bash
   uv run ../cv-inference/cv-inference-git.py get-commits \\
     --author-email "you@email.com" \\
     --since "2024-07-01" \\
     --branch main \\
     --cwd /path/to/repo
   \`\`\`

3. Filter blacklisted commits:
   - Check if message OR file paths contain blacklisted terms
   - Case-insensitive, partial match
   - Log skipped commits to findings.jsonl

4. Analyze remaining for CV value:
   - **High-value:** new features, perf improvements, architecture
   - **Medium-value:** significant bug fixes, non-trivial refactors
   - **Low-value (skip):** typos, formatting, trivial config

5. Group related commits:
   - Multiple commits on same feature → one achievement
   - Example: 5 GraphQL commits → "Built GraphQL API"

6. Anonymize using anonymization_map:
   - Acme Corp → Enterprise client
   - Project Phoenix → Internal platform
   - Preserve: tech skills, frameworks, metrics

7. Output YAML matching \`data/experience/*.yml\`:
   \`\`\`yaml
   - project: Enterprise Client Platform
     entries:
       - Migrated ETL to AWS Glue, reducing time by 60%
       - Implemented data quality checks with Great Expectations
   \`\`\`

8. Update config: \`last_run = today\`

**Read the full subagent instructions from:**
\`../cv-inference/subagents/update-cv.md\`

**Important:**
- NEVER skip blacklist filtering (privacy > CV value)
- ALWAYS anonymize at source (not "fix it later")
- Group related commits for better CV bullets
- Only high/medium value → achievements`,
  model: "sonnet",
  run_in_background: false
})
```

## Success Criteria

- All blacklisted commits skipped (logged)
- Only high/medium value commits → achievements
- Client/project names anonymized consistently
- YAML matches `data/experience/*.yml` structure
- Config updated with `last_run` date
- Skipped commits logged for transparency

## Output Example

```yaml
# CV Updates from 12 commits since 2024-07-01

- project: Enterprise Client Data Platform
  entries:
    - Migrated legacy ETL to AWS Glue, reducing processing time by 60%
    - Implemented data quality checks using Great Expectations
    - Set up monitoring with CloudWatch metrics and alarms

---
Skipped 2 commits due to blacklist:
- abc123: "Update internal-only config" (matched: internal-only)
- def456: "Fix client-secret integration" (matched: client-secret-name)

Findings written to: .claude/skills/cv-inference/findings.jsonl
Config updated: last_run = 2024-07-23
```

## Common Issues

### "Config not found"
→ Run `/cv-inference-init` first

### "No new commits"
→ Check `last_run` date in config, verify repo path

### "Too many blacklist matches"
→ Review blacklist in config, remove false positives

### "Achievements too generic"
→ Check commit messages have enough context

## Files

- **Subagent:** `../cv-inference/subagents/update-cv.md`
- **Python script:** `../cv-inference/cv-inference-git.py`
- **Config:** `.claude/skills/cv-inference/config.json` (read)
- **Findings:** `.claude/skills/cv-inference/findings.jsonl` (written)
