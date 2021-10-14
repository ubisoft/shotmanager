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

        if retimerProps.onlyOnSelection:
            obj_list = context.selected_objects
        else:
            obj_list = context.scene.objects

        # startFrame = retimerProps.start_frame
        # endFrame = retimerProps.end_frame

        ################################
        # For the following lines keep in mind that:
        #    - retimerProps.insert_duration is inclusive
        #    - retimerProps.start_frame is EXCLUSIVE   (in other words it is NOT modified)
        #    - retimerProps.end_frame is EXCLUSIVE     (in other words is the first frame to be offset)
        #
        # But retimeScene() requires INCLUSIVE range of time for the modifications (= all the frames
        # created or deleted, not the moved ones).
        # We then have to adapt the start and end values we get from retimerProps for the function.
        ################################
        if "GLOBAL_OFFSET" == retimerProps.mode:
            if 0 == retimerProps.offset_duration:
                return {"FINISHED"}

            # if offset_duration > 0 we insert time from a point far in negative time
            # if offset_duration < 0 we delete time from a point very far in negative time
            farRefPoint = -10000

            if 0 < retimerProps.offset_duration:
                offsetMode = "INSERT"
            else:
                offsetMode = "DELETE"

            retimer.retimeScene(
                context,
                retimerProps,
                offsetMode,
                obj_list,
                farRefPoint + 1,
                abs(retimerProps.offset_duration),
                retimerProps.gap,
                1.0,
                retimerProps.pivot,
            )

        elif -1 < retimerProps.mode.find("INSERT"):
            start_excl = retimerProps.start_frame if "INSERT_AFTER" == retimerProps.mode else retimerProps.end_frame - 1
            end_excl = start_excl + retimerProps.insert_duration + 1
            # start = startFrame + 1 if "INSERT_AFTER" == retimerProps.mode else endFrame
            print(
                # f"Retimer - Inserting time: new time range: [{start} .. {start + retimerProps.insert_duration - 1}], duration:{retimerProps.insert_duration}"
                f"\nRetimer - Inserting time: new created frames: [{start_excl + 1} .. {end_excl - 1}], duration: {retimerProps.insert_duration}"
            )
            retimer.retimeScene(
                context,
                retimerProps,
                # retimerProps.mode,
                "INSERT",
                obj_list,
                start_excl + 1,
                retimerProps.insert_duration,
                retimerProps.gap,
                1.0,
                retimerProps.pivot,
            )

        elif -1 < retimerProps.mode.find("DELETE"):
            start_excl = retimerProps.start_frame
            end_excl = retimerProps.end_frame
            duration_incl = end_excl - start_excl - 1
            print(
                f"\nRetimer - Deleting time: deleted frames: [{start_excl + 1} .. {end_excl - 1}], duration: {duration_incl}"
            )
            retimer.retimeScene(
                context,
                retimerProps,
                # retimerProps.mode,
                "DELETE",
                obj_list,
                start_excl + 1,
                duration_incl,
                True,
                1.0,
                retimerProps.pivot,
            )
        elif "RESCALE" == retimerProps.mode:
            # *** Warning: due to the nature of the time operation the duration is not computed as for Delete Time ***
            start_excl = retimerProps.start_frame
            end_excl = retimerProps.end_frame
            duration_incl = end_excl - start_excl
            print(
                f"\nRetimer - Rescaling time: modified frames: [{start_excl} .. {end_excl - 1}], duration: {duration_incl}"
            )
            retimer.retimeScene(
                context,
                retimerProps,
                retimerProps.mode,
                obj_list,
                start_excl,
                duration_incl,
                True,
                retimerProps.factor,
                start_excl,
            )

        elif "CLEAR_ANIM" == retimerProps.mode:
            start_excl = retimerProps.start_frame
            end_excl = retimerProps.end_frame
            duration_incl = end_excl - start_excl - 1
            print(
                f"\nRetimer - Deleting animation: cleared frames: [{start_excl + 1} .. {end_excl - 1}], duration:{duration_incl}"
            )
            retimer.retimeScene(
                context,
                retimerProps,
                retimerProps.mode,
                obj_list,
                start_excl + 1,
                duration_incl,
                False,
                retimerProps.factor,
                retimerProps.pivot,
            )
        else:
            print(f"*** Retimer failed: No Retimer mode named {retimerProps.mode} ***")

        context.area.tag_redraw()
        # context.region.tag_redraw()
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

        if retimerProps.move_current_frame:
            # if retimerProps.mode == "INSERT":
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
