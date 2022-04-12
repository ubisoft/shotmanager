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

# import bpy

# from shotmanager.utils import utils
from shotmanager.utils import utils_ui
from shotmanager.utils import utils_greasepencil

from shotmanager.config import config


def draw_greasepencil_play_tools(layout, context, shot, layersListDropdown=None):
    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences

    if shot is None:
        return

    shotIndex = props.getShotIndex(shot)

    # Object and layers ###
    ###################
    objIsGP = False
    selObjName = "-"
    if context.object is not None:
        selObjName = context.object.name
        objIsGP = "GPENCIL" == context.object.type
        if objIsGP:
            gp = context.object
    # mainRow.label(text=f"Sel: {selObjName}, GP: {objIsGP}")

    icon = "GP_SELECT_STROKES"

    box = layout.box()
    # utils_ui.drawSeparatorLine(layout)

    if objIsGP:
        gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)
        gpIsStoryboardFrame = gp_child is not None and gp_child.name == gp.name

        col = box.column()
        if not gpIsStoryboardFrame:
            warningRow = col.row(align=False)
            warningRow.alert = True
            warningRow.label(text="*** Free Scene GP: ")
            warningRow.alert = False
            warningRow.label(text=f"GP:  {gp.name if objIsGP else '-'}")
            warningRow.alert = True
            warningRow.label(text=" ***")

        #     mainRow = col.row(align=False)

        # toolbar ###
        ###################

        # Grease Pencil tools
        ################
        # subSubRow = rightSubRow.row()
        # subSubRow.alignment = "RIGHT"
        # gpToolsSplit = subSubRow.split(factor=0.4)
        # gpToolsRow = gpToolsSplit.row(align=True)

        sepRow = col.row(align=False)
        sepRow.separator(factor=0.5)

        gpOpsRow = col.row(align=False)
        gpOpsRow.scale_y = 1.2

        gpOpsRow.separator(factor=0.1)
        gpToolsRow = gpOpsRow.row(align=True)
        #   gpToolsRow.ui_units_x = 3
        gpToolsRow.scale_x = 2.0
        # gpOpsLeftRow.alignment = "RIGHT"

        if gpIsStoryboardFrame:
            gpToolsRow.operator(
                "uas_shot_manager.select_shot_grease_pencil", text="", icon="RESTRICT_SELECT_OFF"
            ).index = shotIndex
        else:
            gpToolsRow.operator("uas_shot_manager.select_grease_pencil_object", text="", icon="RESTRICT_SELECT_OFF")

        if gp.mode == "PAINT_GPENCIL":
            icon = "GREASEPENCIL"
            gpToolsRow.alert = True
            # row.operator("uas_shot_manager.greasepencilitem", text="", icon=icon).index = index

            gpToolsRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon=icon)
            gpToolsRow.alert = False
        else:
            icon = "OUTLINER_OB_GREASEPENCIL"
            if gpIsStoryboardFrame:
                gpToolsRow.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon=icon)
            else:
                gpToolsRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon=icon)

        if config.devDebug:
            gpToolsRow.operator(
                "uas_shot_manager.update_grease_pencil", text="", icon="FILE_REFRESH"
            ).shotIndex = shotIndex

        gpToolsRow.separator(factor=0.5)

        drawLayersRow(context, props, gpToolsRow, gp, objIsGP)

        gpOpsRightRow = gpOpsRow.row(align=False)
        gpOpsRightRow.alignment = "RIGHT"
        gpOpsRightRow.scale_x = 1.2
        # gpOpsRightRow.separator(factor=0.1)
        gpOpsRightRow.operator("uas_shot_manager.clear_layer", text="", icon="MESH_PLANE")
        gpOpsRightRow.separator(factor=0.5)

        # current frame ###
        ###################
        sepRow = col.row(align=True)
        sepRow.separator(factor=0.5)

        # mainRow = box.row(align=False)
        keysRow = col.row(align=True)
        drawKeysRow(context, props, col, gp, objIsGP)

        # layers ##
        ##################
        sepRow = col.row(align=True)
        sepRow.separator(factor=0.5)

        matRow = col.row(align=False)
        layersRow = matRow.row(align=True)
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

        # Active material ###
        ###################

        materialsRow = matRow.row(align=True)
        if objIsGP:
            materialsRow.label(text="Material:")
            # materialsRow.prop(gp, "material_slots")
            materialsRow.prop(props, "greasePencil_activeMaterial", text="")

        utils_ui.drawSeparatorLine(box)

    # overlay tools
    #########################
    spaceDataViewport = props.getValidTargetViewportSpaceData(context)
    onionSkinIsActive = False
    gridIsActive = False
    if spaceDataViewport is not None:
        onionSkinIsActive = spaceDataViewport.overlay.use_gpencil_onion_skin
        gridIsActive = spaceDataViewport.overlay.use_gpencil_grid

    row = box.row(align=True)
    overlayCol = row.column()
    overlaySplit = overlayCol.split(factor=0.2)
    overlaySplit.label(text="Overlay: ")
    overlayRighRow = overlaySplit.row()
    overlayRighRow.operator("uas_shot_manager.greasepencil_toggleonionskin", depress=onionSkinIsActive)
    overlayRighRow.operator("uas_shot_manager.greasepencil_togglecanvas", depress=gridIsActive)

    overlaySplit = overlayCol.split(factor=0.2)
    overlaySplit.separator()
    overlayRighRow = overlaySplit.row()
    overlayRighRow.prop(spaceDataViewport.overlay, "use_gpencil_fade_layers", text="")
    # row.prop(spaceDataViewport.overlay, "gpencil_fade_layer")
    subOverlayRighRow = overlayRighRow.row()
    subOverlayRighRow.enabled = spaceDataViewport.overlay.use_gpencil_fade_layers
    subOverlayRighRow.prop(prefs, "stb_overlay_layers_opacity", text="Fade Layers", slider=True)


