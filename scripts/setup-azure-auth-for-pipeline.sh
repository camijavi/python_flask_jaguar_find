#!/usr/bin/env bash
set -euo pipefail

APP_RESOURCE_GROUP="${APP_RESOURCE_GROUP:-jaguar-find-rg}"
APP_SERVICE_NAME="${APP_SERVICE_NAME:-jaguar-find-app-service}"
SPEECH_RESOURCE_NAME="${SPEECH_RESOURCE_NAME:-jaguar-find-speech-services}"
CI_IDENTITY_RESOURCE_GROUP="${CI_IDENTITY_RESOURCE_GROUP:-jaguar-find-ci-rg}"
CI_IDENTITY_NAME="${CI_IDENTITY_NAME:-jaguar-find-gh-deploy-identity}"
CI_IDENTITY_LOCATION="${CI_IDENTITY_LOCATION:-westus}"
GITHUB_ENVIRONMENT="${GITHUB_ENVIRONMENT:-production}"

for command_name in az gh python3; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        printf 'Required command not found: %s\n' "$command_name" >&2
        exit 1
    fi
done

az account show >/dev/null
gh auth status >/dev/null

SUBSCRIPTION_NAME="$(az account show --query name -o tsv)"
SUBSCRIPTION_ID="$(az account show --query id -o tsv)"
TENANT_ID="$(az account show --query tenantId -o tsv)"
REPOSITORY="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"

printf 'Azure subscription: %s\nGitHub repository: %s\n' \
    "$SUBSCRIPTION_NAME" "$REPOSITORY"
read -r -p 'Continue with this Azure subscription and repository? [y/N] ' confirmation
if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    printf 'Setup cancelled.\n'
    exit 1
fi

APP_RESOURCE_ID="$(az webapp show \
    --resource-group "$APP_RESOURCE_GROUP" \
    --name "$APP_SERVICE_NAME" \
    --query id -o tsv)"
SPEECH_RESOURCE_ID="$(az cognitiveservices account show \
    --resource-group "$APP_RESOURCE_GROUP" \
    --name "$SPEECH_RESOURCE_NAME" \
    --query id -o tsv)"
SPEECH_ENDPOINT="$(az cognitiveservices account show \
    --resource-group "$APP_RESOURCE_GROUP" \
    --name "$SPEECH_RESOURCE_NAME" \
    --query properties.endpoint -o tsv)"
SPEECH_REGION="$(az cognitiveservices account show \
    --resource-group "$APP_RESOURCE_GROUP" \
    --name "$SPEECH_RESOURCE_NAME" \
    --query location -o tsv)"

APP_PRINCIPAL_ID="$(az webapp identity assign \
    --resource-group "$APP_RESOURCE_GROUP" \
    --name "$APP_SERVICE_NAME" \
    --query principalId -o tsv)"
APP_SPEECH_ROLE_COUNT="$(az role assignment list \
    --scope "$SPEECH_RESOURCE_ID" \
    --query "[?principalId=='${APP_PRINCIPAL_ID}' && roleDefinitionName=='Cognitive Services Speech User'] | length(@)" \
    -o tsv)"
if [[ "$APP_SPEECH_ROLE_COUNT" == "0" ]]; then
    az role assignment create \
        --assignee-object-id "$APP_PRINCIPAL_ID" \
        --assignee-principal-type ServicePrincipal \
        --role 'Cognitive Services Speech User' \
        --scope "$SPEECH_RESOURCE_ID" \
        --output none
fi

APP_SETTING_NAMES="$(az webapp config appsettings list \
    --resource-group "$APP_RESOURCE_GROUP" \
    --name "$APP_SERVICE_NAME" \
    --query '[].name' -o tsv)"
APP_SETTINGS=(
    "DATABASE_PATH=/home/jaguarFind.db"
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true"
    "AZURE_SPEECH_ENDPOINT=${SPEECH_ENDPOINT}"
    "AZURE_SPEECH_REGION=${SPEECH_REGION}"
    "AZURE_SPEECH_RESOURCE_ID=${SPEECH_RESOURCE_ID}"
)
if ! grep -Fxq 'SECRET_KEY' <<<"$APP_SETTING_NAMES"; then
    APP_SETTINGS+=("SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')")
fi
az webapp config appsettings set \
    --resource-group "$APP_RESOURCE_GROUP" \
    --name "$APP_SERVICE_NAME" \
    --settings "${APP_SETTINGS[@]}" \
    --output none
az webapp config set \
    --resource-group "$APP_RESOURCE_GROUP" \
    --name "$APP_SERVICE_NAME" \
    --startup-file './startup.sh' \
    --output none

if [[ "$(az group exists --name "$CI_IDENTITY_RESOURCE_GROUP" -o tsv)" != "true" ]]; then
    az group create \
        --name "$CI_IDENTITY_RESOURCE_GROUP" \
        --location "$CI_IDENTITY_LOCATION" \
        --output none
