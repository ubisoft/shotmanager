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
from bpy.props import FloatProperty, StringProperty, IntProperty

from shotmanager.utils.utils_time import zoom_dopesheet_view_to_range
from shotmanager.utils import utils_ui

from shotmanager.config import config


class UAS_ShotManager_SetTimeRangeStart(Operator):
    bl_idname = "uas_shot_manager.set_time_range_start"
    bl_label = "Set Start Range"
    bl_description = "Set the start time range with the curent time value"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return config.getAddonPrefs().display_frame_range_tool

    def execute(self, context):
        scene = context.scene
        if scene.use_preview_range:
            scene.frame_preview_start = scene.frame_current
        else:
            scene.frame_start = scene.frame_current
        utils_ui.redrawAll(context)
        return {"FINISHED"}


class UAS_ShotManager_SetTimeRangeEnd(Operator):
    bl_idname = "uas_shot_manager.set_time_range_end"
    bl_label = "Set End Range"
    bl_description = "Set the end time range with the curent time value"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return config.getAddonPrefs().display_frame_range_tool

    def execute(self, context):
        scene = context.scene
        if scene.use_preview_range:
            scene.frame_preview_end = scene.frame_current
        else:
            scene.frame_end = scene.frame_current
        utils_ui.redrawAll(context)
        return {"FINISHED"}


class UAS_ShotManager_FrameTimeRange(Operator):
    bl_idname = "uas_shot_manager.frame_time_range"
    bl_label = "Frame Time Range"
    bl_description = "Change the VSE zoom value to fit the scene time range"
    bl_options = {"REGISTER"}

    start: IntProperty(description="Time start", default=-100000)
    end: IntProperty(description="Time end", default=-100000)
    spacerPercent: FloatProperty(
        description="Range of time, in percentage, before and after the time range", min=0.0, max=40.0, default=5
    )

    @classmethod
    def poll(cls, context):
        return config.getAddonPrefs().display_frame_range_tool

    def execute(self, context):
        currentFrame = context.scene.frame_current
        recenterCurrentFrame = False
        if context.scene.use_preview_range:
            rangeStart = context.scene.frame_preview_start if self.start < -10000 else self.start
            rangeEnd = context.scene.frame_preview_end if self.end < -10000 else self.end
        else:
            rangeStart = context.scene.frame_start if self.start < -10000 else self.start
            rangeEnd = context.scene.frame_end if self.end < -10000 else self.end

        if not rangeStart <= currentFrame <= rangeEnd:
            recenterCurrentFrame = True

        # NOTE: possibility to use the optional parameter changeTime: to prevent current time to be changed
        zoom_dopesheet_view_to_range(context, rangeStart, rangeEnd, changeTime=recenterCurrentFrame)
        utils_ui.redrawAll(context)

        return {"FINISHED"}


class UAS_ShotManager_FrameTimeRangeFromShot(Operator):
    bl_idname = "uas_shot_manager.frame_time_range_from_shot"
    bl_label = "Set scene time range with current SHOT range and zoom on it"
    bl_description = (
        "\n+ Ctrl: Zoom on SHOT range without changing time range"
        "\n+ Shift: Set scene time range with current TAKE range and zoom on it"
        "\n+ Ctrl + Shift: Zoom on TAKE range without changing time range"
        "\n+ Alt: Set the preview time range"
    )
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return config.getAddonPrefs().display_frame_range_tool

    action: StringProperty(default="DO_NOTHING")
    spacerPercent: FloatProperty(default=35)

    def invoke(self, context, event):
        self.action = "DO_NOTHING"

        # if not event.ctrl and not event.shift and not event.alt:
        #     self.action = "CURRENT"
        # elif not event.ctrl and event.shift and not event.alt:
        #     self.action = "ALL"

        # this is computed when the operator is called without a specified action
        if "DO_NOTHING" == self.action:
            if event.ctrl and not event.shift and not event.alt:
                self.action = "SHOT"
            elif not event.ctrl and not event.shift:
                self.action = "SHOT_TIMERANGE"
                if event.alt:
                    self.action += "_PREVIEW"

            elif event.ctrl and event.shift and not event.alt:
                self.action = "TAKE"
            elif not event.ctrl and event.shift:
                self.action = "TAKE_TIMERANGE"
                if event.alt:
                    self.action += "_PREVIEW"

        if "DO_NOTHING" == self.action:
            return {"FINISHED"}
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = config.getAddonProps(scene)
        currentShot = props.getCurrentShot()

        if currentShot:
            if "SHOT" in self.action:
                rangeStart = currentShot.start
                rangeEnd = currentShot.end
                bpy.ops.uas_shot_manager.frame_time_range(
                    start=rangeStart, end=rangeEnd, spacerPercent=self.spacerPercent
                )
            elif "TAKE" in self.action:
                currentTake = props.getCurrentTake()
                if currentTake and 0 < currentTake.getNumShots(ignoreDisabled=True):
                    rangeStart = currentTake.getMinFrame(ignoreDisabled=False)
                    rangeEnd = currentTake.getMaxFrame(ignoreDisabled=False)
                    bpy.ops.uas_shot_manager.frame_time_range(
                        start=rangeStart, end=rangeEnd, spacerPercent=self.spacerPercent
                    )

            if "TIMERANGE" in self.action:
                # preview time range
                if "PREVIEW" in self.action:
                    scene.use_preview_range = True
                    scene.frame_preview_start = rangeStart
                    scene.frame_preview_end = rangeEnd
                else:
                    scene.use_preview_range = False
                    scene.frame_start = rangeStart
                    scene.frame_end = rangeEnd

        return {"FINISHED"}


def draw_frame_range_tool_in_editor(self, context):
    layout = self.layout

    row = layout.row(align=True)
    row.separator(factor=3)
    row.alignment = "RIGHT"
    # row.operator("bpy.ops.time.view_all")
    row.operator("uas_shot_manager.set_time_range_start", text="", icon="TRIA_UP_BAR")
    row.operator("uas_shot_manager.frame_time_range", text="", icon="CENTER_ONLY")
    row.operator("uas_shot_manager.frame_time_range_from_shot", text="", icon="PREVIEW_RANGE")
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
    UAS_ShotManager_FrameTimeRangeFromShot,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    # lets add ourselves to the main header
    # bpy.types.TIME_MT_editor_menus.prepend(draw_frame_range_tool_in_editor)

    prefs = config.getAddonPrefs()
    display_frame_range_in_editor(prefs.display_frame_range_tool)


# vse
# bpy.types.SEQUENCER_HT_header.append(draw_frame_range_tool_in_editor)


#   bpy.types.TIME_HT_editor_buttons.append(draw_frame_range_tool_in_editor)
# bpy.types.TIME_MT_editor_menus.append(draw_item)
# bpy.types.TIME_MT_view.append(draw_item)


def unregister():
    display_frame_range_in_editor(False)

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
