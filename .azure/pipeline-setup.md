# GitHub Actions deployment setup

The workflow in `.github/workflows/deploy.yml` runs tests and deploys the Flask
application to the existing Azure App Service on each push to `main`. It uses
GitHub OIDC; no publish profile or Azure client secret is stored in the
repository.

## Configure Azure and GitHub

From the repository root, install and sign in to the Azure CLI and GitHub CLI.
The Azure account must be able to create a user-assigned managed identity and
role assignments, and the GitHub account must be able to administer repository
Actions environments and variables.

Run the setup helper:

```bash
chmod +x scripts/setup-azure-auth-for-pipeline.sh
./scripts/setup-azure-auth-for-pipeline.sh
```

The helper uses the currently selected Azure subscription and asks for
confirmation before making changes. It enables the App Service's system
identity, grants it Speech access, configures the app settings, creates a
separate user-assigned identity for GitHub Actions, scopes that identity to the
App Service, and creates the GitHub `production` environment and its OIDC
federation. It also sets the workflow's environment variables in GitHub.

The helper restricts the `production` environment to the `main` branch. Verify
that policy in the GitHub repository's **Settings → Environments**. Optional
required reviewers add a manual approval step and therefore delay automatic
deployment.

## What is deployed

The workflow deploys application code to the existing App Service; it does not
recreate Azure resources on every push. The Speech resource is provisioned
separately and accessed at runtime using the App Service identity and the
**Cognitive Services Speech User** role. Changes to Azure resource definitions
should be deployed through a separate reviewed IaC workflow.

The ZIP includes `jaguarFind.db` if it is tracked in the repository. Keep that
seed database sanitized; `startup.sh` copies it to `/home/jaguarFind.db` only
when the persistent database does not already exist. Review
[`docs/AZURE_DEPLOYMENT.md`](../docs/AZURE_DEPLOYMENT.md) before changing
database contents or deployment behavior.
