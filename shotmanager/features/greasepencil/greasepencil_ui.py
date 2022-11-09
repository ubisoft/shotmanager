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

from shotmanager.ui import sm_shots_global_settings_ui_cameras
from shotmanager.ui import sm_shots_global_settings_ui_overlays

from shotmanager.utils import utils_ui
from shotmanager.utils import utils_greasepencil


from shotmanager.config import config


def draw_greasepencil_play_tools(self, context, shot, layersListDropdown=None):
    props = config.getAddonProps(context.scene)
    prefs = config.getAddonPrefs()
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
    # utils_ui.separatorLine(layout)

    parentShot = props.getParentShotFromGpChild(editedGpencil)
    objIsValid = parentShot is None

    if True:
        # if objIsGP:
        gp_child = None
        if shot is not None:
            gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)
        gpIsStoryboardFrame = gp_child is not None and gp_child.name == editedGpencil.name

        col = box.column()

        experimRow = col.row()
        experimRow.alert = True
        experimRow.alignment = "CENTER"
        experimRow.label(text="*** Experimental - Still Under Development ***")

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
                freeGPRow.label(text="Free Scene GP : ")
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
            subrightFreeGPRow.prop(
                props.shotsGlobalSettings, "stb_changeCursorPlacement_forFreeGP", text="", icon="CURSOR"
            )

        # toolbar row ###
        ###################
        sepRow = col.row(align=True)
        sepRow.separator(factor=1)

        gpOpsRow = col.row(align=True)
        gpOpsRow.enabled = objIsValid
        # gpOpsRow.scale_y = scale_y_pgOpsRow
        gpOpsRow.separator(factor=leftSepFactor)
        # gpOpsSplit = gpOpsRow.split(factor=0.3)
        gpOpsSplit = gpOpsRow.grid_flow(align=False, columns=4)
        leftgpOpsRow = gpOpsSplit.row(align=True)
        drawGpToolbar(context, leftgpOpsRow, props, editedGpencil, gpIsStoryboardFrame, shotIndex)

        rightgpOpsRow = gpOpsSplit.row(align=True)
        rightgpOpsRow.alignment = "LEFT"

        drawDrawingMatRow(context, rightgpOpsRow, props, objIsValid, objIsGP)

        # autokeyRow.scale_x = 0.75
        autokeyRow = rightgpOpsRow.row(align=True)
        autokeyRow.separator(factor=2.0)
        drawAutokey(context, autokeyRow)

        drawKeyFrameActionsRow(context, props, gpOpsSplit, editedGpencil, objIsGP)
        # rightgpOpsRow.separator(factor=1.0)

        # layersRow = rightgpOpsRow.row(align=True)
        # rightgpOpsRow.alignment = "RIGHT"
        # drawLayersRow(context, props, layersRow, editedGpencil, objIsGP)

        layersRow = gpOpsSplit.row(align=True)
        layersRow.alignment = "RIGHT"
        drawClearLayer(context, layersRow)

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

        ##################
        # layers ##
        ##################
        sepRow = col.row(align=True)
        sepRow.separator(factor=0.5)

        drawMatRow(context, col, props, objIsGP)

        utils_ui.separatorLine(box)

    # overlay tools
    #########################
    row = box.row()
    row.use_property_decorate = False
    row.separator(factor=1.8)
    col = row.column(align=True)
    sm_shots_global_settings_ui_overlays.draw_overlays_global_settings(context, col, mode="GP")


def drawDrawingMatRow(context, layout, props, objIsValid, objIsGP):
    matRow = layout.row(align=False)
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
        # sub.alert = gpl.lock
        sub.prop(gpl, "lock", text="")
    # sub.alert = False
    else:
        sub.label(text="", icon="LOCKED")


def drawMatRow(context, layout, props, objIsGP):
    # Active material ###
    ###################

    if objIsGP:
        materialsRow = layout.row(align=True)
        materialsRow.alignment = "RIGHT"
        materialsRow.label(text="Material:")
        # materialsRow.prop(editedGpencil, "material_slots")
        materialsRow.prop(props, "greasePencil_activeMaterial", text="")


def drawGpToolbar(context, layout, props, editedGpencil, gpIsStoryboardFrame, shotIndex):

    gpToolsRow = layout.row(align=True)
    #   gpToolsRow.ui_units_x = 3
    gpToolsRow.scale_x = 2.0
    # gpOpsLeftRow.alignment = "RIGHT"

    # if gpIsStoryboardFrame:
    objName = ""
    if editedGpencil is not None:
        objName = editedGpencil.name

    gpToolsRow.operator(
        "uas_shot_manager.select_grease_pencil_object", text="", icon="RESTRICT_SELECT_OFF"
    ).gpName = objName
    # else:
    #     gpToolsRow.operator(
    #         "uas_shot_manager.select_shot_grease_pencil", text="", icon="RESTRICT_SELECT_OFF"
    #     )  # .index = shotIndex

    if editedGpencil is not None and editedGpencil.mode == "PAINT_GPENCIL":
        icon = "GREASEPENCIL"
        gpToolsRow.alert = True
        op = gpToolsRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon=icon)
        op.gpName = objName
        op.layerName = props.greasePencil_layersModeB
        gpToolsRow.alert = False
    else:
        # icon = "OUTLINER_OB_GREASEPENCIL"
        icon = "GREASEPENCIL"
        if gpIsStoryboardFrame:
            # wkip operator removed ***
            # gpToolsRow.operator("uas_shot_manager.draw_on_grease_pencil", text="", icon=icon)
            opMode = "DRAW" if props.isContinuousGPEditingModeActive() else "SELECT"

            # if gp == context.active_object and context.active_object.mode == "PAINT_GPENCIL":
            # if gp.mode == "PAINT_GPENCIL":
            icon = "GREASEPENCIL"
            gpToolsRow.alert = True
            op = gpToolsRow.operator("uas_shot_manager.greasepencil_select_and_draw", text="", icon=icon)
            op.index = shotIndex
            op.toggleDrawEditing = True
            op.mode = opMode

        else:
            op = gpToolsRow.operator("uas_shot_manager.toggle_grease_pencil_draw_mode", text="", icon=icon)
            op.gpName = objName
            op.layerName = props.greasePencil_layersModeB
    gpToolsRow.scale_x = 1.0


