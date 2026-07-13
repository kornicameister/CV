# iac/

CloudFormation stacks for one-time manual infrastructure setup. Not integrated with CI/CD.

## Stacks

### `oidc-bedrock.yml`

Creates a GitHub Actions OIDC identity provider and an IAM role that allows the CI `translate` job to call AWS Bedrock (Claude Haiku) for CV translation.

**Deploy (once):**

```bash
cp .env.example .env        # fill in real values
aws cloudformation deploy \
  --template-file iac/oidc-bedrock.yml \
  --stack-name cv-translator-oidc \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides $(cat iac/.env | tr '\n' ' ') \
  --profile <your-profile>
```

**Parameters** (set in `iac/.env`, never committed):

| Parameter | Description |
|---|---|
| `GitHubOrg` | GitHub user or org (e.g. `kornicameister`) |
| `GitHubRepo` | Repository name (e.g. `CV`) |
| `GitHubBranch` | Branch to trust (default: `master`) |
| `AwsAccountId` | Your AWS account ID |
| `BedrockRegion` | Region for Bedrock calls (default: `eu-central-1`) |
| `CreateOIDCProvider` | `true` first time; `false` if OIDC provider already exists |

`iac/.env` is gitignored — see `.env.example` for the template.
