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
import addon_utils

from . import utils

from shotmanager.config import config


def getAddonPrefs():
    """Return the preferences of the add-on"""
    return config.getAddonPrefs()


def getShotManagerAddon():
    """Return the add-on"""
    sm_addon = None
    for addon in addon_utils.modules():
        if addon.bl_info["name"] == "Ubisoft Shot Manager":
            sm_addon = addon
            break
    return sm_addon


def getShotManagerWanring():
    """Return the add-on"""
    addonWarning = ""
    sm_addon = getShotManagerAddon()
    if sm_addon:
        addonWarning = sm_addon.bl_info.get("warning", "")
    return addonWarning


def getUbisoftName():
    """Return the Ubisoft name only if there is no warning message"""
    addonWarning = getShotManagerWanring()
    if "" != addonWarning:
        return ""
    return "Ubisoft"


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

    return bpy.context.scene.UAS_SM_StampInfo_Settings

    prefs = config.getAddonPrefs()
    stampInfoSettings = None

    # if getattr(scene, "UAS_SM_StampInfo_Settings", None) is None:

    stampInfoInstalledVersion = utils.addonVersion("Ubisoft Shot Manager")
    if stampInfoInstalledVersion:
        stampInfoMinVersion = prefs.dependency_min_supported_version("Stamp Info")
        if stampInfoInstalledVersion[1] >= stampInfoMinVersion[1]:
            stampInfoSettings = bpy.context.scene.UAS_SM_StampInfo_Settings
    return stampInfoSettings
