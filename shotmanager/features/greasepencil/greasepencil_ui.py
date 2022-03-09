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

from shotmanager.config import config


def draw_greasepencil_shot_properties(layout, context, shot):
    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences

    if shot is None:
        return

    propertiesModeStr = "Selected " if "SELECTED" == props.current_shot_properties_mode else "Current "

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

    box = layout.box()
    box.use_property_decorate = False
    row = box.row(align=True)

    gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)

    extendSubRow = row.row(align=True)
    # extendSubRow.alignment = "RIGHT"
    subrowleft = extendSubRow.row()
    subrowleft.alignment = "EXPAND"
    subrowleft.scale_x = 0.8
    subrowleft.label(text=propertiesModeStr + "Shot GP:")

    # panelIcon = "TRIA_DOWN" if prefs.shot_greasepencil_expanded and gp_child is not None else "TRIA_RIGHT"
    # extendSubRow.prop(prefs, "shot_greasepencil_expanded", text="", icon=panelIcon, emboss=False)
    # row.separator(factor=1.0)

    # subRow = row.row(align=False)
    # subRow.scale_x = 0.6
    # subRow.label(text="Grease Pencil:")

    if gp_child is None:
        # extendSubRow.enabled = False
        row.operator(
            "uas_shot_manager.add_grease_pencil", text="", icon="ADD", emboss=True
        ).cameraGpName = shot.camera.name
        row.separator(factor=1.4)
        row.prop(props, "display_greasepencil_in_shotlist", text="")
        # subSubRow.separator(factor=0.5)  # prevents stange look when panel is narrow

    else:
        extendSubRow.alignment = "EXPAND"
        subRow = extendSubRow.row(align=False)
        # subRow.scale_x = 0.8
        selSubRow = subRow.row(align=True)
        selSubRow.label(text=gp_child.name)
        selSubRow.operator(
            "uas_shot_manager.select_shot_grease_pencil", text="", icon="RESTRICT_SELECT_OFF"
        ).index = shotIndex

        if gp_child.mode == "PAINT_GPENCIL":
            icon = "GREASEPENCIL"
            selSubRow.alert = True
            selSubRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon=icon)
            selSubRow.alert = False
            # bpy.ops.gpencil.paintmode_toggle()
        else:
            selSubRow.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon="OUTLINER_OB_GREASEPENCIL")

        subSubRow = subRow.row(align=True)
        subSubRow.prop(gp_child, "hide_select", text="")
        subSubRow.prop(gp_child, "hide_viewport", text="")
        subSubRow.prop(gp_child, "hide_render", text="")

        subRow = row.row(align=True)
        # subRow.alignment = "RIGHT"
        subRow.separator(factor=0.9)
        subRow.operator("uas_shot_manager.remove_grease_pencil", text="", icon="PANEL_CLOSE").shotIndex = shotIndex
        subRow.separator()
        subRow.prop(props, "display_greasepencil_in_shotlist", text="")

        mainRow = extendSubRow.row()
        sepRow = mainRow.row()
        sepRow.separator(factor=0.5)

        mainRow = box.row()
        mainRow.separator(factor=0.5)
        col = mainRow.column()
        if config.devDebug:
            # or prefs.shot_greasepencil_expanded:
            subRow = col.row()
            subRow.prop(gp_child, "location")

        subRow = col.row()
        # subRow.prop(shot.gpStoryboard, "distance")
        subRow.prop(shot, "gpDistance")

        row = col.row()
        row.label(text="Canvas: ")

        canvasLayer = utils_greasepencil.get_grease_pencil_layer(
            gp_child, gpencil_layer_name="GP_Canvas", create_layer=False
        )
        if canvasLayer is None:
            # utils_greasepencil.get_grease_pencil_layer
            row.operator("uas_shot_manager.add_canvas_to_grease_pencil", text="+").gpName = gp_child.name
        else:
            row.prop(canvasLayer, "hide", text="")
            row.prop(canvasLayer, "opacity", text="")

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


