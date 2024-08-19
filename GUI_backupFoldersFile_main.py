import logging
import os
import platform
import tkinter as tk
from tkinter.ttk import *
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import subprocess
import psutil
from datetime import datetime
from threading import Thread
import time
import gzip
import win32com.client
import gzip

CONFIG_FILE = 'backup_config.json'
SCRIPT_FILE = 'backupFoldersFiles_exceptionHandling.py'
AUTO_REFRESH_INTERVAL = 5  # seconds

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        messagebox.showerror("Error", f"Failed to load configuration: {e}")
        return {}

def save_config(data):
    try:
        with open(CONFIG_FILE, 'w') as file:
            json.dump(data, file, indent=4)
        update_timestamp()
    except Exception as e:
        logging.error(f"Failed to save config: {e}")
        messagebox.showerror("Error", f"Failed to save configuration: {e}")

def get_last_modified_time():
    try:
        if os.path.exists(CONFIG_FILE):
            return os.path.getmtime(CONFIG_FILE)
        return None
    except Exception as e:
        logging.error(f"Failed to get last modified time: {e}")
        return None

def update_timestamp():
    try:
        timestamp = get_last_modified_time()
        if timestamp:
            last_modified = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            timestamp_label.config(text=f"Last Modified: {last_modified}")
        else:
            timestamp_label.config(text="No configuration file found.")
    except Exception as e:
        logging.error(f"Failed to update timestamp: {e}")

def toggle_service(enable):
    try:
        config = load_config()
        config['run_enabled'] = enable
        save_config(config)
        update_home_status()
    except Exception as e:
        logging.error(f"Failed to toggle service: {e}")
        messagebox.showerror("Error", f"Failed to toggle service: {e}")

def is_script_running(script_name):
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['cmdline'] and script_name in proc.info['cmdline']:
                return True
        return False
    except Exception as e:
        logging.error(f"Failed to check if script is running: {e}")
        return False

def update_home_status():
    try:
        config = load_config()
        if config.get('run_enabled') == 'Y':
            service_status_label.config(text="Service Enabled", bg="green")
        else:
            service_status_label.config(text="Service Disabled", bg="red")

        script_running = is_script_running(SCRIPT_FILE)
        if script_running:
            script_status_label.config(text="Script Running", bg="green")
        else:
            script_status_label.config(text="Script Not Running", bg="red")
    except Exception as e:
        logging.error(f"Failed to update home status: {e}")

def start_script():
    try:
        if not is_script_running(SCRIPT_FILE):
            subprocess.Popen(["python", SCRIPT_FILE])
            messagebox.showinfo("Script Started", "The backup script has started running.")
        update_home_status()
    except Exception as e:
        logging.error(f"Failed to start script: {e}")
        messagebox.showerror("Error", f"Failed to start script: {e}")

def stop_script():
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['cmdline'] and SCRIPT_FILE in proc.info['cmdline']:
                proc.terminate()
                messagebox.showinfo("Script Stopped", "The backup script has been stopped.")
        update_home_status()
    except Exception as e:
        logging.error(f"Failed to stop script: {e}")
        messagebox.showerror("Error", f"Failed to stop script: {e}")

def update_config():
    try:
        config = {
            "run_enabled": run_enabled_var.get(),
            "source_dirs": src_dirs_entry.get().split(';'),
            "dest_dirs": dest_dirs_entry.get().split(';'),
            "log_dirs": log_dirs_entry.get(),  # Add this line
            "log_file": log_file_entry.get(),
            "error_log_file": error_log_entry.get(),
            "sleep_time": int(sleep_time_entry.get()),
            "run_at_startup": run_at_startup_var.get()
        }
        save_config(config)
        set_run_at_startup(config['run_at_startup'])
        messagebox.showinfo("Success", "Configuration saved successfully!")
    except Exception as e:
        logging.error(f"Failed to save configuration: {e}")
        messagebox.showerror("Error", f"Failed to save configuration: {e}")


def select_directory(entry_field):
    try:
        directory = filedialog.askdirectory()
        if directory:
            current_text = entry_field.get()
            if current_text:
                entry_field.insert(tk.END, ';' + directory)
            else:
                entry_field.insert(tk.END, directory)
    except Exception as e:
        logging.error(f"Failed to select directory: {e}")
        messagebox.showerror("Error", f"Failed to select directory: {e}")

def view_log(log_file, log_text_widget):
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as file:
                lines = file.readlines()
                lines.reverse()  # Reverse the log order to display newest first
                log_text_widget.delete(1.0, tk.END)
                log_text_widget.insert(tk.END, ''.join(lines))
        else:
            log_text_widget.delete(1.0, tk.END)
            log_text_widget.insert(tk.END, "Log file not found.")
    except Exception as e:
        logging.error(f"Failed to view log: {e}")
        log_text_widget.delete(1.0, tk.END)
        log_text_widget.insert(tk.END, "Failed to view log.")

