import os
import subprocess

def install_requirements(requirements_file='requirements.txt'):
    """Installs dependencies from requirements.txt."""
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found.")
        return

    print(f"Installing dependencies from {requirements_file}...")
    # Use pip to install the packages globally
    subprocess.check_call(['pip', 'install', '-r', requirements_file])

def main():
    # Path to the requirements.txt file
    requirements_file = 'requirements.txt'

    # Step 1: Install the dependencies
    install_requirements(requirements_file)

    print("Setup complete! All required packages are installed.")

if __name__ == '__main__':
    main()