def draw_greasepencil_play_tools(layout, context, shot, layersListDropdown=None):
    props = context.scene.UAS_shot_manager_props
    # prefs = context.preferences.addons["shotmanager"].preferences

    if shot is None:
        return

    utils_ui.drawSeparatorLine(layout)

    box = layout.box()
    #    row = box.row()
    mainRow = box.row(align=False)

    objIsGP = False
    selObjName = "-"
    if context.object is not None:
        selObjName = context.object.name
        objIsGP = "GPENCIL" == context.object.type
        if objIsGP:
            gp = context.object
    # mainRow.label(text=f"Sel: {selObjName}, GP: {objIsGP}")
    mainRow.label(text=f"GP:  {gp.name if objIsGP else '-'}")

    icon = "GP_SELECT_STROKES"

    if objIsGP:
        layersRow = mainRow.row(align=True)
        layersRow.alignment = "RIGHT"
        # layersRow.prop(gp.data, "layers")
        layersRow.label(text="Layer:")
        # layersRow.prop(prefs, "layersListDropdown", text="Layers")

        # Grease pencil layer.
        gpl = context.active_gpencil_layer
        if gpl and gpl.info is not None:
            text = gpl.info
            maxw = 25
            if len(text) > maxw:
                text = text[: maxw - 5] + ".." + text[-3:]
        else:
            text = ""

        # layout.label(text="Layer:")
        sub = layersRow.row()
        # sub.scale_x = 0.8
        sub.ui_units_x = 6
        sub.popover(
            panel="TOPBAR_PT_gpencil_layers", text=text,
        )

        rightRow = mainRow.row(align=True)
        if gp.mode == "PAINT_GPENCIL":
            rightRow.operator("uas_shot_manager.select_grease_pencil_object", text="", icon="RESTRICT_SELECT_OFF")

            icon = "GREASEPENCIL"
            rightRow.alert = True
            # row.operator("uas_shot_manager.greasepencilitem", text="", icon=icon).index = index

            rightRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon=icon)
            # bpy.ops.gpencil.paintmode_toggle()
        else:

            rightRow.operator("uas_shot_manager.select_grease_pencil_object", text="", icon="RESTRICT_SELECT_OFF")
            icon = config.icons_col["ShotManager_CamGPShot_32"]
            rightRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon_value=icon.icon_id)
            # mainRow.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon_value=icon.icon_id)
            # row.operator("uas_shot_manager.greasepencilitem", text="", icon_value=icon.icon_id).index = index

    mainRow = box.row(align=False)
    keysRow = mainRow.row(align=True)
    keysRow.scale_x = 1.2
    keysRow.alignment = "CENTER"
    keysRow.enabled = objIsGP
    keysRow.operator("uas_shot_manager.greasepencil_previouskey", icon="PREV_KEYFRAME", text="")

    isCurrentFrameOnGPFrame = isCurrentFrameOnGPFrame()
    if isCurrentFrameOnGPFrame:
        iconFrame = "HANDLETYPE_FREE_VEC"
    else:
        iconFrame = "KEYTYPE_MOVING_HOLD_VEC"
    keysRow.operator("uas_shot_manager.greasepencil_addnewframe", icon=iconFrame, text="")
    keysRow.operator("uas_shot_manager.greasepencil_nextkey", icon="NEXT_KEYFRAME", text="")

    # subRow = mainRow.row(align=False)
    # subRow.scale_x = 1.5
    # subRow.alignment = "RIGHT"
    # mainRow.scale_x = 2
    subsubRow = mainRow.row(align=True)
    # subsubRow.label(text="Apply to:")
    subsubRow.scale_x = 0.9
    # subRow.ui_units_x = 14
    subsubRow.alignment = "LEFT"
    subsubRow.prop(props, "greasePencil_layersMode", text="Apply to")

    utils_ui.drawSeparatorLine(layout, lower_height=0.6)

    # box.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon="GP_SELECT_STROKES")
