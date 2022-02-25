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
Shot settings UI
"""

import bpy
from bpy.types import Panel
from bpy.props import StringProperty

from shotmanager.config import config
from shotmanager.utils import utils

# from shotmanager.features.soundBG import soundBG_ui as sBG
from shotmanager.features.cameraBG import cameraBG_ui as cBG
from shotmanager.features.greasepencil import greasepencil_ui as gp

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


##################
# shot properties
##################


def drawShotPropertiesToolbar(layout, context, shot):
    props = context.scene.UAS_shot_manager_props
    row = layout.row(align=False)

    cameraIsValid = shot.isCameraValid()

    # if props.display_notes_in_properties or props.display_cameraBG_in_properties or props.display_greasepencil_in_properties:
    if True:
        # leftrow = row.row(align=False)
        # leftrow.alignment = "LEFT"

        # propertiesModeStr = "Current Shot:  "
        # if "SELECTED" == scene.UAS_shot_manager_props.current_shot_properties_mode:
        #     propertiesModeStr = "Selected Shot:  "
        # leftrow.label(text=propertiesModeStr)

        buttonsrow = row.row(align=True)
        buttonsrow.alignment = "LEFT"
        buttonsrow.separator()

        subrow = buttonsrow.row()
        subrow.alert = not cameraIsValid
        subrow.scale_x = 0.9
        panelIcon = "TRIA_DOWN" if props.expand_shot_properties else "TRIA_RIGHT"
        subrow.prop(props, "expand_shot_properties", toggle=True, icon=panelIcon)

        if props.display_notes_in_properties:
            subrow = buttonsrow.row()
            subrow.scale_x = 0.9
            panelIcon = "TRIA_DOWN" if props.expand_notes_properties else "TRIA_RIGHT"
            subrow.prop(props, "expand_notes_properties", toggle=True, icon=panelIcon)
        if props.display_cameraBG_in_properties:
            subrow = buttonsrow.row()
            subrow.scale_x = 0.9
            panelIcon = "TRIA_DOWN" if props.expand_cameraBG_properties else "TRIA_RIGHT"
            subrow.prop(props, "expand_cameraBG_properties", toggle=True, icon=panelIcon)
        if props.display_greasepencil_in_properties:
            subrow = buttonsrow.row()
            subrow.scale_x = 0.9
            panelIcon = "TRIA_DOWN" if props.expand_greasepencil_properties else "TRIA_RIGHT"
            subrow.prop(props, "expand_greasepencil_properties", toggle=True, icon=panelIcon)

        buttonsrow.separator()
    else:
        propertiesModeStr = (
            "Selected Shot Notes:" if "SELECTED" == props.current_shot_properties_mode else "Current Shot Notes:"
        )
        row.label(text=propertiesModeStr)


class UAS_PT_ShotManager_ShotProperties(Panel):
    bl_label = " "  # "Current Shot Properties" # keep the space !! # Note: text is drawn in gray, not white
    bl_idname = "UAS_PT_Shot_Manager_Shot_Prefs"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng"
    bl_options = {"DEFAULT_CLOSED", "HIDE_HEADER"}
    bl_parent_id = "UAS_PT_Shot_Manager"

    tmpBGPath: StringProperty()

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShotByIndex(props.selected_shot_index)
        val = len(context.scene.UAS_shot_manager_props.getTakes()) and shot
        val = val and not props.dontRefreshUI()
        val = val and (
            props.expand_shot_properties
            or props.expand_notes_properties
            or props.expand_cameraBG_properties
            or props.expand_greasepencil_properties
        )
        return val

    def draw_header(self, context):
        props = context.scene.UAS_shot_manager_props
        layout = self.layout
        # layout.emboss = "NONE"
        propertiesModeStr = (
            "Selected Shot Notes:" if "SELECTED" == props.current_shot_properties_mode else "Current Shot Notes:"
        )
        layout.label(text=propertiesModeStr)

    def draw_header_preset(self, context):
        scene = context.scene
        layout = self.layout
        props = scene.UAS_shot_manager_props
        shot = None
        # if shotPropertiesModeIsCurrent is true then the displayed shot properties are taken from the CURRENT shot, else from the SELECTED one
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShotByIndex(props.selected_shot_index)

        cameraIsValid = shot.isCameraValid()
        itemHasWarnings = not cameraIsValid

        if itemHasWarnings:
            row = layout.row()
            layout.alignment = "RIGHT"
            row.alignment = "RIGHT"
            row.alert = True
            if shot.camera is None:
                row.label(text="*** Camera not defined ! ***")
            else:
                row.label(text="*** Referenced camera not in scene ! ***")

        versionStr = utils.addonVersion("Video Tracks")
        row = layout.row()
        row.enabled = versionStr is not None
        row.operator(
            "uas_shot_manager.go_to_video_tracks", text="", icon="SEQ_STRIP_DUPLICATE"
        ).vseSceneName = "SM_CheckSequence"

    def draw(self, context):
        scene = context.scene
        prefs = context.preferences.addons["shotmanager"].preferences
        props = scene.UAS_shot_manager_props
        iconExplorer = config.icons_col["General_Explorer_32"]

        #  shotPropertiesModeIsCurrent = not ('SELECTED' == props.current_shot_properties_mode)

        shot = None
        # if shotPropertiesModeIsCurrent is true then the displayed shot properties are taken from the CURRENT shot, else from the SELECTED one
        if "SELECTED" == props.current_shot_properties_mode:
            shot = props.getShotByIndex(props.selected_shot_index)
            propertiesModeStr = "Selected "
        else:
            shot = props.getCurrentShot()
            propertiesModeStr = "Current "

        if shot is None:
            return

        cameraIsValid = shot.isCameraValid()
        itemHasWarnings = not cameraIsValid
        currentTakeInd = props.getCurrentTakeIndex()

        layout = self.layout
        layout.use_property_decorate = False

        ######################
        # shot properties
        ######################
        if (
            not (
                props.display_notes_in_properties
                or props.display_cameraBG_in_properties
                or props.display_greasepencil_in_properties
            )
            or props.expand_shot_properties
        ):
            box = layout.box()
            box.use_property_decorate = False
            mainCol = box.column()
            row = mainCol.row()
            # extendSubRow = row.row(align=False)
            subrowleft = row.row()
            subrowleft.scale_x = 0.75
            subrowleft.label(text=propertiesModeStr + "Shot Properties:")

            if itemHasWarnings:
                subrowleft.alert = True
                if shot.camera is None:
                    subrowleft.label(text="*** Camera not defined ! ***")
                else:
                    subrowleft.scale_x = 1.1
                    subrowleft.label(text="*** Referenced camera not in scene ! ***")

            sepRow = mainCol.row()
            sepRow.separator(factor=0.5)
            col = row.column()

            ####################
            # debug infos

            debugRow = col.row()
            if config.devDebug:
                debugRow.label(
                    text=(
                        f"Current Take Ind: {currentTakeInd}, shot.getParentTakeIndex(): {shot.getParentTakeIndex()}      -       shot.parentScene: {shot.parentScene}"
                        # f"Current Take Ind: {currentTakeInd}, Shot Parent Take Ind: {shot.parentTakeIndex}, shot.getParentTakeIndex(): {shot.getParentTakeIndex()}"
                    )
                )
            # elif currentTakeInd != shot.parentTakeIndex:
            #     row = box.row()
            #     row.alert = True
            #     row.label(
            #         text=(
            #             f"!!! Error: Current Take Index is {currentTakeInd}, Shot Parent Take Index is: {shot.parentTakeIndex} !!!"
            #         )
            #     )

            ####################
            # name and color

            nameRow = col.row()
            grid_flow = nameRow.grid_flow(align=False, columns=4, even_columns=False)
            rowCam = grid_flow.row(align=False)
            subRowCam = rowCam.row(align=False)

            subRowCam.prop(shot, "name", text="Name")
            #   grid_flow.scale_x = 0.7
            # rowCam = grid_flow.row(align=False)
            subSubRow = subRowCam.row(align=True)
            subColor = subSubRow.row()
            subColor.scale_x = 0.2
            subColor.prop(shot, "color", text="")
            #   grid_flow.scale_x = 1.0
            subSubRow.separator(factor=1.0)
            subSubRow.prop(props, "display_color_in_shotlist", text="")
            subSubRow.separator(factor=0.5)  # prevents stange look when panel is narrow

            ####################
            # Duration

            durationRow = col.row()
            grid_flow = durationRow.grid_flow(align=True, columns=4, even_columns=False)
            # row.label ( text = r"Duration: " + str(shot.getDuration()) + " frames" )

            rowCam = grid_flow.row(align=False)
            subRowCam = rowCam.row(align=True)

            subRowCam.label(text="Duration: ")

            subRowCam.use_property_split = False
            subRowCam.prop(
                shot,
                "durationLocked",
                text="",
                icon="DECORATE_LOCKED" if shot.durationLocked else "DECORATE_UNLOCKED",
                toggle=True,
            )

            subRowCam.prop(shot, "duration_fp", text="")

            #    grid_flow.label(text=str(shot.getDuration()) + " frames")
            subRowCam.separator(factor=1.0)
            subRowCam.prop(props, "display_duration_in_shotlist", text="")
            subRowCam.separator(factor=0.5)  # prevents stange look when panel is narrow

            ####################
            # camera and lens

            camRow = col.row()
            grid_flow = camRow.grid_flow(align=False, columns=4, even_columns=False)

            if not cameraIsValid:
                grid_flow.alert = True

            rowCam = grid_flow.row(align=False)
            subRowCam = rowCam.row(align=True)
            subRowCam.scale_x = 1.2

            grid_flow = subRowCam.grid_flow(align=True, columns=4, even_columns=False)
            # subSubRowCam = subRowCam.row(align=True)
            grid_flow.scale_x = 0.2
            grid_flow.label(text="Camera:")
            grid_flow.scale_x = 1.8
            grid_flow.prop(shot, "camera", text="")
            grid_flow.scale_x = 0.4
            camlistrow = grid_flow.row(align=True)
            camlistrow.scale_x = 0.6
            numSharedCam = props.getNumSharedCamera(shot.camera)
            camlistrow.alert = 1 < numSharedCam
            camlistrow.operator(
                "uas_shot_manager.list_camera_instances", text=str(numSharedCam)
            ).index = props.selected_shot_index

            if not cameraIsValid:
                grid_flow.alert = True
            subRowCam.separator(factor=1)
            subRowCam.prop(props, "display_camera_in_shotlist", text="")

            subRowCam = rowCam.row(align=True)
            # c.separator( factor = 0.5 )   # prevents strange look when panel is narrow
            subRowCam.scale_x = 1
            #     row.label ( text = "Lens: " )
            subRowCam.use_property_decorate = True
            subSubRowCam = subRowCam.row(align=False)
            subSubRowCam.scale_x = 0.5
            if not cameraIsValid:
                subSubRowCam.alert = True
                subSubRowCam.operator("uas_shot_manager.nolens", text="No Lens")
                subSubRowCam.alert = False
            else:
                subSubRowCam.prop(shot.camera.data, "lens", text="Lens")
            # subRowCam.scale_x = 1.0
            subRowCam.separator(factor=1)  # prevents strange look when panel is narrow
            subRowCam.prop(props, "display_lens_in_shotlist", text="")
            subRowCam.separator(factor=0.5)  # prevents strange look when panel is narrow
            # row.separator(factor=0.5)  # prevents strange look when panel is narrow

            ####################
            # Output

            sepRow = col.row()
            sepRow.scale_y = 0.8
            sepRow.separator()
            outputRow = col.row()
            grid_flow = outputRow.grid_flow(align=False, columns=3, even_columns=False)
            rowCam = grid_flow.row(align=False)
            subRowCam = rowCam.row(align=True)

            subRowCam.label(text="Output: ")
            subRowCam.label(
                text="<Render Root Path> \\ "
                + shot.getParentTake().getName_PathCompliant()
                + " \\ "
                + shot.getOutputMediaPath("SH_VIDEO", providePath=False)
            )
            subRowCam.operator(
                "uas_shot_manager.open_explorer", emboss=True, icon_value=iconExplorer.icon_id, text=""
            ).path = shot.getOutputMediaPath("SH_VIDEO", providePath=False)
            subRowCam.separator(factor=0.5)  # prevents strange look when panel is narrow

            # row.prop ( context.props, "display_duration_in_shotlist", text = "" )

        ######################
        # Notes
        ######################
        if props.display_notes_in_properties and props.expand_notes_properties:
            panelIcon = "TRIA_DOWN" if prefs.shot_notes_expanded else "TRIA_RIGHT"

            box = layout.box()
            box.use_property_decorate = False

            row = box.row()
            # row.prop(prefs, "shot_notes_expanded", text="", icon=panelIcon, emboss=False)
            # row.separator(factor=1.0)
            c = row.column()
            # grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            subrow = c.row()
            # subrow.label(text="Shot Notes:")

            propertiesModeStr = (
                "Selected Shot Notes:" if "SELECTED" == props.current_shot_properties_mode else "Current Shot Notes:"
            )
            subrow.label(text=propertiesModeStr)

            subrow.prop(props, "display_notes_in_shotlist", text="")
            #    subrow.separator(factor=0.5)

            # if prefs.shot_notes_expanded:
            row = box.row()
            row.separator(factor=1.0)
            col = row.column()
            col.scale_y = 0.95
            col.prop(shot, "note01", text="")
            col.prop(shot, "note02", text="")
            col.prop(shot, "note03", text="")
            row.separator(factor=1.0)
            box.separator(factor=0.1)

        ######################
        # Camera background images
        ######################
        if props.display_cameraBG_in_properties and props.expand_cameraBG_properties:
            cBG.draw_cameraBG_shot_properties(self, context, shot)
            cBG.draw_cameraBG_global_properties(self, context)

        ######################
        # Grease pencil
        ######################
        if props.display_greasepencil_in_properties and props.expand_greasepencil_properties:
            gp.draw_greasepencil_shot_properties(self, context, shot)
            gp.draw_greasepencil_global_properties(self, context)


classes = (UAS_PT_ShotManager_ShotProperties,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

