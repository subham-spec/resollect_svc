import logging

from logging.handlers import RotatingFileHandler
from flask import has_request_context, request
from config import LogConfig

log_config = LogConfig()

class AppLogFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            if request.is_json and "requestId" in request.get_json():
                record.id_ = request.get_json()["requestId"]
            else:
                record.id_ = "<N/A>"
        else:
            record.id_ = "<N/A>"
        return super().format(record)


def setup_logger():
    """
        Configure the logger
    """
    logger = logging.getLogger(log_config.LOGGER_NAME)
    # the level should be the lowest level set in handlers
    logger.setLevel(logging.INFO)

    log_format = AppLogFormatter(log_config.LOG_FORMAT)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_format)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    info_handler = RotatingFileHandler(
        log_config.LOG_INFO_FILE_PATH,
        maxBytes=log_config.LOG_MAX_BYTES,
        backupCount=log_config.LOG_BACKUP_COUNT,
    )
    info_handler.setFormatter(log_format)
    info_handler.setLevel(logging.INFO)
    logger.addHandler(info_handler)

    error_handler = RotatingFileHandler(
        log_config.LOG_ERROR_FILE_PATH,
        maxBytes=log_config.LOG_MAX_BYTES,
        backupCount=log_config.LOG_BACKUP_COUNT,
    )
    error_handler.setFormatter(log_format)
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)


logger = logging.getLogger(log_config.LOGGER_NAME)
