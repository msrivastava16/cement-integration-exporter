import requests
import os
import argparse
import base64
import shutil
import zipfile


def get_oauth_token(oauth_url, client_id, client_secret):
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
        exit(1)

def fetch_csrf_token(base_url, oauth_token):
    try:
        response = requests.get(
            f"{base_url}/IntegrationPackages",
            headers={
                'Authorization': f'Bearer {oauth_token}',
                'x-csrf-token': 'fetch'
            }
        )
        response.raise_for_status()
        return response.headers['x-csrf-token']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CSRF token: {e}")
        exit(1)

def post_integration_package(base_url, headers, package_id):
    url = f"{base_url}/IntegrationPackages"
    data = {
        "Id": package_id,
        "Name": package_id,
        "Description": package_id,
        "ShortText": package_id,
        "Version": "1.0.0",
        "SupportedPlatform": "SAP Cloud Integration",
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print(f"Integration package '{package_id}' created successfully.")
        elif response.status_code == 409: # Conflict, package exists
            print(f"Integration package '{package_id}' already exists.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error creating integration package '{package_id}': {e}")
        print(f"Response body: {e.response.text}")

def post_integration_artifact(base_url, headers, package_id, artifact_id, content):
    url = f"{base_url}/IntegrationDesigntimeArtifacts"
    data = {
        "Name": artifact_id,
        "Id": artifact_id,
        "PackageId": package_id,
        "ArtifactContent": content
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print(f"  - Artifact '{artifact_id}' created successfully.")
        elif response.status_code == 409: # Conflict, artifact exists
             print(f"  - Artifact '{artifact_id}' already exists. Skipping.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error creating artifact '{artifact_id}': {e}")
        print(f"Response body: {e.response.text}")

def create_iflow_zip_and_encode(iflow_path):
    temp_zip = shutil.make_archive("temp_iflow", 'zip', iflow_path)
    with open(temp_zip, "rb") as zip_file:
        encoded_zip = base64.b64encode(zip_file.read()).decode("utf-8")
    os.remove(temp_zip)
    return encoded_zip

def main():
    parser = argparse.ArgumentParser(description='Create Integration Packages and Artifacts.')
    parser.add_argument('--source-dir', default='Get_All_Packages', help='The directory containing the packages to restore.')
    args = parser.parse_args()

    oauth_url = os.environ.get("OAUTH_URL")
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    base_url = os.environ.get("BASE_URL")

    if not all([oauth_url, client_id, client_secret, base_url]):
        print("Error: One or more environment variables (OAUTH_URL, CLIENT_ID, CLIENT_SECRET, BASE_URL) are not set.")
        exit(1)

    oauth_token = get_oauth_token(oauth_url, client_id, client_secret)
    csrf_token = fetch_csrf_token(base_url, oauth_token)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {oauth_token}',
        'x-csrf-token': csrf_token
    }

    packages_path = args.source_dir
    if not os.path.isdir(packages_path):
        print(f"Error: Directory '{packages_path}' not found.")
        exit(1)

    package_ids = [name for name in os.listdir(packages_path) if os.path.isdir(os.path.join(packages_path, name))]

    for package_id in package_ids:
        print(f"Processing package: {package_id}")
        post_integration_package(base_url, headers, package_id)
        
        package_path = os.path.join(packages_path, package_id)
        iflow_ids = [name for name in os.listdir(package_path) if os.path.isdir(os.path.join(package_path, name))]

        for iflow_id in iflow_ids:
            iflow_path = os.path.join(package_path, iflow_id)
            print(f"  - Processing iFlow: {iflow_id}")
            
            iflow_content_path = iflow_path
            encoded_content = create_iflow_zip_and_encode(iflow_content_path)
            post_integration_artifact(base_url, headers, package_id, iflow_id, encoded_content)

if __name__ == '__main__':
    main()