# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Logging for Shot Manager
"""

import os
from pathlib import Path

import logging

from shotmanager.config import config


def getLogger(name):
    return logging.getLogger(name)


def getLevelName():
    return logging.getLevelName(_logger.level)


def setLevel(level_name):
    if "NOTSET" == level_name:
        _logger.setLevel(logging.NOTSET)
    elif "DEBUG" == level_name:
        _logger.setLevel(logging.DEBUG)
    elif "INFO" == level_name:
        _logger.setLevel(logging.INFO)
    elif "WARNING" == level_name:
        _logger.setLevel(logging.WARNING)
    elif "ERROR" == level_name:
        _logger.setLevel(logging.ERROR)
    elif "CRITICAL" == level_name:
        _logger.setLevel(logging.CRITICAL)


def set_logger_color(org_string, level=None):
    color_levels = {
        10: "\033[36m{}\033[0m",  # DEBUG
        20: "\033[32m{}\033[0m",  # INFO
        30: "\033[33m{}\033[0m",  # WARNING
        40: "\033[31m{}\033[0m",  # ERROR
        50: "\033[7;31;31m{}\033[0m",  # FATAL/CRITICAL/EXCEPTION
    }
    if level is None:
        return color_levels[20].format(org_string)
    else:
        return color_levels[int(level)].format(org_string)


# https://docs.python.org/fr/3/howto/logging.html
_logger = logging.getLogger(__name__)
_logger.propagate = False
MODULE_PATH = Path(__file__).parent.parent
logging.basicConfig(level=logging.INFO)
_logger.setLevel(logging.INFO)  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

# _logger.info(set_logger_color("test"))
# _logger.debug(set_logger_color("test", level=10))
# _logger.warning(set_logger_color("test", level=30))
# _logger.error(set_logger_color("test", level=40))
# _logger.fatal(set_logger_color("test", level=50))

# _logger.info(f"Logger {str(256) + 'my long very long text'}")
# _logger.info(f"Logger {str(256)}")
# _logger.warning(f"logger {256}")
# _logger.error(f"error {256}")
# _logger.debug(f"debug {256}")


###########
# Logging
###########


class Formatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord):
        """
        The role of this custom formatter is:
        - append filepath and lineno to logging format but shorten path to files, to make logs more clear
        - to append "./" at the begining to permit going to the line quickly with VS Code CTRL+click from terminal
        """
        s = super().format(record)
        pathname = Path(record.pathname).relative_to(MODULE_PATH)
        s += f"  [{os.curdir}{os.sep}{pathname}:{record.lineno}]"
        return s


# def get_logs_directory():
#     def _get_logs_directory():
#         import tempfile

#         if "MIXER_USER_LOGS_DIR" in os.environ:
#             username = os.getlogin()
#             base_shared_path = Path(os.environ["MIXER_USER_LOGS_DIR"])
#             if os.path.exists(base_shared_path):
#                 return os.path.join(os.fspath(base_shared_path), username)
#             logger.error(
#                 f"MIXER_USER_LOGS_DIR env var set to {base_shared_path}, but directory does not exists. Falling back to default location."
#             )
#         return os.path.join(os.fspath(tempfile.gettempdir()), "mixer")

#     dir = _get_logs_directory()
#     if not os.path.exists(dir):
#         os.makedirs(dir)
#     return dir


# def get_log_file():
#     from mixer.share_data import share_data

#     return os.path.join(get_logs_directory(), f"mixer_logs_{share_data.run_id}.log")


def initialize():
    if len(_logger.handlers) == 0:
        _logger.setLevel(logging.WARNING)
        formatter = None

        # call config.initGlobalVariables() to get the config variables (currently done in Shot Manager init)
        if config.devDebug_ignoreLoggerFormatting:
            ch = "~"  # "\u02EB"
            formatter = Formatter(ch + " {message:<140}", style="{")
        else:
            # formatter = Formatter("{asctime} {levelname[0]} {name:<30}  - {message:<80}", style="{")
            formatter = Formatter("SM " + " {message:<80}", style="{")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        _logger.addHandler(handler)

        # handler = logging.FileHandler(get_log_file())
        # handler.setFormatter(formatter)
        # _logger.addHandler(handler)
