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

from shotmanager.utils import utils_ui
from shotmanager.utils import utils_greasepencil

from shotmanager.config import config


def draw_greasepencil_play_tools(self, context, shot, layersListDropdown=None):
    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences
    scene = context.scene
    layout = self.layout

    # if shot is None:
    #     return

    shotIndex = props.getShotIndex(shot)

    scale_y_pgOpsRow = 1.4

    # Object and layers ###
    ###################
    objIsGP = False
    selObjName = "-"
    gpObjectIsPinned = False

    editedGpencil = None
    if "" == props.stb_editedGPencilName or props.stb_editedGPencilName not in scene.objects:
        gpObjectIsPinned = False
        if context.object is not None:
            selObjName = context.object.name
            objIsGP = "GPENCIL" == context.object.type
            if objIsGP:
                editedGpencil = context.object
        # mainRow.label(text=f"Sel: {selObjName}, GP: {objIsGP}")

    else:
        if props.stb_hasPinnedObject:
            gpObjectIsPinned = True
            editedGpencil = scene.objects[props.stb_editedGPencilName]
            objIsGP = "GPENCIL" == editedGpencil.type
        else:
            gpObjectIsPinned = False

            gpFound = False
            if len(context.selected_objects) and context.object is not None:

                selObjName = context.object.name
                if "GPENCIL" == context.object.type:
                    # parentShot = props.getParentShotFromGpChild(context.object)
                    # if parentShot is None:
                    if True:
                        objIsGP = True
                        editedGpencil = context.object
                        gpFound = True

            if not gpFound:
                editedGpencil = scene.objects[props.stb_editedGPencilName]
                objIsGP = "GPENCIL" == editedGpencil.type

    leftSepFactor = 0.1

    box = layout.box()
    # utils_ui.drawSeparatorLine(layout)

    parentShot = props.getParentShotFromGpChild(editedGpencil)
    objIsValid = parentShot is None

    if True:
        # if objIsGP:
        gp_child = None
        if shot is not None:
            gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)
        gpIsStoryboardFrame = gp_child is not None and gp_child.name == editedGpencil.name

        col = box.column()
        col.enabled = objIsGP
        if not gpIsStoryboardFrame:
            freeGPRow = col.row(align=True)

            pinIcon = "PINNED" if gpObjectIsPinned else "UNPINNED"
            # freeGPRow.prop(props, "stb_hasPinnedObject", text="", icon=pinIcon)
            pinOp = freeGPRow.operator(
                "uas_shot_manager.pin_grease_pencil_object", text="", icon=pinIcon, depress=gpObjectIsPinned
            )
            pinOp.pin = not gpObjectIsPinned
            pinOp.pinnedObjName = "-" if editedGpencil is None else editedGpencil.name

            freeGPRow.separator(factor=2)

            freeGPRow.alert = True
            if parentShot is not None:
                freeGPRow.label(text="*** Not a valid Free Scene GP: " + parentShot.name)
            else:
                freeGPRow.label(text="*** Free Scene GP: ")
            freeGPRow.alert = False
            freeGPRow.label(text=f"{editedGpencil.name if objIsGP else '-'}")
            # freeGPRow.alert = True
            # freeGPRow.label(text=" ***")
            # freeGPRow.alert = False

            rightFreeGPRow = freeGPRow.row(align=True)
            rightFreeGPRow.alignment = "RIGHT"
            rightFreeGPRow.ui_units_x = 8
            rightFreeGPRow.prop(props.shotsGlobalSettings, "stb_camPOV_forFreeGP", text="")
            subrightFreeGPRow = rightFreeGPRow.row(align=True)
            subrightFreeGPRow.enabled = props.shotsGlobalSettings.stb_camPOV_forFreeGP
            subrightFreeGPRow.prop(props.shotsGlobalSettings, "stb_strokePlacement_forFreeGP", text="")

        # toolbar row ###
        ###################
        sepRow = col.row(align=True)
        sepRow.separator(factor=1)

        gpOpsRow = col.row(align=True)
        gpOpsRow.enabled = objIsValid
        gpOpsRow.scale_y = scale_y_pgOpsRow
        gpOpsRow.separator(factor=leftSepFactor)
        gpOpsSplit = gpOpsRow.split(factor=0.3)
        leftgpOpsRow = gpOpsSplit.row(align=True)
        drawGpToolbar(context, leftgpOpsRow, editedGpencil, gpIsStoryboardFrame, shotIndex)

        rightgpOpsRow = gpOpsSplit.row(align=True)
        autokeyRow = rightgpOpsRow.row(align=True)
        # rightgpOpsRow.alignment = "LEFT"
        # autokeyRow.scale_x = 0.75
        drawAutokey(context, autokeyRow)

        rightgpOpsRow.separator(factor=0.5)
        layersRow = rightgpOpsRow.row(align=True)
        # rightgpOpsRow.alignment = "RIGHT"
        drawLayersRow(context, props, layersRow, editedGpencil, objIsGP)

        drawClearLayer(context, rightgpOpsRow)

        ###################
        # play bar row ###
        ###################
        sepRow = col.row(align=True)
        sepRow.separator(factor=0.5)

        navRow = col.row(align=True)
        navRow.enabled = objIsValid
        navRow.separator(factor=leftSepFactor)
        navSplit = navRow.split(factor=0.6)
        leftNavRow = navSplit.row(align=True)
        drawPlayBar(context, leftNavRow)
        leftNavRow.separator(factor=1.45)
        drawLayersMode(context, leftNavRow, props)

        rightNavRow = navSplit.row(align=True)
        rightNavRow.separator(factor=1.45)
        drawKeyFrameMessage(context, rightNavRow, editedGpencil, objIsGP)

        # layers ##
        ##################
        sepRow = col.row(align=True)
        sepRow.separator(factor=0.5)

        matRow = col.row(align=False)
        matRow.enabled = objIsValid
        layersRow = matRow.row(align=True)
        layersRow.alignment = "RIGHT"
        # layersRow.prop(editedGpencil.data, "layers")
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

        if objIsGP:
            materialsRow = matRow.row(align=True)
            materialsRow.alignment = "RIGHT"
            materialsRow.label(text="Material:")
            # materialsRow.prop(editedGpencil, "material_slots")
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


