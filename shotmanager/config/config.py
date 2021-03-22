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
To do: module description here.
"""

import bpy

import os
from pathlib import Path
import bpy.utils.previews


def initGlobalVariables():

    # debug ############
    global uasDebug

    # wkip better code: uasDebug = os.environ.get("UasDebug", "0") == "1"
    if "UasDebug" in os.environ.keys():
        uasDebug = bool(int(os.environ["UasDebug"]))
    else:
        uasDebug = True

    uasDebug = True

    global uasDebug_keepVSEContent
    uasDebug_keepVSEContent = True and uasDebug

    global uasDebug_ignoreLoggerFormatting
    uasDebug_ignoreLoggerFormatting = True and uasDebug

    # icons ############
    global icons_col

    pcoll = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "../icons")
    for png in Path(my_icons_dir).rglob("*.png"):
        pcoll.load(png.stem, str(png), "IMAGE")

    icons_col = pcoll

    # import otio ############
    global gMontageOtio
    gMontageOtio = None

    global gSeqEnumList
    gSeqEnumList = None

    global gTracksEnumList
    gTracksEnumList = None


def releaseGlobalVariables():

    global icons_col

    bpy.utils.previews.remove(icons_col)
    icons_col = None