def drawClearLayer(context, layout):
    gpOpsRightRow = layout.row(align=False)
    gpOpsRightRow.alignment = "RIGHT"
    gpOpsRightRow.scale_x = 1.2
    # gpOpsRightRow.separator(factor=0.1)
    gpOpsRightRow.operator("uas_shot_manager.clear_layer", text="", icon="MESH_PLANE")
    # gpOpsRightRow.separator(factor=0.1)


def drawPlayBar(context, layout):
    navRow = layout.row(align=True)
    navRow.scale_y = 1.0
    navRow.scale_x = 2.0
    op = navRow.operator("uas_shot_manager.greasepencil_ui_navigation_keys", icon="PREV_KEYFRAME", text="")
    op.navigDirection = "PREVIOUS"
    op = navRow.operator("uas_shot_manager.greasepencil_ui_navigation_keys", icon="NEXT_KEYFRAME", text="")
    op.navigDirection = "NEXT"
    navRow.scale_x = 1.0


def drawLayersMode(context, layout, props):
    row = layout.row(align=False)
    # row.label(text="Apply to:")
    # row.scale_x = 2
    # row.ui_units_x = 14
    # row.alignment = "LEFT"
    split = row.split(factor=0.4)
    # row.prop(props, "greasePencil_layersMode", text="Apply ")
    split.label(text="Navigate on:")
    split.prop(props, "greasePencil_layersModeB", text="")


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
    # subsubRow.separator(factor=1.0)
    subsubRow.prop(context.tool_settings, "use_keyframe_insert_auto", text="", toggle=True)
    subsubRow.separator(factor=1.0)
    # subsubRow = keysRow.row(align=True)
    # subsubRow.active = bpy.context.tool_settings.use_keyframe_insert_auto
    # subsubRow.popover(
    #     panel="TIME_PT_auto_keyframing",
    #     text="",
    # )


def drawLayersRow(context, props, layout, editedGpencil, objIsGP):
    props = config.getAddonProps(context.scene)
    # prefs = config.getAddonPrefs()
    framePreset = props.stb_frameTemplate
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

    # persp layer #######
    preset_lines = framePreset.getPresetByID("PERSP")
    _draw_layer_button(usageButsSubRow, preset_lines)

    # rough layer #######
    preset_lines = framePreset.getPresetByID("ROUGH")
    _draw_layer_button(usageButsSubRow, preset_lines)


def drawKeyFrameActionsRow(context, props, layout, editedGpencil, objIsGP):
    # prefs = config.getAddonPrefs()
    # framePreset = context.scene.UAS_shot_manager_props.stb_frameTemplate
    currentFrame = context.scene.frame_current

    layerMode = "ACTIVE"  # preset.layerName
    if editedGpencil is None:
        currentFrameIsOnLayerKeyFrame = False
    else:
        currentFrameIsOnLayerKeyFrame = utils_greasepencil.isCurrentFrameOnLayerKeyFrame(
            editedGpencil, currentFrame, layerMode
        )

    actionsButsRow = layout.row(align=True)
    actionsButsRow.scale_x = 1.4

    actionsButsSubRow = actionsButsRow.row(align=True)
    # actionsButsSubRow.enabled = not currentFrameIsOnLayerKeyFrame and objIsGP
    icon = config.icons_col["ShotManager_GPTools_Add_32"]
    op = actionsButsSubRow.operator(
        "uas_shot_manager.greasepencil_setkeyframe", depress=False, icon_value=icon.icon_id, text=""
    )
    op.mode = "ADD"
    if objIsGP:
        op.gpName = editedGpencil.name
        op.layerName = layerMode

    actionsButsSubRow = actionsButsRow.row(align=True)
    # actionsButsSubRow.enabled = not currentFrameIsOnLayerKeyFrame and objIsGP
    icon = config.icons_col["ShotManager_GPTools_Duplicate_32"]
    op = actionsButsSubRow.operator(
        "uas_shot_manager.greasepencil_setkeyframe", depress=False, icon_value=icon.icon_id, text=""
    )
    op.mode = "DUPLICATE"
    if objIsGP:
        op.gpName = editedGpencil.name
        op.layerName = layerMode

    actionsButsSubRow = actionsButsRow.row(align=True)
    #  actionsButsSubRow.enabled = currentFrameIsOnLayerKeyFrame and objIsGP
    icon = config.icons_col["ShotManager_GPTools_Remove_32"]
    op = actionsButsSubRow.operator(
        "uas_shot_manager.greasepencil_setkeyframe", depress=False, icon_value=icon.icon_id, text=""
    )
    op.mode = "REMOVE"
    if objIsGP:
        op.gpName = editedGpencil.name
        op.layerName = layerMode


# actionsButsRow.scale_x = 1.0
