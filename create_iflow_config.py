import argparse
import os

def create_iflow_config(iflow_name, env):
    """
    Creates a configuration file for a given iFlow and environment.
    """
    config_dir = os.path.join("config", "iflows")
    os.makedirs(config_dir, exist_ok=True)
    
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
