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

Read this: https://stackoverflow.com/questions/7274732/extending-the-python-logger

"""

import os
from pathlib import Path

import logging
from logging import DEBUG, INFO, ERROR

from ..config import config


def getLogger(name):
    return _logger


def getLevelName():
    return logging.getLevelName(_logger.level)


# cf https://stackoverflow.com/questions/7274732/extending-the-python-logger


class SM_Logger(logging.getLoggerClass()):
    def __init__(self, name):
        super(SM_Logger, self).__init__(name)

        self._prefix = "SM"
        self._defaultColor = "WHITE"
        self._defaultForm = "STD"

        # colors in terminal: https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
        # Eg:
        # _YELLOW = '\33[33m'
        # _ENDCOLOR = '\033[0m'
        # print(f"{_YELLOW}text{_ENDCOLOR}")

        self._colors = {
            "BLUE": "\33[34m",
            "BLUE_LIGHT": "\33[1;34m",
            "GREEN": "\33[32m",
            "GREEN_LIGHT": "\33[1;32m",
            "GRAY": "\33[1;30m",
            "YELLOW": "\33[33m",
            "YELLOW_LIGHT": "\33[1;33m",
            "ORANGE": "\33[1;31m",
            "RED": "\33[31m",
            "PURPLE": "\33[35m",
            "PURPULE_LIGHT": "\33[1;35m",
            "TURQUOISE": "\33[36m",
            "TURQUOISE_LIGHT": "\33[1;36m",
            "WHITE": "\33[37m",
        }

        # self._formatter_standard = Formatter("\33[36m" + "~Basic +++" + " {message:<140}" + "\033[0m", style="{")
        self._formatter_standard = Formatter(self._prefix + " - " + " {message:<110}", style="{")
        self._formatter_basic = Formatter("\33[36m" + "~Basic +++" + " {message:<140}" + "\033[0m", style="{")
        self._formatter_other = Formatter("\33[36m" + "S OTHER M+" + " {message:<140}" + "\033[0m", style="{")
        self._formatter = {
            "STD": self._formatter_standard,
            "BASIC": self._formatter_basic,
            "OTHER": self._formatter_other,
        }

        self.tags = config.getLoggingTags()

    def _getFormatter(self, col="", form="DEFAULT"):
        color = self._colors[col] if col != "" else ""

        if "STD" == form:
            f = Formatter(color + self._prefix + "  {message:<120}" + "\033[0m", style="{")
        elif "REG" == form:
            if "" == col:
                color = self._colors["YELLOW"]
            f = Formatter(color + "{message:<90}" + "\033[0m", style="{")
        elif "UNREG" == form:
            if "" == col:
                color = self._colors["GRAY"]
            f = Formatter(color + "{message:<90}" + "\033[0m", style="{")
        elif "DEPRECATED" == form:
            if "" == col:
                color = self._colors["ORANGE"]
            f = Formatter(color + "[DEPRECATED] {message:<90}" + "\033[0m", style="{")
        elif "ERROR" == form:
            f = Formatter(color + "Shot Manager: " + " {message:<140}" + "\033[0m", style="{")
        elif "OTHER" == form:
            f = Formatter(color + "~Other +++" + " {message:<140}" + "\033[0m", style="{")
        else:  # "DEFAULT"
            f = Formatter("\033[0m" + "~default +++" + " {message:<140}", style="{")
        return f

    # def debug_basic(self, msg, extra=None, color="GREEN", formatter="OTHER"):
    #     ch = logging.StreamHandler()
    #     ch.setLevel(logging.DEBUG)
    #     ### ch.setFormatter(self.formatter_basic)
    #     # _logger.handlers[0].setFormatter(self.formatter_basic)
    #     _logger.handlers[0].setFormatter(self._formatter[formatter])
    #     super(SM_Logger, self).debug((self._colors[color] + "{}\033[0m").format(msg), extra=extra)
    #     # ch.setFormatter(self.formatter_other)
    #     _logger.handlers[0].setFormatter(self._formatter["OTHER"])

    def debug_form(self, col="GREEN", form="DEFAULT"):
        """Set formatter. To use before call to debug()
        eg: _logger.debug_form(col="GREEN", form="STD")
            _logger.debug("debug test timer green")
        """
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        _logger.handlers[0].setFormatter(self._getFormatter(col, form))

    def _print_ext(self, mode, msg, extra=None, col="", form="STD", tag=None, display=True):
        """
        Args:
            mode: "DEBUG", "INFO", "ERROR"
        """
        if not display:
            return

        # accept or silence message display according to tags (if return is enabled then tag is ignored)
        if tag is not None:
            if tag in self.tags:
                if not self.tags[tag]:
                    return

        form = "DEPRECATED" if "DEPRECATED" == tag else form

        _logger.handlers[0].setFormatter(self._getFormatter(col, form))

        # Note: marvellous parameter: stacklevel allows to get the call from the sender, otherwise
        # it is this function that is used and the path is not good
        # cf https://stackoverflow.com/questions/14406347/python-logging-check-location-of-log-files
        # and https://www.py4u.net/discuss/157715
        if "DEBUG" == mode:
            super(SM_Logger, self).debug(("{}").format(msg), extra=extra, stacklevel=2)
        elif "ERROR" == mode:
            super(SM_Logger, self).error(("{}").format(msg), extra=extra, stacklevel=2)
        # INFO
        else:
            super(SM_Logger, self).info(("{}").format(msg), extra=extra, stacklevel=2)

        _logger.handlers[0].setFormatter(self._getFormatter(self._defaultColor, self._defaultForm))

    def debug_ext(self, msg, extra=None, col="", form="STD", tag=None, display=True):
        """
        eg: _logger.debug_ext(f"message: {text}", tag="DEPRECATED")
        """
        self._print_ext("DEBUG", msg, extra=extra, col=col, form=form, tag=tag, display=display)

    def info_ext(self, msg, extra=None, col="BLUE_LIGHT", form="STD", tag=None, display=True):
        self._print_ext("INFO", msg, extra=extra, col=col, form=form, tag=tag, display=display)

    def error_ext(self, msg, extra=None, col="RED", form="ERROR", tag=None, display=True):
        self._print_ext("ERROR", msg, extra=extra, col=col, form=form, tag=tag, display=display)


class Formatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord):
        """
        The role of this custom formatter is:
        - append filepath and lineno to logging format but shorten path to files, to make logs more clear
        - to append "./" at the begining to permit going to the line quickly with VS Code Ctrl + Click from terminal
        """
        s = super().format(record)

        MODULE_PATH = Path(__file__).parent.parent
        # print("MODULE_PATH:" + str(MODULE_PATH))
        pathname = Path(record.pathname).relative_to(MODULE_PATH)
        s += f"  [{os.curdir}{os.sep}{pathname}:{record.lineno}]"
        return s


def loggerFormatTest(message=""):
    return

    print(message)
    # warning: put back to the application mode afterward
    _logger.setLevel(logging.DEBUG)

    _logger.debug("debug message")
    _logger.info("info message")
    _logger.warning("warning message")
    _logger.error("error message")
    _logger.critical("critical message")

    # _logger.debug_basic("Test Debug Basic")
    # _logger.debug_basic("Test Debug Basic", formatter="BASIC")
    _logger.debug("debug message 02")

    _logger.debug_ext("debug_ext", col="RED", form="STD")
    _logger.debug_ext("debug_ext", col="BLUE", form="BASIC")

    mes = "          - Registering Test Package"
    print(mes)
    _logger.debug_ext(mes, form="REG")
    _logger.debug_ext("debug test override", col="RED", form="REG")

    # use normal debug() call with aformmatter set before
    _logger.debug_form(col="GREEN", form="STD")
    _logger.debug("debug test timer green")


logging.setLoggerClass(SM_Logger)
_logger = logging.getLogger(__name__)

# https://docs.python.org/fr/3/howto/logging.html
# https://stackoverflow.com/questions/11581794/how-do-i-change-the-format-of-a-python-log-message-on-a-per-logger-basis


def initialize():

    if config.devDebug:
        print("Initializing Logger...")
        print(f"len(_logger.handlers): {len(_logger.handlers)}")

    _logger.propagate = False

    logging.basicConfig(level=logging.INFO)
    _logger.setLevel(logging.INFO)  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

    # _logger.setLevel(logging.DEBUG)
    formatter = None

    # call config.initGlobalVariables() to get the config variables (currently done in Shot Manager init)
    if config.devDebug_ignoreLoggerFormatting:
        ch = "~"  # "\u02EB"
        formatter = Formatter("\33[36m" + ch + " {message:<140}" + "\033[0m", style="{")
    else:
        # formatter = Formatter("{asctime} {levelname[0]} {name:<30}  - {message:<80}", style="{")
        formatter = Formatter("SM " + " {message:<80}", style="{")

    if len(_logger.handlers) == 0:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        _logger.addHandler(handler)

    else:
        _logger.handlers[0].setFormatter(formatter)

        # handler = logging.FileHandler(get_log_file())
        # handler.setFormatter(formatter)
        # _logger.addHandler(handler)

    loggerFormatTest()


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
