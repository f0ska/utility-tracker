import logging
import sys
import threading
import warnings
from logging.handlers import RotatingFileHandler

from paths import log_path


APP_LOGGER_NAME = "utilitytracker"
_STATUS_HANDLER = None


class LogStatusHandler(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.warning_count = 0
        self.error_count = 0
        self.last_level = None
        self.last_message = None
        self.seen_count = 0

    def emit(self, record):
        self.warning_count += 1
        if record.levelno >= logging.ERROR:
            self.error_count += 1
        self.last_level = record.levelname
        self.last_message = record.getMessage()

    def get_status(self):
        return {
            "warning_count": self.warning_count,
            "error_count": self.error_count,
            "unseen_count": self.warning_count - self.seen_count,
            "last_level": self.last_level,
            "last_message": self.last_message,
            "log_path": get_log_path(),
        }

    def mark_seen(self):
        self.seen_count = self.warning_count


def get_log_path():
    return log_path()


def setup_logging():
    global _STATUS_HANDLER
    log_path = get_log_path()
    logger = logging.getLogger(APP_LOGGER_NAME)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    _STATUS_HANDLER = LogStatusHandler()
    logger.addHandler(_STATUS_HANDLER)

    logging.captureWarnings(True)
    warnings.simplefilter("default", DeprecationWarning)
    logging.getLogger("py.warnings").handlers = logger.handlers
    logging.getLogger("py.warnings").setLevel(logging.WARNING)
    logging.getLogger("py.warnings").propagate = False

    def log_unhandled_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    sys.excepthook = log_unhandled_exception

    def log_thread_exception(args):
        logger.critical(
            "Unhandled thread exception",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    threading.excepthook = log_thread_exception

    logger.info("Logging initialized: %s", log_path)
    return logger


def get_log_status():
    if _STATUS_HANDLER is None:
        return {
            "warning_count": 0,
            "error_count": 0,
            "unseen_count": 0,
            "last_level": None,
            "last_message": None,
            "log_path": get_log_path(),
        }
    return _STATUS_HANDLER.get_status()


def mark_logs_seen():
    if _STATUS_HANDLER is not None:
        _STATUS_HANDLER.mark_seen()