def drawGpToolbar(context, layout, editedGpencil, gpIsStoryboardFrame, shotIndex):

    gpToolsRow = layout.row(align=True)
    #   gpToolsRow.ui_units_x = 3
    gpToolsRow.scale_x = 2.0
    # gpOpsLeftRow.alignment = "RIGHT"

    # if gpIsStoryboardFrame:
    if editedGpencil is not None and editedGpencil.mode == "PAINT_GPENCIL":
        gpToolsRow.operator("uas_shot_manager.select_grease_pencil_object", text="", icon="RESTRICT_SELECT_ON")
    else:
        gpToolsRow.operator(
            "uas_shot_manager.select_shot_grease_pencil", text="", icon="RESTRICT_SELECT_OFF"
        )  # .index = shotIndex

    if editedGpencil is not None and editedGpencil.mode == "PAINT_GPENCIL":
        icon = "GREASEPENCIL"
        gpToolsRow.alert = True
        gpToolsRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon=icon)
        gpToolsRow.alert = False
    else:
        # icon = "OUTLINER_OB_GREASEPENCIL"
        icon = "GREASEPENCIL"
        if gpIsStoryboardFrame:
            gpToolsRow.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon=icon)
        else:
            gpToolsRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon=icon)


def drawClearLayer(context, layout):
    gpOpsRightRow = layout.row(align=False)
    gpOpsRightRow.alignment = "RIGHT"
    gpOpsRightRow.scale_x = 1.2
    # gpOpsRightRow.separator(factor=0.1)
    gpOpsRightRow.operator("uas_shot_manager.clear_layer", text="", icon="MESH_PLANE")
    # gpOpsRightRow.separator(factor=0.1)


