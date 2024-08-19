import os
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

if __name__ == "__main__":
    while True:
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
