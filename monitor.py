import os
import time
import logging
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil
import git

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Monitor file system events
class MonitorHandler(FileSystemEventHandler):
    def on_created(self, event):
        logging.info(f"File created: {event.src_path}")
        notify_changes(f"File created: {event.src_path}")

    def on_modified(self, event):
        logging.info(f"File modified: {event.src_path}")
        notify_changes(f"File modified: {event.src_path}")

    def on_deleted(self, event):
        logging.info(f"File deleted: {event.src_path}")
        notify_changes(f"File deleted: {event.src_path}")

# Notify the Python AI script about the changes
def notify_changes(message):
    # Placeholder for actual implementation
    pass

# Check if WSL is installed, if not, install WSL and Linux distribution
def check_wsl_installation():
    try:
        output = subprocess.check_output('wsl --list --quiet', shell=True, stderr=subprocess.STDOUT)
        if not output.strip():
            logging.info("WSL not installed. Installing WSL and Ubuntu...")
            subprocess.run(['wsl', '--install', '--distribution', 'Ubuntu'], check=True)
            logging.info("WSL and Ubuntu installation completed.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error checking/installing WSL: {e}")

# Monitor system services
def monitor_services():
    while True:
        services = [s.name() for s in psutil.win_service_iter()]
        for service in services:
            svc = psutil.win_service_get(service)
            status = svc.status()
            if status != 'running':
                logging.info(f"Service {service} is not running")
                notify_changes(f"Service {service} is not running")
        time.sleep(60)

def check_for_updates():
    try:
        repo = git.Repo('.')
        origin = repo.remotes.origin
        origin.fetch()
        local_commit = repo.head.commit
        remote_commit = repo.commit('origin/main')
        if local_commit != remote_commit:
            logging.info("Update found. Pulling changes...")
            origin.pull()
            notify_changes("Script updated to the latest version.")
    except Exception as e:
        logging.error(f"Error checking for updates: {e}")

if __name__ == "__main__":
    # Check and install WSL if necessary
    check_wsl_installation()

    # Start monitoring file system events
    path = "C:\\"  # Specify the path to monitor
    event_handler = MonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        # Monitor services and check for updates
        monitor_services()
        while True:
            check_for_updates()
            time.sleep(3600)  # Check for updates every hour
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
