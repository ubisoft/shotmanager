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

from shotmanager.utils import utils_greasepencil


from shotmanager.config import config


##########################################################
# toolbar rows
##########################################################


def drawDrawingToolbarRow(
    context, layout, props, editedGpencil, gpIsStoryboardFrame, shotIndex, leftSepFactor, objIsGP
):
    scale_y_pgOpsRow = 1.45

    if True:
        gpOpsRow = layout.row(align=True)
        gpOpsRow.scale_y = scale_y_pgOpsRow
        drawGpToolbar(context, props, gpOpsRow, editedGpencil, gpIsStoryboardFrame, shotIndex)

        scale_y_pgOpsRow
        gpOpsRow.scale_y = 1.0
        drawDrawingMatRow(context, gpOpsRow, props, editedGpencil, objIsGP)

        sepRow = layout.row(align=True)
        sepRow.separator(factor=1.0)

    gpOpsRow = layout.row(align=True)
    gpOpsRow.scale_y = scale_y_pgOpsRow
    gpOpsRow.separator(factor=leftSepFactor)

    # not nice when num buttons is 1:
    # gpOpsSplit = gpOpsRow.split(factor=0.3)
    gpOpsSplit = gpOpsRow.grid_flow(align=False, columns=4)

    if False:
        # leftgpOpsRow = gpOpsSplit.row(align=True)
        # leftgpOpsRow.alignment = "LEFT"
        drawGpToolbar(context, props, gpOpsSplit, editedGpencil, gpIsStoryboardFrame, shotIndex)

    # key frames
    #####################
    rightgpOpsRow = gpOpsSplit.row(align=True)

    # rightgpOpsRow.separator(factor=0.5)
    layersRow = rightgpOpsRow.row(align=False)
    # rightgpOpsRow.alignment = "RIGHT"
    drawLayersRow(context, props, layersRow, editedGpencil)

    autokeyRow = rightgpOpsRow.row(align=True)
    rightgpOpsRow.alignment = "CENTER"
    # autokeyRow.scale_x = 0.75
    autokeyRow.separator(factor=1.0)
    drawAutokey(context, autokeyRow)

    # autokeyRow.scale_x = 2.0
    drawKeyFrameActionsRow(context, props, autokeyRow, editedGpencil, gpIsStoryboardFrame)

    drawClearLayer(context, gpOpsSplit, editedGpencil)


def drawDrawingPlaybarRow(context, layout, props, editedGpencil, leftSepFactor, objIsGP):
    navRow = layout.row(align=True)
    navRow.separator(factor=leftSepFactor)
    navSplit = navRow.split(factor=0.6)
    leftNavRow = navSplit.row(align=True)
    drawPlayBar(context, leftNavRow, editedGpencil, objIsGP)
    leftNavRow.separator(factor=1.45)
    drawLayersMode(context, leftNavRow, props)

    rightNavRow = navSplit.row(align=True)
    rightNavRow.separator(factor=1.45)
    drawKeyFrameMessage(context, rightNavRow, editedGpencil, objIsGP)


def drawDrawingMatRow(context, layout, props, editedGpencil, objIsGP):
    matRow = layout.row(align=False)
    layersRow = matRow.row(align=True)
    layersRow.alignment = "RIGHT"
    # layersRow.prop(editedGpencil.data, "layers")
    layersRow.label(text="Layer:")
    # layersRow.prop(prefs, "layersListDropdown", text="Layers")

    # Grease pencil layer.
    # gpl = context.active_gpencil_layer
    gpl = editedGpencil.data.layers.active
    if gpl is not None and gpl.info is not None:
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
        sub.alert = gpl.lock and "OBJECT" != editedGpencil.mode
        sub.prop(gpl, "lock", text="")
        sub.alert = False
    else:
        sub.label(text="", icon="LOCKED")

    # Active material ###
    ###################

    if objIsGP:
        materialsRow = matRow.row(align=False)
        materialsRow.alignment = "RIGHT"
        materialsRow.label(text="Material:")
        # materialsRow.label(text="Material:")
        materialsSubRow = materialsRow.row(align=True)
        materialsSubRow.ui_units_x = 7
        matTxt = "-"
        if editedGpencil:
            matTxt = f"{editedGpencil.active_material.name}"
        materialsSubRow.label(text=matTxt)
        materialsSubRowRight = materialsSubRow.row()
        materialsSubRowRight.ui_units_x = 1
        # materialsRow.prop(editedGpencil, "material_slots")
        materialsSubRowRight.prop(props, "greasePencil_activeMaterial", text="")


