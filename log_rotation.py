import zipfile
from pathlib import Path
from datetime import datetime, timedelta
import os
from logger_setup import get_logger

logger = get_logger()

def rotate_logs(cfg, dry_run=False):
   
    log_dir = Path(cfg.get("log_directory", "./log")).resolve()
    zip_age_days = int(cfg.get("zip_schedule_days", 2))
    retention_days = int(cfg.get("zip_retention_days", 14))

    if not log_dir.exists():
        logger.warning("Log directory %s does not exist", log_dir)
        return

    now = datetime.now()
    zip_before = now - timedelta(days=zip_age_days)
    retention_cutoff = now - timedelta(days=retention_days)

    to_zip = [f for f in log_dir.glob("*.log") if datetime.fromtimestamp(f.stat().st_mtime) < zip_before]

    if not to_zip:
        logger.info("No log files older than %d days to rotate", zip_age_days)
    else:
        zip_name = log_dir / f"logs_{now.strftime('%Y%m%d_%H%M%S')}.zip"
        if dry_run:
            logger.info("[DRY RUN] Would create zip: %s containing %d files", zip_name, len(to_zip))
        else:
            with zipfile.ZipFile(zip_name, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for f in to_zip:
                    try:
                        zf.write(f, arcname=f.name)
                    except Exception as e:
                        logger.error("Failed to add %s to zip: %s", f, e)

            for f in to_zip:
                try:
                    f.unlink()
                except Exception as e:
                    logger.error("Failed to delete original log file %s: %s", f, e)

            logger.info("Zipped %d log files into %s", len(to_zip), zip_name)
            largest_zip = max(log_dir.glob("*.zip"), key=lambda z: z.stat().st_size, default=None)
            if largest_zip:
                logger.info("Largest zip file: %s (%.2f KB)", largest_zip.name, largest_zip.stat().st_size / 1024)

    deleted_count = 0
    for z in log_dir.glob("*.zip"):
        if datetime.fromtimestamp(z.stat().st_mtime) < retention_cutoff:
            try:
                z.unlink()
                deleted_count += 1
            except Exception as e:
                logger.error("Failed to delete old zip file %s: %s", z, e)

    if deleted_count > 0:
        logger.info("Deleted %d zip files older than %d days", deleted_count, retention_days)
