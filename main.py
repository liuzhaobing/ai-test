# -*- coding:utf-8 -*-
import os.path
import logging.config

BASE_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(BASE_DIR, "runtime", "logs")
DATA_DIR = os.path.join(BASE_DIR, "dataset")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "class": "logging.Formatter",
            "format": "[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d]%(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "smartest": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": os.path.join(LOG_DIR, "smartest-test.log"),
            "backupCount": 15,
            "encoding": "utf8",
            "when": "midnight",
        }
    },
    "loggers": {
        "root": {
            "handlers": ["console", "smartest"],
            "level": "INFO"
        }
    }
}
logging.config.dictConfig(LOGGING)

if __name__ == '__main__':
    logging.info(LOG_DIR)
