import requests
import os
import jinja2
from jinja2 import Template
import aiohttp
import asyncio
import ssl
import zipfile
# from dotenv import load_dotenv
# load_dotenv()
# Disable SSL certificate verification
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def write_file(file_path, content):
    lock_file_path = f"{file_path}.lock"
    with open(lock_file_path, 'w') as f:
        f.write("lock")
    with open(file_path, 'wb') as f:
        f.write(content)
    os.remove(lock_file_path)

def create_package_dir(result):
    package_id = result['PackageId']
    package_dir_path = f"./Get_All_Packages/{package_id}/"
    os.makedirs(package_dir_path, exist_ok=True)

def getOAuthToken(oauth_url, client_id, client_secret):
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    auth_response = requests.post(oauth_url, data=payload)
    auth_response.raise_for_status()
    oauth_token = auth_response.json()['access_token']
    return oauth_token



async def fetch_package_ids(base_url, headers):
    base_url = f"{base_url}/IntegrationPackages"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context), headers=headers) as session:
        async with session.get(base_url) as response:
            text = await response.text()
            if response.status != 200:
                return []
            data = await response.json()
            package_ids = [package['Id'] for package in data['d']['results']]
            return package_ids


async def download_package(package_id, package_url, artifacts_url, headers):
    template = jinja2.Template(package_url)
    url = template.render(item=package_id)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context), headers=headers) as session:
        async with session.get(url) as response:
            data = await response.json()
            if 'd' not in data or 'results' not in data['d']:
                print(f"Unexpected artifacts response for package {package_id}: {data}")
                return
            results = data['d']['results']
            for result in results:
                create_package_dir(result)
                id = result['Id']
                version = result['Version']
                template = jinja2.Template(artifacts_url)
                artifact_url = template.render(id=id, version=version)
                dest_path = f"./Get_All_Packages/{package_id}/"
                filename = f"{id}.zip"
                file_path = os.path.join(dest_path, filename)
                async with session.get(artifact_url) as response:
                    content = await response.content.read()
                    write_file(file_path, content)
                    iflow_dir_path = os.path.join(dest_path, id)
                    os.makedirs(iflow_dir_path, exist_ok=True)
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(iflow_dir_path)
            print("completed:", package_id)

# Load env vars
oauth_url = os.environ.get("OAUTH_URL")
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
base_url = os.environ.get("BASE_URL")
package_url = os.environ.get("PACKAGE_URL")
artifacts_url = os.environ.get("ARTIFACTS_URL")

if not all([oauth_url, client_id, client_secret, base_url, package_url, artifacts_url]):
    print("Error: One or more environment variables are not set.")
    exit(1)

oauth_token = getOAuthToken(oauth_url, client_id, client_secret)


async def main():
    tasks = []
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {oauth_token}'
    }
    package_ids = await fetch_package_ids(base_url, headers)
    if not package_ids:
        print("No packages found or error fetching package IDs.")
        return
    for package_id in package_ids:
        tasks.append(asyncio.create_task(download_package(package_id, package_url, artifacts_url, headers)))
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