#     utils_ui.drawSeparatorLine(layout, lower_height=0.6)

# box.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon="GP_SELECT_STROKES")


def drawLayersRow(context, props, layout, gp, objIsGP):
    prefs = context.preferences.addons["shotmanager"].preferences
    currentFrame = context.scene.frame_current

    row = layout.row(align=True)

    icon_OnprevFrame = "KEYFRAME"
    icon_OnFrame = "KEYFRAME_HLT"

    # canvas layer #####
    if prefs.stb_useLayer_Canvas:
        layerName = utils_greasepencil.getGpLayerNameFromID(gp, "CANVAS")
        currentFrameIsOnLayerKeyFrame = None
        depressBut = False
        icon_frame = icon_OnFrame if currentFrameIsOnLayerKeyFrame else icon_OnprevFrame
        if layerName is not None:
            currentFrameIsOnLayerKeyFrame = utils_greasepencil.isCurrentFrameOnLayerKeyFrame(
                gp, currentFrame, layerName
            )
            depressBut = utils_greasepencil.gpLayerIsActive(gp, layerName)
            op = row.operator(
                "uas_shot_manager.greasepencil_setlayerandmat", depress=depressBut, icon=icon_frame, text=""
            )
            op.layerID = "CANVAS"
            op.layerName = layerName
            op.gpObjName = gp.name
        else:
            warningRow = row.row(align=True)
            warningRow.alert = True
            warningRow.enabled = False
            warningRow.operator(
                "uas_shot_manager.greasepencil_setlayerandmat", depress=depressBut, icon=icon_frame, text=""
            ).layerID = ("CANVAS" + "_WARNING")

    # bg layer #########
    if prefs.stb_useLayer_BG_Ink or prefs.stb_useLayer_BG_Fill:
        layerCol = row.column(align=True)
        layerCol.scale_y = 0.5 if prefs.stb_useLayer_BG_Ink and prefs.stb_useLayer_BG_Fill else 1.0

        if prefs.stb_useLayer_BG_Ink:
            layerName = utils_greasepencil.getGpLayerNameFromID(gp, "BG_INK")
            currentFrameIsOnLayerKeyFrame = utils_greasepencil.isCurrentFrameOnLayerKeyFrame(
                gp, currentFrame, layerName
            )
            icon_frame = icon_OnFrame if currentFrameIsOnLayerKeyFrame else icon_OnprevFrame
            depressBut = utils_greasepencil.gpLayerIsActive(gp, layerName)
            op = layerCol.operator(
                "uas_shot_manager.greasepencil_setlayerandmat", depress=depressBut, icon=icon_frame, text=""
            )
            op.layerID = "BG_INK"
            op.layerName = layerName
            op.gpObjName = gp.name
        if prefs.stb_useLayer_BG_Fill:
            layerName = utils_greasepencil.getGpLayerNameFromID(gp, "BG_FILL")
            currentFrameIsOnLayerKeyFrame = utils_greasepencil.isCurrentFrameOnLayerKeyFrame(
                gp, currentFrame, layerName
            )
            icon_frame = icon_OnFrame if currentFrameIsOnLayerKeyFrame else icon_OnprevFrame
            depressBut = utils_greasepencil.gpLayerIsActive(gp, layerName)
            op = layerCol.operator(
                "uas_shot_manager.greasepencil_setlayerandmat", depress=depressBut, icon=icon_frame, text=""
            )
            op.layerID = "BG_FILL"
            op.layerName = layerName
            op.gpObjName = gp.name

    pass


