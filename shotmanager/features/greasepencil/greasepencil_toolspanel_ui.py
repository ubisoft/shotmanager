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
Shot Manager grease pencil tools and specific operators
"""

import bpy

from shotmanager.utils import utils
from shotmanager.utils import utils_ui
from shotmanager.utils import utils_greasepencil

from shotmanager.config import config


def draw_greasepencil_play_tools(layout, context, shot, layersListDropdown=None):
    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences

    if shot is None:
        return

    # utils_ui.drawSeparatorLine(layout)

    box = layout.box()
    #    row = box.row()

    # Object and layers ###
    ###################

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
        sub = layersRow.row(align=True)
        # sub.alignment = "LEFT"
        # sub.scale_x = 0.8
        sub.ui_units_x = 6
        sub.popover(
            panel="TOPBAR_PT_gpencil_layers",
            text=text,
        )
        if gpl and gpl.info is not None:
            sub.alert = gpl.lock
            sub.prop(gpl, "lock", text="")
            sub.alert = False
        else:
            sub.label(text="", icon="LOCKED")

        gpOpsRow = layersRow.row(align=False)
        gpOpsRow.separator(factor=0.1)
        gpOpsLeftRow = gpOpsRow.row(align=True)
        gpOpsLeftRow.ui_units_x = 3
        gpOpsLeftRow.scale_x = 2.0
        # gpOpsLeftRow.alignment = "RIGHT"
        gpOpsLeftRow.operator("uas_shot_manager.select_grease_pencil_object", text="", icon="RESTRICT_SELECT_OFF")

        if gp.mode == "PAINT_GPENCIL":
            icon = "GREASEPENCIL"
            gpOpsLeftRow.alert = True
            # row.operator("uas_shot_manager.greasepencilitem", text="", icon=icon).index = index

            gpOpsLeftRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon=icon)
            # bpy.ops.gpencil.paintmode_toggle()
        else:
            icon = config.icons_col["ShotManager_CamGPShot_32"]
            gpOpsLeftRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon_value=icon.icon_id)
            # mainRow.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon_value=icon.icon_id)
            # row.operator("uas_shot_manager.greasepencilitem", text="", icon_value=icon.icon_id).index = index

        gpOpsRightRow = gpOpsRow.row(align=False)
        # gpOpsRightRow.separator(factor=0.1)
        gpOpsRightRow.operator("uas_shot_manager.clear_layer", text="", icon="MESH_PLANE")

    # Active material ###
    ###################

    materialsRow = box.row(align=True)
    if objIsGP:
        materialsRow.label(text="Material:")
        # materialsRow.prop(gp, "material_slots")
        materialsRow.prop(props, "greasePencil_activeMaterial", text="")

    # current frame ###
    ###################

    mainRow = box.row(align=False)
    keysRow = mainRow.row(align=True)
    keysRow.scale_x = 1.2
    keysRow.alignment = "CENTER"
    keysRow.enabled = objIsGP
    keysRow.operator("uas_shot_manager.greasepencil_previouskey", icon="PREV_KEYFRAME", text="")

    isCurrentFrameOnGPFrame = False
    if objIsGP:
        isCurrentFrameOnGPFrame = utils_greasepencil.isCurrentFrameOnLayerFrame(
            gp, context.scene.frame_current, props.greasePencil_layersMode
        )
    else:
        keysRow.enabled = False

    if isCurrentFrameOnGPFrame:
        # iconFrame = "HANDLETYPE_FREE_VEC"
        iconFrame = "ADD"
        iconFrame = "KEYFRAME_HLT"
    else:
        iconFrame = "KEYTYPE_MOVING_HOLD_VEC"
        iconFrame = "KEYFRAME"
    # iconFrame = "ADD"
    keysRow.operator("uas_shot_manager.greasepencil_addnewframe", icon=iconFrame, text="")
    # keysRow.enabled = True
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

    mainRow.label(text="Drawing on GP frame: ")
    subsubRow = mainRow.row(align=True)
    gpFrameStr = "-"
    if objIsGP:
        if isCurrentFrameOnGPFrame:
            gpFrameStr = "Current"
        else:
            subsubRow.alert = True
            gpFrameStr = str(utils_greasepencil.getLayerPreviousFrame(gp, context.scene.frame_current, "ACTIVE"))
    subsubRow.label(text=gpFrameStr)

    row = box.row(align=False)

    spaceDataViewport = props.getValidTargetViewportSpaceData(context)
    onionSkinIsActive = False
    gridIsActive = False
    if spaceDataViewport is not None:
        onionSkinIsActive = spaceDataViewport.overlay.use_gpencil_onion_skin
        gridIsActive = spaceDataViewport.overlay.use_gpencil_grid

    row.operator("uas_shot_manager.greasepencil_toggleonionskin", depress=onionSkinIsActive)
    row.operator("uas_shot_manager.greasepencil_togglecanvas", depress=gridIsActive)
    row = box.row(align=False)
    row.prop(spaceDataViewport.overlay, "use_gpencil_fade_layers", text="")
    # row.prop(spaceDataViewport.overlay, "gpencil_fade_layer")
    row.prop(prefs, "stb_overlay_layers_opacity")


#     utils_ui.drawSeparatorLine(layout, lower_height=0.6)

# box.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon="GP_SELECT_STROKES")
