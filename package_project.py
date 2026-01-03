import shutil
import os
import datetime

def make_zip(source_dir, output_filename):
    # Create a zip file
    shutil.make_archive(output_filename, 'zip', source_dir)
    print(f"✅ Successfully created: {output_filename}.zip")

if __name__ == "__main__":
    # Current directory
    source = os.getcwd()
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    output = f"doc_consistency_agent_v{timestamp}"
    
    print(f"Zipping content from: {source}...")
    # This will create the zip in the current directory
    make_zip(source, output)