fi
if ! az identity show \
    --resource-group "$CI_IDENTITY_RESOURCE_GROUP" \
    --name "$CI_IDENTITY_NAME" \
    --output none 2>/dev/null; then
    az identity create \
        --resource-group "$CI_IDENTITY_RESOURCE_GROUP" \
        --name "$CI_IDENTITY_NAME" \
        --location "$CI_IDENTITY_LOCATION" \
        --output none
fi

CI_CLIENT_ID="$(az identity show \
    --resource-group "$CI_IDENTITY_RESOURCE_GROUP" \
    --name "$CI_IDENTITY_NAME" \
    --query clientId -o tsv)"
CI_PRINCIPAL_ID="$(az identity show \
    --resource-group "$CI_IDENTITY_RESOURCE_GROUP" \
    --name "$CI_IDENTITY_NAME" \
    --query principalId -o tsv)"
CI_APP_ROLE_COUNT="$(az role assignment list \
    --scope "$APP_RESOURCE_ID" \
    --query "[?principalId=='${CI_PRINCIPAL_ID}' && roleDefinitionName=='Website Contributor'] | length(@)" \
    -o tsv)"
if [[ "$CI_APP_ROLE_COUNT" == "0" ]]; then
    az role assignment create \
        --assignee-object-id "$CI_PRINCIPAL_ID" \
        --assignee-principal-type ServicePrincipal \
        --role 'Website Contributor' \
        --scope "$APP_RESOURCE_ID" \
        --output none
fi

FEDERATED_CREDENTIAL_COUNT="$(az identity federated-credential list \
    --resource-group "$CI_IDENTITY_RESOURCE_GROUP" \
    --identity-name "$CI_IDENTITY_NAME" \
    --query "[?name=='github-${GITHUB_ENVIRONMENT}'] | length(@)" \
    -o tsv)"
if [[ "$FEDERATED_CREDENTIAL_COUNT" == "0" ]]; then
    az identity federated-credential create \
        --resource-group "$CI_IDENTITY_RESOURCE_GROUP" \
        --identity-name "$CI_IDENTITY_NAME" \
        --name "github-${GITHUB_ENVIRONMENT}" \
        --issuer 'https://token.actions.githubusercontent.com' \
        --subject "repo:${REPOSITORY}:environment:${GITHUB_ENVIRONMENT}" \
        --audiences 'api://AzureADTokenExchange' \
        --output none
fi

if ! gh api "repos/${REPOSITORY}/environments/${GITHUB_ENVIRONMENT}" >/dev/null 2>&1; then
    printf '{"deployment_branch_policy":{"protected_branches":false,"custom_branch_policies":true}}' |
        gh api --method PUT \
            "repos/${REPOSITORY}/environments/${GITHUB_ENVIRONMENT}" \
            --input - >/dev/null
fi

ENVIRONMENT_POLICY="$(gh api \
    "repos/${REPOSITORY}/environments/${GITHUB_ENVIRONMENT}" \
    --jq '.deployment_branch_policy.custom_branch_policies')"
if [[ "$ENVIRONMENT_POLICY" != "true" ]]; then
    printf 'The existing GitHub environment must allow custom branch policies; restrict it to main, then rerun this script.\n' >&2
    exit 1
fi

if ! gh api --paginate \
    "repos/${REPOSITORY}/environments/${GITHUB_ENVIRONMENT}/deployment-branch-policies" \
    --jq '.[].name' | grep -Fxq main; then
    gh api --method POST \
        "repos/${REPOSITORY}/environments/${GITHUB_ENVIRONMENT}/deployment-branch-policies" \
        --field name=main >/dev/null
fi

gh variable set AZURE_CLIENT_ID \
    --body "$CI_CLIENT_ID" --repo "$REPOSITORY" --env "$GITHUB_ENVIRONMENT"
gh variable set AZURE_TENANT_ID \
    --body "$TENANT_ID" --repo "$REPOSITORY" --env "$GITHUB_ENVIRONMENT"
gh variable set AZURE_SUBSCRIPTION_ID \
    --body "$SUBSCRIPTION_ID" --repo "$REPOSITORY" --env "$GITHUB_ENVIRONMENT"
gh variable set AZURE_RESOURCE_GROUP \
    --body "$APP_RESOURCE_GROUP" --repo "$REPOSITORY" --env "$GITHUB_ENVIRONMENT"
gh variable set AZURE_WEBAPP_NAME \
    --body "$APP_SERVICE_NAME" --repo "$REPOSITORY" --env "$GITHUB_ENVIRONMENT"

printf 'Azure Speech runtime access, GitHub OIDC, and production environment variables are configured.\n'
