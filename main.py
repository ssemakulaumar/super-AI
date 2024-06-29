import os
import sys
import subprocess
import logging
import time
import pyttsx3
import speech_recognition as sr
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
import pyautogui
import json
from datetime import datetime
import socket
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox

logging.basicConfig(level=logging.INFO)

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()
# Initialize speech recognition
recognizer = sr.Recognizer()
# Initialize keyboard and mouse controllers
keyboard = KeyboardController()
mouse = MouseController()

CONFIG_FILE = "config.json"
REPO_URL = "https://github.com/ssemakulaumar/super-AI"
MAIN_FILE_PATH = "main.py"

def run_command(command, check=True):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        logging.error(f"Command failed: {command}")
        logging.error(result.stderr)
        raise RuntimeError(result.stderr)
    return result.stdout.strip()

def install_package(package):
    run_command(f"pip install {package}")

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

    # Install additional packages if not already installed
    try:
        import pyttsx3
        import speech_recognition as sr
        import pocketsphinx
        import pynput
        import pyautogui
        import requests
        import bs4
    except ImportError as e:
        logging.info(f"Package not found: {e.name}. Installing now.")
        install_package(e.name)

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

def is_online():
    try:
        # Try to fetch data from Google DNS
        run_command("ping -c 1 8.8.8.8", check=False)
        return True
    except subprocess.CalledProcessError:
        return False

def listen_for_command():
    with sr.Microphone() as source:
        tts_engine.say("Listening for command")
        tts_engine.runAndWait()
        logging.info("Listening for command...")
        audio = recognizer.listen(source)
        try:
            if is_online():
                command = recognizer.recognize_google(audio).lower()
            else:
                command = recognizer.recognize_sphinx(audio).lower()
            logging.info(f"Command received: {command}")
            return command
        except sr.UnknownValueError:
            tts_engine.say("Sorry, I did not understand that.")
            tts_engine.runAndWait()
            return None

def process_voice_command(command):
    if command is None:
        return

    if "type" in command:
        text = command.replace("type", "").strip()
        tts_engine.say(f"Typing: {text}")
        tts_engine.runAndWait()
        keyboard.type(text)
    elif "move mouse to" in command:
        coords = command.replace("move mouse to", "").strip().split()
        if len(coords) == 2:
            x, y = int(coords[0]), int(coords[1])
            tts_engine.say(f"Moving mouse to {x}, {y}")
            tts_engine.runAndWait()
            mouse.position = (x, y)
    elif "click" in command:
        tts_engine.say("Clicking mouse")
        tts_engine.runAndWait()
        mouse.click(MouseController().Button.left, 1)
    elif "update" in command:
        tts_engine.say("Checking for updates")
        tts_engine.runAndWait()
        if check_for_updates():
            update_script()
            update_environment()
            restart_script()
        else:
            tts_engine.say("No updates found.")
            tts_engine.runAndWait()
    elif "log in" in command:
        # Securely handle credentials with environment variables
        username = os.getenv("PC_USERNAME")
        password = os.getenv("PC_PASSWORD")
        if username and password:
            tts_engine.say("Logging in")
            tts_engine.runAndWait()
            keyboard.type(username)
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
            keyboard.type(password)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
        else:
            tts_engine.say("Credentials not set. Please set PC_USERNAME and PC_PASSWORD environment variables.")
            tts_engine.runAndWait()
    elif "open" in command:
        app_name = command.replace("open", "").strip()
        tts_engine.say(f"Opening {app_name}")
        tts_engine.runAndWait()
        run_command(f'start {app_name}')
    elif "switch display" in command:
        tts_engine.say("Switching display")
        tts_engine.runAndWait()
        pyautogui.hotkey('ctrl', 'win', 'left' if 'left' in command else 'right')
    elif "search" in command:
        query = command.replace("search", "").strip()
        tts_engine.say(f"Searching for {query}")
        tts_engine.runAndWait()
        search_results = search_internet(query)
        tts_engine.say(f"Top result: {search_results[0]}")
        tts_engine.runAndWait()
    elif "connect to VPN" in command:
        vpn_profile = command.replace("connect to VPN", "").strip()
        tts_engine.say(f"Connecting to VPN: {vpn_profile}")
        tts_engine.runAndWait()
        connect_to_vpn(vpn_profile)
    elif "connect to UDP" in command:
        address, port = command.replace("connect to UDP", "").strip().split()
        tts_engine.say(f"Connecting to UDP server at {address}:{port}")
        tts_engine.runAndWait()
        connect_to_udp_server(address, int(port))
    # Add more voice commands as needed

