import requests
import os
import jinja2
import aiohttp
import asyncio
import ssl
import zipfile
import argparse

# Disable SSL certificate verification
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def getOAuthToken(oauth_url, client_id, client_secret):
    """Fetches OAuth token."""
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    try:
        auth_response = requests.post(oauth_url, data=payload)
        auth_response.raise_for_status()
        return auth_response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print(f"Error getting OAuth token: {e}")
        return None

async def find_and_download_iflow(iflow_name, version, package_url, artifacts_url, headers, base_output_dir):
    """Finds a specific iFlow across all packages and downloads it."""
    base_url = f"{os.environ.get('BASE_URL')}/IntegrationPackages"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context), headers=headers) as session:
        try:
            async with session.get(f"{base_url}?$format=json") as response:
                response.raise_for_status()
                data = await response.json()
                package_ids = [package['Id'] for package in data['d']['results']]
        except aiohttp.ClientError as e:
            print(f"Error fetching packages: {e}")
            return False

        for package_id in package_ids:
            template = jinja2.Template(package_url)
            url = template.render(item=package_id)
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if 'd' not in data or 'results' not in data['d']:
                        continue
                    
                    for result in data['d']['results']:
                        if result['Id'] == iflow_name:
                            # Use specified version or default to active version
                            iflow_version = version if version != 'active' else result['Version']
                            
                            dest_path = os.path.join(base_output_dir, result['PackageId'])
                            os.makedirs(dest_path, exist_ok=True)
                            
                            artifact_template = jinja2.Template(artifacts_url)
                            artifact_url = artifact_template.render(id=result['Id'], version=iflow_version)
                            
                            async with session.get(artifact_url) as artifact_response:
                                artifact_response.raise_for_status()
                                content = await artifact_response.read()
                                
                                file_path = os.path.join(dest_path, f"{result['Id']}.zip")
                                with open(file_path, 'wb') as f:
                                    f.write(content)
                                
                                iflow_dir_path = os.path.join(dest_path, result['Id'])
                                os.makedirs(iflow_dir_path, exist_ok=True)
                                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                                    zip_ref.extractall(iflow_dir_path)
                                
                                print(f"Successfully downloaded iFlow '{result['Id']}' (version: {iflow_version}) from package '{result['PackageId']}'")
                                return True
            except aiohttp.ClientError as e:
                print(f"Error processing package {package_id}: {e}")
                continue
                
    print(f"iFlow '{iflow_name}' not found in any package.")
    return False

async def main():
    """Main function to parse arguments and start the download."""
    parser = argparse.ArgumentParser(description="Download a single iFlow artifact.")
    parser.add_argument("--iflow", required=True, help="The ID of the iFlow to download.")
    parser.add_argument("--version", default="active", help="The version of the iFlow to download (default: active).")
    parser.add_argument("--output_dir", default="./Get_All_Packages", help="The base directory to save the iFlow.")
    args = parser.parse_args()

    oauth_url = os.environ.get("OAUTH_URL")
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    base_url_env = os.environ.get("BASE_URL")
    package_url = os.environ.get("PACKAGE_URL")
    artifacts_url = os.environ.get("ARTIFACTS_URL")

    if not all([oauth_url, client_id, client_secret, base_url_env, package_url, artifacts_url]):
        print("Error: One or more required environment variables are not set.")
        exit(1)

    oauth_token = getOAuthToken(oauth_url, client_id, client_secret)
    if not oauth_token:
        exit(1)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {oauth_token}',
        'X-CSRF-Token': 'fetch'
    }

    if not await find_and_download_iflow(args.iflow, args.version, package_url, artifacts_url, headers, args.output_dir):
        exit(1)

if __name__ == '__main__':
    asyncio.run(main())
