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
Retimer operators
"""

import bpy
from bpy.types import Panel, Operator
from bpy.props import IntProperty, EnumProperty, BoolProperty, FloatProperty, StringProperty

from . import retimer


##########
# Retimer
##########

class UAS_ShotManager_GetTimeRange(Operator):
    bl_idname = "uas_shot_manager.gettimerange"
    bl_label = "Get Time Range"
    bl_description = "Get current time range and use it for the time changes"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        retimerProps = context.scene.UAS_shot_manager_props.retimer
        scene = context.scene

        if scene.use_preview_range:
            retimerProps.start_frame = scene.frame_preview_start
            retimerProps.end_frame = scene.frame_preview_end
        else:
            retimerProps.start_frame = scene.frame_start
            retimerProps.end_frame = scene.frame_end

        return {"FINISHED"}


class UAS_ShotManager_GetCurrentFrameFor(Operator):
    bl_idname = "uas_shot_manager.getcurrentframefor"
    bl_label = "Get Current Frame"
    bl_description = "Use the current frame for the specifed component"
    bl_options = {"INTERNAL"}

    propertyToUpdate: StringProperty()

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        retimerProps = props.retimer

        currentFrame = scene.frame_current

        if "start_frame" == self.propertyToUpdate:
            retimerProps.start_frame = currentFrame
        elif "end_frame" == self.propertyToUpdate:
            retimerProps.end_frame = currentFrame
        else:
            retimerProps[self.propertyToUpdate] = currentFrame

        return {"FINISHED"}


class UAS_ShotManager_RetimerApply(Operator):
    bl_idname = "uas_shot_manager.retimerapply"
    bl_label = "Apply Retime"
    bl_description = "Apply retime"
    bl_options = {"UNDO"}

    def execute(self, context):
        retimerProps = context.scene.UAS_shot_manager_props.retimer
        #TOFIX wkip wkip wkip temp
        applToVSE = setattr(retimerProps, "applyToVse", True)

        if retimerProps.onlyOnSelection:
            obj_list = context.selected_objects
        else:
            obj_list = context.scene.objects

        startFrame = retimerProps.start_frame
        endFrame = retimerProps.end_frame

        if "GLOBAL_OFFSET" == retimerProps.mode:
            if 0 == retimerProps.offset_duration:
                return {"FINISHED"}

            # if offset_duration > 0 we insert time from a point far in negative time
            # if offset_duration < 0 we delete time from a point very far in negative time
            farRefPoint = -5000
            
            if 0 < retimerProps.offset_duration:
                offsetMode = "INSERT"
            else:
                offsetMode = "DELETE"

            retimer.retimeScene(
                context.scene,
                offsetMode,
                obj_list,
                farRefPoint + 1,
                abs(retimerProps.offset_duration),
                retimerProps.gap,
                1.0,
                retimerProps.pivot,
                retimerProps.applyToObjects,
                retimerProps.applyToShapeKeys,
                retimerProps.applytToGreasePencil,
                retimerProps.applyToShots,
                retimerProps.applyToVse,
            )
        elif -1 < retimerProps.mode.find("INSERT"):
            retimer.retimeScene(
                context.scene,
                #retimerProps.mode,
                "INSERT",
                obj_list,
                startFrame + 1 if "INSERT_AFTER" == retimerProps.mode else endFrame,
                retimerProps.insert_duration,
                retimerProps.gap,
                1.0,
                retimerProps.pivot,
                retimerProps.applyToObjects,
                retimerProps.applyToShapeKeys,
                retimerProps.applytToGreasePencil,
                retimerProps.applyToShots,
                retimerProps.applyToVse,
            )
        elif -1 < retimerProps.mode.find("DELETE"):
            print(f"start of deleted range: {startFrame + 1}, end:{endFrame}, duration:{endFrame - startFrame - 1}")
            retimer.retimeScene(
                context.scene,
                #retimerProps.mode,
                "DELETE",
                obj_list,
                startFrame + 1,
                endFrame - startFrame - 1,
                True,
                1.0,
                retimerProps.pivot,
                retimerProps.applyToObjects,
                retimerProps.applyToShapeKeys,
                retimerProps.applytToGreasePencil,
                retimerProps.applyToShots,
                retimerProps.applyToVse,
            )
        elif "RESCALE" == retimerProps.mode:
            retimer.retimeScene(
                context.scene,
                retimerProps.mode,
                obj_list,
                startFrame,
                endFrame - startFrame,
                True,
                retimerProps.factor,
                startFrame,
                retimerProps.applyToObjects,
                retimerProps.applyToShapeKeys,
                retimerProps.applytToGreasePencil,
                retimerProps.applyToShots,
                retimerProps.applyToVse,
            )
        elif "CLEAR_ANIM" == retimerProps.mode:
            retimer.retimeScene(
                context.scene,
                retimerProps.mode,
                obj_list,
                startFrame + 1,
                endFrame - startFrame,
                False,
                retimerProps.factor,
                retimerProps.pivot,
                retimerProps.applyToObjects,
                retimerProps.applyToShapeKeys,
                retimerProps.applytToGreasePencil,
                False,
                retimerProps.applyToVse,
            )
        else:
            retimer.retimer(
                context.scene,
                retimerProps.mode,
                obj_list,
                startFrame,
                endFrame,
                retimerProps.gap,
                retimerProps.factor,
                retimerProps.pivot,
                retimerProps.applyToObjects,
                retimerProps.applyToShapeKeys,
                retimerProps.applytToGreasePencil,
                retimerProps.applyToShots,
                retimerProps.applyToVse,
            )

        context.area.tag_redraw()
        # context.region.tag_redraw()
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

        if retimerProps.move_current_frame:
            #if retimerProps.mode == "INSERT":
            if -1 < retimerProps.mode.find("INSERT"):
                context.scene.frame_current = context.scene.frame_current + (
                    retimerProps.end_frame - retimerProps.start_frame
                )

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_GetTimeRange,
    UAS_ShotManager_GetCurrentFrameFor,
    UAS_ShotManager_RetimerApply,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
