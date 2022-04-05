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

from shotmanager.utils import utils
from shotmanager.utils import utils_ui
from shotmanager.utils import utils_greasepencil

from shotmanager.features.greasepencil import greasepencil_toolspanel_ui as gp

from shotmanager.config import config


def draw_greasepencil_shot_properties(layout, context, shot):
    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences

    if shot is None:
        return

    propertiesModeStr = "Selected " if "SELECTED" == props.current_shot_properties_mode else "Current "
    leftSepFactor = 0.5
    hSepFactor = 0.5

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
    row = box.row(align=True)

    # grease pencil
    ################

    if props.display_greasepencil_in_properties:  # and props.expand_greasepencil_properties:
        gp.draw_greasepencil_play_tools(layout, context, shot, layersListDropdown=prefs.layersListDropdown)

    extendSubRow = row.row(align=True)
    # extendSubRow.alignment = "RIGHT"
    subrowleft = extendSubRow.row()
    subrowleft.alignment = "EXPAND"
    # subrowleft.scale_x = 0.8
    subrowleft.label(text=propertiesModeStr + "Shot Storyboard Frame:")

    # panelIcon = "TRIA_DOWN" if prefs.shot_greasepencil_expanded and gp_child is not None else "TRIA_RIGHT"
    # extendSubRow.prop(prefs, "shot_greasepencil_expanded", text="", icon=panelIcon, emboss=False)
    # row.separator(factor=1.0)

    # subRow = row.row(align=False)
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
        subRow.operator("uas_shot_manager.remove_grease_pencil", text="", icon="PANEL_CLOSE").shotIndex = shotIndex
        subRow.prop(props, "display_greasepencil_in_shotlist", text="")

        # name and visibility tools
        ################
        # extendSubRow.alignment = "EXPAND"
        subRow = box.row(align=False)
        # subRow.scale_x = 0.8
        leftSubRow = subRow.row(align=True)
        leftSubRow.alignment = "LEFT"
        leftSubRow.label(text="GP Object: ")
        leftSubRow.label(text=gp_child.name)

        rightSubRow = subRow.row(align=True)
        rightSubRow.alignment = "RIGHT"
        rightSubRow.prop(gp_child, "hide_select", text="")
        rightSubRow.prop(gp_child, "hide_viewport", text="")
        rightSubRow.prop(gp_child, "hide_render", text="")

        # Tools
        ################

        mainRow = box.row()
        mainRow.separator(factor=leftSepFactor)
        col = mainRow.column()

        # Grease Pencil tools
        ################
        subRow = col.row()
        gpToolsSplit = subRow.split(factor=0.4)
        # gpToolsRow1 = subRow.row(align=False)
        gpToolsRow = gpToolsSplit.row(align=True)
        gpToolsRow.alignment = "LEFT"
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

        gpToolsRow.operator("uas_shot_manager.update_grease_pencil", text="", icon="FILE_REFRESH").shotIndex = shotIndex

        # subRow.alignment = "LEFT"
        gpDistRow = gpToolsSplit.row(align=True)
        gpDistRow.scale_x = 1.2
        gpDistRow.use_property_split = True
        gpDistRow.alignment = "RIGHT"
        # gpDistRow.label(text="Distance:")
        gpDistRow.prop(gpProperties, "distanceFromOrigin", text="Distance:", slider=True)

        # Debug settings
        ################
        # if config.devDebug:

        # animation
        ################
        # panelIcon = "TRIA_DOWN" if prefs.stb_anim_props_expanded else "TRIA_RIGHT"
        animRow = col.row()
        utils_ui.collapsable_panel(
            animRow, prefs, "stb_anim_props_expanded", alert=False, text="Animate Frame Transform"
        )
        # animRow.label(text="Animate Frame Transform")
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
            transformRow.prop(gp_child, "scale")

            transformRow = col.row()
            transformRow.separator(factor=0.6)
            transformRow = col.row(align=True)
            transformRow.alignment = "RIGHT"
            # transformRow.ui_units_x = 2
            if gp_child.motion_path is None:
                transformRow.operator("object.paths_calculate", text="Calculate...", icon="OBJECT_DATA")
            else:
                # transformRow.operator("object.paths_update", text="Update Paths", icon="OBJECT_DATA")
                transformRow.operator("object.paths_update_visible", text="Update All Paths", icon="WORLD")
                transformRow.operator("object.paths_clear", text="", icon="X")

            row = col.row()
            row.separator(factor=0.4)

        row = col.row()
        row.separator(factor=hSepFactor)
        row = col.row()
        row.label(text="Canvas: ")

        canvasLayer = utils_greasepencil.get_grease_pencil_layer(
            gp_child, gpencil_layer_name="GP_Canvas", create_layer=False
        )
        if canvasLayer is None:
            # utils_greasepencil.get_grease_pencil_layer
            row.operator("uas_shot_manager.add_canvas_to_grease_pencil", text="+").gpName = gp_child.name
        else:
            # row.prop(canvasLayer, "opacity", text="")
            row.prop(gpProperties, "canvasOpacity", slider=True, text="Opacity")
            row.prop(canvasLayer, "hide", text="")
            row = col.row()
            row.separator(factor=2)
            row.prop(gpProperties, "canvasSize", slider=True)

        row = col.row()
        row.separator(factor=0.5)

    # row = box.row()
    # row.operator("uas_shot_manager.change_grease_pencil_opacity").gpObjectName = gp_child


def draw_greasepencil_global_properties(layout, context):
    props = context.scene.UAS_shot_manager_props

    box = layout.box()
    row = box.row()
    row.label(text="Shots Global Control:")
    rightRow = row.row()
    rightRow.alignment = "RIGHT"
    rightRow.prop(props.shotsGlobalSettings, "alsoApplyToDisabledShots")

    # Grease pencil
    # ######################

    row = box.row()
    row.use_property_decorate = False
    row.separator()

    col = row.column()
    subRow = col.row()

    grid_flow = subRow.grid_flow(align=False, columns=4, even_columns=False)
    grid_flow.label(text="Grease Pencil:")
    grid_flow.operator("uas_shots_settings.use_greasepencil", text="Turn On").useGreasepencil = True
    grid_flow.operator("uas_shots_settings.use_greasepencil", text="Turn Off").useGreasepencil = False
    grid_flow.prop(props.shotsGlobalSettings, "greasepencilAlpha", text="Alpha")
    c = row.column()
    c.operator("uas_shot_manager.remove_grease_pencil", text="", icon="PANEL_CLOSE")

    col.separator(factor=0.5)
