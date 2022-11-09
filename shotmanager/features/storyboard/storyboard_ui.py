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
Greasep pencil and storyboard draw functions for UI
"""

# from shotmanager.utils import utils
from shotmanager.utils import utils_ui
from shotmanager.utils import utils_greasepencil
from shotmanager.utils.utils_ui import propertyColumn

from shotmanager.ui import sm_shots_global_settings_ui_cameras
from shotmanager.ui import sm_shots_global_settings_ui_overlays


from shotmanager.config import config

from . import storyboard_drawing_ui as drawing_ui


def draw_greasepencil_shot_properties(layout, context, shot):
    props = config.getAddonProps(context.scene)
    prefs = config.getAddonPrefs()

    if shot is None:
        return

    propertiesModeStr = "Selected " if "SELECTED" == props.current_shot_properties_mode else "Current "
    hSepFactor = 0.5

    devDebug_displayAdv = config.devDebug and False

    cameraIsValid = shot.isCameraValid()
    if not cameraIsValid:
        box = layout.box()
        row = box.row()
        row.label(text=propertiesModeStr + "Shot Grease Pencil:")
        row.alert = True
        if shot.camera is None:
            row.label(text="*** Camera not defined ! ***")
        else:
            row.scale_x = 1.1
            row.label(text="*** Referenced camera not in scene ! ***")
        return

    shotIndex = props.getShotIndex(shot)

    gpProperties = shot.getGreasePencilProps(mode="STORYBOARD")

    gp_child = None
    gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)

    box = layout.box()
    box.use_property_decorate = False
    col = box.column()
    row = col.row(align=True)

    # grease pencil
    ################

    extendSubRow = row.row(align=True)
    # extendSubRow.alignment = "RIGHT"
    subrowleft = extendSubRow.row()
    #  subrowleft.alignment = "EXPAND"
    # subrowleft.scale_x = 0.8

    subsubrowleft = subrowleft.row(align=True)
    subsubrowleft.alignment = "LEFT"
    subsubrowleft.label(text=propertiesModeStr + "Shot Storyboard Frame:")

    # panelIcon = "TRIA_DOWN" if prefs.shot_greasepencil_expanded and gp_child is not None else "TRIA_RIGHT"
    # extendSubRow.prop(prefs, "shot_greasepencil_expanded", text="", icon=panelIcon, emboss=False)
    # row.separator(factor=1.0)

    # subRow.scale_x = 0.6
    # subRow.label(text="Grease Pencil:")

    if gp_child is None:
        # extendSubRow.enabled = False
        subrowright = row.row(align=True)
        subrowright.alignment = "RIGHT"
        subrowright.label(text="Add a Storyboard Frame Here ")
        subrowright.label(icon="FORWARD")
        subrowright.separator(factor=1.0)

        row.operator("uas_shot_manager.add_grease_pencil", text="", icon="ADD", emboss=True).shotName = shot.name
        row.separator(factor=1.4)
        row.prop(props, "display_greasepencil_in_shotlist", text="")
        # subSubRow.separator(factor=0.5)  # prevents stange look when panel is narrow

    elif gpProperties is None:
        subRow = extendSubRow.row(align=False)
        subRow.alert = True
        subRow.label(text="*** No gpStoryboard property on shot ***")
        subRow = extendSubRow.row(align=False)
        subRow.operator("uas_shot_manager.add_grease_pencil", text="", icon="ADD", emboss=True).shotName = shot.name

    else:
        # extendSubRow.alignment = "EXPAND"
        subRow = extendSubRow.row(align=False)
        subRow.separator(factor=0.9)
        # subRow.ui_units_x = 8
        subRow.alignment = "RIGHT"

        propSubRow = subRow.row(align=True)
        propSubRow.ui_units_x = 5
        propSubRow.prop(gpProperties, "visibility", text="")
        propSubRow.prop(gp_child, "hide_select", text="")

        subRow.operator("uas_shot_manager.remove_grease_pencil", text="", icon="PANEL_CLOSE").shotIndex = shotIndex
        subRow.prop(props, "display_greasepencil_in_shotlist", text="")

        ################
        # Name and visibility tools
        ################
        # extendSubRow.alignment = "EXPAND"
        row = col.row()
        row.separator(factor=0.2)

        subRow = col.row(align=False)
        # subRow.scale_x = 0.8
        leftSubRow = subRow.row(align=True)
        leftSubRow.alignment = "LEFT"
        # leftSubRow.separator(factor=1)

        gpToolsRow = leftSubRow.row(align=True)
        # gpToolsRow.alignment = "RIGHT"
        gpToolsRow.scale_x = 2
        gpToolsRow.operator(
            "uas_shot_manager.select_shot_grease_pencil", text="", icon="RESTRICT_SELECT_OFF"
        ).index = shotIndex
        if config.devDebug or True:
            gpToolsRow.operator(
                "uas_shot_manager.update_grease_pencil", text="", icon="FILE_REFRESH"
            ).shotIndex = shotIndex
        gpToolsRow.scale_x = 1

        textSubRow = subRow.row(align=True)
        textSubRow.alignment = "LEFT"
        # gpToolsRow.scale_x = 2
        # leftSubRow.separator(factor=1)
        textSubRow.label(text="  GP: ")
        textSubRow.label(text=gp_child.name)

        if config.devDebug:
            infoRow = textSubRow.row()
            infoRow.alignment = "RIGHT"
            if gp_child == context.object:
                infoRow.label(text="   Same as Context")
            else:
                infoRow.alert = True
                infoRow.label(text="   Diff from Context")

        rightSubRow = subRow.row(align=True)
        rightSubRow.alignment = "RIGHT"

        # detach GP
        rightSubRow.operator(
            "uas_shot_manager.detach_storyboard_frame", text="", icon="DECORATE_LIBRARY_OVERRIDE"
        ).shotIndex = shotIndex

        # Grease Pencil tools
        ################
        if devDebug_displayAdv:

            # subSubRow = rightSubRow.row()
            # subSubRow.alignment = "RIGHT"
            # gpToolsSplit = subSubRow.split(factor=0.4)
            # gpToolsRow = gpToolsSplit.row(align=True)

            gpToolsRow = rightSubRow
            gpToolsRow.alignment = "RIGHT"
            gpToolsRow.scale_x = 2
            gpToolsRow.operator(
                "uas_shot_manager.select_shot_grease_pencil", text="", icon="RESTRICT_SELECT_OFF"
            ).index = shotIndex

            if gp_child.mode == "PAINT_GPENCIL":
                icon = "GREASEPENCIL"
                gpToolsRow.alert = True
                gpToolsRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon=icon)
                gpToolsRow.alert = False
                # bpy.ops.gpencil.paintmode_toggle()
            else:
                # wkip operator removed ***
                # gpToolsRow.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon="OUTLINER_OB_GREASEPENCIL")

                opMode = "DRAW" if props.isContinuousGPEditingModeActive() else "SELECT"

                # if gp == context.active_object and context.active_object.mode == "PAINT_GPENCIL":
                # if gp.mode == "PAINT_GPENCIL":
                icon = "GREASEPENCIL"
                gpToolsRow.alert = True
                op = gpToolsRow.operator("uas_shot_manager.greasepencil_select_and_draw", text="ttt", icon=icon)
                op.index = shotIndex
                op.toggleDrawEditing = True
                op.mode = opMode

            gpToolsRow.operator(
                "uas_shot_manager.update_grease_pencil", text="", icon="FILE_REFRESH"
            ).shotIndex = shotIndex

        # distance ##############
        #############
        # subRow.alignment = "LEFT"
        # gpDistRow = gpToolsSplit.row(align=True)
        # gpDistRow.scale_x = 1.2
        # gpDistRow.use_property_split = True
        # gpDistRow.alignment = "RIGHT"
        # # gpDistRow.label(text="Distance:")
        # gpDistRow.prop(gpProperties, "distanceFromOrigin", text="Distance:", slider=True)

        # Debug settings
        ################
        # if devDebug_displayAdv:
        #     subRow = box.row(align=False)
        #     leftSubRow = subRow.row(align=True)
        #     leftSubRow.alignment = "LEFT"

        #     rightSubRow = subRow.row(align=True)
        #     rightSubRow.alignment = "RIGHT"
        #     rightSubRow.prop(gp_child, "hide_select", text="")
        #     rightSubRow.prop(gp_child, "hide_viewport", text="")
        #     rightSubRow.prop(gp_child, "hide_render", text="")

        #####################
        # Drawing tools
        #####################
        gpIsStoryboardFrame = True
        editedGpencil = gp_child
        leftSepFactor = 0.1
        objIsGP = True

        row = col.row()
        row.separator(factor=1.0)
        drawing_ui.drawDrawingToolbarRow(
            context, col, props, editedGpencil, gpIsStoryboardFrame, shotIndex, leftSepFactor, objIsGP
        )

        row = col.row()
        row.separator(factor=1.2)
        drawing_ui.drawDrawingPlaybarRow(context, col, props, editedGpencil, leftSepFactor, objIsGP)

        # row = col.row()
        # row.separator(factor=0.5)
        # drawing_ui.drawDrawingMatRow(context, col, props, objIsGP)

        #####################
        # Canvas
        #####################

        # row = col.row()
        # row.separator(factor=hSepFactor)

        utils_ui.separatorLine(col, padding_bottom=1.4, padding_top=0.6)

        row = col.row()

        canvasSplitRow = row.split(factor=0.32)
        canvasTitleRow = utils_ui.collapsable_panel(
            canvasSplitRow, prefs, "stb_canvas_props_expanded", alert=False, text="Canvas"
        )
        #  canvasTitleRow.label(text="Canvas")
        # canvasSplitRow.separator(factor=0.1)

        props = config.getAddonProps(context.scene)
        canvasPreset = props.stb_frameTemplate.getPresetByID("CANVAS")
        canvasName = "_Canvas_" if canvasPreset is None else canvasPreset.layerName

        canvasLayer = utils_greasepencil.get_grease_pencil_layer(
            gp_child, gpencil_layer_name=canvasName, create_layer=False
        )
        if canvasLayer is None:
            # utils_greasepencil.get_grease_pencil_layer
            canvasSplitRow.operator("uas_shot_manager.add_canvas_to_grease_pencil", text="+").gpName = gp_child.name
        else:
            rightCanvasSplitRow = canvasSplitRow.row()
            rightCanvasSplitRow.prop(gpProperties, "canvasOpacity", slider=True, text="Opacity")
            rightCanvasSplitRow.prop(canvasLayer, "hide", text="")

        if prefs.stb_canvas_props_expanded:

            col.separator(factor=0.5)

            canvasRow = col.row()
            canvasRow.separator(factor=2.0)
            canvasBox = canvasRow.box()
            canvasCol = canvasBox.column()

            splitRow = canvasCol.split(factor=0.3)
            splitRow.label(text=" Size:")
            rightSplitRow = splitRow.row(align=True)
            # rightSplitRow.use_property_split = False
            # rightSplitRow.use_property_decorate = False
            rightSplitRow.prop(gpProperties, "canvasSize", text="", slider=True)

            splitRow = canvasCol.split(factor=0.3)
            # splitRow.separator(factor=2)
            splitRow.label(text=" Distance:")
            splitRow.prop(gpProperties, "distanceFromOrigin", text="", slider=True)

            col.separator(factor=0.9)

        # animation
        ################
        # panelIcon = "TRIA_DOWN" if prefs.stb_anim_props_expanded else "TRIA_RIGHT"
        animRowTitle = col.row()

        channelsLocked = (
            gp_child.lock_location[0]
            and gp_child.lock_location[1]
            and gp_child.lock_location[2]
            and gp_child.lock_rotation[0]
            and gp_child.lock_rotation[1]
            and gp_child.lock_rotation[2]
            and gp_child.lock_scale[0]
            and gp_child.lock_scale[1]
            and gp_child.lock_scale[2]
        )

        collapsable_panel_animateTransformations(
            animRowTitle,
            prefs,
            "stb_anim_props_expanded",
            text="Animate Frame Transformation",
            gp_child=gp_child,
            lockItem="ALL",
            depressedOp=not channelsLocked,
        )
        if prefs.stb_anim_props_expanded:
            lockSplitFactor = 0.9

            def _drawAxisText(propsCol, axisText, warningMessage=False):
                ZPropsRow = propsCol.row(align=True)
                ZPropsRow.alignment = "RIGHT"
                textPropsRow = ZPropsRow.row(align=True)
                textPropsRow.alignment = "RIGHT"
                textPropsRow.ui_units_x = 4
                if warningMessage:
                    textPropsRow.alert = True
                    textPropsRow.label(text="Don't Change !")
                else:
                    textPropsRow.label(text=" ")

                axisPropsRow = ZPropsRow.row(align=True)
                axisPropsRow.alignment = "RIGHT"
                axisPropsRow.label(text=axisText)

            col.separator(factor=0.5)
            animRow = col.row()
            animRow.separator(factor=2.0)
            animBox = animRow.box()
            transformCol = animBox.column()

            # location
            ###################
            locLocked = not (gp_child.lock_location[0] and gp_child.lock_location[1] and gp_child.lock_location[2])
            transformCol.label(text="Location:")
            transformRow = transformCol.row()
            transformRow.alignment = "CENTER"
            transformRow.use_property_split = True
            transformRow.use_property_decorate = True
            propsCol = propertyColumn(transformRow)
            propsCol.enabled = locLocked

            _drawAxisText(propsCol, "X", warningMessage=False)
            _drawAxisText(propsCol, "Y", warningMessage=False)
            _drawAxisText(propsCol, "Z", warningMessage=True)

            rightRow = transformRow.row()
            rightRow.alignment = "RIGHT"

            rightSubRow = rightRow.row()
            transfoRow = rightSubRow.row()
            transfoRow.enabled = locLocked
            transfoRow.prop(gp_child, "location", text="")
            splitRightCol = rightSubRow.column()

            subCol = splitRightCol.column(align=True)
            draw_lock_but(subCol, gp_child, "LOCK_LOCATION_X")
            draw_lock_but(subCol, gp_child, "LOCK_LOCATION_Y")
            draw_lock_but(subCol, gp_child, "LOCK_LOCATION_Z")

            # rotation
            ###################
            transformCol.separator(factor=0.5)
            rotLocked = not (gp_child.lock_rotation[0] and gp_child.lock_rotation[1] and gp_child.lock_rotation[2])
            transformCol.label(text="Rotation:")
            transformRow = transformCol.row()
            transformRow.alignment = "CENTER"
            transformRow.use_property_split = True
            transformRow.use_property_decorate = True
            propsCol = propertyColumn(transformRow)
            propsCol.enabled = rotLocked

            _drawAxisText(propsCol, "X", warningMessage=True)
            _drawAxisText(propsCol, "Y", warningMessage=True)
            _drawAxisText(propsCol, "Z", warningMessage=False)

            rightRow = transformRow.row()
            rightRow.alignment = "RIGHT"

            rightSubRow = rightRow.row()
            transfoRow = rightSubRow.row()
            transfoRow.enabled = rotLocked
            transfoRow.prop(gp_child, "rotation_euler", text="")
            splitRightCol = rightSubRow.column()

            subCol = splitRightCol.column(align=True)
            draw_lock_but(subCol, gp_child, "LOCK_ROTATION_X")
            draw_lock_but(subCol, gp_child, "LOCK_ROTATION_Y")
            draw_lock_but(subCol, gp_child, "LOCK_ROTATION_Z")

            # scale
            ###################
            transformCol.separator(factor=0.5)
            scaleLocked = not (gp_child.lock_scale[0] and gp_child.lock_scale[1] and gp_child.lock_scale[2])
            transformCol.label(text="Scale:")
            transformRow = transformCol.row()
            transformRow.alignment = "CENTER"
            transformRow.use_property_split = True
            transformRow.use_property_decorate = True
            propsCol = propertyColumn(transformRow)
            propsCol.enabled = scaleLocked

            _drawAxisText(propsCol, "X", warningMessage=False)
            _drawAxisText(propsCol, "Y", warningMessage=False)
            _drawAxisText(propsCol, "Z", warningMessage=False)

            rightRow = transformRow.row()
            rightRow.alignment = "RIGHT"

            rightSubRow = rightRow.row()
            transfoRow = rightSubRow.row()
            transfoRow.enabled = scaleLocked
            transfoRow.prop(gp_child, "scale", text="")
            splitRightCol = rightSubRow.column()

            subCol = splitRightCol.column(align=True)
            draw_lock_but(subCol, gp_child, "LOCK_SCALE_X")
            draw_lock_but(subCol, gp_child, "LOCK_SCALE_Y")
            draw_lock_but(subCol, gp_child, "LOCK_SCALE_Z")

            transformRow = transformCol.row()
            transformRow.separator(factor=hSepFactor)

            # motion path
            ###################

            transformRow = animBox.row(align=False)
            transformRow.separator(factor=4)
            transformRowSplit = transformRow.split(factor=0.32)
            # transformRow.alignment = "RIGHT"
            # transformRow.ui_units_x = 2
            transformRowSplit.label(text="Motion Path:")

            transformRowSubSplit = transformRowSplit.split(factor=lockSplitFactor)

            if gp_child.motion_path is None:
                transformRowSubSplit.operator("object.paths_calculate", text="Calculate...", icon="OBJECT_DATA")
            else:
                transformRowSplitRow = transformRowSubSplit.row()
                # transformRow.operator("object.paths_update", text="Update Paths", icon="OBJECT_DATA")
                transformRowSplitRow.operator("object.paths_update_visible", text="Update All Paths", icon="WORLD")
                transformRowSplitRow.operator("object.paths_clear", text="", icon="X")

            col.separator(factor=0.3)

        # row = col.row()
        # row.separator(factor=0.5)

    # row = box.row()
    # row.operator("uas_shot_manager.change_grease_pencil_opacity").gpName = gp_child


def draw_lock_but(layout, gp_child, lockItem):
    """lockItem can be LOCK_LOCATION_X, ..."""
    embossOp = True
    depressedOp = True
    alertOp = False
    enableOp = True
    icon = "DECORATE_UNLOCKED"

    if "LOCK_LOCATION_X" == lockItem:
        if gp_child.lock_location[0]:
            depressedOp = False
            icon = "DECORATE_LOCKED"
    elif "LOCK_LOCATION_Y" == lockItem:
        if gp_child.lock_location[1]:
            depressedOp = False
            icon = "DECORATE_LOCKED"
    elif "LOCK_LOCATION_Z" == lockItem:
        # has to be locked !!!
        if gp_child.lock_location[2]:
            depressedOp = False
            icon = "DECORATE_LOCKED"
            enableOp = False
        else:
            alertOp = False

    elif "LOCK_ROTATION_X" == lockItem:
        # has to be locked !!!
        if gp_child.lock_rotation[0]:
            depressedOp = False
            icon = "DECORATE_LOCKED"
            enableOp = False
        else:
            alertOp = False
    elif "LOCK_ROTATION_Y" == lockItem:
        # has to be locked !!!
        if gp_child.lock_rotation[1]:
            depressedOp = False
            icon = "DECORATE_LOCKED"
            enableOp = False
        else:
            alertOp = False
    elif "LOCK_ROTATION_Z" == lockItem:
        if gp_child.lock_rotation[2]:
            depressedOp = False
            icon = "DECORATE_LOCKED"

    elif "LOCK_SCALE_X" == lockItem:
        if gp_child.lock_scale[0]:
            depressedOp = False
            icon = "DECORATE_LOCKED"
    elif "LOCK_SCALE_Y" == lockItem:
        if gp_child.lock_scale[1]:
            depressedOp = False
            icon = "DECORATE_LOCKED"
    elif "LOCK_SCALE_Z" == lockItem:
        if gp_child.lock_scale[2]:
            depressedOp = False
            icon = "DECORATE_LOCKED"

    subCol_axisRow = layout.row()
    subCol_axisRow.alert = alertOp
    subCol_axisRow.enabled = enableOp
    op = subCol_axisRow.operator(
        "uas_shot_manager.lock_anim_channel", text="", icon=icon, emboss=embossOp, depress=depressedOp
    )
    op.gpName = gp_child.name
    op.lockItem = lockItem
    op.lockValue = depressedOp
    if alertOp:
        subCol_axisRow.label(text="Should be locked")


def draw_greasepencil_global_properties(layout, context):
    props = config.getAddonProps(context.scene)
    prefs = config.getAddonPrefs()

    box = layout.box()
    row = box.row()
    titleRow = utils_ui.collapsable_panel(
        row, prefs, "stb_global_props_expanded", alert=False, text="Storyboard Frames Global Control "
    )

    # titleRow.label(text=" Storyboard Frames Global Control:")

    if prefs.stb_global_props_expanded:
        rightRow = row.row()
        rightRow.alignment = "RIGHT"
        rightRow.prop(props.shotsGlobalSettings, "alsoApplyToDisabledShots")

        # Grease pencil
        # ######################

        row = box.row()
        row.use_property_decorate = False
        row.separator(factor=1.8)

        col = row.column()
        subRow = col.row()

        grid_flow = subRow.grid_flow(align=False, columns=2, even_columns=True)

        draw_distance(grid_flow, props)

        # grid_flow.separator(factor=1.0)
        # subSubRow = grid_flow.row()
        # subSubRow.scale_x = 0.6
        # grid_flow.use_property_split = False
        grid_flow.prop(prefs, "stb_global_visibility", text="")
        # grid_flow.operator("uas_shots_settings.use_greasepencil", text="Turn On").useGreasepencil = True
        # grid_flow.operator("uas_shots_settings.use_greasepencil", text="Turn Off").useGreasepencil = False
        # grid_flow.prop(props.shotsGlobalSettings, "greasepencilAlpha", text="Alpha")
        rowCol = subRow.row()
        rowCol.operator(
            "uas_shot_manager.remove_grease_pencil", text="", icon="PANEL_CLOSE"
        ).alsoApplyToDisabledShots = props.shotsGlobalSettings.alsoApplyToDisabledShots

        col.separator(factor=0.5)

        subRow = col.row()
        draw_frame_grid(subRow)

        # cameras tools
        #########################
        col.separator(factor=0.5)
        sm_shots_global_settings_ui_cameras.draw_camera_global_settings(context, col, mode="STORYBOARD")

        utils_ui.separatorLine(box, padding_bottom=0.0, padding_top=0.1)

        # overlays tools
        #########################
        row = box.row()
        row.use_property_decorate = False
        row.separator(factor=1.8)
        col = row.column(align=True)
        sm_shots_global_settings_ui_overlays.draw_overlays_global_settings(context, col, mode="STORYBOARD")

        row = col.row(align=True)
        row.separator(factor=0.5)


def draw_frame_grid(layout):
    row = layout.row(align=True)
    row.scale_x = 1.5
    row.label(text="Frame Grid:")

    subRow = row.row(align=True)
    subRow.scale_x = 3.0
    subRow.operator("uas_shot_manager.storyboard_grid_update", text="", icon="LIGHTPROBE_GRID")
    row.operator("uas_shot_manager.storyboard_grid_display_settings", text="", icon="SETTINGS")
    row.scale_x = 1


def draw_distance(layout, props):
    row = layout.row(align=True)
    row.label(text="Distance:")
    # subRow = layout.row(align=True)
    # subRow.scale_x = 1.0
    row.prop(props.shotsGlobalSettings, "stb_distanceFromOrigin", text="")
    # row.label(text="    |")


def collapsable_panel_animateTransformations(
    layout, data, property: str, alert: bool = False, text=None, gp_child=None, lockItem="ALL", depressedOp=True
):
    """Draw an arrow to collapse or extend a panel.
    Return the title row
    Args:
        layout: parent component
        data: the object with the properties
        property: the boolean used to store the rolled-down state of the panel
        alert: is the title bar of the panel is drawn in alert mode
        text: the title of the panel
    eg: collapsable_panel(layout, addon_props, "display_users", text="Server Users")
        if addon_props.addonPrefs_ui_expanded: ...
    """
    row = layout.row(align=True)

    row.alignment = "LEFT"
    # row.scale_x = 0.9
    row.alert = alert
    row.prop(
        data,
        property,
        icon="TRIA_DOWN" if getattr(data, property) else "TRIA_RIGHT",
        icon_only=True,
        emboss=False,
        text=text,
    )

    icon = "DECORATE_UNLOCKED" if depressedOp else "DECORATE_LOCKED"

    row.separator(factor=0.2)
    # lockAnimChannels

    # row.label(text=text)

    if alert:
        row.label(text="", icon="ERROR")
    row.alert = False

    subRow = layout.row()
    subRow.alignment = "RIGHT"

    op = subRow.operator("uas_shot_manager.lock_anim_channel", text="", icon=icon, emboss=True, depress=depressedOp)
    op.gpName = gp_child.name
    op.lockItem = lockItem
    op.lockValue = depressedOp

    # if text is not None:
    #     row.label(text=text)
    # return getattr(data, property)
    return row