def drawPlayBar(context, layout):
    navRow = layout.row(align=True)
    navRow.scale_y = 1.2
    navRow.scale_x = 2.0
    navRow.operator("uas_shot_manager.greasepencil_previouskey", icon="PREV_KEYFRAME", text="")
    navRow.operator("uas_shot_manager.greasepencil_nextkey", icon="NEXT_KEYFRAME", text="")
    navRow.scale_x = 1.0


def drawLayersMode(context, layout, props):
    row = layout.row(align=False)
    # row.label(text="Apply to:")
    # row.scale_x = 2
    # row.ui_units_x = 14
    # row.alignment = "LEFT"
    row.prop(props, "greasePencil_layersMode", text="Apply ")
    row.prop(props, "greasePencil_layersModeB", text="Apply ")


def drawKeyFrameMessage(context, layout, editedGpencil, objIsGP):
    keyFrameRow = layout.row(align=True)

    isCurrentFrameOnGPFrame = False
    if objIsGP:
        isCurrentFrameOnGPFrame = utils_greasepencil.isCurrentFrameOnLayerKeyFrame(
            editedGpencil, context.scene.frame_current, "ACTIVE"
        )
    else:
        keyFrameRow.enabled = False

    subsubRow = keyFrameRow.row(align=True)
    subsubRow.alignment = "CENTER"

    subsubRow.label(text="Drawing on fr.: ")
    gpFrameStr = "-"
    if objIsGP:
        if isCurrentFrameOnGPFrame:
            gpFrameStr = f"{context.scene.frame_current} (Current)"
        else:
            subsubRow.alert = True
            prevFrame = utils_greasepencil.getLayerPreviousFrame(editedGpencil, context.scene.frame_current, "ACTIVE")
            gpFrameStr = f"{prevFrame}".rjust(6, " ")
    subsubRow.label(text=gpFrameStr)


def drawAutokey(context, layout):
    # auto key (code from the timeline of Blender)

    # subsubRow = keysRow.row(align=True)
    subsubRow = layout
    subsubRow.prop(context.tool_settings, "use_keyframe_insert_auto", text="", toggle=True)
    subsubRow.separator()
    # subsubRow = keysRow.row(align=True)
    # subsubRow.active = bpy.context.tool_settings.use_keyframe_insert_auto
    # subsubRow.popover(
    #     panel="TIME_PT_auto_keyframing",
    #     text="",
    # )


