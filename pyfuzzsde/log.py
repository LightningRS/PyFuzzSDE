#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/log.py
# @Time:    2021/04/13 15:00:00
# @Version: 0.0.1
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE log module
# @Changelog:
#    2021/04/13: Create project

import logging
import logging.config
import sys


class SDELogger:
    is_debug = False
    logging_config = {
        'version': 1.0,
        'formatters': {
            'generic': {
                'format': '%(asctime)s [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s',
                'datefmt': '[%Y-%m-%d %H:%M:%S]',
                'class': 'logging.Formatter',
            },
            'debug': {
                'format': '%(asctime)s [%(pathname)s:%(lineno)d] [%(funcName)s] [%(levelname)s] %(message)s',
                'datefmt': '[%Y-%m-%d %H:%M:%S]',
                'class': 'logging.Formatter',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'generic',
                'stream': sys.stdout,
            },
        },
        'loggers': {
            'PyFuzzSDE.root': {
                'handlers': ['console'],
                'level': 'INFO',
            },
        },
    }

    @staticmethod
    def init():
        logging.config.dictConfig(SDELogger.logging_config)

    @staticmethod
    def enable_debug():
        SDELogger.is_debug = True
        SDELogger.logging_config['handlers']['console']['formatter'] = 'debug'
        SDELogger.logging_config['loggers']['PyFuzzSDE.root']['level'] = 'DEBUG'
        SDELogger.init()

    @staticmethod
    def enable_log_file(file_path: str):
        SDELogger.logging_config['handlers']['file'] = {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'debug' if SDELogger.is_debug else 'generic',
            'encoding': 'utf-8',
            'filename': file_path,
            'interval': 1,
            'backupCount': 30,
            'when': 'D',
        }
        SDELogger.logging_config['loggers']['PyFuzzSDE.root']['handlers'].append('file')
        SDELogger.init()


SDELogger.init()
logger = logging.getLogger('PyFuzzSDE.root')
