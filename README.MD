# iFlow Mass Downloader

This Python script is designed to asynchronously fetch and download iFlow packages from a specified base URL.

## Overview

The script performs the following tasks:

1.  Authenticates using OAuth 2.0 client credentials.
2.  Fetches a CSRF token.
3.  Fetches all iFlow package IDs.
4.  Asynchronously downloads all iFlows for each package.

## Dependencies

Install the required Python libraries using pip:

```bash
pip install -r requirements.txt
```

## GitHub Actions Workflow

This project uses a GitHub Actions workflow to download and export iFlows.

### Triggering the Workflow

1.  Go to the "Actions" tab of your GitHub repository.
2.  In the left sidebar, click on the "iFlow Mass Downloader" workflow.
3.  Click the "Run workflow" dropdown button.
4.  Select the environment (`dev` or `stage`) you want to run the workflow against.
5.  Click the "Run workflow" button.

### Exporting to a Different Repository

The workflow is configured to export the downloaded iFlows to a *separate* GitHub repository. A new branch will be created in the target repository with a name based on the date and time of the workflow run (e.g., `iflow-updates-YYYY-MM-DD-HH-MM-SS`).

**Important Configuration for Export:**

In addition to the secrets listed below, you must also:

1.  **Update the Target Repository Path:** In the `.github/workflows/iflow_downloader.yml` file, locate the `Checkout target repository` step and change `your-org/your-target-repo` to the actual organization/username and repository name where you want the iFlows to be committed.

2.  **Add `TARGET_REPO_PAT` Secret:** Create a GitHub Personal Access Token (PAT) with `repo` scope (full control of private repositories) and add it as a GitHub secret named `TARGET_REPO_PAT` in your repository settings. This PAT will be used by the workflow to push to the target repository.

### Configuration

This workflow uses secrets to store sensitive information like API keys and URLs. You must configure the following secrets in your GitHub repository settings before running the workflow:

*   `OAUTH_URL`: The OAuth token URL.
*   `CLIENT_ID`: The client ID for OAuth authentication.
*   `CLIENT_SECRET`: The client secret for OAuth authentication.
*   `BASE_URL`: The base URL of the iFlow service.
*   `PACKAGE_URL`: The URL for fetching iFlow packages.
*   `ARTIFACTS_URL`: The URL for fetching iFlow artifacts.
*   `TARGET_REPO_PAT`: (New) Personal Access Token with `repo` scope for pushing to the target repository.

To add these secrets:

1.  Go to your GitHub repository's "Settings" tab.
2.  In the "Security" section of the left sidebar, click on "Secrets and variables" > "Actions".
3.  Click the "New repository secret" button for each secret listed above and add the corresponding value.