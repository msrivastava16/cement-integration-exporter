import requests
import os
import csv
import base64

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

oauth_url = os.environ.get("OAUTH_URL")
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
base_url = os.environ.get("BASE_URL")

if not all([oauth_url, client_id, client_secret, base_url]):
    print("Error: One or more environment variables are not set.")
    exit(1)

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
    if response.status_code == 201:
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

            if response.status_code == 201:
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