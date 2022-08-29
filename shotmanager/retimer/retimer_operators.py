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
from bpy.types import Operator
from bpy.props import StringProperty

from . import retimer

from shotmanager.utils.utils_storyboard import getStoryboardObjects
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

##########
# Retimer
##########


class UAS_ShotManager_RetimerInitialize(Operator):
    bl_idname = "uas_shot_manager.retimerinitialize"
    bl_label = "Initialize Retimer"
    bl_description = "Initialize Retimer and all its ApplyTo settings"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        retimerProps = context.scene.UAS_shot_manager_props.retimer

        retimerProps.initialize()

        return {"FINISHED"}


class UAS_ShotManager_GetTimeRange(Operator):
    bl_idname = "uas_shot_manager.gettimerange"
    bl_label = "Get Time Range"
    bl_description = "Get current time range and use it for the time changes"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        retimeEngine = context.scene.UAS_shot_manager_props.retimer.retimeEngine
        scene = context.scene

        if scene.use_preview_range:
            retimeEngine.start_frame = scene.frame_preview_start
            retimeEngine.end_frame = scene.frame_preview_end
        else:
            retimeEngine.start_frame = scene.frame_start
            retimeEngine.end_frame = scene.frame_end

        return {"FINISHED"}


class UAS_ShotManager_GetCurrentFrameFor(Operator):
    bl_idname = "uas_shot_manager.getcurrentframefor"
    bl_label = "Get Current Frame"
    bl_description = "Use the current frame for the specifed component"
    bl_options = {"INTERNAL"}

    propertyToUpdate: StringProperty()

    def execute(self, context):
        scene = context.scene
        retimeEngine = scene.UAS_shot_manager_props.retimer.retimeEngine

        currentFrame = scene.frame_current

        if "start_frame" == self.propertyToUpdate:
            retimeEngine.start_frame = currentFrame
        elif "end_frame" == self.propertyToUpdate:
            retimeEngine.end_frame = currentFrame
        else:
            retimeEngine[self.propertyToUpdate] = currentFrame

        return {"FINISHED"}


class UAS_ShotManager_RetimerApply(Operator):
    bl_idname = "uas_shot_manager.retimerapply"
    bl_label = "Apply Retime"
    bl_description = "Apply retime"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        retimeEngine = context.scene.UAS_shot_manager_props.retimer.retimeEngine
        retimerApplyToSettings = context.scene.UAS_shot_manager_props.retimer.getCurrentApplyToSettings()

        if retimerApplyToSettings.onlyOnSelection:
            sceneObjs = [obj for obj in context.selected_objects]
        else:
            sceneObjs = [obj for obj in context.scene.objects]

        if not retimerApplyToSettings.applyToStoryboardShots:
            stbObjs = getStoryboardObjects(context.scene)
            for obj in stbObjs:
                if obj in sceneObjs:
                    sceneObjs.remove(obj)

        # startFrame = retimeEngine.start_frame
        # endFrame = retimeEngine.end_frame

        ################################
        # For the following lines keep in mind that:
        #    - retimeEngine.insert_duration is inclusive
        #    - retimeEngine.start_frame is EXCLUSIVE   (in other words it is NOT modified)
        #    - retimeEngine.end_frame is EXCLUSIVE     (in other words is the first frame to be offset)
        #
        # But retimeScene() requires INCLUSIVE range of time for the modifications (= all the frames
        # created or deleted, not the moved ones).
        # We then have to adapt the start and end values we get from retimeEngine for the function.
        ################################
        if "GLOBAL_OFFSET" == retimeEngine.mode:
            if 0 == retimeEngine.offset_duration:
                return {"FINISHED"}

            # if offset_duration > 0 we insert time from a point far in negative time
            # if offset_duration < 0 we delete time from a point very far in negative time
            farRefPoint = -100000

            retimer.retimeScene(
                context,
                "GLOBAL_OFFSET",
                retimerApplyToSettings,
                sceneObjs,
                farRefPoint + 1,
                retimeEngine.offset_duration,
                retimeEngine.gap,
            )

        elif -1 < retimeEngine.mode.find("INSERT"):
            start_excl = retimeEngine.start_frame if "INSERT_AFTER" == retimeEngine.mode else retimeEngine.end_frame - 1
            end_excl = start_excl + retimeEngine.insert_duration + 1
            # start = startFrame + 1 if "INSERT_AFTER" == retimeEngine.mode else endFrame
            print(
                # f"Retimer - Inserting time: new time range: [{start} .. {start + retimeEngine.insert_duration - 1}], duration:{retimeEngine.insert_duration}"
                f"\nRetimer - Inserting time: new created frames: [{start_excl + 1} .. {end_excl - 1}], duration: {retimeEngine.insert_duration}"
            )
            retimer.retimeScene(
                context,
                "INSERT",
                retimerApplyToSettings,
                sceneObjs,
                start_excl + 1,
                retimeEngine.insert_duration,
                retimeEngine.gap,
                1.0,
                retimeEngine.pivot,
            )

        elif -1 < retimeEngine.mode.find("DELETE"):
            start_excl = retimeEngine.start_frame
            end_excl = retimeEngine.end_frame
            duration_incl = end_excl - start_excl - 1
            print(
                f"\nRetimer - Deleting time: deleted frames: [{start_excl + 1} .. {end_excl - 1}], duration: {duration_incl}"
            )
            retimer.retimeScene(
                context,
                "DELETE",
                retimerApplyToSettings,
                sceneObjs,
                start_excl + 1,
                duration_incl,
                True,
                1.0,
                retimeEngine.pivot,
            )
        elif "RESCALE" == retimeEngine.mode:
            # *** Warning: due to the nature of the time operation the duration is not computed as for Delete Time ***
            start_excl = retimeEngine.start_frame
            end_excl = retimeEngine.end_frame
            duration_incl = end_excl - start_excl
            print(
                f"\nRetimer - Rescaling time: modified frames: [{start_excl} .. {end_excl - 1}], duration: {duration_incl}"
            )
            retimer.retimeScene(
                context,
                "RESCALE",
                retimerApplyToSettings,
                sceneObjs,
                start_excl,
                duration_incl,
                True,
                retimeEngine.factor,
                start_excl,
            )

        elif "CLEAR_ANIM" == retimeEngine.mode:
            start_excl = retimeEngine.start_frame
            end_excl = retimeEngine.end_frame
            duration_incl = end_excl - start_excl - 1
            print(
                f"\nRetimer - Deleting animation: cleared frames: [{start_excl + 1} .. {end_excl - 1}], duration:{duration_incl}"
            )
            retimer.retimeScene(
                context,
                "CLEAR_ANIM",
                retimerApplyToSettings,
                sceneObjs,
                start_excl + 1,
                duration_incl,
                False,
                retimeEngine.factor,
                retimeEngine.pivot,
            )
        else:
            print(f"*** Retimer failed: No Retimer mode named {retimeEngine.mode} ***")

        context.area.tag_redraw()
        # context.region.tag_redraw()
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

        if retimeEngine.move_current_frame:
            # if retimeEngine.mode == "INSERT":
            if -1 < retimeEngine.mode.find("INSERT"):
                context.scene.frame_current = context.scene.frame_current + (
                    retimeEngine.end_frame - retimeEngine.start_frame
                )

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_RetimerInitialize,
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
