import argparse
import sys
import traceback
from pathlib import Path

try:
    import config as config_module
except ImportError:
    config_module = None

try:
    import permissions as permissions_module
except ImportError:
    permissions_module = None

try:
    import logger_setup as logger_setup_module
except ImportError:
    logger_setup_module = None

try:
    import scheduler as scheduler_module
except ImportError:
    scheduler_module = None

VERSION = "0.1.0"

def show_help():
    help_text = f"""
USAGE: python3 main.py [OPTIONS]

DESCRIPTION
  Minimal log rotation service for CIS 341 project. This program zips .log
  files in a configured folder every N days and keeps retention policies.

EXAMPLES
  Run once:
    python3 main.py --once --config-file log.cfg
  Install service:
    python3 main.py --install-service --service-name course-log-rotation

OPTIONS
  --once                 Run rotation once and exit
  --service              Run as a long-running service
  --install-service      Generate and install service unit
  --service-name NAME    Systemd service name (default: course-log-rotation.service)
  --config-file PATH     Path to configuration file (default: ./log.cfg)
  --override KEY=VALUE   Override config value (repeatable)
  --version              Print version and exit
  -h, --help             Print this help and exit

EXIT CODES
  0 success
  1 general error
  2 configuration error
  3 permission error
  4 runtime error
"""
    print(help_text)

def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--service", action="store_true")
    parser.add_argument("--install-service", action="store_true")
    parser.add_argument("--service-name", default="course-log-rotation.service")
    parser.add_argument("--config-file", default="log.cfg")
    parser.add_argument("--override", action="append", default=[])
    parser.add_argument("--version", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    return parser.parse_args()

def apply_overrides(config_dict, overrides_list):
    for item in overrides_list:
        if "=" not in item:
            continue
        key, val = item.split("=", 1)
        config_dict[key.strip()] = val.strip()

def get_config(config_path, override_list):
    if config_module and hasattr(config_module, "load_config"):
        try:
            config_dict = config_module.load_config(config_path)
        except Exception:
            sys.exit(2)
    else:
        config_dict = {
            "log_directory": "./log",
            "max_folder_size_mb": "100",
            "zip_schedule_days": "2",
            "zip_retention_days": "14",
            "log_file": "./app.log",
        }
    apply_overrides(config_dict, override_list)
    return config_dict

def run_program():
    show_help()
    arguments = get_args()
    
    if arguments.help:
        sys.exit(0)
    
    if arguments.version:
        print(f"course-log-rotation version {VERSION}")
        sys.exit(0)
    
    try:
        configuration = get_config(arguments.config_file, arguments.override)
    except SystemExit:
        raise
    
    if permissions_module and hasattr(permissions_module, "ensure_allowed_user"):
        try:
            permissions_module.ensure_allowed_user()
        except PermissionError:
            sys.exit(3)
    
    if logger_setup_module and hasattr(logger_setup_module, "init"):
        logger_setup_module.init(configuration.get("log_file", "./app.log"))
    
    if arguments.install_service:
        try:
            import service as service_module
        except ImportError:
            service_module = None
        
        if service_module and hasattr(service_module, "install_systemd_unit"):
            service_module.install_systemd_unit(arguments.service_name, configuration, main_entry=Path(__file__).absolute())
            sys.exit(0)
        else:
            sys.exit(1)
    
    try:
        if arguments.once:
            if scheduler_module and hasattr(scheduler_module, "run_once"):
                scheduler_module.run_once(configuration)
            else:
                print("scheduler not implemented")
        elif arguments.service:
            if scheduler_module and hasattr(scheduler_module, "run_service_loop"):
                scheduler_module.run_service_loop(configuration)
            else:
                print("scheduler not implemented")
        else:
            if scheduler_module and hasattr(scheduler_module, "run_once"):
                scheduler_module.run_once(configuration)
            else:
                print("no mode selected")
                sys.exit(1)
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        sys.exit(4)
    
    sys.exit(0)

if __name__ == "__main__":
    run_program()