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
Draw the names of the libraries and add-ons required by this add-on
"""

import bpy
from ..utils import utils


def drawDependencies(context, layout: bpy.types.UILayout, **kwargs):

    box = layout.box()
    row = box.row()
    row.label(text="Dependencies:")
    row = box.row()
    row.separator()
    splitFactor = 0.3

    # OpenTimelineIO
    ####################
    split = row.split(factor=splitFactor)
    split.label(text="- OpenTimelineIO:")
    try:
        import opentimelineio as otio

        otioVersion = otio.__version__
        split.label(text=f"V. {otioVersion}  installed")
    except Exception:
        subRow = split.row()
        subRow.alert = True
        if (2, 93, 0) < bpy.app.version:
            subRow.label(text="Module not yet available on Blender 2.93 and 3.x")
        else:
            subRow.label(text="Module not found  - Related features disabled")

    # Ubisoft Stamp Info
    ####################
    row = box.row()
    row.separator()
    split = row.split(factor=splitFactor)
    split.label(text="- Stamp Info:")
    stampInfo_versionStr = utils.addonVersion("Stamp Info")

    rightRow = split.row()
    subRow = rightRow.row()
    # stampInfoAvailable = getattr(bpy.context.scene, "UAS_StampInfo_Settings", None) is not None
    if stampInfo_versionStr is not None:
        subRow.label(text=f"V. {stampInfo_versionStr[0]} installed")
    else:
        subRow.alert = True
        subRow.label(text="Add-on not found  - Related features disabled")

    subRow2 = rightRow.row()
    subRow2.alignment = "RIGHT"

    doc_op = subRow2.operator("shotmanager.open_documentation_url", text="", icon="HELP")
    doc_op.path = "https://github.com/ubisoft/stampinfo"
    doc_op.tooltip = "Open Stamp Info project on GitHub: " + doc_op.path

    box.separator(factor=0.2)
