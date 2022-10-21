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
Dependencies installation
"""

import bpy

from ..utils.utils_os import internet_on, module_can_be_imported, is_admin
from . import addon_error_prefs

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def install_library(lib_names, pip_retries=2, pip_timeout=-100):
    """Install the specified external libraries
    Args:
        lib_names (tupple): the current name of the library and its package name
        eg: ("PIL", "pillow")
    Return:
        A tupple made of the error message and the error index
        eg: ("Err.1: Cannot connect to Internet. Blocked by firewall?", 1)
    """
    error_messages = []
    # return ["Debug message"]

    lib_name = lib_names[0]
    lib_already_installed = module_can_be_imported(lib_name)

    _logger.debug_ext(
        f"Checking for lib {lib_name}: {'' if lib_already_installed else 'Not yet '}installed", col="GREEN"
    )

    if not lib_already_installed:

        outputMess = f"   # {lib_name} Install Failed: "
        # NOTE: possible issue on Mac OS, check the content of the function internet_on()
        if not internet_on():
            errorInd = 1
            errorMess = f"Err.{errorInd}: Cannot connect to Internet. Blocked by firewall?"
            _logger.error_ext(outputMess + errorMess)
            error_messages.append((errorMess, errorInd))
            return error_messages

        # print("Internet connection OK - Firewall may still block package downloads")
        import subprocess
        import os
        import sys
        from pathlib import Path

        pyExeFile = sys.executable
        # we have to go above \bin dir
        localPyDir = str((Path(pyExeFile).parent).parent) + "\\lib\\site-packages\\"
        tmp_file = localPyDir + "ShotManager_Tmp.txt"

        if not is_admin():
            from os.path import isfile

            if isfile(tmp_file):
                try:
                    os.remove(tmp_file)
                except Exception:
                    errorInd = 21
                    errorMess = f"Err.{errorInd}: Cannot modify to Blender Python folder. Need Admin rights?"
                    _logger.error_ext(outputMess + errorMess)
                    error_messages.append((errorMess, errorInd))
                    return error_messages

            if not os.access(localPyDir, os.W_OK):
                _logger.warning_ext(f"No access to: {localPyDir}")
                # we try to create a file to see if we can write into the folder
                # this allows the unzipped versions of blender to receive the installation

                try:
                    f = open(tmp_file, "w")
                    f.write("Temp file for Ubisoft Shot Manager")
                    f.close()
                except Exception as e:
                    _logger.error_ext(f"e: {e}")
                    errorInd = 22
                    errorMess = f"Err.{errorInd}: Cannot write to Blender Python folder. Need Admin rights?"
                    _logger.error_ext(outputMess + errorMess)
                    error_messages.append((errorMess, errorInd))
                    return error_messages
            else:
                _logger.warning_ext(f"Not in Admin mode but Has access to: {localPyDir}")

                try:
                    f = open(tmp_file, "w")
                    f.write("Temp file for Ubisoft Shot Manager")
                    f.close()
                except Exception as e:
                    _logger.error_ext(f"e: {e}")
                    errorInd = 23
                    errorMess = (
                        f"Err.{errorInd}: Has access but cannot write to Blender Python folder. Need Admin rights?"
                    )
                    _logger.error_ext(outputMess + errorMess)
                    error_messages.append((errorMess, errorInd))
                    return error_messages

        try:
            # NOTE: to prevent a strange situation where pip finds and/or installs the library in the OS Python directory
            # we force the installation in the current Blender Python \lib\site-packages with the use of "--ignore-installed"
            # "--default-timeout" has been replaced by "--timeout" (tbc)
            if 0 >= pip_timeout:
                pip_timeout = 100
            subError = subprocess.run(
                [
                    pyExeFile,
                    "-m",
                    "pip",
                    "--default-timeout",
                    str(pip_timeout),
                    "--retries",
                    str(pip_retries),
                    "install",
                    lib_names[1],
                    # "git+https://github.com/PixarAnimationStudios/OpenTimelineIO.git",
                    # "opentimelineio==0.11.0",
                    "--ignore-installed",
                ]
            )
            # print(f"    - subError.returncode: {subError.returncode}")
            if 0 == subError.returncode:
                # NOTE: one possible returned error is "Requirement already satisfied". This case should not appear since
                # we test is the module is already there with the function module_can_be_imported
                if module_can_be_imported(lib_name):
                    # print(f"Library {lib_name} correctly installed")
                    pass
                else:
                    errorInd = 3
                    errorMess = f"Err.{errorInd}: Library {lib_name} installed but cannot be imported"
                    _logger.error_ext(f"    subError: {subError}")
                    _logger.error_ext(outputMess + errorMess)
                    _logger.error_ext("    Possibly installed in a wrong Python instance folder - Contact the support")
                    error_messages.append((errorMess, errorInd))
            else:
                errorInd = 4
                errorMess = f"Err.{errorInd}: Library {lib_name} cannot be downloaded"
                _logger.error_ext(f"    subError: {subError}")
                _logger.error_ext(outputMess + errorMess)
                error_messages.append((errorMess, errorInd))

                # send the error
                subError.check_returncode()

        # except Exception as ex:
        # except ReadTimeoutError as ex:
        #     pass

        except subprocess.CalledProcessError as ex:
            _logger.error_ext(ex.output)
            if 0 == ex.returncode:
                errorInd = 5
                errorMess = f"Err.{errorInd}: Error during installation of library {lib_name}"
            else:
                # template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                # message = template.format(type(ex).__name__, ex.args)
                # _logger.error_ext(f"message: {message}")

                errorInd = 6
                errorMess = f"Err.{errorInd}: Error during installation of library {lib_name}"
            _logger.error_ext(outputMess + errorMess)
            error_messages.append((errorMess, errorInd))

    return error_messages


def install_dependencies(dependencies_list, retries=2, timeout=100):
    """Install the add-on dependecies
    Args:
        dependencies_list (list): a list of tupples with the display name of the libraries and their package name
        eg: [("PIL", "pillow")]
        retries (int): number of times pip will retry downloading a package
        timeout (int, in seconds): time waited by pip for the download
    Returns:
        0 if everything went well, the error code (>0) otherwise
    """
    for dependencyLib in dependencies_list:
        installation_errors = install_library(dependencyLib, pip_retries=retries, pip_timeout=timeout)

        if len(installation_errors):
            _logger.error_ext(
                "   !!! Something went wrong during the installation of the add-on - Check the Shot Manager add-on Preferences panel !!!\n"
            )
            addon_error_prefs.register()
            prefs_addon = config.getAddonPrefs()
            prefs_addon.error_message = installation_errors[0][0]
            return installation_errors[0][1]
    return 0


def unregister_from_failed_install():
    # unregistering add-on in the case it has been registered with install errors
    prefs_addon = config.getAddonPrefs()
    if hasattr(prefs_addon, "install_failed") and prefs_addon.install_failed:
        _logger.error_ext("\n*** --- Unregistering Failed Install for Shot Manager Add-on --- ***")
        addon_error_prefs.unregister()
        return True
    return False