def auto_refresh_logs(log_file, log_text_widget):
    while True:
        try:
            view_log(log_file, log_text_widget)
            time.sleep(AUTO_REFRESH_INTERVAL)
        except Exception as e:
            logging.error(f"Failed to auto-refresh logs: {e}")

def set_run_at_startup(enable):
    system_platform = platform.system()
    try:
        if system_platform == 'Windows':
            # Path to the Startup folder
            startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            shortcut_path = os.path.join(startup_folder, f"{SCRIPT_FILE}.lnk")
            
            if enable == 'Y':
                # Create a shortcut
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortcut(shortcut_path)
                shortcut.TargetPath = os.path.abspath(SCRIPT_FILE)
                shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(SCRIPT_FILE))
                shortcut.IconLocation = os.path.abspath(SCRIPT_FILE)
                shortcut.Save()
            elif os.path.exists(shortcut_path):
                os.remove(shortcut_path)
        elif system_platform == 'Linux':
            startup_file = os.path.expanduser(f'~/.config/autostart/{SCRIPT_FILE}.desktop')
            if enable == 'Y':
                with open(startup_file, 'w') as file:
                    file.write(f'[Desktop Entry]\nType=Application\nExec=python3 "{os.path.abspath(SCRIPT_FILE)}"\nHidden=false\nNoDisplay=false\nX-GNOME-Autostart-enabled=true\nName={SCRIPT_FILE}')
            elif os.path.exists(startup_file):
                os.remove(startup_file)
        elif system_platform == 'Darwin':  # macOS
            startup_file = os.path.expanduser(f'~/Library/LaunchAgents/{SCRIPT_FILE}.plist')
            if enable == 'Y':
                plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
                <plist version="1.0">
                <dict>
                    <key>Label</key>
                    <string>{SCRIPT_FILE}</string>
                    <key>ProgramArguments</key>
                    <array>
                        <string>python3</string>
                        <string>{os.path.abspath(SCRIPT_FILE)}</string>
                    </array>
                    <key>RunAtLoad</key>
                    <true/>
                </dict>
                </plist>
                """
                with open(startup_file, 'w') as file:
                    file.write(plist_content)
            elif os.path.exists(startup_file):
                os.remove(startup_file)
    except Exception as e:
        logging.error(f"Failed to set run at startup: {e}")

# Load the initial configuration and update the timestamp
config = load_config()

# Create the main window
root = tk.Tk()
root.title("Backup Configuration")
root.geometry("800x600")

# Create tabs
tab_control = ttk.Notebook(root)
home_tab = ttk.Frame(tab_control)
config_tab = ttk.Frame(tab_control)
error_tab = ttk.Frame(tab_control)
tab_control.add(home_tab, text="Home")
tab_control.add(config_tab, text="Configuration")
tab_control.add(error_tab, text="Errors")
tab_control.pack(expand=1, fill="both")

# Home Tab

# Service Status Section
service_frame = tk.LabelFrame(home_tab, text="Service Status", padx=10, pady=10)
service_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
service_status_label = tk.Label(service_frame, text="Service Disabled", bg="red", width=25)
service_status_label.pack(padx=10, pady=10)
Button(service_frame, text="Enable Service", command=lambda: toggle_service('Y'), width=20).pack(padx=10, pady=5)
Button(service_frame, text="Disable Service", command=lambda: toggle_service('N'), width=20).pack(padx=10, pady=5)

# Refresh Status Button
Button(home_tab, text="Refresh Status", command=update_home_status, width=20).grid(row=0, column=1, padx=10, pady=5)

# Script Execution Section
script_frame = tk.LabelFrame(home_tab, text="Script Execution", padx=10, pady=10)
script_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
script_status_label = tk.Label(script_frame, text="Script Not Running", bg="red", width=25)
script_status_label.pack(padx=10, pady=10)
Button(script_frame, text="Start Script", command=start_script, width=20).pack(padx=10, pady=5)
Button(script_frame, text="Stop Script", command=stop_script, width=20).pack(padx=10, pady=5)

# Log Viewing Section
log_frame = tk.LabelFrame(home_tab, text="Logs", padx=10, pady=10)
log_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
log_text = scrolledtext.ScrolledText(log_frame, width=90, height=15)
log_text.pack(padx=10, pady=10)
Button(log_frame, text="View/Reload Logs", command=lambda: view_log(config['log_file'], log_text)).pack(padx=10, pady=5)

## Threads =================================================
# Start auto-refresh thread
log_auto_refresh_thread = Thread(target=auto_refresh_logs, args=(config['log_file'], log_text), daemon=True)
log_auto_refresh_thread.start()

# Configuration Tab

# Run Enabled
tk.Label(config_tab, text="Run Enabled (Y/N)").grid(row=0, column=0, padx=10, pady=5, sticky="w")
run_enabled_var = tk.StringVar(value=config.get('run_enabled', 'Y'))
run_enabled_entry = Entry(config_tab, textvariable=run_enabled_var, width=60)
run_enabled_entry.grid(row=0, column=1, padx=10, pady=5)

# Source Directories
tk.Label(config_tab, text="Source Directories (separate with ;)").grid(row=1, column=0, padx=10, pady=5, sticky="w")
src_dirs_entry = Entry(config_tab, width=60)
src_dirs_entry.grid(row=1, column=1, padx=10, pady=5)
src_dirs_entry.insert(tk.END, ';'.join(config['source_dirs']))
Button(config_tab, text="Browse", command=lambda: select_directory(src_dirs_entry)).grid(row=1, column=2, padx=5, pady=5)

# Destination Directories
tk.Label(config_tab, text="Destination Directories (separate with ;)").grid(row=2, column=0, padx=10, pady=5, sticky="w")
dest_dirs_entry = Entry(config_tab, width=60)
dest_dirs_entry.grid(row=2, column=1, padx=10, pady=5)
dest_dirs_entry.insert(tk.END, ';'.join(config['dest_dirs']))
Button(config_tab, text="Browse", command=lambda: select_directory(dest_dirs_entry)).grid(row=2, column=2, padx=5, pady=5)

# Log Directories
tk.Label(config_tab, text="Log Directories").grid(row=7, column=0, padx=10, pady=5, sticky="w")
log_dirs_entry = Entry(config_tab, width=60)
log_dirs_entry.grid(row=7, column=1, padx=10, pady=5)
log_dirs_entry.insert(tk.END, ';'.join(config.get('log_dirs', '')))  # Default to empty if not set

# Browse Button for Log Directories
Button(config_tab, text="Browse", command=lambda: select_directory(log_dirs_entry)).grid(row=7, column=2, padx=5, pady=5)

# Log File
tk.Label(config_tab, text="Log File").grid(row=3, column=0, padx=10, pady=5, sticky="w")
log_file_entry = Entry(config_tab, width=60)
log_file_entry.grid(row=3, column=1, padx=10, pady=5)
log_file_entry.insert(tk.END, config['log_file'])

# Error Log File
tk.Label(config_tab, text="Error Log File").grid(row=4, column=0, padx=10, pady=5, sticky="w")
error_log_entry = Entry(config_tab, width=60)
error_log_entry.grid(row=4, column=1, padx=10, pady=5)
error_log_entry.insert(tk.END, config['error_log_file'])

# Sleep Time
tk.Label(config_tab, text="Sleep Time (seconds)").grid(row=5, column=0, padx=10, pady=5, sticky="w")
sleep_time_entry = Entry(config_tab, width=60)
sleep_time_entry.grid(row=5, column=1, padx=10, pady=5)
sleep_time_entry.insert(tk.END, config['sleep_time'])

# Run at Startup Checkbox
tk.Label(config_tab, text="Run at Startup").grid(row=6, column=0, padx=10, pady=5, sticky="w")
run_at_startup_var = tk.StringVar(value=config.get('run_at_startup', 'N'))
run_at_startup_check = tk.Checkbutton(config_tab, variable=run_at_startup_var, onvalue='Y', offvalue='N')
run_at_startup_check.grid(row=6, column=1, sticky="w")

# Save Button
Button(config_tab, text="Save Configuration", command=update_config).grid(row=8, column=1, pady=20)

# Timestamp Label
timestamp_label = tk.Label(config_tab, text="Last Modified: ", fg="blue")
timestamp_label.grid(row=9, column=1, padx=10, pady=10, sticky="w")

# Error Tab
error_log_frame = tk.LabelFrame(error_tab, text="Error Logs", padx=10, pady=10)
error_log_frame.pack(fill="both", expand=True, padx=10, pady=10)
error_log_text = scrolledtext.ScrolledText(error_log_frame, width=90, height=25)
error_log_text.pack(padx=10, pady=10)
Button(error_log_frame, text="View/Reload Error Logs", command=lambda: view_log(config['error_log_file'], error_log_text)).pack(padx=10, pady=5)

# Initialize the timestamp label with the current timestamp
update_timestamp()

# Initialize the home status
update_home_status()

# Run the GUI loop
root.mainloop()