def drawLayersRow(context, props, layout, editedGpencil, objIsGP):
    # prefs = context.preferences.addons["shotmanager"].preferences
    framePreset = context.scene.UAS_shot_manager_props.stb_frameTemplate
    currentFrame = context.scene.frame_current

    def _draw_layer_button(layout, preset):
        if "CANVAS" != preset.id and not preset.used:
            return

        if editedGpencil is None:
            op = layout.operator(
                "uas_shot_manager.greasepencil_setlayerandmat", depress=False, icon=icon_OnprevFrame, text=""
            )
        else:
            layerExists = utils_greasepencil.gpLayerExists(editedGpencil, preset.layerName)

            if preset.layerName is not None and layerExists:
                currentFrameIsOnLayerKeyFrame = utils_greasepencil.isCurrentFrameOnLayerKeyFrame(
                    editedGpencil, currentFrame, preset.layerName
                )
                icon_frame = icon_OnFrame if currentFrameIsOnLayerKeyFrame else icon_OnprevFrame
                depressBut = utils_greasepencil.gpLayerIsActive(editedGpencil, preset.layerName)
                op = layout.operator(
                    "uas_shot_manager.greasepencil_setlayerandmat", depress=depressBut, icon=icon_frame, text=""
                )
                op.layerID = preset.id
                op.layerName = preset.layerName
                op.materialName = preset.materialName
                op.gpObjName = editedGpencil.name
            else:
                warningRow = layout.row(align=True)
                icon_frame = icon_OnprevFrame
                warningRow.alert = True
                warningRow.enabled = False
                warningRow.operator(
                    "uas_shot_manager.greasepencil_setlayerandmat", depress=False, icon=icon_frame, text=""
                ).layerID = f"{preset.id}_WARNING"

    usageButsRow = layout.row(align=True)
    # row.scale_x = 2.0
    # row.alignment = "EXPAND"
    # row.ui_units_x = 10

    icon_OnprevFrame = "KEYFRAME"
    icon_OnFrame = "KEYFRAME_HLT"

    # canvas layer #####
    preset = framePreset.getPresetByID("CANVAS")
    if preset is not None:
        _draw_layer_button(usageButsRow, preset)

    usageButsSubRow = usageButsRow.row(align=True)
    usageButsSubRow.scale_x = 2.0

    # BG layers #########
    preset_lines = framePreset.getPresetByID("BG_LINES")
    preset_fills = framePreset.getPresetByID("BG_FILLS")
    if preset_lines.used or preset_fills.used:
        layerCol = usageButsSubRow.column(align=True)
        layerCol.scale_y = 0.5 if preset_lines.used and preset_fills.used else 1.0
        _draw_layer_button(layerCol, preset_lines)
        _draw_layer_button(layerCol, preset_fills)

    # MG layers #########
    preset_lines = framePreset.getPresetByID("MG_LINES")
    preset_fills = framePreset.getPresetByID("MG_FILLS")
    if preset_lines.used or preset_fills.used:
        layerCol = usageButsSubRow.column(align=True)
        layerCol.scale_y = 0.5 if preset_lines.used and preset_fills.used else 1.0
        _draw_layer_button(layerCol, preset_lines)
        _draw_layer_button(layerCol, preset_fills)

    # FG layers #########
    preset_lines = framePreset.getPresetByID("FG_LINES")
    preset_fills = framePreset.getPresetByID("FG_FILLS")
    if preset_lines.used or preset_fills.used:
        layerCol = usageButsSubRow.column(align=True)
        layerCol.scale_y = 0.5 if preset_lines.used and preset_fills.used else 1.0
        _draw_layer_button(layerCol, preset_lines)
        _draw_layer_button(layerCol, preset_fills)

    # Rough layer #######
    preset_lines = framePreset.getPresetByID("ROUGH")
    _draw_layer_button(usageButsSubRow, preset_lines)


def drawKeysRow(context, props, layout, editedGpencil, objIsGP):
    keysRow = layout.row(align=True)
    keysRow.scale_x = 1.4
    keysRow.alignment = "CENTER"
    keysRow.enabled = objIsGP
    keysRow.operator("uas_shot_manager.greasepencil_previouskey", icon="PREV_KEYFRAME", text="")

    isCurrentFrameOnGPFrame = False
    if objIsGP:
        isCurrentFrameOnGPFrame = utils_greasepencil.isCurrentFrameOnLayerKeyFrame(
            editedGpencil, context.scene.frame_current, props.greasePencil_layersMode
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
    subsubRow.prop(props, "greasePencil_layersMode", text="Apply to")

    # settingsRow = settingsRow.row(align=True)
    subsubRow = settingsRow.row(align=True)
    subsubRow.alignment = "CENTER"
    subsubRow.label(text="Drawing on key frame: ")
    gpFrameStr = "-"
    if objIsGP:
        if isCurrentFrameOnGPFrame:
            gpFrameStr = "Current"
        else:
            subsubRow.alert = True
            gpFrameStr = str(
                utils_greasepencil.getLayerPreviousFrame(editedGpencil, context.scene.frame_current, "ACTIVE")
            )
    subsubRow.label(text=gpFrameStr)
