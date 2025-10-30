import os
from pathlib import Path
import tempfile
import textwrap
from config import parse_key_value_lines, merge_overrides, load_config, DEFAULTS


def test_parse_key_value_lines_basic():
    text = """
    # comment
    log_directory=./logs
    zip_schedule_days=3
    """
    result = parse_key_value_lines(text)
    assert result["log_directory"] == "./logs"
    assert result["zip_schedule_days"] == "3"
    assert "#" not in "".join(result.keys())


def test_merge_overrides():
    base = {"a": "1", "b": "2"}
    overrides = ["b=99", "c=3"]
    merged = merge_overrides(base, overrides)
    assert merged["b"] == "99"
    assert merged["c"] == "3"


def test_load_config_file(tmp_path):
    cfg_file = tmp_path / "log.cfg"
    cfg_file.write_text("log_directory=./tmp_logs\nzip_schedule_days=5")

    cfg = load_config(str(cfg_file))
    assert "log_directory" in cfg
    assert cfg["zip_schedule_days"] == "5"


def test_load_config_file_not_found(tmp_path, capsys):
    cfg_file = tmp_path / "missing.cfg"
    cfg = load_config(str(cfg_file))
    captured = capsys.readouterr()
    assert "using defaults" in captured.out
    assert cfg["log_directory"] == DEFAULTS["log_directory"]
