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
from bpy.types import Operator

from ..utils import utils


class UAS_ShotManager_OT_About(Operator):
    bl_idname = "uas_shot_manager.about"
    bl_label = "About Shot Manager..."
    bl_description = "More information about Shot Manager..."
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props
        layout = self.layout
        box = layout.box()

        # Version
        ###############
        row = box.row()
        row.separator()
        row.label(
            text="Version: " + props.version()[0] + " - (" + "August 2021" + ")" + " -  Ubisoft"
        )

        # Authors
        ###############
        row = box.row()
        row.separator()
        row.label(text="Written by Julien Blervaque (aka Werwack), Romain Carriquiry Borchiari")

        # Purpose
        ###############
        row = box.row()
        row.label(text="Purpose:")
        row = box.row()
        row.separator()
        col = row.column()
        col.label(text="Create a set of camera shots and edit them")
        col.label(text="in the 3D View as you would do with video clips.")

        # Dependencies
        ###############
        row = box.row()
        row.label(text="Dependencies:")
        row = box.row()
        row.separator()
        splitFactor = 0.3

        split = row.split(factor=splitFactor)
        split.label(text="- OpenTimelineIO:")
        try:
            import opentimelineio as otio

            otioVersion = otio.__version__
            split.label(text=f"V. {otioVersion}  installed")
        except Exception as e:
            subRow = split.row()
            subRow.alert = True
            subRow.label(text="Module not found")

        row = box.row()
        row.separator()
        split = row.split(factor=splitFactor)
        split.label(text="- Stamp Info:")
        versionStr = utils.addonVersion("Stamp Info")
        if props.isStampInfoAvailable() and versionStr is not None:
            split.label(text=f"V. {versionStr[0]} installed")
        else:
            subRow = split.row()
            subRow.alert = True
            subRow.label(text="Add-on not found (not mandatory though)")

        box.separator()

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


_classes = (UAS_ShotManager_OT_About,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
