import os
import time
from pathlib import Path
from monitor import LogMonitor

class DummyLogger:
    def __init__(self):
        self.info = []
        self.warning = []
        self.error = []
    def info(self, msg): self.info.append(msg)
    def warning(self, msg): self.warning.append(msg)
    def error(self, msg): self.error.append(msg)

def test_calculate_directory_size(tmp_path, monkeypatch):
    (tmp_path / "a.log").write_text("12345")
    m = LogMonitor(str(tmp_path), 1)
    m.logger = DummyLogger()
    size = m.calculate_directory_size()
    assert size > 0

def test_check_size_threshold_over(tmp_path, monkeypatch):
    big_file = tmp_path / "b.log"
    big_file.write_bytes(b"x" * (1024 * 1024 * 2))  # 2MB
    m = LogMonitor(str(tmp_path), 1)
    m.logger = DummyLogger()
    assert m.check_size_threshold() is True

def test_get_zip_files_info(tmp_path):
    z1 = tmp_path / "a.zip"
    z1.write_text("fakezip")
    m = LogMonitor(str(tmp_path), 1)
    info = m.get_zip_files_info()
    assert info["total_count"] == 1
    assert info["largest_file_name"].endswith(".zip")

def test_run_monitoring_checks(tmp_path):
    (tmp_path / "small.log").write_text("data")
    m = LogMonitor(str(tmp_path), 1)
    m.logger = DummyLogger()
    m.run_monitoring_checks()
    assert any("Starting" in msg for msg in m.logger.info)
