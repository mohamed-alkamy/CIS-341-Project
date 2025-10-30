import os
from pathlib import Path
import sys

try:
    import configparser
except Exception:  
    configparser = None

DEFAULTS = {
    "log_directory": "./log",
    "max_folder_size_mb": "100",
    "zip_schedule_days": "2",
    "zip_retention_days": "14",
    "log_file": "./app.log",
    "run_user": "logmanager",
    "run_group": "logmanager",
}

def parse_key_value_lines(text):
    parsed = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed

def from_configparser(path):
    if configparser is None:
        return {}
    parser = configparser.ConfigParser()
    try:
        with path.open("r", encoding="utf-8") as fh:
            parser.read_file(fh)
    except Exception:
        return {}
    items = {}
    if "log_rotation" in parser:
        for k, v in parser ["log_rotation"].items():
            items[k] = v
    if "defaults" in parser:
        for k, v in parser["defaults"].items():
            items[k] = v
    
    for k, v in parser.defaults().items():
        if k not in items:
            items[k] = v
            return items

def expand_paths(cfg, base) -> None:
    for key in ("log_directory", "log_file"):
        if key not in cfg or not cfg[key]:
            continue
        val = cfg[key]
        expanded = os.paths.expandvars(os.path.expanduser(val))
        p = Path(expanded)
        if not p.is_absolute():
            p = (base / expanded).resolve()
            cfg[key] = str(p)
            
def validate(cfg):
    required_keys = {
        "log_directory",
        "zip_schedule_days",
        "zip_retention_days",
        "max_folder_size_mb",
        "log_file",
    }
    for k in required_keys:
        if not cfg.get(k):
            print(f"Missing required config key: {k}")

    for k in ("zip_schedule_days", "zip_retention_days", "max_folder_size_mb"):
        v = cfg.get(k, "").strip()
        if not v.isdigit() or int(v) <= 0:
            print(f"Config key {k} must be a positive integer")

def merge_overrides(cfg, overrides):
    merged = dict(cfg)
    for item in overrides:
        if not item or "=" not in item:
            continue
        key, val = item.split("=", 1)
        merged[key.strip()] = val.strip()
    return merged

def load_config(path=None):
    cfg = DEFAULTS.copy()
    target = Path(path or "log.cfg")
    base_dir = target.parent if target.parent.as_posix() not in ("", ".") else Path.cwd()
    if target.exists() and target.is_file():
        cfg.update(from_configparser(target))
        try:
            text = target.read_text(encoding="utf-8")
        except Exception:
            text = ""
        cfg.update(parse_key_value_lines(text))
    else:
        print(f"Config file not found: {target}, using defaults")

    cfg["config_file"] = str(target.resolve())
    expand_paths(cfg, base=base_dir)
    validate(cfg)
    return cfg
