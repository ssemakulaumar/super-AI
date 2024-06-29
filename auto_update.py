import os
import sys
import subprocess
import logging
import time

logging.basicConfig(level=logging.INFO)

def run_command(command, check=True):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        logging.error(f"Command failed: {command}")
        logging.error(result.stderr)
        raise RuntimeError(result.stderr)
    return result.stdout.strip()

def check_prerequisites():
    try:
        git_version = run_command("git --version", check=False)
        if "git version" not in git_version:
            raise RuntimeError("Git is not installed or not found in PATH.")
        logging.info(f"Git found: {git_version}")
        
        python_version = run_command("python --version", check=False)
        if "Python" not in python_version:
            raise RuntimeError("Python is not installed or not found in PATH.")
        logging.info(f"Python found: {python_version}")
        
        pip_version = run_command("pip --version", check=False)
        if "pip" not in pip_version:
            raise RuntimeError("pip is not installed or not found in PATH.")
        logging.info(f"pip found: {pip_version}")
        
    except RuntimeError as e:
        logging.error(f"Prerequisite check failed: {e}")
        sys.exit(1)

def install_prerequisites():
    logging.info("Please install the necessary prerequisites manually:")
    logging.info("1. Git: https://git-scm.com/download/win")
    logging.info("2. Python: https://www.python.org/downloads/")
    logging.info("3. pip: Usually included with Python installation. If not, follow: https://pip.pypa.io/en/stable/installation/")
    sys.exit(1)

def check_for_updates():
    logging.info("Checking for updates...")
    run_command("git fetch")
    local_commit = run_command("git rev-parse HEAD")
    remote_commit = run_command("git rev-parse origin/main")
    if local_commit != remote_commit:
        logging.info("Update found.")
        return True
    logging.info("No updates found.")
    return False

def update_script():
    logging.info("Updating script...")
    run_command("git pull origin main")

def update_environment():
    logging.info("Updating environment...")
    run_command("pip install --upgrade -r requirements.txt")
    run_command("pip install --upgrade pip")

def restart_script():
    logging.info("Restarting script...")
    python = sys.executable
    os.execl(python, python, *sys.argv)

def main():
    check_prerequisites()
    
    while True:
        if check_for_updates():
            update_script()
            update_environment()
            restart_script()
        else:
            logging.info("Script is up to date. Sleeping for 1 hour.")
            time.sleep(3600)  # Check for updates every hour

if __name__ == "__main__":
    install_prerequisites()
    main()
