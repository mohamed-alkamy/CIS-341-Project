
import os
import pwd
import grp
from logger_setup import get_logger



logger = get_logger()


def get_current_user():
    try:
        return pwd.getpwuid(os.getuid()).pw_name
    except Exception:
        return os.environ.get("USER", "unknown")


def get_allowed_user():
    return os.environ.get("LOG_ALLOWED_USER", "logmanager")


def ensure_allowed_user():
    
    current_user = get_current_user()
    allowed_user = get_allowed_user()

    if current_user != allowed_user:
        logger.error(
            f"Permission denied: current user '{current_user}' "
            f"is not allowed to run this service (expected '{allowed_user}')"
        )
        raise PermissionError(f"Only '{allowed_user}' is allowed to run this service.")
    else:
        logger.info(f"permission check passed for user '{current_user}'.")


def delegate_ownership(new_user: str):
   
    current_user = get_current_user()
    allowed_user = get_allowed_user()

    if current_user != allowed_user:
        logger.error(
            f"Only '{allowed_user}' can assign ownership, "
            f"but '{current_user}' tried."
        )
        raise PermissionError("only the current owner can assign ownership.")

    os.environ["LOG_ALLOWED_USER"] = new_user
    logger.info(f"ownership assigned to '{new_user}'.")
    return new_user
