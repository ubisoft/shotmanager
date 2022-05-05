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
Grease pencil UI
"""

# from shotmanager.utils import utils
from shotmanager.utils import utils_ui
from shotmanager.utils import utils_greasepencil

from shotmanager.config import config

from . import storyboard_drawing_ui as drawing_ui


def draw_greasepencil_shot_properties(layout, context, shot):
    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences

    if shot is None:
        return

    propertiesModeStr = "Selected " if "SELECTED" == props.current_shot_properties_mode else "Current "
    hSepFactor = 0.5

    devDebug_displayAdv = config.devDebug and False

    gp_child = None
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
    #    gpProperties = shot.gpStoryboard if hasattr(shot, "gpStoryboard") else None
    gpProperties = None
    if len(shot.greasePencils):
        gpProperties = shot.greasePencils[0]

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
    subrowleft.alignment = "EXPAND"
    # subrowleft.scale_x = 0.8
    subrowleft.label(text=propertiesModeStr + "Shot Storyboard Frame:")

    # panelIcon = "TRIA_DOWN" if prefs.shot_greasepencil_expanded and gp_child is not None else "TRIA_RIGHT"
    # extendSubRow.prop(prefs, "shot_greasepencil_expanded", text="", icon=panelIcon, emboss=False)
    # row.separator(factor=1.0)

    # subRow.scale_x = 0.6
    # subRow.label(text="Grease Pencil:")

    if gp_child is None:
        # extendSubRow.enabled = False
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
        extendSubRow.alignment = "EXPAND"
        subRow = extendSubRow.row(align=False)
        subRow.separator(factor=0.9)
        subRow.ui_units_x = 8

        propSubRow = subRow.row(align=True)
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
        if config.devDebug:
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
                infoRow.label(text="Same as Context")
            else:
                infoRow.alert = True
                infoRow.label(text="Diff from Context")

        rightSubRow = subRow.row(align=True)
        rightSubRow.alignment = "RIGHT"

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
                gpToolsRow.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon="OUTLINER_OB_GREASEPENCIL")

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

        utils_ui.drawSeparatorLine(col, lower_height=1.4, higher_height=0.6)

        row = col.row()

        canvasSplitRow = row.split(factor=0.3)
        utils_ui.collapsable_panel(canvasSplitRow, prefs, "stb_canvas_props_expanded", alert=False, text="Canvas")
        # canvasSplitRow.label(text=" ")
        # canvasSplitRow.separator(factor=0.1)

        props = context.scene.UAS_shot_manager_props
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

            sepRow = col.row()
            sepRow.separator(factor=0.5)

            splitRow = col.split(factor=0.3)
            splitRow.label(text="   Size:")
            rightSplitRow = splitRow.row(align=True)
            # rightSplitRow.use_property_split = False
            # rightSplitRow.use_property_decorate = False
            rightSplitRow.prop(gpProperties, "canvasSize", text="", slider=True)

            splitRow = col.split(factor=0.3)
            # splitRow.separator(factor=2)
            splitRow.label(text="   Distance:")
            splitRow.prop(gpProperties, "distanceFromOrigin", text="", slider=True)

        # animation
        ################
        # panelIcon = "TRIA_DOWN" if prefs.stb_anim_props_expanded else "TRIA_RIGHT"
        animRow = col.row()
        utils_ui.collapsable_panel(
            animRow, prefs, "stb_anim_props_expanded", alert=False, text="Animate Frame Transformation"
        )
        if prefs.stb_anim_props_expanded:
            transformRow = col.row()
            transformRow.separator(factor=hSepFactor)
            # or prefs.shot_greasepencil_expanded:
            transformRow = col.row()
            # transformRow.label(text="Location:")
            transformRow.use_property_split = True
            transformRow.use_property_decorate = True
            transformRow.prop(gp_child, "location")

            transformRow = col.row()
            transformRow.use_property_split = True
            transformRow.use_property_decorate = True
            transformRow.prop(gp_child, "rotation_euler")

            transformRow = col.row()
            transformRow.use_property_split = True
            transformRow.use_property_decorate = True
            transformRow.prop(gp_child, "scale")

            # transformRow = col.row()
            # transformRow.label(text="test")
            # transformRow.use_property_split = True
            # transformRow.use_property_decorate = True
            # transformRow.prop(gp_child.location, "x")

            transformRow = col.row()
            transformRow.separator(factor=0.6)
            transformRow = col.row(align=True)
            transformRow.separator(factor=5)
            transformRowSplit = transformRow.split(factor=0.32)
            # transformRow.alignment = "RIGHT"
            # transformRow.ui_units_x = 2
            transformRowSplit.label(text="Motion Path:")
            if gp_child.motion_path is None:
                transformRowSplit.operator("object.paths_calculate", text="Calculate...", icon="OBJECT_DATA")
            else:
                transformRowSplitRow = transformRowSplit.row()
                # transformRow.operator("object.paths_update", text="Update Paths", icon="OBJECT_DATA")
                transformRowSplitRow.operator("object.paths_update_visible", text="Update All Paths", icon="WORLD")
                transformRowSplitRow.operator("object.paths_clear", text="", icon="X")

            row = col.row()
            row.separator(factor=0.4)

        # row = col.row()
        # row.separator(factor=0.5)

    # row = box.row()
    # row.operator("uas_shot_manager.change_grease_pencil_opacity").gpName = gp_child


def draw_greasepencil_global_properties(layout, context):
    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences

    box = layout.box()
    row = box.row()
    row.label(text="Storyboard Frames Global Control:")
    rightRow = row.row()
    rightRow.alignment = "RIGHT"
    rightRow.prop(props.shotsGlobalSettings, "alsoApplyToDisabledShots")

    # Grease pencil
    # ######################

    row = box.row()
    row.use_property_decorate = False
    # row.separator()

    col = row.column()
    subRow = col.row()

    grid_flow = subRow.grid_flow(align=False, columns=3, even_columns=False)
    # grid_flow.label(text="Grease Pencil:")
    # grid_flow.label(text="rr")
    grid_flow.operator("uas_shot_manager.update_storyboard_grid", text="", icon="LIGHTPROBE_GRID")
    grid_flow.separator(factor=1.0)
    grid_flow.prop(prefs, "stb_global_visibility", text="")
    # grid_flow.operator("uas_shots_settings.use_greasepencil", text="Turn On").useGreasepencil = True
    # grid_flow.operator("uas_shots_settings.use_greasepencil", text="Turn Off").useGreasepencil = False
    # grid_flow.prop(props.shotsGlobalSettings, "greasepencilAlpha", text="Alpha")
    rowCol = subRow.row()
    rowCol.operator(
        "uas_shot_manager.remove_grease_pencil", text="", icon="PANEL_CLOSE"
    ).alsoApplyToDisabledShots = props.shotsGlobalSettings.alsoApplyToDisabledShots

    utils_ui.drawSeparatorLine(col, lower_height=1.4, higher_height=0.4)

    # overlay tools
    #########################
    spaceDataViewport = props.getValidTargetViewportSpaceData(context)
    onionSkinIsActive = False
    gridIsActive = False
    if spaceDataViewport is not None:
        onionSkinIsActive = spaceDataViewport.overlay.use_gpencil_onion_skin
        gridIsActive = spaceDataViewport.overlay.use_gpencil_grid

    row = col.row(align=False)
    overlayCol = row.column()
    overlaySplit = overlayCol.split(factor=0.2)
    overlaySplit.label(text="Overlay: ")
    overlayRighRow = overlaySplit.row()
    overlayRighRow.operator("uas_shot_manager.greasepencil_toggleonionskin", depress=onionSkinIsActive)
    overlayRighRow.operator("uas_shot_manager.greasepencil_togglecanvas", depress=gridIsActive)

    row = col.row(align=False)
    overlaySplit = row.split(factor=0.2)
    overlaySplit.separator()
    overlayRighRow = overlaySplit.row()
    overlayRighRow.prop(spaceDataViewport.overlay, "use_gpencil_fade_layers", text="")
    # row.prop(spaceDataViewport.overlay, "gpencil_fade_layer")
    subOverlayRighRow = overlayRighRow.row()
    subOverlayRighRow.enabled = spaceDataViewport.overlay.use_gpencil_fade_layers
    subOverlayRighRow.prop(prefs, "stb_overlay_layers_opacity", text="Fade Layers", slider=True)

    row = col.row(align=True)
    row.separator(factor=0.5)
