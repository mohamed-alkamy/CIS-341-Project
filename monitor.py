import os
import glob
from datetime import datetime

"""
This module keeps track of the log folder used by the project.
It checks how much space the folder is taking up and gives a warning
if it goes over a certain limit. It also looks at any zipped log files
and reports how many there are and which one is the largest. The goal
is to make sure logs are managed properly and don’t fill up the system.
"""

class LogMonitor:
    
    
    def __init__(self, log_directory, size_threshold_mb):
        
        self.log_directory = log_directory
        self.size_threshold_bytes = int(size_threshold_mb) * 1024 * 1024 
        self.logger = None
        
        try:
            from logger_setup import get_logger
            self.logger = get_logger()
        except Exception:
            pass
    
    def _log_info(self, message):
        if self.logger:
            self.logger.info(message)
        else:
            print(f"INFO: {message}")
    
    def _log_warning(self, message):
        if self.logger:
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")
    
    def _log_error(self, message):
        if self.logger:
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")
    
    def calculate_directory_size(self):
        total_size_bytes = 0
        try:
            if not os.path.exists(self.log_directory):
                self._log_warning(f"Log directory does not exist: {self.log_directory}")
                return 0
            
            for dir_path, dir_names, file_names in os.walk(self.log_directory):
                for file_name in file_names:
                    file_path = os.path.join(dir_path, file_name)
                    if os.path.exists(file_path):
                        total_size_bytes += os.path.getsize(file_path)
            
            return total_size_bytes
        
        except Exception as e:
            self._log_error(f"Error calculating directory size: {e}")
            return 0
    
    def check_size_threshold(self):
        try:
            total_size_bytes = self.calculate_directory_size()
            size_mb = total_size_bytes / (1024 * 1024)
            threshold_mb = self.size_threshold_bytes / (1024 * 1024)
            
            self._log_info(f"Current directory size: {size_mb:.2f} MB")
            
            if total_size_bytes >= self.size_threshold_bytes:
                self._log_warning(
                    f"Directory size threshold exceeded! "
                    f"Current: {size_mb:.2f} MB, Threshold: {threshold_mb:.2f} MB"
                )
                return True
            
            return False
        
        except Exception as e:
            self._log_error(f"Error checking size threshold: {e}")
            return False
    
    def get_zip_files_info(self):
        try:
            zip_pattern = os.path.join(self.log_directory, '*.zip')
            zip_files_list = glob.glob(zip_pattern)
            
            if not zip_files_list:
                self._log_info("No zipped files found")
                return {
                    'total_count': 0,
                    'largest_file_name': None,
                    'largest_file_size': 0,
                    'largest_file_timestamp': None
                }
            
            largest_file_name = None
            largest_file_size = 0
            largest_file_timestamp = None
            
            for zip_file_path in zip_files_list:
                file_size = os.path.getsize(zip_file_path)
                if file_size > largest_file_size:
                    largest_file_size = file_size
                    largest_file_name = os.path.basename(zip_file_path)
                    largest_file_timestamp = datetime.fromtimestamp(
                        os.path.getctime(zip_file_path)
                    ).strftime('%Y-%m-%d %H:%M:%S')
            
            return {
                'total_count': len(zip_files_list),
                'largest_file_name': largest_file_name,
                'largest_file_size': largest_file_size,
                'largest_file_timestamp': largest_file_timestamp
            }
        
        except Exception as e:
            self._log_error(f"Error getting zipped files info: {e}")
            return {
                'total_count': 0,
                'largest_file_name': None,
                'largest_file_size': 0,
                'largest_file_timestamp': None
            }
    
    def log_zip_statistics(self):
        
        try:
            info = self.get_zip_files_info()
            
            self._log_info(f"Total zipped files: {info['total_count']}")
            
            if info['largest_file_name']:
                size_mb = info['largest_file_size'] / (1024 * 1024)
                self._log_info(
                    f"Largest zipped file: {info['largest_file_name']} "
                    f"(Size: {size_mb:.2f} MB, Created: {info['largest_file_timestamp']})"
                )
            else:
                self._log_info("No zipped files to report")
        
        except Exception as e:
            self._log_error(f"Error logging zipped files stats: {e}")
    
    def run_monitoring_checks(self):
        self._log_info("Starting monitoring check...")
        self.check_size_threshold()
        self.log_zip_statistics()
        self._log_info("Monitoring check completed")


def create_monitor(log_directory, size_threshold_mb):
    return LogMonitor(log_directory, size_threshold_mb)
