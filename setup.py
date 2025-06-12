import os
import subprocess
import sys

missing_data = False
missing_scripts = False
missing_files = False

def install_requirements():
    """Installs dependencies from requirements.txt"""
    if not os.path.exists("requirements.txt"):
        print("⚠️  requirements.txt not found!")
        global missing_files
        missing_files = True
        return False
    
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        sys.exit(1)

def check_and_create_directories():
    """Checks and creates the required directory structure"""
    main_directories = [
        "data",
        "neo4j_data", 
        "scripts"
    ]
    
    data_subdirectories = [
        "data/original_openAIRE_data",
        "data/projects_data_csv", 
        "data/ror_data"
    ]
    
    script_subdirectories = [
        "scripts/kg_pipeline"
    ]
    
    print("📁 Checking directory structure...")
    
    for directory in main_directories + data_subdirectories + script_subdirectories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created: {directory}")
        else:
            print(f"📂 Already exists: {directory}")

def check_required_files():
    """Checks for the presence of required files"""
    global missing_files, missing_scripts

    print("\nChecking for required files...")
    
    required_files = ["requirements.txt", "setup.py"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"⚠️  Missing file: {file}")
            missing_files = True
        else:
            print(f"✅ File exists: {file}")
    
    expected_scripts = [
        "scripts/kg_pipeline/01_format_openaire_json.py",
        "scripts/kg_pipeline/02_extract_projects_to_csv.py", 
        "scripts/kg_pipeline/03_enrich_funders_with_ror.py",
        "scripts/kg_pipeline/04_fetch_project_publications.py",
        "scripts/kg_pipeline/05_import_to_neo4j.py"
    ]
    
    print("\nChecking pipeline scripts...")
    for script in expected_scripts:
        if not os.path.exists(script):
            print(f"⚠️  Missing script: {script}")
            missing_scripts = True
        else:
            print(f"✅ Script found: {script}")

def check_data_content():
    """Checks if data directories contain expected files"""
    global missing_data

    print("\nChecking data directory contents...")
    
    def check_dir(path, name, required_format, example_source):
        global missing_data
        if os.path.exists(path):
            files = os.listdir(path)
            if not files:
                print(f"⚠️  {name} directory is empty!")
                print(f"Please download from: {example_source}")
                print(f"Required format: {required_format}\n")
                missing_data = True
            else:
                print(f"✅ {name} contains {len(files)} file(s).")
    
    check_dir("data/ror_data", "ror_data", "CSV", "https://zenodo.org/records/15475023")
    check_dir("data/original_openAIRE_data", "original_openAIRE_data", "JSON", "https://zenodo.org/records/14851262")

    csv_path = "data/projects_data_csv"
    if os.path.exists(csv_path):
        csv_files = [f for f in os.listdir(csv_path) if f.endswith('.csv')]
        if csv_files:
            print(f"✅ projects_data_csv contains {len(csv_files)} CSV file(s).")
        else:
            print("📂 projects_data_csv is empty (will be filled by the pipeline).")

def main():
    """Main function to set up the project"""
    print("OpenAIRE Knowledge Graph Setup")
    print("=" * 40)
    
    install_requirements()
    check_and_create_directories()
    check_required_files()
    check_data_content()
    
    if missing_data or missing_scripts or missing_files:
        print("\n⚠️  Project setup completed with missing components.")
        if missing_files:
            print("   - Some essential files are missing.")
        if missing_scripts:
            print("   - Some pipeline scripts are missing.")
        if missing_data:
            print("   - Some data directories are empty. Please download the required data (see messages above).")
        print("\nAfter fixing the above, you can start the pipeline, e.g.:")
        print("    python scripts/kg_pipeline/01_format_openaire_json.py")
    else:
        print("\n✅ Project setup completed successfully!")

if __name__ == "__main__":
    main()
