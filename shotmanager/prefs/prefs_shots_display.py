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
Shot template list preferences
"""

import bpy
from bpy.types import Operator

from shotmanager.utils.utils_ui import propertyColumn
from shotmanager.config import config

#############
# Preferences
#############


class UAS_ShotManager_Shots_Prefs(Operator):
    bl_idname = "uas_shot_manager.shots_prefs"
    bl_label = "Shots Display and Manipulation Settings"
    bl_description = "Display the Shots Display and Manipulation Settings panel"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context):
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()

        layout = self.layout

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        # Shot List display
        ################
        sceneDisplayRow = layout.row()
        sceneDisplayRow.label(text="Shot List Display:")
        sceneDisplayRightRow = sceneDisplayRow.row()
        sceneDisplayRightRow.alignment = "RIGHT"
        sceneDisplayRightRow.label(text="(in Current Scene)")

        box = layout.box()
        box.use_property_decorate = False

        # main column, to allow title offset
        maincol = box.column()

        # empty spacer column
        row = maincol.row()
        col = row.column()
        col.scale_x = 0.4
        col.label(text=" ")
        col = row.column()

        col.separator(factor=0.5)
        col.use_property_split = False
        col.prop(props, "display_selectbut_in_shotlist", text="Display Camera Select Button")
        col.prop(props, "display_enabled_in_shotlist", text="Display Enabled State")
        col.prop(props, "display_getsetcurrentframe_in_shotlist", text="Display Get/Set current Frame Buttons")

        col.prop(props, "display_cameraBG_in_shotlist")
        col.prop(props, "display_greasepencil_in_shotlist")

        col.separator(factor=1.7)
        col.prop(props, "highlight_all_shot_frames", text="Highlight Framing Values When Equal to Current Time")
        col.prop(props, "display_duration_after_time_range", text="Display Shot Duration After Time Range")
        col.prop(props, "use_camera_color", text="Use Camera Color for Shots ")

        col.use_property_split = False
        col.separator(factor=1.7)
        row = col.row()
        row.label(text="Display Shot Properties Mode:")
        row.prop(props, "current_shot_properties_mode", text="")
        row.separator()

        layout.separator(factor=2)

    def execute(self, context):
        return {"FINISHED"}


_classes = (UAS_ShotManager_Shots_Prefs,)


def register():

    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
