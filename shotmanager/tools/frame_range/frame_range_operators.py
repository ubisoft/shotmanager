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
Frame Range operators
"""

import bpy
from bpy.types import Operator
from bpy.props import FloatProperty

from shotmanager.utils.utils_time import zoom_dopesheet_view_to_range


class UAS_ShotManager_SetTimeRangeStart(Operator):
    bl_idname = "uas_shot_manager.set_time_range_start"
    bl_label = "Set Start Range"
    bl_description = "Set the start time range with the curent time value"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.context.preferences.addons["shotmanager"].preferences.display_frame_range_tool

    def execute(self, context):
        scene = context.scene
        if scene.use_preview_range:
            scene.frame_preview_start = scene.frame_current
        else:
            scene.frame_start = scene.frame_current
        return {"FINISHED"}


class UAS_ShotManager_SetTimeRangeEnd(Operator):
    bl_idname = "uas_shot_manager.set_time_range_end"
    bl_label = "Set End Range"
    bl_description = "Set the end time range with the curent time value"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.context.preferences.addons["shotmanager"].preferences.display_frame_range_tool

    def execute(self, context):
        scene = context.scene
        if scene.use_preview_range:
            scene.frame_preview_end = scene.frame_current
        else:
            scene.frame_end = scene.frame_current
        return {"FINISHED"}


class UAS_ShotManager_FrameTimeRange(Operator):
    bl_idname = "uas_shot_manager.frame_time_range"
    bl_label = "Frame Time Range"
    bl_description = "Change the VSE zoom value to fit the scene time range"
    bl_options = {"REGISTER"}

    spacerPercent: FloatProperty(
        description="Range of time, in percentage, before and after the time range", min=0.0, max=40.0, default=5
    )

    @classmethod
    def poll(cls, context):
        return bpy.context.preferences.addons["shotmanager"].preferences.display_frame_range_tool

    # def invoke(self, context, event):
    #     props = context.scene.UAS_shot_manager_props

    #     return {"FINISHED"}

    def execute(self, context):
        if context.scene.use_preview_range:
            zoom_dopesheet_view_to_range(context, context.scene.frame_preview_start, context.scene.frame_preview_end)
        else:
            zoom_dopesheet_view_to_range(context, context.scene.frame_start, context.scene.frame_end)
        return {"FINISHED"}


def draw_frame_range_tool_in_editor(self, context):
    layout = self.layout

    row = layout.row(align=True)
    row.separator(factor=3)
    row.alignment = "RIGHT"
    # row.operator("bpy.ops.time.view_all")
    row.operator("uas_shot_manager.set_time_range_start", text="", icon="TRIA_UP_BAR")
    row.operator("uas_shot_manager.frame_time_range", text="", icon="CENTER_ONLY")
    row.operator("uas_shot_manager.set_time_range_end", text="", icon="TRIA_UP_BAR")


def display_frame_range_in_editor(display_value):
    if display_value:
        bpy.types.TIME_MT_editor_menus.append(draw_frame_range_tool_in_editor)
    else:
        bpy.types.TIME_MT_editor_menus.remove(draw_frame_range_tool_in_editor)


_classes = (
    UAS_ShotManager_SetTimeRangeStart,
    UAS_ShotManager_SetTimeRangeEnd,
    UAS_ShotManager_FrameTimeRange,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    # lets add ourselves to the main header
    # bpy.types.TIME_MT_editor_menus.prepend(draw_frame_range_tool_in_editor)

    prefs = bpy.context.preferences.addons["shotmanager"].preferences
    display_frame_range_in_editor(prefs.display_frame_range_tool)

    # vse
    # bpy.types.SEQUENCER_HT_header.append(draw_frame_range_tool_in_editor)


#   bpy.types.TIME_HT_editor_buttons.append(draw_frame_range_tool_in_editor)
# bpy.types.TIME_MT_editor_menus.append(draw_item)
# bpy.types.TIME_MT_view.append(draw_item)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

    display_frame_range_in_editor(False)