##########################################################
# buttons
##########################################################


def drawGpToolbar(context, props, layout, editedGpencil, gpIsStoryboardFrame, shotIndex):

    gpToolsRow = layout.row(align=True)
    #   gpToolsRow.ui_units_x = 3
    gpToolsRow.scale_x = 2.0
    # gpOpsLeftRow.alignment = "RIGHT"

    devDebug_displayAdv = False

    # if gpIsStoryboardFrame:
    # if devDebug_displayAdv:
    #     if editedGpencil.mode == "PAINT_GPENCIL":
    #         gpToolsRow.operator("uas_shot_manager.select_grease_pencil_object", text="", icon="RESTRICT_SELECT_ON")
    #     else:
    #         gpToolsRow.operator(
    #             "uas_shot_manager.select_shot_grease_pencil", text="", icon="RESTRICT_SELECT_OFF"
    #         )  # .index = shotIndex

    # if editedGpencil.mode == "PAINT_GPENCIL":
    if "OBJECT" != editedGpencil.mode:
        icon = "GREASEPENCIL"
        gpToolsRow.alert = True
        gpToolsRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon=icon)
        gpToolsRow.alert = False
    else:
        # icon = "OUTLINER_OB_GREASEPENCIL"
        icon = "OUTLINER_DATA_GP_LAYER"
        # if gpIsStoryboardFrame:
        # wkip operator removed ***
        # gpToolsRow.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon=icon)

        opMode = "DRAW" if props.isContinuousGPEditingModeActive() else "SELECT"

        # if gp == context.active_object and context.active_object.mode == "PAINT_GPENCIL":
        # if gp.mode == "PAINT_GPENCIL":
        op = gpToolsRow.operator("uas_shot_manager.greasepencil_select_and_draw", text="", icon=icon)
        op.index = shotIndex
        op.toggleDrawEditing = True
        op.mode = opMode

        # else:
        #     gpToolsRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon=icon)

    # WPAINT_HLT SCULPTMODE_HLT
    if devDebug_displayAdv:
        gpToolsRow.operator(
            "uas_shot_manager.update_grease_pencil", text="", icon="SCULPTMODE_HLT"
        ).shotIndex = shotIndex
        gpToolsRow.operator("uas_shot_manager.update_grease_pencil", text="", icon="WPAINT_HLT").shotIndex = shotIndex

    if devDebug_displayAdv:
        gpToolsRow.operator("uas_shot_manager.update_grease_pencil", text="", icon="FILE_REFRESH").shotIndex = shotIndex

    gpToolsRow.scale_x = 1.0


def drawClearLayer(context, layout, editedGpencil):
    gpOpsRightRow = layout.row(align=False)
    gpOpsRightRow.alignment = "RIGHT"
    gpOpsRightRow.scale_x = 1.2
    # gpOpsRightRow.separator(factor=0.1)
    gpOpsRightRow.operator_context = "INVOKE_DEFAULT"
    gpOpsRightRow.operator("uas_shot_manager.clear_layer", text="", icon="MESH_PLANE").gpName = editedGpencil.name
    # gpOpsRightRow.operator("uas_shot_manager.clear_layer", text="", icon="MESH_PLANE").mode = "CURRENT_STB_FRAME"
    # gpOpsRightRow.separator(factor=0.1)


def drawPlayBar(context, layout, editedGpencil, objIsGP):
    navRow = layout.row(align=True)
    navRow.scale_y = 1.0
    navRow.scale_x = 2.0
    op = navRow.operator("uas_shot_manager.greasepencil_ui_navigation_keys", icon="PREV_KEYFRAME", text="")
    op.navigDirection = "PREVIOUS"
    op.gpName = editedGpencil.name
    op = navRow.operator("uas_shot_manager.greasepencil_ui_navigation_keys", icon="NEXT_KEYFRAME", text="")
    op.navigDirection = "NEXT"
    op.gpName = editedGpencil.name
    navRow.scale_x = 1.0


