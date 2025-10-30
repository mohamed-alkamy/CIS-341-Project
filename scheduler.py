
import time
import threading
from datetime import datetime, timedelta

from config import load_config
from logger_setup import get_logger
from log_rotation import rotate_logs  

logger = get_logger()

def seconds_until_next_run(every_n_days=2, run_hour=0, run_minute=0):
   
    now = datetime.now()
    today_run = now.replace(hour=run_hour, minute=run_minute, second=0, microsecond=0)
    if now < today_run:
        next_run = today_run
    else:
        next_run = today_run + timedelta(days=every_n_days)
    return max(0, (next_run - now).total_seconds())

def schedule_periodic(func, every_n_days=2):

    def _run_and_reschedule():
        try:
            logger.info("Starting scheduled log rotation job")
            func(load_config("log.cfg"))
            logger.info("Log rotation job finished")
        except Exception as e:
            logger.error("Error in scheduled job: %s", e)
        finally:
            s = seconds_until_next_run(every_n_days)
            logger.info("Next run scheduled in %.2f hours", s / 3600)
            threading.Timer(s, _run_and_reschedule).start()
    
    initial_delay = seconds_until_next_run(every_n_days)
    logger.info("First run scheduled in %.2f hours", initial_delay / 3600)
    threading.Timer(initial_delay, _run_and_reschedule).start()


def run_once(configuration: dict):

    try:
        logger.info("Running single log rotation")
        rotate_logs(configuration)
        logger.info("Single run completed")
    except Exception as exc:
        logger.error("Error during single run: %s", exc)


def run_service_loop(configuration: dict):
    every = int(configuration.get("zip_schedule_days", 2))
    schedule_periodic(rotate_logs, every_n_days=every)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        logger.info("Service loop interrupted by user")

if __name__ == "__main__":
    cfg = load_config("log.cfg")
    run_service_loop(cfg)
