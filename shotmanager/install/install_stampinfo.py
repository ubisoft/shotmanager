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
StampInfo installation
"""

from pathlib import Path

import bpy

from ..utils import utils
from ..utils.utils_os import internet_on, module_can_be_imported, is_admin

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

# not called anymore
def install_stampinfo_addon():
    error_messages = []
    # return ["Debug message"]

    prefs = bpy.context.preferences.addons["shotmanager"].preferences

    installStampInfo = False

    # is StampInfo installed?
    stampInfoInstalledVersion = utils.addonVersion("Stamp Info")
    if stampInfoInstalledVersion:
        stampInfoMinVersion = prefs.dependency_min_supported_version("Stamp Info")
        if stampInfoInstalledVersion[1] < stampInfoMinVersion[1]:
            installStampInfo = True
    else:
        installStampInfo = True

        # is version up-to-date?
        # dependency_min_supported_version("Stamp Info")

        # if not then install

        # is admin?

        # is online?
        # if not internet_on():

        # print("Internet connection OK - Firewall may still block package downloads")
    if installStampInfo:
        import os

        if installStampInfo:
            _logger.debug_ext("Installing Stamp Info ")

            packagePath = str(Path(__file__).parent.parent) + "\\distr\\"
            fileList = sorted(os.listdir(packagePath))

            # packagesList is a list of file names, NOT FILE PATHS
            packagesList = [item for item in fileList if item.endswith(".zip")]

            if len(packagesList):
                packageFullPath = os.path.join(packagePath, packagesList[0])

                # get stamp info version from archive name
                packageVersion = utils.addonVersionFromFileName(packagesList[0])
                if packageVersion is None:
                    _logger.warning_ext(
                        f"Stamp Info installation canceled: add-on version not found in file name: {packageFullPath}"
                    )
                    return

                if stampInfoInstalledVersion is not None and stampInfoInstalledVersion[1] > packageVersion[1]:
                    _logger.warning_ext(
                        "Stamp Info installed version is more recent than the one provided with Shot Manager - Add-on is not re-installed"
                    )
                    _logger.debug_ext(
                        f"Stamp Info installed version: {stampInfoInstalledVersion[0]}, package version provided with Shot Manager: {packageVersion[0]}"
                    )
                    installStampInfo = False

                if installStampInfo:
                    bpy.ops.preferences.addon_install(
                        overwrite=True,
                        target="DEFAULT",
                        filepath=packageFullPath,
                        filter_folder=True,
                        filter_python=False,
                        # filter_glob="*.zip",
                        filter_glob=packagesList[0],
                    )
                    bpy.ops.preferences.addon_refresh()
                    _logger.debug_ext(f"StampInfo installed from {packagesList[0]}")
            else:
                _logger.warning_ext(f"No archive found to install Stamp Info add-on in {packagePath}")

    stampInfoInstalledVersion = utils.addonVersion("Stamp Info")
    if stampInfoInstalledVersion:
        _logger.info_ext("Enabling Stamp Info add-on")
        bpy.ops.preferences.addon_enable(module="stampinfo")

        try:
            prefs_stampInfo = bpy.context.preferences.addons["shotmanager"].preferences
            prefs_stampInfo.checkForNewAvailableVersion = False
        except Exception as e:
            _logger.error_ext(
                f"Cannot change the property checkForNewAvailableVersion in Stamp Info preferences. Error: {e}"
            )
