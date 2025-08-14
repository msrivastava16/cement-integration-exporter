import argparse
import os

def create_iflow_config(iflow_name, env):
    """
    Creates a configuration file for a given iFlow and environment,
    placing it inside a 'config' folder at the same level as the iFlow directory.
    """
    base_search_dir = "Get_All_Packages"
    iflow_dir_path = None
    package_dir_path = None

    # Find the directory of the downloaded iFlow
    for root, dirs, files in os.walk(base_search_dir):
        if iflow_name in dirs:
            potential_path = os.path.join(root, iflow_name)
            # A simple check to verify it's an extracted iFlow directory
            if os.path.isdir(os.path.join(potential_path, 'src')) or os.path.isdir(os.path.join(potential_path, 'META-INF')):
                 iflow_dir_path = potential_path
                 package_dir_path = root
                 break # Stop after finding the first match

    if not iflow_dir_path:
        print(f"Error: Could not find the directory for iFlow '{iflow_name}' in '{base_search_dir}'.")
        print("Please ensure the iFlow was downloaded correctly before running this script.")
        exit(1)

    # Create the config directory next to the iFlow directory, inside the package folder
    # e.g., Get_All_Packages/SimpleDemoPackage2/iflow2-config/
    config_dir = os.path.join(package_dir_path, f"{iflow_name}-config")
    os.makedirs(config_dir, exist_ok=True)

    # Create the properties file inside the new config directory
    # e.g., Get_All_Packages/SimpleDemoPackage2/iflow2-config/iflow2-dev.properties
    config_file_path = os.path.join(config_dir, f"{iflow_name}-{env}.properties")

    with open(config_file_path, "w") as f:
        f.write(f"# Configuration for iFlow '{iflow_name}' in '{env}' environment\n")
        f.write(f"iflow.name={iflow_name}\n")
        f.write(f"environment={env}\n")
        # Add more environment-specific configurations here

    print(f"Successfully created configuration file: {config_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create iFlow configuration file.")
    parser.add_argument("--iflow", required=True, help="Name of the iFlow")
    parser.add_argument("--env", required=True, help="Environment (e.g., dev, stage, prod)")
    args = parser.parse_args()

    create_iflow_config(args.iflow, args.env)
