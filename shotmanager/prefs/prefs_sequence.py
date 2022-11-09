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
Preference panel for the sequences
"""

import bpy
from bpy.types import Operator


class UAS_ShotManager_Sequence_Prefs(Operator):
    bl_idname = "uas_shot_manager.sequence_prefs"
    bl_label = "Sequence Settings"
    bl_description = "Display the sequence Settings panel\nfor the Shot Manager instanced in this scene"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        props = config.getAddonProps(context.scene)
        # prefs = config.getAddonPrefs()
        layout = self.layout

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        ##################
        # Overriden by project settings
        ##################

        if props.use_project_settings:
            row = layout.row()
            row.alert = True
            row.label(text="Overriden by Project Settings:")
        else:
            # layout.label(text="Others")
            pass
        box = layout.box()
        box.use_property_decorate = False
        box.enabled = not props.use_project_settings
        col = box.column()
        col.use_property_split = True
        col.prop(props, "naming_shot_format", text="Shot Naming Template")

        # row = layout.row()
        # row.label(text="Handles:")
        col.prop(props, "render_sequence_prefix")

        col.prop(props, "renderSingleFrameShotAsImage")

        col.separator()
        row = col.row()
        row.prop(props, "use_handles", text="Use Handles")
        subrow = row.row()
        subrow.enabled = props.project_use_shot_handles
        subrow.prop(props, "handles", text="Handles")
        col.separator()

        # Edit ######
        layout.separator(factor=1)
        layout.label(text="Edit:")
        box = layout.box()
        box.use_property_decorate = False
        col = box.column()

        col.use_property_split = True

        namingRow = col.row(align=False)
        namingRowSplit = namingRow.split(factor=0.5)
        namingRowLeft = namingRowSplit.row()
        namingRowLeft.alignment = "RIGHT"
        namingRowLeft.label(text="Index of the First Frame in the Edit")
        namingRowRight = namingRowSplit.row(align=True)
        namingRowRight.prop(props, "editStartFrame", text="")

        # box.separator(factor=0.5)

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


_classes = (UAS_ShotManager_Sequence_Prefs,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