def drawLayersMode(context, layout, props):
    row = layout.row(align=False)
    # row.label(text="Apply to:")
    # row.scale_x = 2
    # row.ui_units_x = 14
    # row.alignment = "LEFT"
    split = row.split(factor=0.4)
    split.label(text="Navigate on:")
    split.prop(props, "greasePencil_layersMode", text="")


#  row.prop(props, "greasePencil_layersModeB", text="Apply ")


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


def drawLayersRow(context, props, layout, editedGpencil):
    props = config.getAddonProps(context.scene)
    # prefs = config.getAddonPrefs()
    framePreset = props.stb_frameTemplate
    currentFrame = context.scene.frame_current

    def _draw_layer_button(layout, preset, row_scale_x=1.0, enabled=True):
        if preset is None:
            return

        if "CANVAS" != preset.id and not preset.used:
            return

        layerExists = utils_greasepencil.gpLayerExists(editedGpencil, preset.layerName)

        if preset.layerName is not None and layerExists:
            layerRow = layout.row(align=True)
            layerRow.enabled = enabled
            layerRow.scale_x = row_scale_x

            currentFrameIsOnLayerKeyFrame = utils_greasepencil.isCurrentFrameOnLayerKeyFrame(
                editedGpencil, currentFrame, preset.layerName
            )
            if utils_greasepencil.isLayerVisibile(editedGpencil, preset.layerName):
                icon_frame = icon_OnFrame if currentFrameIsOnLayerKeyFrame else icon_OnprevFrame
                sm_icon_id = 0
            else:
                icon_frame = "NONE"
                sm_icon = config.icons_col[
                    "ShotManager_GPToolsHiddenKey_32"
                    if currentFrameIsOnLayerKeyFrame
                    else "ShotManager_GPToolsHidden_32"
                ]
                sm_icon_id = sm_icon.icon_id

            depressBut = utils_greasepencil.gpLayerIsActive(editedGpencil, preset.layerName)
            op = layerRow.operator(
                "uas_shot_manager.greasepencil_setlayerandmatandvisib",
                depress=depressBut,
                icon=icon_frame,
                icon_value=sm_icon_id,
                text="",
            )
            op.layerID = preset.id
            op.layerName = preset.layerName
            op.materialName = preset.materialName
            op.gpObjName = editedGpencil.name
        else:
            warningRow = layout.row(align=True)
            icon_frame = icon_OnprevFrame
            warningRow.scale_x = row_scale_x
            warningRow.alert = True
            warningRow.enabled = False
            op = warningRow.operator(
                "uas_shot_manager.greasepencil_setlayerandmatandvisib", depress=False, icon=icon_frame, text=""
            )
            op.layerID = f"{preset.id}_WARNING"

    usageButsRow = layout.row(align=True)
    # row.scale_x = 2.0
    # row.alignment = "EXPAND"
    # row.ui_units_x = 10

    icon_OnprevFrame = "KEYFRAME"
    icon_OnFrame = "KEYFRAME_HLT"

    # canvas layer #####
    preset = framePreset.getPresetByID("CANVAS")
    if preset is not None:
        _draw_layer_button(usageButsRow, preset, enabled=False)

    usageButsSubRow = usageButsRow.row(align=True)
    usageButsSubRow.scale_x = 2.0

    doubleLine_scale_y = 0.54
    # BG layers #########
    preset_lines = framePreset.getPresetByID("BG_LINES")
    preset_fills = framePreset.getPresetByID("BG_FILLS")
    if (preset_lines is not None and preset_lines.used) or (preset_fills is not None and preset_fills.used):
        layerCol = usageButsSubRow.column(align=True)
        layerCol.scale_y = doubleLine_scale_y if preset_lines.used and preset_fills.used else 1.0
        _draw_layer_button(layerCol, preset_lines)
        _draw_layer_button(layerCol, preset_fills)

    # MG layers #########
    preset_lines = framePreset.getPresetByID("MG_LINES")
    preset_fills = framePreset.getPresetByID("MG_FILLS")
    if (preset_lines is not None and preset_lines.used) or (preset_fills is not None and preset_fills.used):
        layerCol = usageButsSubRow.column(align=True)
        layerCol.scale_y = doubleLine_scale_y if preset_lines.used and preset_fills.used else 1.0
        _draw_layer_button(layerCol, preset_lines)
        _draw_layer_button(layerCol, preset_fills)

    # FG layers #########
    preset_lines = framePreset.getPresetByID("FG_LINES")
    preset_fills = framePreset.getPresetByID("FG_FILLS")
    if (preset_lines is not None and preset_lines.used) or (preset_fills is not None and preset_fills.used):
        layerCol = usageButsSubRow.column(align=True)
        layerCol.scale_y = doubleLine_scale_y if preset_lines.used and preset_fills.used else 1.0
        _draw_layer_button(layerCol, preset_lines)
        _draw_layer_button(layerCol, preset_fills)

    # # persp layer #######
    # if preset_lines.used or preset_fills.used:
    #     layerCol = usageButsSubRow.column(align=True)
    #     layerCol.scale_y = doubleLine_scale_y if preset_lines.used and preset_fills.used else 1.0

    preset_persp = framePreset.getPresetByID("PERSP")
    if preset_persp is not None and preset_persp.used:
        # layersubRow = usageButsSubRow.row(align=True)
        # layersubRow.scale_x = 0.5
        _draw_layer_button(usageButsSubRow, preset_persp, row_scale_x=0.75)

    # rough layer #######
    preset_rough = framePreset.getPresetByID("ROUGH")
    if preset_rough is not None and preset_rough.used:
        _draw_layer_button(usageButsSubRow, preset_rough)

    layout.separator(factor=1.0)
    # usageButsSubRow.scale_x = 1.0
    # layout.scale_x = 1.0


