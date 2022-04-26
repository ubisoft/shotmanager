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

from shotmanager.config import config

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


#############
# Shot Item
#############


class UAS_UL_ShotManager_Storyboard_Items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        props = context.scene.UAS_shot_manager_props
        current_shot_index = props.current_shot_index

        itemHasWarnings = False

        # display_getsetcurrentframe_in_shotlist = props.display_getsetcurrentframe_in_shotlist
        display_getsetcurrentframe_in_shotlist = False

        cam = "Cam" if current_shot_index == index else ""
        currentFrame = context.scene.frame_current

        # check if the camera still exists in the scene
        cameraIsValid = item.isCameraValid()
        itemHasWarnings = not cameraIsValid

        takeContainsSharedCameras = props.isThereSharedCamerasInTake()
        if takeContainsSharedCameras:
            numSharedCam = props.getNumSharedCamera(item.camera)
        else:
            numSharedCam = 2

        # draw the Duration components

        if item.enabled:
            icon = config.icons_col[f"ShotMan_Enabled{cam}"]
            if item.start <= context.scene.frame_current <= item.end:
                icon = config.icons_col[f"ShotMan_EnabledCurrent{cam}"]
        else:
            icon = config.icons_col[f"ShotMan_Disabled{cam}"]

        if item.camera is None or itemHasWarnings:
            layout.alert = True

        row = layout.row()

        row.operator("uas_shot_manager.set_current_shot", icon_value=icon.icon_id, text="").index = index

        if (
            props.display_selectbut_in_shotlist
            or props.display_color_in_shotlist
            or props.display_cameraBG_in_shotlist
            or props.display_greasepencil_in_shotlist
        ):
            row = layout.row(align=True)
            row.scale_x = 1.0
            if props.display_selectbut_in_shotlist:
                row.operator("uas_shot_manager.shots_selectcamera", text="", icon="RESTRICT_SELECT_OFF").index = index

            if props.display_notes_in_properties and props.display_notes_in_shotlist:
                row = row.row(align=True)
                row.scale_x = 1.0

                if item.hasNotes():
                    icon = config.icons_col["ShotManager_NotesData_32"]
                    row.operator("uas_shot_manager.shots_shownotes", text="", icon_value=icon.icon_id).index = index
                else:
                    icon = config.icons_col["ShotManager_NotesNoData_32"]
                    row.operator("uas_shot_manager.shots_shownotes", text="", icon_value=icon.icon_id).index = index
                    # emptyIcon = config.icons_col["General_Empty_32"]
                    # row.operator(
                    #     "uas_shot_manager.shots_shownotes", text="", icon_value=emptyIcon.icon_id
                    # ).index = index
                row.scale_x = 1.0

            if props.display_cameraBG_in_properties and props.display_cameraBG_in_shotlist:
                row = row.row(align=True)
                row.scale_x = 0.9
                # icon = "VIEW_CAMERA" if item.hasBGImage() else "BLANK1"
                icon = (
                    config.icons_col["ShotManager_CamBGShot_32"]
                    if item.hasBGImage()
                    else config.icons_col["ShotManager_CamBGNoShot_32"]
                )
                row.operator("uas_shot_manager.cambgitem", text="", icon_value=icon.icon_id).index = index
                row.scale_x = 1

            if props.display_storyboard_in_properties and props.display_greasepencil_in_shotlist:
                row = row.row(align=True)
                row.scale_x = 1.1

                gp = item.getGreasePencilObject()
                if gp is None:
                    icon = config.icons_col["ShotManager_CamGPNoShot_32"]
                    row.operator("uas_shot_manager.greasepencilitem", text="", icon_value=icon.icon_id).index = index
                else:
                    # if gp == context.active_object and context.active_object.mode == "PAINT_GPENCIL":
                    if gp.mode == "PAINT_GPENCIL":
                        icon = "GREASEPENCIL"
                        row.alert = True
                        row.operator("uas_shot_manager.greasepencilitem", text="", icon=icon).index = index
                    else:
                        icon = config.icons_col["ShotManager_CamGPShot_32"]
                        row.operator(
                            "uas_shot_manager.greasepencilitem", text="", icon_value=icon.icon_id
                        ).index = index
                row.scale_x = 0.9

            if takeContainsSharedCameras:
                camrow = row.row(align=True)
                camrow.scale_x = 0.5
                camrow.alert = 1 < numSharedCam
                camrow.operator("uas_shot_manager.list_camera_instances", text=str(numSharedCam)).index = index
                camrow.scale_x = 0.2

            if props.display_color_in_shotlist:
                row = row.row(align=True)
                row.scale_x = 0.2
                row.prop(item, "color", text="")
                row.scale_x = 0.45

        row = layout.row(align=True)

        row.scale_x = 1.0
        if props.display_enabled_in_shotlist:
            row.prop(item, "enabled", text="")
            row.separator(factor=0.9)
        row.scale_x = 0.8
        row.label(text=item.name)

        ###########
        # shot values
        ###########

        row = layout.row(align=True)
        row.scale_x = 2.0
        grid_flow = row.grid_flow(align=True, columns=7, even_columns=False)
        grid_flow.use_property_split = False
        button_x_factor = 0.6

        # currentFrameInEdit = props.
        # start
        ###########
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
            grid_flow.operator("uas_shot_manager.shottimeinedit", text=str(shotEditStart)).shotSource = f"[{index},0]"
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

        grid_flow.scale_x = 1.5

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
            row = layout.row(align=True)
            grid_flow = row.grid_flow(align=True, columns=2, even_columns=False)
            grid_flow.use_property_split = False
            # grid_flow.scale_x = button_x_factor - 0.1
            if props.display_duration_in_shotlist:
                grid_flow.scale_x = 1.7
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
                grid_flow.scale_x = 0.8
                grid_flow.prop(item, "duration_fp", text="")
            else:
                pass
                # grid_flow.scale_x = 0.1
                # grid_flow.operator("uas_shot_manager.shot_duration", text="").index = index
            grid_flow.alert = False

        # camera
        ###########
        row = layout.row(align=True)
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
            if item.camera is not None:
                grid_flow.prop(item.camera.data, "lens", text="Lens")
            else:
                grid_flow.alert = True
                grid_flow.operator("uas_shot_manager.nolens", text="-").index = index
                grid_flow.alert = False
            grid_flow.scale_x = 1.0


classes = (UAS_UL_ShotManager_Storyboard_Items,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)