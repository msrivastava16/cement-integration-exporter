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

A new branch and pull request will be created with the downloaded iFlows.

### Configuration

This workflow uses secrets to store sensitive information like API keys and URLs. You must configure the following secrets in your GitHub repository settings before running the workflow:

*   `OAUTH_URL`: The OAuth token URL.
*   `CLIENT_ID`: The client ID for OAuth authentication.
*   `CLIENT_SECRET`: The client secret for OAuth authentication.
*   `BASE_URL`: The base URL of the iFlow service.
*   `PACKAGE_URL`: The URL for fetching iFlow packages.
*   `ARTIFACTS_URL`: The URL for fetching iFlow artifacts.

To add these secrets:

1.  Go to your GitHub repository's "Settings" tab.
2.  In the "Security" section of the left sidebar, click on "Secrets and variables" > "Actions".
3.  Click the "New repository secret" button for each secret listed above and add the corresponding value.
