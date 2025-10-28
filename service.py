import os
from pathlib import Path
import getpass
import shutil
import sys

UNIT_TEMPLATE = """[Unit]
Description=Course Project Log Rotation Service
After=network.target

[Service]
Type=simple
User={user}
Group={group}
ExecStart={python} {entry} --service --config-file {config}
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

def generate_systemd_unit(service_name="course-log-rotation.service", user=None, group=None, entry="/usr/local/bin/course_log_rotation", config="/etc/course_project/log.cfg"):
    if user is None:
        user = getpass.getuser()
    if group is None:
        group = user
    python = shutil.which("python3") or "/usr/bin/python3"
    unit = UNIT_TEMPLATE.format(user=user, group=group, python=python, entry=entry, config=config)
    return unit

def install_systemd_unit(service_name, cfg, main_entry: Path):
    unit_text = generate_systemd_unit(service_name, user=cfg.get("run_user", None), group=cfg.get("run_group", None),
                                      entry=str(main_entry), config=str(Path(cfg.get("config_file", "log.cfg")).absolute()))
    unit_path = Path("/etc/systemd/system") / service_name
    if os.geteuid() != 0:
        print("You are not root. To install, run the following as root:\n")
        print("--- UNIT START ---")
        print(unit_text)
        print("--- UNIT END ---\n")
        print(f"Then run:")
        print(f"  sudo mv /path/to/unit /etc/systemd/system/{service_name}")
        print("  sudo systemctl daemon-reload")
        print(f"  sudo systemctl enable {service_name}")
        print(f"  sudo systemctl start {service_name}")
        return
    with open(unit_path, "w") as fh:
        fh.write(unit_text)
    print(f"Wrote systemd unit to {unit_path}")
    os.system("systemctl daemon-reload")
    os.system(f"systemctl enable {service_name}")
    os.system(f"systemctl start {service_name}")
    print("Service installed and started.")

def daemonize_for_dev():
    pid = os.fork()
    if pid > 0:
        print(f"Daemon started with pid {pid}")
        sys.exit(0)
    os.setsid()
    os.stdout.flush()
    os.stderr.flush()
    with open("/dev/null", "rb", 0) as f:
        os.dup2(f.fileno(), 0)
    with open("/dev/null", "ab", 0) as f:
        os.dup2(f.fileno(), 1)
        os.dup2(f.fileno(), 2)
