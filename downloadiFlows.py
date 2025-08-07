import requests
import os
import jinja2
from jinja2 import Template
import aiohttp
import asyncio
import ssl


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

# Get OAuth Token
def getOAuthToken(oauth_url, client_id, client_secret):
    auth_response = requests.post(oauth_url, auth=(client_id, client_secret))
    oauth_token = auth_response.json()['access_token']
    return oauth_token

# Fetch CSRF Token
def fetchCSRFToken(base_url, oauth_token):
    csrf_response = requests.get(base_url, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {oauth_token}',
        'x-csrf-token': 'fetch'
    })
    csrf_token = csrf_response.headers['x-csrf-token']
    return csrf_token

#get package ids 
async def fetch_package_ids(base_url, headers):
    base_url = f"{base_url}/IntegrationPackages"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context), headers=headers) as session:
        async with session.get(base_url) as response:
            data = await response.json()
            package_ids = [package['Id'] for package in data['d']['results']]
            return package_ids

# download the iflows
async def download_package(package_id, package_url, artifacts_url, headers):
    template = jinja2.Template(package_url)
    url = template.render(item=package_id)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context), headers=headers) as session:
        async with session.get(url) as response:
            results = (await response.json())['d']['results']
            for result in results:
                # create directory for packages
                create_package_dir(result)
                # Download All flows for package
                id = result['Id']
                version = result['Version']
                template = jinja2.Template(artifacts_url)
                url = template.render(id=id, version=version)
                dest_path = f"./Get_All_Packages/{package_id}/"
                filename = f"{id}.zip"
                file_path = os.path.join(dest_path, filename)
                async with session.get(url) as response:
                    content = await response.content.read()
                    write_file(file_path, content)
                    iflow_dir_path = os.path.join(dest_path, id)
                    os.makedirs(iflow_dir_path, exist_ok=True)
                    os.system(f"unzip -q -o {file_path} -d {iflow_dir_path}")
            print("completed:" + package_id)

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
csrf_token = fetchCSRFToken(base_url, oauth_token)

# Disable SSL certificate verification
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


async def main():
    tasks = []
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {oauth_token}',
        'x-csrf-token': csrf_token
    }
    package_ids = await fetch_package_ids(base_url,headers)

    for package_id in package_ids:
        tasks.append(asyncio.create_task(download_package(
            package_id, package_url, artifacts_url, headers)))

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())