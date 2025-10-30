from pathlib import Path
from datetime import datetime, timedelta
import zipfile
import time
from log_rotation import rotate_logs

class DummyLogger:
    def __init__(self):
        self.info_msgs = []
        self.error_msgs = []
        self.warning_msgs = []
    def info(self, msg, *args): self.info_msgs.append(msg % args if args else msg)
    def error(self, msg, *args): self.error_msgs.append(msg % args if args else msg)
    def warning(self, msg, *args): self.warning_msgs.append(msg % args if args else msg)

def make_old_file(path):
    path.write_text("data")
    old_time = time.time() - 86400 * 5
    os.utime(path, (old_time, old_time))

def test_rotate_logs_creates_zip(tmp_path, monkeypatch):
    log_dir = tmp_path
    f1 = log_dir / "app.log"
    make_old_file(f1)

    dummy = DummyLogger()
    monkeypatch.setattr("log_rotation.logger", dummy)

    cfg = {"log_directory": str(log_dir), "zip_schedule_days": "2", "zip_retention_days": "14"}
    rotate_logs(cfg, dry_run=False)

    zip_files = list(log_dir.glob("*.zip"))
    assert zip_files, "Expected a zip file to be created"
    assert any("Zipped" in msg for msg in dummy.info_msgs)


def test_rotate_logs_dry_run(tmp_path, monkeypatch):
    log_dir = tmp_path
    f1 = log_dir / "old.log"
    make_old_file(f1)

    dummy = DummyLogger()
    monkeypatch.setattr("log_rotation.logger", dummy)

    cfg = {"log_directory": str(log_dir), "zip_schedule_days": "2", "zip_retention_days": "14"}
    rotate_logs(cfg, dry_run=True)

    # Dry run: no zip file should be created
    assert not list(log_dir.glob("*.zip"))
    assert any("DRY RUN" in msg for msg in dummy.info_msgs)
