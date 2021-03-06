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
Functions to manipulate Shot Manager
"""

import bpy

from . import utils


def sceneHasShotManagerData(scene):
    """Return True if the scene contains Shot Manager data"""
    try:
        propGrp = scene["UAS_shot_manager_props"]
        propGrp = True
    except Exception:
        propGrp = False
    return propGrp


def getStampInfo():
    """Return the Stamp Info settings instance, None if Stamp Info is not installed
    or its version is not supported"""
    prefs = bpy.context.preferences.addons["shotmanager"].preferences
    stampInfoSettings = None

    # if getattr(scene, "UAS_StampInfo_Settings", None) is None:

    stampInfoInstalledVersion = utils.addonVersion("Stamp Info")
    if stampInfoInstalledVersion:
        stampInfoMinVersion = prefs.dependency_min_supported_version("Stamp Info")
        if stampInfoInstalledVersion[1] >= stampInfoMinVersion[1]:
            stampInfoSettings = bpy.context.scene.UAS_StampInfo_Settings
    return stampInfoSettings
