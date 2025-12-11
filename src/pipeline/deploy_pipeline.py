
import os
from craft_ai_sdk import CraftAiSdk

# Configuration
# You typically need to set these in your environment or .env file
# CRAFT_AI_ENVIRONMENT_URL="https://..."
# CRAFT_AI_ACCESS_TOKEN="..."

def deploy():
    # 1. Initialize SDK
    sdk = CraftAiSdk(
        environment_url=os.getenv("CRAFT_AI_ENVIRONMENT_URL"),
        sdk_token=os.getenv("CRAFT_AI_ACCESS_TOKEN")
    )

    # 2. Define the pipeline
    # We are deploying the 'run_consistency_check' function from 'src/pipeline/pipeline_logic.py'
    # Note: simple_deploy or create_pipeline usages vary by SDK version. 
    # This is a generic representations based on common patterns.
    
    pipeline_name = "doc-consistency-check"
    
    print(f"Deploying pipeline '{pipeline_name}'...")

    try:
        # Assuming sdk.create_pipeline or similar exists
        # We point to the local function. The SDK usually handles zipping/uploading dependencies 
        # based on a requirements.txt or similar, or we might need to specify a docker image.
        
        pipeline = sdk.create_pipeline(
            pipeline_name=pipeline_name,
            function_path="src/pipeline/pipeline_logic.py", # Path to file
            function_name="run_consistency_check",          # Function symbol
            container_config={
                "requirements_path": "requirements.txt"     # Ensure scikit-learn is here
            }
        )
        
        print(f"Pipeline deployed successfully: {pipeline}")
        return pipeline

    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    # Ensure env vars are loaded
    from dotenv import load_dotenv
    load_dotenv()
    
    deploy()
