# Async Package Downloader

This Python script is designed to asynchronously fetch and download packages from a specified base URL using asyncio and aiohttp libraries.

## Overview

The script performs the following tasks:

1. Reads configuration from `config.yml` file for OAuth URL, client ID, client secret, base URL, package URL, and artifacts URL.

2. Gets an OAuth token using client credentials (client ID and client secret).

3. Fetches a CSRF token from the base URL using the OAuth token.

4. Fetches package IDs from the base URL using the CSRF token.

5. Downloads all iflows for each package asynchronously.

## Instructions

### 1. Environment Setup

Before running the script, ensure you have Python 3.x installed on your system.

### 2. Install Dependencies

Install the required Python libraries using pip:
```bash
pip install requests aiohttp jinja2 pyyaml
```

### 3. Configuration
Create a config.yml file with the following structure:

```yaml
all:
  tenants:
    dev:
      oAuthUrl: "dev_oauth_url"
      client_id: "dev_client_id"
      client_secret: "dev_client_secret"
      baseURL: "dev_base_url"
      PackageURL: "dev_package_url"
      ArtifactsURL: "dev_artifacts_url"
    stage:
      oAuthUrl: "stage_oauth_url"
      client_id: "stage_client_id"
      client_secret: "stage_client_secret"
      baseURL: "stage_base_url"
      PackageURL: "stage_package_url"
      ArtifactsURL: "stage_artifacts_url"
```
Replace the placeholder values with your actual OAuth URLs, client IDs, client secrets, base URLs, package URLs, and artifacts URLs for both the dev and stage environments.

### 4. Execute the Script
Run the script with the desired environment as an argument (dev or stage):

```bash
python async_package_downloader.py dev
```
or
```bash
python async_package_downloader.py stage
```
The script will fetch and download packages from the specified environment accordingly.

> Note: Make sure you have proper permissions and network connectivity to access the specified URLs and download packages.


### 5. Setup and execute inside a docker containr

1. Build the Docker Image:

Open a terminal/command prompt, navigate to the directory containing your Dockerfile and Python script, and run the following 

command to build the Docker image:
```bash
docker build -t async-package-downloader .
```

Replace async-package-downloader with your desired image name.

2. Run the Docker Container:

Once the image is built, you can run the Docker container using the following command:

```bash
docker run async-package-downloader
```

By default, the script will run with the dev environment. If you want to run it with the stage environment, modify the command like this:

```bash
docker run async-package-downloader stage
```
