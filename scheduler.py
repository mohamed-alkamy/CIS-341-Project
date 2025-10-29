# scheduler.py
import time
import threading
from datetime import datetime, timedelta

from config import load_config
from logger_setup import get_logger
from log_rotation import rotate_logs  # make sure log_rotation.py is in the same folder

# Initialize config and logger
cfg = load_config("log.cfg")
logger = get_logger()

def seconds_until_next_run(every_n_days=2, run_hour=0, run_minute=0):
    """
    Calculate seconds until next scheduled run at midnight every `every_n_days`.
    """
    now = datetime.now()
    today_run = now.replace(hour=run_hour, minute=run_minute, second=0, microsecond=0)
    if now < today_run:
        next_run = today_run
    else:
        next_run = today_run + timedelta(days=every_n_days)
    return max(0, (next_run - now).total_seconds())

def schedule_periodic(func, every_n_days=2):
    """
    Schedule a function to run every N days at midnight.
    """
    def _run_and_reschedule():
        try:
            logger.info("Starting scheduled log rotation job")
            func(cfg)
            logger.info("Log rotation job finished")
        except Exception as e:
            logger.error("Error in scheduled job: %s", e)
        finally:
            # Compute seconds until next run and reschedule
            s = seconds_until_next_run(every_n_days)
            logger.info("Next run scheduled in %.2f hours", s / 3600)
            threading.Timer(s, _run_and_reschedule).start()
    
    # Schedule first run
    initial_delay = seconds_until_next_run(every_n_days)
    logger.info("First run scheduled in %.2f hours", initial_delay / 3600)
    threading.Timer(initial_delay, _run_and_reschedule).start()

if __name__ == "__main__":
    # Schedule the log rotation
    schedule_periodic(rotate_logs, every_n_days=int(cfg.get("zip_schedule_days", 2)))

    # Keep the main thread alive
    try:
        while True:
            time.sleep(3600)  # Sleep in 1-hour increments
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
