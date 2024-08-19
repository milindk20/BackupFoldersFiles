from datetime import datetime
import gzip
import os
from threading import Thread
import time
import shutil
import hashlib
import logging
import json

def calculate_checksum(file_path):
    """Calculate MD5 checksum of a file."""
    try:
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating checksum for {file_path}: {e}")
        raise

def get_permissions(file_path):
    """Get file permissions."""
    try:
        return oct(os.stat(file_path).st_mode)[-3:]
    except Exception as e:
        logging.error(f"Error getting permissions for {file_path}: {e}")
        raise

def is_file_changed(src_file, dest_file):
    """Check if the file has changed by comparing checksum and modification time."""
    try:
        if not os.path.exists(dest_file):
            return True
        
        src_checksum = calculate_checksum(src_file)
        dest_checksum = calculate_checksum(dest_file)
        
        return src_checksum != dest_checksum
    except Exception as e:
        logging.error(f"Error comparing files {src_file} and {dest_file}: {e}")
        return False

def backup_files(src_dir, dest_dir):
    """Backup files from src_dir to dest_dir with logging, excluding '.stfolder'."""
    try:
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
                    try:
                        checksum = calculate_checksum(src_file)
                        permissions = get_permissions(src_file)
                        
                        shutil.copy2(src_file, dest_file)
                        logging.info(f"Backed up file: {src_file} -> {dest_file} | Checksum: {checksum} | Permissions: {permissions}")
                    except Exception as e:
                        error_message = f"Failed to back up file: {src_file} -> {dest_file} | Error: {e}"
                        logging.error(error_message)
                        with open(ERROR_LOG_FILE, 'a') as error_log:
                            error_log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {error_message}\n")
                else:
                    logging.info(f"File unchanged, skipping backup: {src_file}")
    except Exception as e:
        logging.error(f"Error during backup process from {src_dir} to {dest_dir}: {e}")
        raise

import os
import gzip
from datetime import datetime, timedelta

def mtime(filepath):
    return os.path.getmtime(filepath)

def rotate_logs():
    log_file = config.get('log_file', 'backup.log')
    error_log_file = config.get('error_log_file', 'error.log')
    one_day_ago = datetime.now().timestamp() - 86400  # 86400 seconds = 1 day

    # Check if log_file exists and is older than one day
    if os.path.exists(log_file):
        if mtime(log_file) < one_day_ago:
            new_log_file = f"{log_file}.{datetime.now().strftime('%Y-%m-%d')}.log.gz"
            with open(log_file, 'rb') as f_in:
                with gzip.open(new_log_file, 'wb') as f_out:
                    f_out.writelines(f_in)
            open(log_file, 'w').close()  # Clear the old log file
    
    # Check if error_log_file exists and is older than one day
    if os.path.exists(error_log_file):
        if mtime(error_log_file) < one_day_ago:
            new_error_log_file = f"{error_log_file}.{datetime.now().strftime('%Y-%m-%d')}.log.gz"
            with open(error_log_file, 'rb') as f_in:
                with gzip.open(new_error_log_file, 'wb') as f_out:
                    f_out.writelines(f_in)
            open(error_log_file, 'w').close()  # Clear the old log file



def move_gzipped_logs():
    log_dir = config.get('log_dirs', '')
    if not log_dir[0]:
        logging.error("No log directories specified.")
        return
    if not os.path.exists(log_dir[0]):
        logging.error(f"Log directory {log_dir[0]} does not exist.")
        return
    
    # Move .log.gz files to the log directory
    for file in os.listdir('.'):
        if file.endswith('.log.gz'):
            try:
                shutil.move(file, os.path.join(log_dir[0], file))
            except Exception as e:
                logging.error(f"Failed to move {file}: {e}")


if __name__ == "__main__":
    while True:
        # print(os.getcwd())
        try:
            # Load configuration from file
            with open('backup_config.json', 'r') as config_file:
                config = json.load(config_file)

            # Configuration
            SOURCE_DIRS = config['source_dirs']
            DEST_DIRS = config['dest_dirs']
            LOG_FILE = config['log_file']
            ERROR_LOG_FILE = config['error_log_file']
            SLEEP_TIME = config['sleep_time']
            RUN_ENABLED = config['run_enabled']  # Y = will run, anything else no run

            # Logging configuration
            logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')
            
            ## Threads =================================================

            # Start auto-refresh thread
            rotate_logs_auto_thread = Thread(target=rotate_logs, daemon=True)
            rotate_logs_auto_thread.start()
            Gzip_logs_auto_thread = Thread(target=move_gzipped_logs, daemon=True)
            Gzip_logs_auto_thread.start()

            if RUN_ENABLED == "Y":
                for src_dir, dest_dir in zip(SOURCE_DIRS, DEST_DIRS):
                    backup_files(src_dir, dest_dir)
            else:
                logging.info(f"Run Disabled, Exiting Process: {__name__}")

            time.sleep(SLEEP_TIME)

        except json.JSONDecodeError as e:
            logging.error(f"Error loading configuration: {e}")
        except FileNotFoundError as e:
            logging.error(f"Configuration file not found: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
