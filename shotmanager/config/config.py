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
Global variables
"""

import bpy

import os
from pathlib import Path
import bpy.utils.previews


def getShotManagerPrefs():
    """Return the preferences of the add-on"""
    return bpy.context.preferences.addons["shotmanager"].preferences


def initGlobalVariables():

    # debug ############
    global devDebug

    # wkip better code: devDebug = os.environ.get("devDebug", "0") == "1"
    if "devDebug" in os.environ.keys():
        devDebug = bool(int(os.environ["devDebug"]))
    else:
        devDebug = False

    # change this value to force debug at start time
    devDebug = True

    global devDebug_lastRedrawTime
    devDebug_lastRedrawTime = -1

    # keep the intermediate images after rendering (ie the original  Blender renderings
    # and the Stamp Info temporaty images)
    global devDebug_keepVSEContent
    devDebug_keepVSEContent = False

    global devDebug_ignoreLoggerFormatting
    devDebug_ignoreLoggerFormatting = True and devDebug

    # installation #############
    # internet/github timeout, in seconds

    global LATEST_VERSION_TIMEOUT
    LATEST_VERSION_TIMEOUT = 1

    # icons ############
    global icons_col

    pcoll = bpy.utils.previews.new()
    # my_icons_dir = os.path.join(os.path.dirname(__file__), "../icons")
    currentDir = os.path.dirname(__file__)
    addon_dir = Path(currentDir).parent
    my_icons_dir = os.path.join(addon_dir, "icons")
    for png in Path(my_icons_dir).rglob("*.png"):
        pcoll.load(png.stem, str(png), "IMAGE")

    icons_col = pcoll

    # preferences ##########
    global defaultLayout
    # defaultLayout = "STORYBOARD"
    defaultLayout = "PREVIZ"

    # ui ##########
    global gMouseScreenPos
    gMouseScreenPos = [0.0, 0.0]

    # keymaps ##########
    global gAddonKeymaps
    gAddonKeymaps = []

    # interactive shots stack ############
    global tmpTimelineModalRect
    tmpTimelineModalRect = None

    global gShotsStack_forceRedraw_debug
    gShotsStack_forceRedraw_debug = False

    global gShotsStackInfos
    gShotsStackInfos = None

    global gModulePath
    gModulePath = None

    global gShotsStack_ui_scale
    gShotsStack_ui_scale = 1.25

    # dependencies #############
    global STAMP_INFO_MIN_VERSION
    STAMP_INFO_MIN_VERSION = ("1.3.5", 1003005)

    # otio #############
    global gImportOpenTimelineIO
    gImportOpenTimelineIO = True

    global gMontageOtio
    gMontageOtio = None

    global gSeqEnumList
    gSeqEnumList = None

    global gTracksEnumList
    gTracksEnumList = None

    global gRedrawShotStack
    gRedrawShotStack = False

    # used to "pre draw": do the drawing computation but not the actual draw
    # this is useful to prepare all the graphics components without having an
    # uncomplete widget display
    global gRedrawShotStack_preDrawOnly
    gRedrawShotStack_preDrawOnly = False


def releaseGlobalVariables():

    global icons_col

    bpy.utils.previews.remove(icons_col)
    icons_col = None


def getLoggingTags():
    tags = dict()

    # debug tags
    tags["DEPRECATED"] = False

    tags["REG"] = False
    tags["UNREG"] = False

    tags["INIT_AND_DATA"] = True

    tags["SHOTS_PLAY_MODE"] = True

    tags["RENDER"] = False
    tags["LAYOUT"] = False
    tags["RETIMER"] = True

    tags["EDIT_IO"] = True

    tags["TIMELINE_EVENT"] = False
    tags["SHOTSTACK_EVENT"] = False
    tags["EVENT"] = False

    # info tags
    tags["RENDERTIME"] = False

    return tags
