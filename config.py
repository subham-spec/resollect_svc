from dataclasses import dataclass

@dataclass(frozen=True)
class LogConfig:
    LOGGER_NAME: str = "resollect_application"
    LOG_FORMAT: str = "[%(asctime)s] [%(levelname)s] [%(filename)s] [%(funcName)s:%(lineno)s] [%(id_)s]: %(message)s"
    LOG_MAX_BYTES: str = 10**6
    LOG_BACKUP_COUNT: str = 1
    LOG_INFO_FILE_PATH: str = "resollect_application_info.log"
    LOG_ERROR_FILE_PATH: str = "resollect_application_error.log"