def drawKeyFrameActionsRow(context, props, layout, editedGpencil, gpIsStoryboardFrame):
    # prefs = config.getAddonPrefs()
    # framePreset = context.scene.UAS_shot_manager_props.stb_frameTemplate
    currentFrame = context.scene.frame_current

    layerMode = "ACTIVE"  # preset.layerName
    currentFrameIsOnLayerKeyFrame = utils_greasepencil.isCurrentFrameOnLayerKeyFrame(
        editedGpencil, currentFrame, layerMode
    )

    actionsButsRow = layout.row(align=True)
    actionsButsRow.scale_x = 1.4

    actionsButsSubRow = actionsButsRow.row(align=True)
    # actionsButsSubRow.enabled = not currentFrameIsOnLayerKeyFrame
    icon = config.icons_col["ShotManager_GPTools_Add_32"]
    op = actionsButsSubRow.operator(
        "uas_shot_manager.greasepencil_setkeyframe", depress=False, icon_value=icon.icon_id, text=""
    )
    op.mode = "ADD"
    op.gpName = editedGpencil.name
    op.layerName = layerMode

    actionsButsSubRow = actionsButsRow.row(align=True)
    # actionsButsSubRow.enabled = not currentFrameIsOnLayerKeyFrame
    icon = config.icons_col["ShotManager_GPTools_Duplicate_32"]
    op = actionsButsSubRow.operator(
        "uas_shot_manager.greasepencil_setkeyframe", depress=False, icon_value=icon.icon_id, text=""
    )
    op.mode = "DUPLICATE"
    op.gpName = editedGpencil.name
    op.layerName = layerMode

    actionsButsSubRow = actionsButsRow.row(align=True)
    # actionsButsSubRow.enabled = currentFrameIsOnLayerKeyFrame
    icon = config.icons_col["ShotManager_GPTools_Remove_32"]
    op = actionsButsSubRow.operator(
        "uas_shot_manager.greasepencil_setkeyframe", depress=False, icon_value=icon.icon_id, text=""
    )
    op.mode = "REMOVE"
    op.gpName = editedGpencil.name
    op.layerName = layerMode


# actionsButsRow.scale_x = 1.0
