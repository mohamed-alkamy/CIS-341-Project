# permissions.py
import os
import pwd
import grp
from logger_setup import get_logger

"""
this module make sure that the log rotation service
runs only under an authorized user account. by default,
it should be executed by 'logmanager', but ownership
can be assigned to another user through configuration
or command-line parameters.
"""

logger = get_logger()


def get_current_user():
    """return the username of the user running the program."""
    try:
        return pwd.getpwuid(os.getuid()).pw_name
    except Exception:
        return os.environ.get("USER", "unknown")


def get_allowed_user():
    """read the allowed username from config or environment."""
    return os.environ.get("LOG_ALLOWED_USER", "logmanager")


def ensure_allowed_user():
    """
    check that the current user is allowed to run this service or not.
    raise PermissionError if not.
    """
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
    """
    allow logmanager to assign ownership to another user.
    This updates an environment variable (for simplicity).
    """
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
