# test_permissions.py
import os
import pytest
import permissions


def test_get_current_user_returns_string():
    user = permissions.get_current_user()
    assert isinstance(user, str)
    assert len(user) > 0


def test_ensure_allowed_user_passes(monkeypatch):
    monkeypatch.setattr(permissions, "get_current_user", lambda: "logmanager")
    monkeypatch.setenv("LOG_ALLOWED_USER", "logmanager")
    permissions.ensure_allowed_user()  # Should not raise


def test_ensure_allowed_user_raises(monkeypatch):
    monkeypatch.setattr(permissions, "get_current_user", lambda: "someone_else")
    monkeypatch.setenv("LOG_ALLOWED_USER", "logmanager")
    with pytest.raises(PermissionError):
        permissions.ensure_allowed_user()


def test_delegate_ownership_success(monkeypatch):
    monkeypatch.setattr(permissions, "get_current_user", lambda: "logmanager")
    monkeypatch.setenv("LOG_ALLOWED_USER", "logmanager")
    new_user = permissions.delegate_ownership("tester")
    assert new_user == "tester"
    assert os.environ.get("LOG_ALLOWED_USER") == "tester"


def test_delegate_ownership_fail(monkeypatch):
    monkeypatch.setattr(permissions, "get_current_user", lambda: "unauthorized")
    monkeypatch.setenv("LOG_ALLOWED_USER", "logmanager")
    with pytest.raises(PermissionError):
        permissions.delegate_ownership("tester")
