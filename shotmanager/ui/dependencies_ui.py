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

# from ..utils import utils
from shotmanager.config import config

# import platform


def drawDependencies(context, layout: bpy.types.UILayout, **kwargs):
    # prefs = config.getAddonPrefs()

    splitFactor = 0.45

    box = layout.box()
    col = box.column()

    ####################
    # dependencies to other add-ons
    ####################

    # titleRow = col.row()
    # titleRow.label(text="Add-on Dependencies:")
    # titleRow.separator()

    # col.separator(factor=0.5)

    # Ubisoft Stamp Info
    ####################
    # row = col.row()
    # row.separator()

    # split = row.split(factor=splitFactor)
    # split.label(text="- Stamp Info:")
    # stampInfoInstalledVersion = utils.addonVersion("Stamp Info")

    # def _displayHelp():
    #     subRow2 = rightRow.row()
    #     subRow2.alignment = "RIGHT"

    #     doc_op = subRow2.operator("shotmanager.open_documentation_url", text="", icon="HELP")
    #     doc_op.path = "https://github.com/ubisoft/stampinfo"
    #     doc_op.tooltip = "Open Stamp Info project on GitHub: " + doc_op.path

    # def _displayDownloadLatest():
    #     subRow2 = rightRow.row()
    #     subRow2.alignment = "RIGHT"
    #     subRow2.alert = True

    #     doc_op = subRow2.operator("shotmanager.open_documentation_url", text="Latest", icon="WORLD_DATA")
    #     doc_op.path = "https://github.com/ubisoft/stampinfo/releases/latest"
    #     doc_op.tooltip = "Open Stamp Info latest release page on GitHub: " + doc_op.path

    # rightRow = split.row()
    # subRow = rightRow.row()
    # # stampInfoAvailable = getattr(bpy.context.scene, "UAS_SM_StampInfo_Settings", None) is not None
    # if stampInfoInstalledVersion is None:
    #     subRow.alert = True
    #     subRow.label(text="Add-on not found - Related features disabled")
    # else:
    #     stampInfoMinVersion = prefs.dependency_min_supported_version("Stamp Info")
    #     if stampInfoInstalledVersion[1] < stampInfoMinVersion[1]:
    #         subRow.alert = True
    #         subRow.label(text=f"V. {stampInfoInstalledVersion[0]} too old - Related features disabled")
    #         _displayDownloadLatest()
    #     else:
    #         subRow.label(text=f"V. {stampInfoInstalledVersion[0]} installed")
    #         _displayHelp()

    # col.separator()

    ####################
    # required Python libs
    ####################

    titleRow = col.row()
    titleRow.label(text="Required Python Libraries:")
    titleRow.separator()

    col.separator(factor=0.5)

    row = col.row()
    row.separator()

    # OpenTimelineIO
    ####################

    split = row.split(factor=splitFactor)
    split.label(text="- OpenTimelineIO:")

    rightRow = split.row()
    subRow = rightRow.row()

    try:
        import opentimelineio as otio

        otioVersion = otio.__version__
        subRow.label(text=f"V. {otioVersion}  installed")
    except Exception:
        subRow = col.row()
        subRow.separator()
        subRow.alert = True
        if (2, 93, 0) < bpy.app.version:
            # if platform.system() != "Windows":
            #     subRow.label(text="Module not yet available on Blender 2.93+ for Mac and Linux ")
            # else:
            subRowCol = subRow.column()
            subRowCol.scale_y = 0.7
            subRowCol.label(text="Module not found - Try to relaunch Blender in Admin mode ")
            row = subRowCol.row(align=True)
            row.label(text="If the issue persists check the Installation Troubles FAQ:")
            row = subRowCol.row(align=True)
            rowRight = row.row()
            rowRight.scale_y = 1.2
            rowRight.alignment = "RIGHT"
            rowRight.scale_x = 1.0
            doc_op = rowRight.operator("shotmanager.open_documentation_url", text="Shot Manager FAQ")
            doc_op.path = "https://ubisoft-shotmanager.readthedocs.io/en/latest/troubleshoot/faq.html#installation"
            doc_op.tooltip = "Open online FAQ: " + doc_op.path
            subRowCol.separator(factor=0.3)
        else:
            subRow.label(text="Module not found  - Related features disabled")

    subRow2 = rightRow.row()
    subRow2.alignment = "RIGHT"

    doc_op = subRow2.operator("shotmanager.open_documentation_url", text="", icon="HELP")
    doc_op.path = "https://github.com/PixarAnimationStudios/OpenTimelineIO"
    doc_op.tooltip = "Open OpenTimelineIO GitHup project: " + doc_op.path

    # Pillow
    ####################
    # subRow.label(text="Module not found  - Add-on cannot run normally")

    row = col.row()
    row.separator()

    split = row.split(factor=splitFactor)
    split.label(text="- PIL (Python Imaging Library):")

    rightRow = split.row()
    subRow = rightRow.row()

    try:
        import PIL as pillow

        pillowVersion = pillow.__version__
        subRow.label(text=f"V. {pillowVersion}  installed")
    except Exception:
        subRow = col.row()
        subRow.separator()
        subRow.alert = True

        subRowCol = subRow.column()
        subRowCol.scale_y = 0.7
        subRowCol.label(text="Module not found - Try to relaunch Blender in Admin mode ")
        row = subRowCol.row(align=True)
        row.label(text="If the issue persists check the Installation Troubles FAQ:")
        row = subRowCol.row(align=True)
        rowRight = row.row()
        rowRight.scale_y = 1.2
        rowRight.alignment = "RIGHT"
        rowRight.scale_x = 1.0
        doc_op = rowRight.operator("shotmanager.open_documentation_url", text="Shot Manager FAQ")
        doc_op.path = "https://ubisoft-shotmanager.readthedocs.io/en/latest/troubleshoot/faq.html#installation"
        doc_op.tooltip = "Open online FAQ: " + doc_op.path
        subRowCol.separator(factor=0.3)

    subRow2 = rightRow.row()
    subRow2.alignment = "RIGHT"

    # doc_op = subRow2.operator("shotmanager.open_documentation_url", text="", icon="HELP")
    # doc_op.path = "https://github.com/PixarAnimationStudios/OpenTimelineIO"
    # doc_op.tooltip = "Open OpenTimelineIO GitHup project: " + doc_op.path

    col.separator(factor=0.4)