def drawKeysRow(context, props, layout, gp, objIsGP):
    keysRow = layout.row(align=True)
    keysRow.scale_x = 1.4
    keysRow.alignment = "CENTER"
    keysRow.enabled = objIsGP
    keysRow.operator("uas_shot_manager.greasepencil_previouskey", icon="PREV_KEYFRAME", text="")

    isCurrentFrameOnGPFrame = False
    if objIsGP:
        isCurrentFrameOnGPFrame = utils_greasepencil.isCurrentFrameOnLayerKeyFrame(
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
    frameOpRow = keysRow.row(align=True)
    frameOpRow.operator("uas_shot_manager.greasepencil_newkeyframe", icon=iconFrame, text="")
    frameOpRow.operator("uas_shot_manager.greasepencil_duplicatekeyframe", icon=iconFrame, text="")

    delFrameOpRow = frameOpRow.row(align=True)
    delFrameOpRow.enabled = isCurrentFrameOnGPFrame
    delFrameOpRow.operator("uas_shot_manager.greasepencil_deletekeyframe", icon="PANEL_CLOSE", text="")

    # keysRow.enabled = True
    keysRow.operator("uas_shot_manager.greasepencil_nextkey", icon="NEXT_KEYFRAME", text="")

    # subRow = mainRow.row(align=False)
    # subRow.scale_x = 1.5
    # subRow.alignment = "RIGHT"
    # mainRow.scale_x = 2
    settingsRow = layout.row(align=False)
    subsubRow = settingsRow.row(align=True)
    # subsubRow.label(text="Apply to:")
    subsubRow.scale_x = 0.9
    # subRow.ui_units_x = 14
    subsubRow.alignment = "LEFT"
    subsubRow.separator(factor=2)
    subsubRow.prop(props, "greasePencil_layersMode", text="Apply to")

    # settingsRow = settingsRow.row(align=True)
    subsubRow = settingsRow.row(align=True)
    subsubRow.alignment = "CENTER"
    subsubRow.label(text="Drawing on: ")
    gpFrameStr = "-"
    if objIsGP:
        if isCurrentFrameOnGPFrame:
            gpFrameStr = "Current"
        else:
            subsubRow.alert = True
            gpFrameStr = str(utils_greasepencil.getLayerPreviousFrame(gp, context.scene.frame_current, "ACTIVE"))
    subsubRow.label(text=gpFrameStr)