def set_environment_variables():
    config = {}
    if not os.path.exists(CONFIG_FILE):
        username = input("Enter your PC username: ")
        password = input("Enter your PC password: ")
        config["PC_USERNAME"] = username
        config["PC_PASSWORD"] = password
        with open(CONFIG_FILE, "w") as config_file:
            json.dump(config, config_file)
    else:
        with open(CONFIG_FILE, "r") as config_file:
            config = json.load(config_file)
    
    os.environ["PC_USERNAME"] = config["PC_USERNAME"]
    os.environ["PC_PASSWORD"] = config["PC_PASSWORD"]

def append_new_script(script_code):
    with open(MAIN_FILE_PATH, "a") as main_file:
        main_file.write("\n\n# Auto-generated script\n")
        main_file.write(script_code)
    logging.info("Appended new script to main file.")

def commit_changes():
    try:
        run_command("git add .")
        run_command(f"git commit -m 'Auto-update at {datetime.now()}'")
        run_command("git push origin main")
        logging.info("Committed and pushed changes to GitHub.")
    except RuntimeError as e:
        logging.error(f"Failed to commit changes: {e}")

def search_internet(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    for g in soup.find_all(class_='BVG0Nb'):
        results.append(g.get_text())
    return results

def connect_to_vpn(profile):
    try:
        run_command(f"openvpn --config {profile}.ovpn")
        logging.info(f"Connected to VPN profile: {profile}")
    except RuntimeError as e:
        logging.error(f"Failed to connect to VPN: {e}")

def connect_to_udp_server(address, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b"Hello, server", (address, port))
        data, server = sock.recvfrom(4096)
        logging.info(f"Received data from UDP server: {data}")
    except socket.error as e:
        logging.error(f"Failed to connect to UDP server: {e}")

def create_gui():
    def on_search():
        query = entry_search.get()
        results = search_internet(query)
        messagebox.showinfo("Search Results", "\n".join(results[:5]))

    def on_connect_vpn():
        profile = entry_vpn.get()
        connect_to_vpn(profile)
        messagebox.showinfo("VPN", f"Connected to VPN profile: {profile}")

    def on_connect_udp():
        address = entry_udp_address.get()
        port = int(entry_udp_port.get())
        connect_to_udp_server(address, port)
        messagebox.showinfo("UDP", f"Connected to UDP server at {address}:{port}")

    root = tk.Tk()
    root.title("Voice Command GUI")

    tk.Label(root, text="Search Query:").grid(row=0, column=0, padx=10, pady=10)
    entry_search = tk.Entry(root)
    entry_search.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(root, text="Search", command=on_search).grid(row=0, column=2, padx=10, pady=10)

    tk.Label(root, text="VPN Profile:").grid(row=1, column=0, padx=10, pady=10)
    entry_vpn = tk.Entry(root)
    entry_vpn.grid(row=1, column=1, padx=10, pady=10)
    tk.Button(root, text="Connect to VPN", command=on_connect_vpn).grid(row=1, column=2, padx=10, pady=10)

    tk.Label(root, text="UDP Address:").grid(row=2, column=0, padx=10, pady=10)
    entry_udp_address = tk.Entry(root)
    entry_udp_address.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(root, text="UDP Port:").grid(row=3, column=0, padx=10, pady=10)
    entry_udp_port = tk.Entry(root)
    entry_udp_port.grid(row=3, column=1, padx=10, pady=10)
    tk.Button(root, text="Connect to UDP", command=on_connect_udp).grid(row=3, column=2, padx=10, pady=10)

    root.mainloop()

def main():
    check_prerequisites()
    set_environment_variables()
    
    while True:
        if check_for_updates():
            update_script()
            update_environment()
            restart_script()
        else:
            tts_engine.say("Script is up to date. Checking for voice commands.")
            tts_engine.runAndWait()
            command = listen_for_command()
            process_voice_command(command)
            logging.info("Sleeping for 1 hour.")
            time.sleep(3600)  # Check for updates every hour

if __name__ == "__main__":
    check_prerequisites()
    create_gui()
    main()
