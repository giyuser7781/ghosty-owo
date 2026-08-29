import os
import sys
import json
import subprocess
import time

def install_colorama():
    try:
        import colorama
    except ImportError:
        print("Installing colorama for colorful terminal output...")
        subprocess.run([sys.executable, "-m", "pip", "install", "colorama"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

install_colorama()
from colorama import init, Fore, Style

init(autoreset=True)

class Colors:
    CYAN = Fore.CYAN
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    DIM = Style.DIM
    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL

def log_step(step_num, message):
    print(f"\n{Colors.CYAN}{Colors.BOLD}[ Step {step_num} ]{Colors.RESET} {Colors.BOLD}{message}{Colors.RESET}")

def log_info(message):
    print(f"{Colors.DIM} -> {message}{Colors.RESET}")

def log_success(message):
    print(f"{Colors.GREEN} -> {message}{Colors.RESET}")

def log_warn(message):
    print(f"{Colors.YELLOW} -> [!] {message}{Colors.RESET}")

def log_error(message):
    print(f"{Colors.RED} -> [X] {message}{Colors.RESET}")

def is_termux():
    return "PREFIX" in os.environ and "com.termux" in os.environ.get("PREFIX", "")

def is_windows():
    return os.name == "nt"

def banner():
    print(rf"""
    {Colors.DIM}Welcome to GhoSty OwO V4.1 Setup Assistant{Colors.RESET}
    {Colors.DIM}Made With <3 By @jijaghosty • Async Development{Colors.RESET}
{Colors.GREEN}{"="*60}{Colors.RESET}""")

def setup_dependencies():
    log_step(1, "Installing Dependencies")
    
    if is_termux():
        log_info("Termux Android environment detected. Installing required system packages first...")
        subprocess.run("pkg update -y && pkg upgrade -y", shell=True)
        subprocess.run("pkg install tur-repo -y", shell=True)
        subprocess.run("pkg install clang make pkg-config libjpeg-turbo libpng freetype python python-pip python-numpy python-pillow -y", shell=True)
        subprocess.run("pip install setuptools wheel packaging cython", shell=True)
        log_success("Termux system dependencies installed.")
    
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        log_error(f"{requirements_file} not found! Cannot install dependencies.")
        return
        
    log_info("Installing Python dependencies from requirements.txt...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], check=True)
        log_success("All Python dependencies installed successfully.")
    except Exception as e:
        log_error(f"Failed to install requirements: {e}")

def verify_and_setup_config():
    log_step(2, "Configuration Setup")
    
    config_file = "config.json"
    default_config = {
        "MAIN_TOKEN": "",
        "WEB_DASHBOARD": True
    }
    
    if not os.path.exists(config_file):
        log_warn("config.json not found. Creating a new one...")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        config_data = default_config
    else:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception:
            log_error("Could not parse config.json. Recreating default...")
            config_data = default_config
            
    token_val = config_data.get("MAIN_TOKEN", "").strip()
    
    if not token_val:
        log_warn("Main Discord Token is empty!")
        choice = input(f"{Colors.BOLD}Would you like to enter your Main Discord Token now? (y/N): {Colors.RESET}").strip().lower()
        if choice in ("y", "yes"):
            user_token = input(f"{Colors.CYAN}{Colors.BOLD}Enter Main Discord Token: {Colors.RESET}").strip()
            if (user_token.startswith('"') and user_token.endswith('"')) or (user_token.startswith("'") and user_token.endswith("'")):
                user_token = user_token[1:-1].strip()
            if user_token:
                config_data["MAIN_TOKEN"] = user_token
                with open(config_file, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=4)
                log_success("Main Token saved to config.json!")
            else:
                log_warn("Empty token entered. Remember to edit config.json manually.")
        else:
            log_info("Skipped token entry. Remember to edit config.json before starting.")
    else:
        log_success(f"Main Discord Token found in config.json.")

    tokens_file = "tokens.txt"
    if not os.path.exists(tokens_file):
        log_warn(f"{tokens_file} not found. Creating an empty one...")
        with open(tokens_file, "w", encoding="utf-8") as f:
            pass
            
    with open(tokens_file, "r", encoding="utf-8") as f:
        worker_tokens = [line.strip() for line in f if line.strip()]
        
    if not worker_tokens:
        log_warn(f"{tokens_file} is empty. You need worker tokens to use the bot.")
    else:
        log_success(f"Found {len(worker_tokens)} worker token(s) in {tokens_file}.")
        
    channels_file = "channels.txt"
    if not os.path.exists(channels_file):
        log_warn(f"{channels_file} not found. Creating an empty one...")
        with open(channels_file, "w", encoding="utf-8") as f:
            pass
            
    with open(channels_file, "r", encoding="utf-8") as f:
        channels = [line.strip() for line in f if line.strip()]
        
    if not channels:
        log_warn(f"{channels_file} is empty. The bots won't know which channels to farm in.")
    else:
        log_success(f"Found {len(channels)} channel ID(s) in {channels_file}.")


def generate_launch_helpers():
    log_step(3, "Generating Launch Helpers")
    
    setup_files_dir = "setup_files"
    os.makedirs(setup_files_dir, exist_ok=True)
    
    run_bat = os.path.join(setup_files_dir, "run.bat")
    with open(run_bat, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("title GhoSty OwO V4.1\n")
        f.write('cd /d "%~dp0\\.."\n')
        f.write("python main.py\n")
        f.write("if errorlevel 1 (\n")
        f.write("    echo.\n")
        f.write("    echo [!] Program exited with an error. Check configuration or dependencies.\n")
        f.write("    pause\n")
        f.write(")\n")
        
    setup_bat = os.path.join(setup_files_dir, "setup.bat")
    with open(setup_bat, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("title GhoSty OwO V4.1 - Setup Assistant\n")
        f.write('cd /d "%~dp0\\.."\n')
        f.write("python setup.py\n")
        f.write("if errorlevel 1 (\n")
        f.write("    echo.\n")
        f.write("    echo [!] Setup exited with an error.\n")
        f.write("    pause\n")
        f.write(")\n")
        
    run_sh = os.path.join(setup_files_dir, "run.sh")
    with open(run_sh, "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write('PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"\n')
        f.write('cd "$PROJECT_DIR" || exit 1\n\n')
        f.write("if command -v python3 >/dev/null 2>&1; then\n")
        f.write('    python3 main.py "$@"\n')
        f.write("elif command -v python >/dev/null 2>&1; then\n")
        f.write('    python main.py "$@"\n')
        f.write("else\n")
        f.write('    echo "[!] Python is not installed or not in PATH."\n')
        f.write("    exit 1\n")
        f.write("fi\n")
    if not is_windows():
        try:
            os.chmod(run_sh, 0o755)
        except Exception:
            pass

    termux_sh = os.path.join(setup_files_dir, "termux_setup.sh")
    with open(termux_sh, "w", encoding="utf-8") as f:
        f.write("#!/data/data/com.termux/files/usr/bin/bash\n\n")
        f.write('if [ ! -d "/storage/emulated/0" ]; then\n')
        f.write('    echo -e "\\033[93m[!] Requesting storage access. Tap ALLOW on your phone screen.\\033[0m"\n')
        f.write("    termux-setup-storage\n")
        f.write("    sleep 3\n")
        f.write("fi\n\n")
        f.write("pkg update -y && pkg upgrade -y\n")
        f.write("pkg install tur-repo -y\n")
        f.write("pkg install clang make pkg-config libjpeg-turbo libpng freetype python python-pip python-numpy python-pillow -y\n\n")
        f.write("pip install setuptools wheel packaging cython\n\n")
        f.write('PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"\n')
        f.write('cd "$PROJECT_DIR" || exit 1\n\n')
        f.write('if [ -f "setup.py" ]; then\n')
        f.write("    python setup.py\n")
        f.write("else\n")
        f.write("    python3 setup.py\n")
        f.write("fi\n")
    if not is_windows():
        try:
            os.chmod(termux_sh, 0o755)
        except Exception:
            pass
            
    log_success(f"Launch helper scripts generated in {setup_files_dir}/")


def display_launch_instructions():
    log_step(4, "Ready to Launch & Execution Commands")
    
    print(f"{Colors.GREEN}{Colors.BOLD}Setup is complete! You can run GhoSty OwO V4.1 using the commands below:{Colors.RESET}\n")

    cwd = os.getcwd()
    run_bat_path = os.path.join(cwd, "setup_files", "run.bat")
    run_sh_path = os.path.join(cwd, "setup_files", "run.sh")

    if is_termux():
        print(f"  {Colors.CYAN}{Colors.BOLD}[Android (Termux) Run Command]:{Colors.RESET}")
        print(f"  {Colors.YELLOW}cd \"{cwd}\" && python main.py{Colors.RESET}\n")
        print(f"  {Colors.DIM}Or simply run:{Colors.RESET} {Colors.YELLOW}bash \"{run_sh_path}\"{Colors.RESET}\n")
    elif is_windows():
        print(f"  {Colors.CYAN}{Colors.BOLD}[Windows (CMD / PowerShell) Run Command]:{Colors.RESET}")
        print(f"  {Colors.YELLOW}cd /d \"{cwd}\" && python main.py{Colors.RESET}\n")
        print(f"  {Colors.DIM}Or double-click:{Colors.RESET} {Colors.YELLOW}{run_bat_path}{Colors.RESET}\n")
    else:
        print(f"  {Colors.CYAN}{Colors.BOLD}[Linux / macOS Run Command]:{Colors.RESET}")
        print(f"  {Colors.YELLOW}cd \"{cwd}\" && python3 main.py{Colors.RESET}\n")
        print(f"  {Colors.DIM}Or run:{Colors.RESET} {Colors.YELLOW}bash \"{run_sh_path}\"{Colors.RESET}\n")


def run_main_script():
    log_info("Starting GhoSty OwO V4.1...")
    try:
        subprocess.run([sys.executable, "main.py"], check=False)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}GhoSty OwO stopped by user.{Colors.RESET}")
    except Exception as e:
        log_error(f"Error while running main.py: {e}")

def main():
    banner()
    setup_dependencies()
    verify_and_setup_config()
    generate_launch_helpers()
    display_launch_instructions()
    
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.RESET}")
    try:
        run_now = input(f"{Colors.BOLD}Would you like to start GhoSty OwO V4.1 right now? (Y/n): {Colors.RESET}").strip().lower()
        if run_now in ("", "y", "yes"):
            print()
            run_main_script()
        else:
            print(f"\n{Colors.CYAN}You can start the bot anytime using the commands shown above. Enjoy!{Colors.RESET}\n")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting setup.")

if __name__ == "__main__":
    main()
