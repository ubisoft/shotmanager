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
Shot properties UI
"""

from shotmanager.utils import utils_ui

from shotmanager.ui import sm_shots_global_settings_ui_cameras

# from shotmanager.ui import sm_shots_global_settings_ui_overlays

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


##################
# shot properties
##################


def draw_shot_properties(layout, context, shot):
    scene = context.scene
    props = config.getAddonProps(scene)
    # prefs = config.getAddonPrefs()
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

    layout.use_property_decorate = False
    rowSepFactor = 0.7

    def _drawPropRow(
        layout,
        leftLabel=None,
        leftProp=None,
        leftPropCheckbx=None,
        leftAlert=False,
        rightLabel=None,
        rightProp=None,
        rightUnits_x=None,
        rightPropCheckbx=None,
        rightAlert=False,
    ):
        row = mainCol.row()
        grid_flow = row.grid_flow(align=False, columns=4, even_columns=False)

        # if not cameraIsValid:
        #     grid_flow.alert = True

        leftRow = grid_flow.row(align=False)
        leftRow.alert = leftAlert
        subRowCam = leftRow.row(align=True)
        subRowCam.scale_x = 1.2

        grid_flow = subRowCam.grid_flow(align=True, columns=4, even_columns=False)
        # subSubRowCam = subRowCam.row(align=True)
        grid_flow.scale_x = 0.2
        if leftLabel is not None:
            grid_flow.label(text=leftLabel)
        grid_flow.scale_x = 1.8
        if leftProp is not None:
            grid_flow.prop(shot, leftProp, text="")
        grid_flow.scale_x = 0.8

        # camlistrow = grid_flow.row(align=True)
        # camlistrow.scale_x = 0.6
        # numSharedCam = props.getNumSharedCamera(shot.camera)
        # camlistrow.alert = 1 < numSharedCam
        # camlistrow.operator(
        #     "uas_shot_manager.list_camera_instances", text=str(numSharedCam)
        # ).index = props.selected_shot_index

        # if not cameraIsValid:
        #     grid_flow.alert = True
        # subRowCam.separator(factor=1)

        if rightLabel is not None:
            subRowCam.label(text=rightLabel)
        if leftPropCheckbx is not None:
            subRowCam.prop(props, leftPropCheckbx, text="")

        rightRow = leftRow.row(align=True)
        # c.separator( factor = 0.5 )   # prevents strange look when panel is narrow
        # rightRow.scale_x = 1

        subRightRow = rightRow.row(align=False)
        subRightRow.scale_x = 0.5

        if rightUnits_x is not None:
            subRightRow.ui_units_x = rightUnits_x

        subRightRow.prop(shot, rightProp, text="")
        # subSubRowCam.prop(shot, rightProp)

        # subRowCam.scale_x = 1.0
        rightRow.separator(factor=1)  # prevents strange look when panel is narrow
        if rightPropCheckbx is not None:
            rightRow.prop(props, rightPropCheckbx, text="")
        else:
            rightRow.separator(factor=2)  # prevents strange look when panel is narrow
        rightRow.separator(factor=0.5)  # prevents strange look when panel is narrow
        # row.separator(factor=0.5)  # prevents strange look when panel is narrow

    ######################
    # shot properties
    ######################

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

    # sepRow = mainCol.row()
    # sepRow.separator(factor=0.1)

    ####################
    # debug infos

    debugRow = mainCol.row()
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

    _drawPropRow(
        mainCol,
        leftLabel="Name:",
        leftProp="name",
        rightLabel=None,
        rightProp="color",
        rightUnits_x=0.8,
        rightPropCheckbx="display_color_in_shotlist",
    )

    ####################
    # Type
    _drawPropRow(
        mainCol,
        rightLabel="Type:",
        rightProp="shotType",
        rightPropCheckbx=None,
    )

    sepRow = mainCol.row()
    sepRow.separator(factor=rowSepFactor)

    ####################
    # Duration
    # _drawPropRow(
    #     mainCol,
    #     rightLabel="Duration:",
    #     rightProp="type",
    #     rightPropCheckbx=None,
    # )

    durationRow = mainCol.row()
    grid_flow = durationRow.grid_flow(align=True, columns=4, even_columns=False)
    # row.label ( text = r"Duration: " + str(shot.getDuration()) + " frames" )

    rowCam = grid_flow.row(align=False)
    subRowCam = rowCam.row(align=True)

    subRowCam.label(text="Duration: ")

    subRowCam.use_property_split = False
    subRowCam.prop(shot, "duration_fp", text="")
    subRowCam.prop(
        shot,
        "durationLocked",
        text="",
        icon="DECORATE_LOCKED" if shot.durationLocked else "DECORATE_UNLOCKED",
        toggle=True,
    )

    #    grid_flow.label(text=str(shot.getDuration()) + " frames")
    subRowCam.separator(factor=1.0)
    subRowCam.prop(props, "display_duration_in_shotlist", text="")
    subRowCam.separator(factor=0.5)  # prevents stange look when panel is narrow

    sepRow = mainCol.row()
    sepRow.separator(factor=rowSepFactor)

    ####################
    # camera and lens

    # _drawPropRow(
    #     mainCol,
    #     leftProp="camera",
    #     leftPropCheckbx="display_camera_in_shotlist",
    #     leftAlert=not cameraIsValid,
    #     rightProp="camera",
    #     rightPropCheckbx="display_camera_in_shotlist",
    #     rightAlert=not cameraIsValid,
    # )

    camRow = mainCol.row()
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

    ###############
    # Cam frustum
    camRow = mainCol.row()
    # camRow.scale_x = 0.8
    camRow.alignment = "RIGHT"
    if not cameraIsValid:
        camRow.alert = True
        camRow.operator("uas_shot_manager.nodisplaysize", text="No Size")
        camRow.alert = False
    else:
        camRow.prop(shot.camera.data, "display_size", text="Frustum Size")
    camRow.separator(factor=2.8)

    ####################
    # Output

    sepRow = mainCol.row()
    sepRow.scale_y = 0.8
    sepRow.separator()
    outputRow = mainCol.row()
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


def draw_shots_global_properties(layout, context):
    props = config.getAddonProps(context.scene)
    prefs = config.getAddonPrefs()

    box = layout.box()
    row = box.row()
    utils_ui.collapsable_panel(row, prefs, "shot_global_props_expanded", alert=False, text="Shots Global Control ")

    if prefs.shot_global_props_expanded:
        # rightRow = row.row()
        # rightRow.alignment = "RIGHT"
        # rightRow.prop(props.shotsGlobalSettings, "alsoApplyToDisabledShots")

        # -
        ######################

        # Shot grease pencil
        ######################

        if False and props.getCurrentLayout().display_storyboard_in_properties:

            # box.label(text="Camera Background Images:")

            subBox = box.box()
            subBox.use_property_decorate = False

            row = subBox.row()
            # row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            grid_flow.label(text="Grease Pencil:")
            grid_flow.operator("uas_shots_settings.use_greasepencil", text="Turn On").useGreasepencil = True
            grid_flow.operator("uas_shots_settings.use_greasepencil", text="Turn Off").useGreasepencil = False
            grid_flow.prop(props.shotsGlobalSettings, "greasepencilAlpha", text="Alpha")
            c = row.column()
            c.operator("uas_shot_manager.remove_grease_pencil", text="", icon="PANEL_CLOSE")

            #  row.separator(factor=0.5)  # prevents stange look when panel is narrow

        # cameras tools
        #########################
        row = box.row()
        row.use_property_decorate = False
        row.separator(factor=1.8)
        col = row.column(align=True)
        sm_shots_global_settings_ui_cameras.draw_camera_global_settings(context, col, mode="SHOT")
        # sm_shots_global_settings_ui_overlays.draw_overlays_global_settings(context, col, mode="SHOT")
