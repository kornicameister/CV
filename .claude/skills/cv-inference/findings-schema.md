# Findings Database Schema

**File:** `.claude/skills/cv-inference/findings.jsonl`

**Format:** JSON Lines (one JSON object per line)

## Purpose

Local knowledge base of CV inference findings. Written by subagent, read by main agent for summary presentation. NOT tracked in git.

## Entry Types

### 1. Blacklist Term (Init Phase)

```jsonl
{
  "type": "blacklist_term",
  "category": "client|project|proprietary|marker",
  "term": "Acme Corp",
  "context": "commit abc123: 'Add Acme Corp dashboard'",
  "confidence": "high|medium|low",
  "ambiguous": false,
  "timestamp": "2024-07-23T10:30:00Z"
}
```

**Fields:**
- `category`: One of: client (company names), project (codenames), proprietary (internal systems), marker (sensitivity flags)
- `term`: The sensitive term detected
- `context`: Where it was found (commit hash + message)
- `confidence`: Detection confidence (high = obvious, low = needs review)
- `ambiguous`: True if term could be tech name (e.g., "Phoenix")

### 2. Achievement (Update Phase)

```jsonl
{
  "type": "achievement",
  "commits": ["abc123", "def456"],
  "category": "experience",
  "project": "Enterprise Client Platform",
  "bullet": "Migrated legacy ETL to AWS Glue, reducing processing time by 60%",
  "value": "high|medium",
  "anonymized": true,
  "anonymization_map": {"Acme Corp": "Enterprise Client"},
  "skipped_commits": [],
  "timestamp": "2024-07-23T10:35:00Z"
}
```

**Fields:**
- `commits`: List of commit hashes that contributed to this achievement
- `category`: Which CV section (experience, skills, achievements)
- `project`: Anonymized project name
- `bullet`: CV-ready bullet point text
- `value`: High (new features, perf improvements) or medium (refactors, fixes)
- `anonymized`: Whether anonymization was applied
- `anonymization_map`: Terms replaced (for audit trail)
- `skipped_commits`: Commits filtered by blacklist (for transparency)

### 3. Skipped Commit (Blacklist Filter)

```jsonl
{
  "type": "skipped_commit",
  "hash": "abc123",
  "reason": "blacklist_match",
  "matched_term": "internal-only",
  "message": "Update internal-only config",
  "timestamp": "2024-07-23T10:32:00Z"
}
```

**Fields:**
- `hash`: Commit hash
- `reason`: Why skipped (blacklist_match, low_value, merge_commit)
- `matched_term`: Which blacklist term matched
- `message`: Commit message (for audit)

## Usage

### Writing (Subagent)

```python
import json
from datetime import datetime

finding = {
    "type": "achievement",
    "commits": ["abc123"],
    "bullet": "Built GraphQL API...",
    "timestamp": datetime.utcnow().isoformat()
}

with open(".claude/skills/cv-inference/findings.jsonl", "a") as f:
    f.write(json.dumps(finding) + "\n")
```

### Reading (Main Agent)

```python
import json

findings = []
with open(".claude/skills/cv-inference/findings.jsonl") as f:
    for line in f:
        findings.append(json.loads(line))

# Filter by type
achievements = [f for f in findings if f["type"] == "achievement"]
blacklist_terms = [f for f in findings if f["type"] == "blacklist_term"]
```

## Maintenance

- File is gitignored (privacy)
- Grows append-only (audit trail)
- Can be truncated per run: `> findings.jsonl` before subagent starts
- Subagent clears old findings at start of each mode (init vs update)
