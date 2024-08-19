Backup Files And Folders Tool
Code Explanation
backupFoldersFiles.py
This Python script is designed to back up files from specified source directories to corresponding destination directories. It includes features like checksum verification, file permission preservation, and error logging. Let's break down the code section by section:
1. Importing Modules
python
Copy code
import os
import time
import shutil
import hashlib
import logging
import json
•	os: For interacting with the operating system, e.g., file paths and directory operations.
•	time: For sleeping between backup cycles and timestamping logs.
•	shutil: For file operations like copying files.
•	hashlib: For generating checksums (MD5) to verify file integrity.
•	logging: For logging information and errors.
•	json: For reading the configuration from a JSON file.
2. Helper Functions
calculate_checksum(file_path)
python
Copy code
def calculate_checksum(file_path):
    """Calculate MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()
•	This function calculates the MD5 checksum of a file, which is used to verify if a file has changed by comparing it with another file's checksum.
get_permissions(file_path)
python
Copy code
def get_permissions(file_path):
    """Get file permissions."""
    return oct(os.stat(file_path).st_mode)[-3:]
•	This function retrieves the file permissions in octal format (e.g., 755), which is useful for maintaining the same permissions in the backup.
is_file_changed(src_file, dest_file)
python
Copy code
def is_file_changed(src_file, dest_file):
    """Check if the file has changed by comparing checksum and modification time."""
    if not os.path.exists(dest_file):
        return True
    
    src_checksum = calculate_checksum(src_file)
    dest_checksum = calculate_checksum(dest_file)
    
    return src_checksum != dest_checksum
•	This function checks if the file at dest_file exists and, if it does, compares its checksum with the source file. If the checksums differ, it returns True (indicating the file has changed), otherwise False.
3. Core Backup Function
backup_files(src_dir, dest_dir)
python
Copy code
def backup_files(src_dir, dest_dir):
    """Backup files from src_dir to dest_dir with logging, excluding '.stfolder'."""
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    for root, dirs, files in os.walk(src_dir):
        # Skip the .stfolder directory
        if '.stfolder' in dirs:
            dirs.remove('.stfolder')
        
        relative_path = os.path.relpath(root, src_dir)
        dest_path = os.path.join(dest_dir, relative_path)
        
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_path, file)
            
            if is_file_changed(src_file, dest_file):
                checksum = calculate_checksum(src_file)
                permissions = get_permissions(src_file)
                
                try:
                    shutil.copy2(src_file, dest_file)
                    logging.info(f"Backed up file: {src_file} -> {dest_file} | Checksum: {checksum} | Permissions: {permissions}")
                except Exception as e:
                    error_message = f"Failed to back up file: {src_file} -> {dest_file} | Error: {e}"
                    logging.error(error_message)
                    with open(ERROR_LOG_FILE, 'a') as error_log:
                        error_log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {error_message}\n")
            else:
                logging.info(f"File unchanged, skipping backup: {src_file}")
•	This function handles the actual backup process:
o	It creates the destination directory if it doesn't exist.
o	It walks through all files and subdirectories in the source directory.
o	It skips a special directory named .stfolder.
o	For each file, it checks if the file has changed using is_file_changed. If so, it backs up the file by copying it to the destination directory, preserving the file's metadata (e.g., permissions and modification time).
o	It logs the success or failure of each file copy operation.
4. Main Execution Loop
python
Copy code
if __name__ == "__main__":
    while True:
        # Load configuration from file
        with open('backup_config.json', 'r') as config_file:
            config = json.load(config_file)

        # Configuration
        SOURCE_DIRS = config['source_dirs']
        DEST_DIRS = config['dest_dirs']
        LOG_FILE = config['log_file']
        ERROR_LOG_FILE = config['error_log_file']
        SLEEP_TIME = config['sleep_time']
        RUN_ENABLED = config['run_enabled'] # Y = will run , anything else no run

        # Logging configuration
        logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

        if RUN_ENABLED=="Y":
            for src_dir, dest_dir in zip(SOURCE_DIRS, DEST_DIRS):
                backup_files(src_dir, dest_dir)
        else:
            logging.info(f"Run Disabled, Exiting Process: {__name__}")
        
        time.sleep(SLEEP_TIME)
•	The script enters an infinite loop (while True:) where it:
o	Loads the configuration from a JSON file (backup_config.json). This configuration includes:
	Source and destination directories.
	Log and error log file paths.
	Sleep time between backup cycles.
	A flag (RUN_ENABLED) to enable or disable the backup process.
o	Configures logging to output messages to the specified log file.
o	If the backup process is enabled (RUN_ENABLED == "Y"), it calls backup_files() for each pair of source and destination directories.
o	If the backup process is disabled, it logs a message and exits.
o	The script then sleeps for the specified time (SLEEP_TIME) before repeating the process.
Summary
•	Purpose: The script is designed to back up files from one or more source directories to corresponding destination directories while checking if the files have changed.
•	Key Features:
o	Checksums are used to detect changes.
o	File permissions are preserved.
o	Logging is implemented for both successful and failed operations.
o	The script is controlled via a JSON configuration file and runs in a loop, periodically checking and backing up files as configured.
Json File
This JSON configuration file is used by the backup script to control how it operates. Each key-value pair in this file represents a specific configuration setting for the script. Here's an explanation of each part:
JSON Structure
json
Copy code
{
    "run_enabled": "N",
    "source_dirs": [
        "C:\\Users\\Milind\\Music\\"
    ],
    "dest_dirs": [
        "D:\\AutoBackup\\Music\\"
    ],
    "log_file": "backupFoldersFiles.log",
    "error_log_file": "error.log",
    "sleep_time": 30
}
Key-Value Pairs
1.	"run_enabled": "N"
o	Purpose: Controls whether the backup process should run or not.
o	Value:
	"Y": The script will perform the backup process.
	"N": The script will not perform the backup process and will exit after logging that the run is disabled.
2.	"source_dirs": ["C:\\Users\\Milind\\Music\\"]
o	Purpose: Specifies the source directories that contain the files you want to back up.
o	Value:
	"C:\\Users\\Milind\\Music\\": This is the directory on the user's system where the files to be backed up are located. You can list multiple directories here, and the script will back up files from each listed directory.
3.	"dest_dirs": ["D:\\AutoBackup\\Music\\"]
o	Purpose: Specifies the destination directories where the backed-up files should be stored.
o	Value:
	"D:\\AutoBackup\\Music\\": This is the directory on the user's system where the backed-up files will be stored. It corresponds to the source directory listed under source_dirs. Each source directory should have a corresponding destination directory listed in the same order.
4.	"log_file": "backupFoldersFiles.log"
o	Purpose: Defines the file where the script will log information about the backup process.
o	Value:
	"backupFoldersFiles.log": The name of the log file where the script records details about which files were backed up, skipped, or if any errors occurred.
5.	"error_log_file": "error.log"
o	Purpose: Specifies the file where the script will log errors that occur during the backup process.
o	Value:
	"error.log": The name of the error log file where the script records details about any errors or issues that prevent files from being backed up.
6.	"sleep_time": 30
o	Purpose: Sets the time interval (in seconds) between each backup cycle.
o	Value:
	30: The script will wait for 30 seconds after completing one backup cycle before starting the next cycle.
Summary
•	This configuration file tells the backup script:
o	Not to run the backup process ("run_enabled": "N").
o	Where to find the files to back up ("source_dirs").
o	Where to store the backed-up files ("dest_dirs").
o	Which file to use for logging ("log_file").
o	Which file to use for error logging ("error_log_file").
o	How long to wait between backup cycles ("sleep_time": 30 seconds).

