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
from bpy.types import Panel, Operator, Menu

from ..config import config


class UAS_ShotManager_Features(Operator):
    bl_idname = "uas_shot_manager.features"
    bl_label = "Features"
    bl_description = "Controls the features available in the shot Manager panel"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props
        layout = self.layout

        layout.label(text="Display Takes and Shots additionnal features:")
        box = layout.box()

        # empty spacer column
        row = box.row()
        col = row.column()
        col.scale_x = 1.0
        col.label(text=" ")
        col = row.column()

        ################
        # Notes
        subrow = col.row()
        subrow.scale_x = 1.5
        icon = config.icons_col["ShotManager_NotesData_32"]
        notesIcon = "TEXT"
        notesIcon = "WORDWRAP_OFF"
        subrow.prop(props, "display_notes_in_properties", text="", icon_value=icon.icon_id)
        subrow.label(text="Takes and Shots Notes")

        ################
        # Camera BG
        subrow = col.row()
        subrow.scale_x = 1.5
        icon = config.icons_col["ShotManager_CamBGVisible_32"]
        subrow.prop(props, "display_camerabgtools_in_properties", text="", icon_value=icon.icon_id)
        subrow.label(text="Camera Backgrounds")

        ################
        # Grease Pencil
        subrow = col.row()
        subrow.scale_x = 1.5
        icon = config.icons_col["ShotManager_CamGPVisible_32"]
        subrow.prop(props, "display_greasepencil_in_properties", text="", icon_value=icon.icon_id)
        subrow.label(text="Camera Grease Pencil")

        layout.separator()
        layout.label(text="Display additionnal panels:")
        box = layout.box()

        # empty spacer column
        row = box.row()
        col = row.column()
        col.scale_x = 1.0
        col.label(text=" ")
        col = row.column()

        ################
        # Retimer
        subrow = col.row()
        subrow.scale_x = 1.5
        subrow.prop(props, "display_retimer_in_properties", text="", icon="TIME")
        subrow.label(text="Retimer")

        layout.separator()
        layout.label(text="Other:")
        row = layout.row()
        row.separator(factor=2)
        row.prop(props, "display_advanced_infos")

        layout.separator(factor=2)

    def execute(self, context):
        return {"FINISHED"}


_classes = (UAS_ShotManager_Features,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
