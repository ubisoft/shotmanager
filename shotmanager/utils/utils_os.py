# GPLv3 License
#
# Copyright (C) 2020 Ubisoft
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
Utility functions that may require os/platform specific adjustments
"""

import subprocess
import os
from pathlib import Path, PurePath
import platform
import requests

import typing

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def getPlatformName():
    if "Windows" == platform.system():
        return "Windows"
    elif "Darwin" == platform.system():
        return "Mac"
    elif "Linux" == platform.system():
        return "Linux"
    return None


def open_folder(path: str):
    """
    Open a path or an URL with the application specified by the os
    """
    if "Windows" == platform.system():
        subprocess.Popen(f'explorer "{Path(path)}"')
    elif "Darwin" == platform.system():
        subprocess.check_call(["open", "--", path])
    elif "Linux" == platform.system():
        subprocess.check_call(["xdg-open", path])


def delete_folder(dir_path: str):
    if os.path.exists(dir_path):
        files_in_directory = os.listdir(dir_path)
        # filtered_files = [file for file in files_in_directory if file.endswith(".png") or file.endswith(".wav")]

        for file in files_in_directory:
            path_to_file = os.path.join(dir_path, file)
            try:
                os.remove(path_to_file)
            except Exception:
                # _logger.exception(f"\n*** File locked (by system?): {path_to_file}")
                print(f"\n*** File locked (by system?): {path_to_file}")
        try:
            os.rmdir(dir_path)
        except OSError as error:
            _logger.warning_ext(f"Cannot delete directory: {dir_path}, error:{error}")


def open_media_in_player(path: str):
    if not os.path.exists(path):
        _logger.info_ext(f"Media to open not found: {path}")
        return

    if "Windows" == platform.system():
        os.startfile(path)
    elif "Darwin" == platform.system():
        # subprocess.call(("open", path))
        # subprocess.check_call(['open', '-a', 'Quicktime Player', path)
        subprocess.check_call(["open", "--", path])
    elif "Linux" == platform.system():
        subprocess.call(("xdg-open", path))


def get_dir_separator_char():
    separator = "*"
    if "Windows" == platform.system():
        separator = "\\"
    elif "Darwin" == platform.system():
        separator = "/"
    elif "Linux" == platform.system():
        separator = "/"

    # _logger.info_ext(f"OS Specific: get_dir_separator_char: Platform is: {getPlatformName()}")

    return separator


def format_path_for_os(path: str, addSeparatorAtTheEnd: bool = True):
    """Format the provided path for the current OS.
    Path can be a file or a directory.
    Return a formated string.
    Args:
        addSeparatorAtTheEnd: it path is a folder then add a folder separator characted at the end of it"""

    formattedPath = str(PurePath(path))

    # if "Windows" == platform.system():
    #     # convert \\ to \
    #     formattedPath.replace("\\\\", "++++")
    #     formattedPath.replace("++++", "\\")

    isFile = "" != Path(formattedPath).suffix

    if not isFile and addSeparatorAtTheEnd:
        formattedPath = formattedPath + get_dir_separator_char()
        # _logger.info_ext(f"OS Specific: format_path_for_os: formattedPath: {formattedPath}")

    return formattedPath


def internet_on(timeoutList: typing.List[int] = None):
    """Check if a web url can be reached.
    Args:
        timeoutList: list of times to pool the net. Eg: [1, 2, 5]. Default is [1, 5, 10]
    Return True if the url is found, False otherwise.
    *** Warning: On Mac OS False is always returned if the certifi Python lib is not installed.
    The returned value has then be forced to True. ***
    See: https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error
    """
    import urllib.request
    import urllib.error

    url = "https://google.com"

    if timeoutList is None:
        timesOut = [1, 5, 10]
    else:
        timesOut = timeoutList

    if "Windows" == platform.system():
        for timeout in timesOut:
            try:
                urllib.request.urlopen(url, timeout=timeout)
                return True
            except urllib.error.URLError:
                pass

    elif "Darwin" == platform.system():
        import ssl

        gcontext = ssl.SSLContext()
        for timeout in timesOut:
            try:
                urllib.request.urlopen(url, context=gcontext, timeout=timeout)
                return True
            except urllib.error.URLError:
                pass

    elif "Linux" == platform.system():
        # https://stackoverflow.com/questions/20913411/test-if-an-internet-connection-is-present-in-python
        import socket

        for timeout in timesOut:
            try:
                # see if we can resolve the host name -- tells us if there is
                # a DNS listening
                host = socket.gethostbyname(url)
                # connect to the host -- tells us if the host is actually reachable
                s = socket.create_connection((host, 80), 2)
                s.close()
                return True
            except Exception:
                pass  # we ignore any errors, returning False
    return False


def module_can_be_imported(name):
    """Check if the specified module already exists in the current Python environment
    To get a submodule: eg: module_can_be_imported("stampinfo.otio")
    """
    modules_list = []
    try:
        __import__(name, fromlist=modules_list)
        return True
    except ModuleNotFoundError:
        return False


def is_admin():
    """Return True if the current session is run in Admin mode"""
    import ctypes
    import os

    try:
        is_user_admin = os.getuid() == 0
    except AttributeError:
        is_user_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_user_admin


def get_latest_release_version(url, verbose=False, use_debug=False):
    """Return a string with the latest release version available online on gitHub, None otherwise
    Args:
        url eg: 'https://github.com/ubisoft/shotmanager/releases/latest'
    """
    latestReleaseVersion = None

    if use_debug:
        # using json: https://betterprogramming.pub/how-to-work-with-json-files-in-python-bedb5b37cbc9
        import json

        jsonFile = "Z:/EvalSofts/Blender/DevPython/UAS_ShotManager_Addon/resources/test_data/test_add_on_version.json"
        # with open(jsonFile, "r") as read_file:
        #     data = json.load(read_file)

        with open(jsonFile) as jsonFile:
            jsonObject = json.load(jsonFile)
            jsonFile.close()

        print(f"jsonObject: {jsonObject}")
        jsonFile.close()
        latestReleaseVersion = jsonObject["add_on_version"]
        print(f"latestReleaseVersion: {latestReleaseVersion}")

        return latestReleaseVersion

    # NOTE: possible issue on Mac OS, check the content of the function internet_on()
    if not internet_on():
        errorInd = 1
        errorMess = f"{errorInd}: Cannot connect to Internet to check the latest add-on version. Blocked by firewall?"
        if verbose:
            _logger.warning_ext(errorMess)
        return None

    # NOTE: read https://docs.python-requests.org/en/latest/user/quickstart/#timeouts
    # and https://stackoverflow.com/questions/21965484/timeout-for-python-requests-get-entire-response

    # NOTE: timeout is not a time limit on the entire response download; rather, an exception is
    # raised if the server has not issued a response for timeout seconds (more precisely,
    # if no bytes have been received on the underlying socket for timeout seconds).
    # If no timeout is specified explicitly, requests do not time out.

    # r = requests.get(url)
    timeoutInSec = config.LATEST_VERSION_TIMEOUT
    # latestReleaseVersion = "1.0.0"

    # dirty fix to avoir HTTPS warning
    requests.packages.urllib3.disable_warnings()

    # wkipwkipwkip some work and test to do here...
    r = requests.get(url, verify=False, timeout=timeoutInSec)
    latestReleaseVersion = r.url.split("/")[-1]
    try:
        r = requests.get(url, verify=False, timeout=timeoutInSec)
        latestReleaseVersion = r.url.split("/")[-1]
    except Exception as requestExcept:
        _logger.info_ext(f"Exception in Update Check: {requestExcept}", col="RED")

    return latestReleaseVersion
