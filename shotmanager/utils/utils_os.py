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
from pathlib import Path
import platform
import requests

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def open_folder(path):
    """
    Open a path or an URL with the application specified by the os
    """
    if "Darwin" == platform.system():
        subprocess.check_call(["open", "--", path])
    elif "Linux" == platform.system():
        subprocess.check_call(["xdg-open", path])
    elif "Windows" == platform.system():
        subprocess.Popen(f'explorer "{Path(path)}"')


def delete_folder(dir_path):
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
        except Exception:
            print("Cannot delete Dir: ", dir_path)


def internet_on():
    """Check if a web url can be reached.
    Return True if the url is found, False otherwise.
    *** Warning: On Mac OS False is always returned if the certifi Python lib is not installed.
    The returned value has then be forced to True. ***
    See: https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error
    """
    import urllib.request
    import urllib.error

    url = "https://google.com"

    # Mac specific:
    if "Darwin" == platform.system():
        # return True
        import ssl

        gcontext = ssl.SSLContext()
        for timeout in [1, 5, 10]:
            try:
                urllib.request.urlopen(url, context=gcontext, timeout=timeout)
                return True
            except urllib.error.URLError:
                pass
    else:
        for timeout in [1, 5, 10]:
            try:
                urllib.request.urlopen(url, timeout=timeout)
                return True
            except urllib.error.URLError:
                pass

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
    timeoutInSec = 2
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
