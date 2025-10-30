import builtins
from datetime import datetime, timedelta
import scheduler

def test_seconds_until_next_run_future(monkeypatch):
    now = datetime(2025, 1, 1, 10, 0, 0)
    monkeypatch.setattr("scheduler.datetime", type("dt", (), {"now": lambda: now, "replace": datetime.replace}))
    result = scheduler.seconds_until_next_run(every_n_days=2)
    assert result > 0

def test_schedule_periodic_starts(monkeypatch):
    calls = []
    def dummy_func(cfg): calls.append("called")
    class DummyTimer:
        def __init__(self, delay, func): self.delay, self.func = delay, func
        def start(self): calls.append("timer_started")

    monkeypatch.setattr("scheduler.threading.Timer", DummyTimer)
    monkeypatch.setattr("scheduler.logger", type("L", (), {"info": lambda *a, **kw: None, "error": lambda *a, **kw: None})())

    scheduler.schedule_periodic(dummy_func, every_n_days=1)
    assert "timer_started" in calls
