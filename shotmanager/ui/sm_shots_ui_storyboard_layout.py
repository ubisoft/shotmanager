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
UI for the shots - storyboard layout - in the shots list component
"""

import bpy

from . import sm_shots_ui_common

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


#############
# Shot Item
#############


class UAS_UL_ShotManager_Storyboard_Items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        props = config.getAddonProps(context.scene)
        current_shot_index = props.current_shot_index
        scene = context.scene

        itemHasWarnings = False

        # display_getsetcurrentframe_in_shotlist = props.display_getsetcurrentframe_in_shotlist
        display_getsetcurrentframe_in_shotlist = False

        currentIconIsOrange = True
        # orange = "_Orange" if currentIconIsOrange else ""
        # cam = f"Cam{orange}" if current_shot_index == index else ""
        currentFrame = context.scene.frame_current

        # check if the camera still exists in the scene
        cameraIsValid = item.isCameraValid()
        itemHasWarnings = not cameraIsValid

        takeContainsSharedCameras = props.isThereSharedCamerasInTake()
        if takeContainsSharedCameras:
            numSharedCam = props.getNumSharedCamera(item.camera)
        else:
            numSharedCam = 2

        # draw shot type
        ##########################

        mainRow = layout.row(align=True)

        sm_shots_ui_common.drawShotType(scene, mainRow, props, item, index, current_shot_index, itemHasWarnings)

        mainRow.separator(factor=0.8)

        if props.display_selectbut_in_shotlist or props.display_color_in_shotlist or props.display_cameraBG_in_shotlist:
            row = mainRow.row(align=True)
            row.scale_x = 1.0
            if props.display_selectbut_in_shotlist:
                row.operator("uas_shot_manager.shots_selectcamera", text="", icon="RESTRICT_SELECT_OFF").index = index

            if props.getCurrentLayout().display_cameraBG_in_properties and props.display_cameraBG_in_shotlist:
                camRow = row.row(align=True)
                camRow.scale_x = 0.9
                # icon = "VIEW_CAMERA" if item.hasBGImage() else "BLANK1"
                icon = (
                    config.icons_col["ShotManager_CamBGShot_32"]
                    if item.hasBGImage()
                    else config.icons_col["ShotManager_CamBGNoShot_32"]
                )
                camRow.operator("uas_shot_manager.cambgitem", text="", icon_value=icon.icon_id).index = index
                camRow.scale_x = 1

            if takeContainsSharedCameras:
                camrow = row.row(align=True)
                camrow.scale_x = 0.5
                camrow.alert = 1 < numSharedCam
                camrow.operator("uas_shot_manager.list_camera_instances", text=str(numSharedCam)).index = index
                camrow.scale_x = 0.2

            if props.display_color_in_shotlist:
                colRow = row.row(align=True)
                colRow.scale_x = 0.2
                colRow.prop(item, "color", text="")
                colRow.scale_x = 0.45

        if props.display_greasepencil_in_shotlist or props.getCurrentLayout().display_storyboard_in_properties:

            mainRow.separator(factor=0.8)
            stbRow = mainRow.row(align=True)
            stbRow.scale_x = 1.0

            if props.getCurrentLayout().display_storyboard_in_properties and props.display_greasepencil_in_shotlist:
                sm_shots_ui_common.drawStoryboardRow(stbRow, props, item, index)

            if props.getCurrentLayout().display_notes_in_properties and props.display_notes_in_shotlist:
                sm_shots_ui_common.drawNotesRow(stbRow, props, item, index)

        mainRow.separator(factor=0.6)
        sm_shots_ui_common.drawShotName(mainRow, props, item)

        ###########
        # shot values
        ###########

        row = mainRow.row(align=True)
        row.scale_x = 1.2
        grid_flow = row.grid_flow(align=True, columns=7, even_columns=False)
        grid_flow.use_property_split = False
        button_x_factor = 0.6

        # currentFrameInEdit = props.
        # start
        ###########
        if False:
            if props.display_edit_times_in_shotlist:
                # grid_flow.scale_x = button_x_factor
                # if display_getsetcurrentframe_in_shotlist:
                #     grid_flow.operator(
                #         "uas_shot_manager.getsetcurrentframe", text="", icon="TRIA_DOWN_BAR"
                #     ).shotSource = f"[{index},0]"

                grid_flow.scale_x = 0.3
                shotEditStart = item.getEditStart()
                if currentFrame == item.start:
                    if props.highlight_all_shot_frames or current_shot_index == index:
                        grid_flow.alert = True
                # grid_flow.prop(item, "start", text="")
                # grid_flow.label(text=str(shotDuration))
                grid_flow.operator(
                    "uas_shot_manager.shottimeinedit", text=str(shotEditStart)
                ).shotSource = f"[{index},0]"
                grid_flow.alert = False
            else:
                grid_flow.scale_x = button_x_factor
                if display_getsetcurrentframe_in_shotlist:
                    grid_flow.operator(
                        "uas_shot_manager.getsetcurrentframe", text="", icon="TRIA_DOWN_BAR"
                    ).shotSource = f"[{index},0]"

                grid_flow.scale_x = 0.3
                if currentFrame == item.start:
                    if props.highlight_all_shot_frames or current_shot_index == index:
                        grid_flow.alert = True
                grid_flow.prop(item, "start", text="")
                grid_flow.alert = item.camera is None or itemHasWarnings

        # duration
        ###########

        # display_duration_after_time_range
        # if not props.display_duration_after_time_range:
        #     grid_flow.scale_x = button_x_factor - 0.1
        #     grid_flow.prop(
        #         item,
        #         "durationLocked",
        #         text="",
        #         icon="DECORATE_LOCKED" if item.durationLocked else "DECORATE_UNLOCKED",
        #         toggle=True,
        #     )

        #     if props.highlight_all_shot_frames or current_shot_index == index:
        #         if item.start <= currentFrame and currentFrame <= item.end:
        #             grid_flow.alert = True

        #     if props.display_duration_in_shotlist:
        #         grid_flow.scale_x = 0.3
        #         grid_flow.prop(item, "duration_fp", text="")
        #     else:
        #         grid_flow.scale_x = 0.05
        #         grid_flow.operator("uas_shot_manager.shot_duration", text="").index = index
        #     grid_flow.alert = item.camera is None or itemHasWarnings
        # else:
        # grid_flow.scale_x = 1.5

        grid_flow.scale_x = 1.2

        # end
        ###########
        # if props.display_edit_times_in_shotlist:
        #     grid_flow.scale_x = 0.4
        #     shotEditEnd = item.getEditEnd()
        #     if currentFrame == item.end:
        #         if props.highlight_all_shot_frames or current_shot_index == index:
        #             grid_flow.alert = True
        #     grid_flow.operator("uas_shot_manager.shottimeinedit", text=str(shotEditEnd)).shotSource = f"[{index},1]"
        #     grid_flow.alert = False

        #     # grid_flow.scale_x = button_x_factor - 0.2
        #     # if display_getsetcurrentframe_in_shotlist:
        #     #     grid_flow.operator(
        #     #         "uas_shot_manager.getsetcurrentframe", text="", icon="TRIA_DOWN_BAR"
        #     #     ).shotSource = f"[{index},1]"
        # else:
        #     grid_flow.scale_x = 0.4
        #     if currentFrame == item.end:
        #         if props.highlight_all_shot_frames or current_shot_index == index:
        #             grid_flow.alert = True
        #     grid_flow.prop(item, "end", text="")
        #     grid_flow.alert = item.camera is None or itemHasWarnings

        #     grid_flow.scale_x = button_x_factor - 0.2
        #     if display_getsetcurrentframe_in_shotlist:
        #         grid_flow.operator(
        #             "uas_shot_manager.getsetcurrentframe", text="", icon="TRIA_DOWN_BAR"
        #         ).shotSource = f"[{index},1]"

        if props.display_duration_after_time_range:
            # mainRow.separator(factor=0.6)
            drawDurationAfterTimeRange(mainRow, props, item, currentFrame, current_shot_index, index)

        # camera
        ###########
        row = mainRow.row(align=True)
        grid_flow = row.grid_flow(align=True, columns=3, even_columns=False)
        grid_flow.use_property_split = False
        grid_flow.scale_x = 2.6

        if props.display_camera_in_shotlist:
            if item.camera is None:
                grid_flow.alert = True
            grid_flow.prop(item, "camera", text="")
            grid_flow.scale_x = 0.3

            camlistrow = grid_flow.row(align=True)
            # camlistrow.scale_x = 1.0
            #  numSharedCam = props.getNumSharedCamera(item.camera)
            camlistrow.alert = 1 < numSharedCam
            camlistrow.operator("uas_shot_manager.list_camera_instances", text=str(numSharedCam)).index = index
            if item.camera is None:
                grid_flow.alert = False

        if props.display_lens_in_shotlist:
            grid_flow.scale_x = 0.4
            grid_flow.use_property_decorate = True
            if item.isCameraValid():
                grid_flow.prop(item.camera.data, "lens", text="Lens")
            else:
                grid_flow.alert = True
                grid_flow.operator("uas_shot_manager.nolens", text="-").index = index
                grid_flow.alert = False
            grid_flow.scale_x = 1.0


#####################################################################
# Functions
#####################################################################


def drawDurationAfterTimeRange(layout, props, item, currentFrame, current_shot_index, index):
    displayDurationLocked = False

    row = layout.row(align=displayDurationLocked)
    grid_flow = row.grid_flow(align=displayDurationLocked, columns=2, even_columns=False)
    grid_flow.use_property_split = False
    # grid_flow.scale_x = button_x_factor - 0.1
    if props.display_duration_in_shotlist:
        grid_flow.scale_x = 1.2
    if displayDurationLocked:
        grid_flow.prop(
            item,
            "durationLocked",
            text="",
            icon="DECORATE_LOCKED" if item.durationLocked else "DECORATE_UNLOCKED",
            toggle=True,
        )

    if props.highlight_all_shot_frames or current_shot_index == index:
        if item.start <= currentFrame and currentFrame <= item.end:
            grid_flow.alert = True

    if props.display_duration_in_shotlist:
        grid_flow.scale_x = 0.6
        grid_flow.prop(item, "duration_fp", text="")
    else:
        pass
        # grid_flow.scale_x = 0.1
        # grid_flow.operator("uas_shot_manager.shot_duration", text="").index = index
    grid_flow.alert = False


#####################################################################

classes = (UAS_UL_ShotManager_Storyboard_Items,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
