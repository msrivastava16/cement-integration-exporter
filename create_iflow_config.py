import argparse
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

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
        return None

def create_iflow_config(iflow_name, env):
    """
    Creates a configuration file for a given iFlow and environment,
    placing it inside a 'config' folder.
    The configuration is fetched from the /IntegrationDesigntimeArtifacts API.
    """
    oauth_url = os.getenv("OAUTH_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    base_url = os.getenv("BASE_URL")

    if not all([oauth_url, client_id, client_secret, base_url]):
        print("Error: Ensure OAUTH_URL, CLIENT_ID, CLIENT_SECRET, and BASE_URL are set in your .env file.")
        exit(1)

    token = get_oauth_token(oauth_url, client_id, client_secret)
    if not token:
        exit(1)

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    
    # Correctly format the filter query
    #api_url = f"{base_url}/IntegrationDesigntimeArtifacts?$filter=Id eq '{iflow_name}'"
    api_url = f"{base_url}/IntegrationDesigntimeArtifacts(Id='{iflow_name}',Version='active')/Configurations?$format=json"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'd' in data and 'results' in data['d'] and data['d']['results']:
            config_data = data['d']['results']
            iflow_version = 'active'
            #iflow_version = iflow_data.get('Version')            

            config_dir = "config"
            os.makedirs(config_dir, exist_ok=True)
            
            filename = f"{iflow_name}_{iflow_version}_{env}.json"
            file_path = os.path.join(config_dir, filename)

            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=4)

            print(f"Successfully created configuration file: {file_path}")
        else:
            print(f"Error: No iFlow found with the name '{iflow_name}'.")
            print("API Response:", response.text)


    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create iFlow configuration file from API response.")
    parser.add_argument("--iflow", required=True, help="ID of the iFlow")
    parser.add_argument("--env", required=True, help="Environment (e.g., dev, stage, prod)")
    args = parser.parse_args()

    create_iflow_config(args.iflow, args.env)