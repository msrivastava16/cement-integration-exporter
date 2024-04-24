import requests
import os
import yaml
import argparse
import jinja2
from jinja2 import Template
import csv
import base64


def write_file(file_path, content):
    lock_file_path = f"{file_path}.lock"
    with open(lock_file_path, 'w') as f:
        f.write("lock")
    with open(file_path, 'wb') as f:
        f.write(content)
    os.remove(lock_file_path)

#get tenant config
def getConfig(args):
    with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)

    oauth_url = config["all"]["tenants"]["dev"]["oAuthUrl"]
    client_id = config["all"]["tenants"]["dev"]["client_id"]
    client_secret = config["all"]["tenants"]["dev"]["client_secret"]
    base_url = config["all"]["tenants"]["dev"]["baseURL"]
    package_url = config["all"]["tenants"]["dev"]["PackageURL"]
    artifacts_url = config["all"]["tenants"]["dev"]["ArtifactsURL"]

    if args.environment == 'dev':
        # Do something for the dev environment
        print("dev selected")
    elif args.environment == 'stage':
        # Do something for the stage environment
        oauth_url = config["all"]["tenants"]["stage"]["oAuthUrl"]
        client_id = config["all"]["tenants"]["stage"]["client_id"]
        client_secret = config["all"]["tenants"]["stage"]["client_secret"]
        base_url = config["all"]["tenants"]["stage"]["baseURL"]
        package_url = config["all"]["tenants"]["stage"]["PackageURL"]
        artifacts_url = config["all"]["tenants"]["stage"]["ArtifactsURL"]
        print("stage selected")
    else:
        print("no such tenant")
    return oauth_url, client_id, client_secret, base_url, package_url, artifacts_url

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

parser = argparse.ArgumentParser(description='choose you tenant')
parser.add_argument('environment', choices=[ 'dev', 'stage'], help='The tenant to use')
args = parser.parse_args()

oauth_url, client_id, client_secret, base_url, package_url, artifacts_url = getConfig(args)

oauth_token = getOAuthToken(oauth_url, client_id, client_secret)
csrf_token = fetchCSRFToken(base_url, oauth_token)

def post_integration_package(headers):
    url = f"{base_url}/IntegrationPackages"
    data = {
        "Id": "OfficeWorksSFTPInterfaces",
        "Name": "OfficeWorksSFTPInterfaces",
        "Description": "OfficeWorksSFTPInterfaces",
        "ShortText": "OfficeWorksSFTPInterfaces",
        "Version": "1.0.0",
        "SupportedPlatform": "SAP Cloud Integration",
    }
    print(url)
    response = requests.post(url, headers=headers, json=data)
    print(response.text)
    if response.status_code == 200:
        print("Integration package successfully created.")
    else:
        print("Error creating integration package. Status code:", response.status_code)

def post_integration_artifact(headers):
    csv_file = "MassiFlowCreate.csv"
    url = f"{base_url}/IntegrationDesigntimeArtifacts"
    print(url)
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = f"{row['Source']} to {row['Destination']} - {row['Process']} iFlow"
            id = f"{row['Source']}to{row['Destination']}{row['Process']}iFlow"
            data = {
                "Name": name,
                "Id": id,
                "PackageId": "OfficeWorksSFTPInterfaces",
                "ArtifactContent": ""
            }

            # Read the zip file and encode it in base64
            with open("Test-iFlow.zip", "rb") as zip_file:
                zip_content = zip_file.read()
                encoded_zip = base64.b64encode(zip_content).decode("utf-8")
                data["ArtifactContent"] = encoded_zip

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                print(f"Integration flow '{name}' successfully created.")
            else:
                print(f"Error creating integration flow '{name}'. Status code:", response.status_code)

def main():
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {oauth_token}',
        'x-csrf-token': csrf_token
    }

    # Call the function to make the POST request
    post_integration_package(headers)

    post_integration_artifact(headers)

if __name__ == '__main__':
    main()