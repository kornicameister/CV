---
name: cv-inference
description: Use when user asks to analyze git commits for CV updates, initialize CV inference blacklist, or update CV with recent work achievements. Triggers on "cv inference", "update cv from commits", "analyze commits for cv", "cv-inference init", "cv-inference update"
---

# CV Inference from Git Commits

## Overview

Analyzes git commit history to infer CV-worthy achievements, then outputs YAML ready to paste into `data/experience/*.yml`. Automatically anonymizes client/project names and respects per-project blacklist.

**IMPORTANT: When user invokes `/cv-inference`, ask them which mode:**
- **"init"** — First-time setup: infers blacklist from git history, presents for approval
- **"update"** — Regular usage: analyzes new commits using existing blacklist

If user doesn't specify, check if `.claude/skills/cv-inference/config.json` exists:
- **Exists** → run update mode
- **Does NOT exist** → run init mode

**Two modes:**
1. **Init** — First setup: infers blacklist from git history, presents to user for approval
2. **Update** — Regular usage: analyzes new commits using existing blacklist

## When to Use

- User asks to "update CV from recent work"
- User wants to "analyze commits for CV achievements"
- First-time setup in a new project repo
- After completing significant work, before updating CV manually

**Do NOT use for:**
- Analyzing CV content itself (that's in `data/*.yml`)
- Refactoring existing CV YAML
- Generating cover letters or LinkedIn posts

## Quick Reference

| Command | What it does |
|---------|-------------|
| `uv run cv-inference-git.py get-user-email` | Get configured git user.email |
| `uv run cv-inference-git.py get-commits --author-email "email@domain.com" --since 2024-01-01` | Get commits by author email since date |
| `uv run cv-inference-git.py get-commit-details <hash>` | Get full commit details with diff |
| `uv run cv-inference-git.py sample-commits --rate 10` | Sample every 10th commit (for init) |
| `/cv-inference:init` | Initialize blacklist for first time |
| `/cv-inference:update` | Analyze new commits for CV updates |

## Implementation

### Mode 1: Initialize Blacklist (`/cv-inference:init`)

**Goal:** Build blacklist of sensitive terms that should NOT appear in CV.

**IMPORTANT: Delegate to subagent to preserve main context.**

**Steps:**

1. **Spawn subagent for analysis**
   ```
   Agent({
     description: "Initialize CV inference blacklist from git history",
     prompt: "Sample git history from /path/to/repo, infer sensitive terms (client names, project codenames, proprietary systems), write findings to .claude/skills/cv-inference/findings.jsonl. Return categorized summary for user approval.",
     model: "sonnet",  // Needs LLM inference for sensitive term detection
     run_in_background: false
   })
   ```
   
   **Why Sonnet:** Blacklist inference requires semantic understanding of commit messages to distinguish client names from tech terms (e.g., "Phoenix" = Elixir framework vs project codename).

2. **Subagent workflow:**
   - Sample git history efficiently:
     ```bash
     uv run cv-inference-git.py sample-commits --rate 10 --branch main --cwd /path/to/repo
     ```
   - Infer sensitive terms via LLM:
     - Client names (companies, organizations)
     - Project codenames (internal names, acronyms)
     - Proprietary systems (internal tools, custom platforms)
     - Sensitivity markers ("confidential", "internal-only", "NDA")
   - Write detailed findings to `.claude/skills/cv-inference/findings.jsonl`:
     ```jsonl
     {"type":"client","term":"Acme Corp","context":"commit abc123","confidence":"high"}
     {"type":"project","term":"Project Phoenix","context":"commit def456","confidence":"medium"}
     ```
   - Return summary to main agent

3. **Main agent: Get git user email and confirm with user**
   ```bash
   uv run cv-inference-git.py get-user-email --cwd /path/to/repo
   ```
   Present to user:
   ```
   Detected git user.email: tomasz.trebski@gmail.com
   
   Is this the correct email for filtering YOUR commits? (yes/no)
   If no, provide the correct email address.
   ```

4. **Main agent: Present categorized blacklist to user**
   ```
   Detected client names:
   - Acme Corp
   - ClientXYZ Inc.

   Detected project codenames:
   - Project Phoenix
   - internal-tool-alpha

   Detected sensitivity markers:
   - do-not-publish
   - confidential
   ```

5. **Ask user to review and approve**
   - User can ADD terms manually
   - User can REMOVE false positives (e.g., "Phoenix" if it's the Elixir framework)
   - User confirms before saving

6. **Ask about git hook installation (default: YES)**
   ```
   Install git hook for automatic notifications? (Y/n)
   
   This will add post-merge hook to monitored repos, so you get notified
   when new commits appear on main/master.
   ```
   
   **If user accepts (default):**
   - Ask for repo path(s) to monitor
   - **For each repo, check if `.git/hooks/post-merge` exists:**
   
   **If hook DOES NOT exist:**
   - Copy `post-merge.hook` to `.git/hooks/post-merge`
   - Make executable: `chmod +x`
   
   **If hook EXISTS:**
   - Show current hook content to user (first 20 lines)
   - Ask: "Hook already exists. How to proceed?"
     - **Merge (recommended):** Add cv-inference logic to existing hook
     - **Overwrite:** Backup old hook to `post-merge.backup`, install new
     - **Skip:** Don't install hook for this repo
   
   **If user chooses Merge:**
   - Append cv-inference logic to existing hook
   - Preserve existing hook behavior
   - Add separator comment: `# === CV Inference (added by skill) ===`

7. **Save to config**
   - Write to `.claude/skills/cv-inference/config.json`
   - Format:
     ```json
     {
       "blacklist": ["term1", "term2"],
       "author_email": "tomasz.trebski@gmail.com",
       "since_date": "2024-01-01",
       "monitored_repos": ["/path/to/work/repo"]
     }
     ```

**Red Flags:**
- Saving blacklist without user confirmation
- Not categorizing terms (flat list is harder to review)
- Over-flagging common tech terms (React, AWS, Docker)
- Not handling ambiguous terms (ask user about "Phoenix")
- Installing hook without asking (should default YES but still ask)
- **CRITICAL:** Overwriting existing hook without checking first
- **CRITICAL:** Not showing existing hook content before overwrite
- **CRITICAL:** Installing hook without user permission when one exists

---

### Mode 2: Update CV (`/cv-inference:update`)

**Goal:** Analyze commits since last run, infer CV-worthy achievements, output anonymized YAML.

**IMPORTANT: Delegate to subagent to preserve main context.**

**Steps:**

1. **Load config from `.claude/skills/cv-inference/config.json`**
   - Get blacklist, author name, last run date

2. **Spawn subagent for analysis**
   ```
   Agent({
     description: "Analyze git commits for CV updates",
     prompt: "Load config from .claude/skills/cv-inference/config.json. Get commits since last run using cv-inference-git.py, filter blacklist, infer CV-worthy achievements (high/medium value only), anonymize using anonymization_map from config. Write detailed findings to .claude/skills/cv-inference/findings.jsonl. Return YAML matching data/experience/*.yml structure for user review.",
     model: "sonnet",  // Needs semantic analysis for achievement inference + anonymization
     run_in_background: false
   })
   ```
   
   **Why Sonnet:** Achievement inference requires understanding commit context, grouping related commits, and maintaining consistent anonymization.

3. **Subagent workflow:**
   - Get commits since last run:
     ```bash
     uv run cv-inference-git.py get-commits \
       --author "Tomasz Trębski" \
       --since "2024-07-01" \
       --branch main \
       --cwd /path/to/repo
     ```
   - Filter blacklisted commits
   - Skip commits where message OR file paths contain blacklisted terms
   - Log skipped commits for transparency:
     ```
     Skipped 3 commits due to blacklist:
     - abc123: "Update internal-only config"
     - def456: "Fix client-secret-name integration"
     ```

4. **Analyze remaining commits for CV value**
   - High-value: new features, performance improvements, architecture decisions
   - Medium-value: bug fixes, refactors, minor features
   - Low-value: typo fixes, formatting, config tweaks (skip these)

5. **Group related commits**
   - Multiple small commits → one achievement
   - Example: 5 commits implementing GraphQL API → "Built GraphQL API for user data access"

6. **Anonymize references**
   - Client names → "Client A", "Enterprise client"
   - Project codenames → "Internal tooling platform", "Data pipeline"
   - Proprietary tech → Industry-standard equivalents when possible
   - Preserve technical details (languages, frameworks, patterns)

7. **Output YAML matching `data/experience/*.yml` structure**
   ```yaml
   - project: Data Pipeline Modernization
     entries:
       - Migrated legacy ETL to AWS Glue, reducing processing time by 60%
       - Implemented data quality checks using Great Expectations
       - Set up monitoring with CloudWatch metrics and alarms
   ```

8. **Update config with last run date**
   ```json
   {
     "last_run": "2024-07-23"
   }
   ```

**Red Flags:**
- Using real client names ("I'll just use Acme Corp, it's faster")
- Ignoring blacklist ("This commit is too valuable to skip")
- Over-inferring trivial changes as achievements
- Inconsistent anonymization (Client A → Acme Corp in different places)
- Wrong YAML structure (doesn't match data/experience/*.yml)

---

## Anonymization Rules

### What to anonymize:
- ✅ Client company names
- ✅ Project codenames (non-public)
- ✅ Proprietary systems (internal tools)
- ✅ Customer-specific details

### What to preserve:
- ✅ Technical skills (Python, AWS, GraphQL)
- ✅ Frameworks/libraries (React, Django, CDK)
- ✅ Design patterns (microservices, event-driven)
- ✅ Metrics (improved by 50%, reduced from X to Y)

### Replacement patterns:
| Original | Replacement |
|----------|-------------|
| "Acme Corp dashboard" | "Enterprise client dashboard" |
| "Project Phoenix API" | "Internal API platform" |
| "AcmeDB integration" | "Custom database integration" |
| "ClientXYZ pipeline" | "Data processing pipeline" |

---

## Common Mistakes

### Mistake 1: Analyzing every commit
**Problem:** Large repos have 1000+ commits, processing all is slow.
**Fix:** Use sampling for init (every 10th commit), use `--since` for updates.

### Mistake 2: Skipping user confirmation in init
**Problem:** Blacklist may have false positives (Phoenix = framework not codename).
**Fix:** Always present categorized list and ask user to review.

### Mistake 3: Inconsistent anonymization
**Problem:** "Client A" in one bullet, "Acme Corp" in another.
**Fix:** Build anonymization map upfront, apply consistently across all bullets.

### Mistake 4: Over-inferring
**Problem:** Typo fix → "Improved code quality through rigorous review".
**Fix:** Filter low-value commits (formatting, typos, trivial config changes).

### Mistake 5: Wrong YAML structure
**Problem:** Output doesn't match `data/experience/*.yml` schema.
**Fix:** Read existing experience YAML first, match structure exactly:
```yaml
- project: Project Name
  entries:
    - Bullet point 1
    - Bullet point 2
```

---

## Git Hook Setup (Optional)

To get notified when main/master has new commits:

1. **Create post-merge hook** in monitored repo:
   ```bash
   # .git/hooks/post-merge
   #!/bin/bash
   BRANCH=$(git rev-parse --abbrev-ref HEAD)
   if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
     echo "✨ New commits on $BRANCH - consider running /cv-inference:update in your CV repo"
   fi
   ```

2. **Make executable:**
   ```bash
   chmod +x .git/hooks/post-merge
   ```

3. **Test:**
   ```bash
   git pull origin main
   # Should see notification
   ```

---

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I'll skip blacklist, user can edit later" | Sensitive data in CV is expensive to fix. Initialize first. |
| "This commit is too valuable to skip" | Privacy > CV completeness. Blacklist is non-negotiable. |
| "I'll use real names then anonymize in final CV" | Anonymize at source. Easier to verify, prevents leaks. |
| "Sampling loses information" | Blacklist inference needs patterns, not exhaustive list. Sample is sufficient. |
| "User will know what I mean" | Ambiguous terms (Phoenix) need clarification. Ask, don't guess. |
| "I'll just analyze commit messages" | Diffs contain context (file paths, code changes). Use both. |
| "Hook doesn't exist yet, safe to install" | ALWAYS check. Overwriting existing hook destroys user's workflow. |
| "I'll merge hooks automatically" | Show existing content, get permission. Blind merge breaks things. |

---

## Real-World Impact

**Before cv-inference:**
- Manual CV updates: 2-3 hours per quarter
- Risk of including sensitive client names
- Achievements forgotten or understated

**After cv-inference:**
- CV updates: 15 minutes per quarter
- Zero sensitive data leaks (blacklist enforcement)
- More comprehensive achievement tracking
