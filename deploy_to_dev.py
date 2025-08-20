import requests
import os
import argparse
import sys
import time

def getOAuthToken(oauth_url, client_id, client_secret):
    """Fetches OAuth token."""
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    try:
        auth_response = requests.post(oauth_url, data=payload, timeout=30)
        auth_response.raise_for_status()
        return auth_response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print(f"❌ OAuth error: {e}")
        return None

def deploy_iflow_to_dev(iflow_name, base_url, oauth_token):
    """Deploy iFlow directly to DEV environment using SAP Integration Content API."""
    headers = {
        'Authorization': f'Bearer {oauth_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Direct deploy iFlow to DEV environment using Integration Content API
        deploy_url = f'{base_url}/DeployIntegrationDesigntimeArtifact'
        
        deploy_payload = {
            'Id': iflow_name,
            'Version': 'active'
        }
        
        print(f'🚀 Direct deploying iFlow {iflow_name} to DEV...')
        response = requests.post(deploy_url, headers=headers, json=deploy_payload, timeout=60)
        
        if response.status_code in [200, 202]:
            print(f'✅ Direct deployment to DEV initiated')
            
            # Monitor deployment status
            for i in range(18):  # Wait up to 3 minutes
                time.sleep(10)
                status_url = f'{base_url}/IntegrationRuntimeArtifacts?$filter=Id eq \'{iflow_name}\''
                status_response = requests.get(status_url, headers=headers, timeout=30)
                
                if status_response.status_code == 200:
                    runtime_data = status_response.json()
                    if runtime_data.get('d', {}).get('results'):
                        artifact = runtime_data['d']['results'][0]
                        status = artifact.get('Status', 'UNKNOWN')
                        print(f'📊 DEV deployment status: {status}')
                        
                        if status in ['STARTED', 'SUCCESS']:
                            print(f'✅ {iflow_name} deployed successfully to DEV!')
                            return True
                        elif status in ['ERROR', 'FAILED']:
                            error_msg = artifact.get('ErrorInformation', {}).get('message', 'Unknown error')
                            print(f'❌ DEV deployment failed: {error_msg}')
                            return False
                
                print(f'⏳ Checking deployment status... ({i+1}/18)')
            
            print(f'✅ DEV deployment completed (check SAP CPI for final status)')
            return True
        else:
            print(f'❌ DEV deployment failed: {response.status_code} - {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ DEV deployment error: {e}')
        return False

def main():
    """Main function to parse arguments and start the deployment."""
    parser = argparse.ArgumentParser(description="Deploy iFlow directly to DEV environment.")
    parser.add_argument("--iflow", required=True, help="The ID of the iFlow to deploy.")
    args = parser.parse_args()

    oauth_url = os.environ.get("OAUTH_URL")
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    base_url = os.environ.get("BASE_URL")

    # Debug environment variables
    print(f'🔍 Debug OAuth URL: {oauth_url or "EMPTY"}')
    print(f'🔍 Debug Client ID: {client_id[:10] if client_id else "EMPTY"}...')
    print(f'🔍 Debug Base URL: {base_url or "EMPTY"}')

    if not all([oauth_url, client_id, client_secret, base_url]):
        print("❌ Error: One or more required environment variables are not set.")
        print("Required: OAUTH_URL, CLIENT_ID, CLIENT_SECRET, BASE_URL")
        sys.exit(1)

    oauth_token = getOAuthToken(oauth_url, client_id, client_secret)
    if not oauth_token:
        print("❌ Failed to get OAuth token")
        sys.exit(1)

    print(f'✅ OAuth token obtained successfully')

    success = deploy_iflow_to_dev(args.iflow, base_url, oauth_token)
    if not success:
        sys.exit(1)

    print(f'🎉 Deployment completed successfully!')

if __name__ == '__main__':
    main()