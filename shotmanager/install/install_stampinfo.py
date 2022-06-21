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

import bpy

from ..utils import utils
from ..utils.utils_os import internet_on, module_can_be_imported, is_admin
from . import addon_error_prefs

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


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
        import subprocess
        import os
        import sys
        from pathlib import Path

        pyExeFile = sys.executable
        # we have to go above \bin dir
        localPyDir = str((Path(pyExeFile).parent).parent) + "\\lib\\site-packages\\"
        tmp_file = localPyDir + "ShotManager_Tmp.txt"

        if installStampInfo:

            _logger.debug_ext("Installing Stamp Info ")
            package_path = os.path.join(
                os.path.dirname(__file__),
                "..\\distr\\Ubisoft_StampInfo_V1-3-1.zip",
            )

            bpy.ops.preferences.addon_install(
                overwrite=True,
                target="DEFAULT",
                filepath=package_path,
                filter_folder=True,
                filter_python=False,
                filter_glob="*.zip",
            )
            print("\nWkInbetween")
            bpy.ops.preferences.addon_refresh()
            print("\nWkInbetween 02")

    stampInfoInstalledVersion = utils.addonVersion("Stamp Info")
    if stampInfoInstalledVersion:
        _logger.info_ext("Enabling Stamp Info add-on")
        bpy.ops.preferences.addon_enable(module="stampinfo")
