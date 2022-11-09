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
Pref tools
"""

import bpy
from bpy.types import Operator

from shotmanager.config import config


#############
# Preferences
#############


class UAS_ShotManager_Tools_Prefs(Operator):
    bl_idname = "uas_shot_manager.tools_prefs"
    bl_label = "Tools Settings"
    bl_description = (
        "Display the Sequence Timeline, Interactive Shots Stack and Edit Settings panel"
        "\nfor the Shot Manager instanced in this scene"
    )
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context):
        # props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()
        # scale_x = 0.85

        layout = self.layout
        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        ################
        ################

        # Sequence timeline ######
        # layout.separator(factor=1)
        layout.label(text="Timeline Editor Tools:")
        box = layout.box()
        box.use_property_decorate = False

        # empty spacer column
        row = box.row()
        col = row.column()
        col.scale_x = 0.3
        col.label(text=" ")
        col = row.column()

        col.use_property_split = False
        # col.use_property_decorate = False
        col.prop(prefs, "display_frame_range_tool", text="Display Frame Range Tool")

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


_classes = (UAS_ShotManager_Tools_Prefs,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
