import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
from datetime import datetime

CONFIG_FILE = 'backup_config.json'

def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def save_config(data):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(data, file, indent=4)
    update_timestamp()

def get_last_modified_time():
    """Return the last modified time of the configuration file."""
    if os.path.exists(CONFIG_FILE):
        return os.path.getmtime(CONFIG_FILE)
    return None

def update_timestamp():
    """Update the timestamp label with the last modified time of the configuration file."""
    timestamp = get_last_modified_time()
    if timestamp:
        last_modified = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        timestamp_label.config(text=f"Last Modified: {last_modified}")
    else:
        timestamp_label.config(text="No configuration file found.")

def update_config():
    try:
        config = {
            "run_enabled": run_enabled_var.get(),
            "source_dirs": src_dirs_entry.get().split(';'),
            "dest_dirs": dest_dirs_entry.get().split(';'),
            "log_file": log_file_entry.get(),
            "error_log_file": error_log_entry.get(),
            "sleep_time": int(sleep_time_entry.get())
        }
        save_config(config)
        messagebox.showinfo("Success", "Configuration saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")

def select_directory(entry_field):
    directory = filedialog.askdirectory()
    if directory:
        current_text = entry_field.get()
        if current_text:
            entry_field.insert(tk.END, ';' + directory)
        else:
            entry_field.insert(tk.END, directory)

# Load the initial configuration and update the timestamp
config = load_config()

# Create the main window
root = tk.Tk()
root.title("Backup Configuration")

# Run Enabled
tk.Label(root, text="Run Enabled (Y/N)").grid(row=0, column=0, padx=10, pady=5, sticky="w")
run_enabled_var = tk.StringVar(value=config.get('run_enabled', 'Y'))
run_enabled_entry = tk.Entry(root, textvariable=run_enabled_var, width=60)
run_enabled_entry.grid(row=0, column=1, padx=10, pady=5)

# Source Directories
tk.Label(root, text="Source Directories (separate with ;)").grid(row=1, column=0, padx=10, pady=5, sticky="w")
src_dirs_entry = tk.Entry(root, width=60)
src_dirs_entry.grid(row=1, column=1, padx=10, pady=5)
src_dirs_entry.insert(tk.END, ';'.join(config['source_dirs']))
tk.Button(root, text="Browse", command=lambda: select_directory(src_dirs_entry)).grid(row=1, column=2, padx=5, pady=5)

# Destination Directories
tk.Label(root, text="Destination Directories (separate with ;)").grid(row=2, column=0, padx=10, pady=5, sticky="w")
dest_dirs_entry = tk.Entry(root, width=60)
dest_dirs_entry.grid(row=2, column=1, padx=10, pady=5)
dest_dirs_entry.insert(tk.END, ';'.join(config['dest_dirs']))
tk.Button(root, text="Browse", command=lambda: select_directory(dest_dirs_entry)).grid(row=2, column=2, padx=5, pady=5)

# Log File
tk.Label(root, text="Log File").grid(row=3, column=0, padx=10, pady=5, sticky="w")
log_file_entry = tk.Entry(root, width=60)
log_file_entry.grid(row=3, column=1, padx=10, pady=5)
log_file_entry.insert(tk.END, config['log_file'])

# Error Log File
tk.Label(root, text="Error Log File").grid(row=4, column=0, padx=10, pady=5, sticky="w")
error_log_entry = tk.Entry(root, width=60)
error_log_entry.grid(row=4, column=1, padx=10, pady=5)
error_log_entry.insert(tk.END, config['error_log_file'])

# Sleep Time
tk.Label(root, text="Sleep Time (seconds)").grid(row=5, column=0, padx=10, pady=5, sticky="w")
sleep_time_entry = tk.Entry(root, width=60)
sleep_time_entry.grid(row=5, column=1, padx=10, pady=5)
sleep_time_entry.insert(tk.END, config['sleep_time'])

# Save Button
tk.Button(root, text="Save Configuration", command=update_config).grid(row=6, column=1, pady=20)

# Timestamp Label
timestamp_label = tk.Label(root, text="Last Modified: ", fg="blue")
timestamp_label.grid(row=7, column=1, padx=10, pady=10, sticky="w")

# Initialize the timestamp label with the current timestamp
update_timestamp()

# Run the GUI loop
root.mainloop()
