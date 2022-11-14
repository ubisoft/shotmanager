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
Rendering UI
"""

from pathlib import Path

import bpy
from bpy.types import Panel

from ..config import config
from ..utils import utils
from ..utils import utils_ui

from shotmanager.utils.utils_shot_manager import getShotManagerWanring
from shotmanager.warnings.warnings_ui import drawWarnings


class UAS_PT_ShotManagerRenderPanelStdalone(Panel):
    bl_idname = "UAS_PT_ShotManagerRenderPanelStdalone"
    bl_label = " Shot Manager - Render" + " - V. " + utils.addonVersion("Ubisoft Shot Manager")[0]
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng - Render"

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()
        displayPanel = prefs.separatedRenderPanel
        displayPanel = displayPanel and props.getCurrentShot() is not None

        return displayPanel and prefs.display_render_panel

    def draw_header(self, context):

        props = config.getAddonProps(context.scene)
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)
        row.label(icon="RENDER_ANIMATION")

        if props.use_project_settings:
            if "" == props.project_name:
                row.alert = True
                row.label(text="<No Project Name>")
                row.alert = False
            else:
                row.label(text=props.project_name)

        addonWarning = getShotManagerWanring()
        if "" != addonWarning:
            betaRow = row.row()
            betaRow.alert = True
            if "beta" in addonWarning.lower():
                betaRow.label(text=" ** BETA **")
            else:
                betaRow.label(text=f" *** {addonWarning} ***")

    def draw_header_preset(self, context):
        drawHeaderPreset(self, context)

    def draw(self, context):
        draw3DRenderPanel(self, context)


class UAS_PT_ShotManagerRenderPanel(Panel):
    bl_label = "Rendering"
    bl_idname = "UAS_PT_ShotManagerRenderPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()
        val = not props.dontRefreshUI() and len(props.takes) and len(props.get_shots())
        val = val and not prefs.separatedRenderPanel
        return val and prefs.display_render_panel

    # def check(self, context):
    #     # should we redraw when a button is pressed?
    #     if True:
    #         return True
    #     return False

    def draw_header(self, context):
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)
        # icon = config.icons_col["ShotManager_Retimer_32"]
        # row.label(icon=icon.icon_id)
        row.label(icon="RENDER_ANIMATION")

    def draw_header_preset(self, context):
        drawHeaderPreset(self, context)

    def draw(self, context):
        draw3DRenderPanel(self, context)


def drawHeaderPreset(self, context):
    layout = self.layout
    layout.emboss = "NONE"
    row = layout.row(align=True)

    if config.devDebug:
        subrow = row.row(align=True)
        subrow.alert = True
        subrow.operator("uas_shot_manager.render_prefs", icon="PREFERENCES", text="")

    versionStr = utils.addonVersion("Video Tracks")
    subRow = row.row()
    subRow.enabled = versionStr is not None
    subRow.operator(
        "uas_shot_manager.go_to_video_tracks", text="", icon="SEQ_STRIP_DUPLICATE"
    ).vseSceneName = "SM_CheckSequence"

    row.separator(factor=0.5)
    icon = config.icons_col["General_Explorer_32"]
    row.operator("uas_shot_manager.open_explorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
        bpy.data.filepath
    )

    row.separator(factor=0.5)
    row.menu("UAS_MT_Shot_Manager_prefs_rendermenu", icon="PREFERENCES", text="")
    row.separator(factor=1.0)


def drawRenderInfos(context, layout):
    def _getResText(imgRes_x, imgRes_y, finalRes_x, finalRes_y):
        infosStr = f"Image Res: {imgRes_x} x {imgRes_y},  "
        infosStr += f"Final Res: {finalRes_x} x {finalRes_y},  "
        return infosStr

    scene = context.scene
    props = config.getAddonProps(context.scene)
    iconExplorer = config.icons_col["General_Explorer_32"]

    sepHeight = 0.2
    sepFactor = 1

    if props.displayStillProps:
        renderPreset = props.renderSettingsStill
    elif props.displayAnimationProps:
        renderPreset = props.renderSettingsAnim
    elif props.displayAllEditsProps:
        renderPreset = props.renderSettingsAll
    elif props.displayOtioProps:
        renderPreset = props.renderSettingsOtio
    elif props.displayPlayblastProps:
        renderPreset = props.renderSettingsPlayblast

    # imgRes = props.getRenderResolution()
    # imgRes = props.convertToSupportedRenderResolution(imgRes)
    # finalRes = props.getRenderResolutionForFinalOutput(resPercentage=100)
    # finalRes = props.convertToSupportedRenderResolution(finalRes)

    imgRes = props.getOutputResolution(scene, renderPreset, "FINAL_RENDERED_IMG_RES", forceMultiplesOf2=True)
    finalRes = props.getOutputResolution(scene, renderPreset, "FINAL_FRAMED_IMG_RES", forceMultiplesOf2=True)

    ######################################

    col = layout.column()
    col.scale_y = 0.7

    utils_ui.separatorLine(col, padding_bottom=1.5, padding_top=0.2)

    titleRow = col.row()
    titleRow.label(text="Output Infos:")
    if props.use_project_settings:
        subTitleRow = titleRow.row()
        if (
            (props.displayStillProps and props.renderSettingsStill.bypass_rendering_project_settings)
            or (props.displayAnimationProps and props.renderSettingsAnim.bypass_rendering_project_settings)
            or (props.displayAllEditsProps and props.renderSettingsAll.bypass_rendering_project_settings)
        ):
            subTitleRow.alert = True
            subTitleRow.label(text="- Bypassing Project Settings -")
        else:
            subTitleRow.label(text="- Using Project Settings -")
        fps = props.project_fps
    else:
        # fps = scene.render.fps
        fps = utils.getSceneEffectiveFps(scene)

    col.separator(factor=0.5)

    row = col.row()
    row.separator(factor=sepFactor)

    #     infosStr = f"Image Res: {props.project_resolution_x} x {props.project_resolution_y}, "
    #     infosStr += f"Final Res: {props.project_resolution_framed_x} x {props.project_resolution_framed_y}, "
    #     infosStr += f"{props.project_fps} fps"
    # else:
    #     infosStr = f"Image Res: {scene.render.resolution_x} x {scene.render.resolution_y}, "
    #     infosStr += f"Final Res: {props.project_resolution_framed_x} x {props.project_resolution_framed_y}, "
    #     # infosStr = f"{scene.render.fps} fps"
    #     infosStr = f"{utils.getSceneEffectiveFps(scene)} fps"

    # STILL ###
    if props.displayStillProps:
        # if props.renderSettingsStill.bypass_rendering_project_settings:
        #     finalRes = props.getRenderResolutionForFinalOutput(
        #         resPercentage=props.renderSettingsStill.resolutionPercentage,
        #         useStampInfo=props.renderSettingsStill.useStampInfo,
        #     )
        #     finalRes = props.convertToSupportedRenderResolution(finalRes)

        infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
        infosStr += f"{fps} fps"
        row.label(text=infosStr)

        # TODO wkip
        if not props.use_project_settings and 100 != scene.render.resolution_percentage:
            row = col.row()
            row.alert = True
            row.label(text="*** Warning: Resolution Percentage is not 100% ***")
            infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
            row = col.row()
            row.alert = True
            row.separator(factor=sepFactor)
            row.label(text=infosStr)

        col.separator(factor=sepHeight)
        row = col.row()
        filePath = props.getCurrentShot().getOutputMediaPath("SH_STILL", specificFrame=bpy.context.scene.frame_current)
        row.separator(factor=sepFactor)
        row.label(text="Current Image: " + filePath)
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath
        col.separator()

    # ANIMATION ###
    elif props.displayAnimationProps:
        # if props.renderSettingsAnim.bypass_rendering_project_settings:
        #     finalRes = props.getRenderResolutionForFinalOutput(
        #         resPercentage=props.renderSettingsAnim.resolutionPercentage,
        #         useStampInfo=props.renderSettingsAnim.useStampInfo,
        #     )
        #     finalRes = props.convertToSupportedRenderResolution(finalRes)

        infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
        infosStr += f"{fps} fps"
        row.label(text=infosStr)

        # TODO wkip
        if not props.use_project_settings and 100 != scene.render.resolution_percentage:
            row = col.row()
            row.alert = True
            row.label(text="*** Warning: Resolution Percentage is not 100% ***")
            infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
            row = col.row()
            row.alert = True
            row.separator(factor=sepFactor)
            row.label(text=infosStr)

        col.separator(factor=sepHeight)
        row = col.row()
        filePath = props.getCurrentShot().getOutputMediaPath("SH_VIDEO", provideName=False)
        row.separator(factor=sepFactor)
        row.label(text="Rendered in: " + filePath)
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath
        col.separator()

    # ALL SHOTS ###
    elif props.displayAllEditsProps:
        # if props.renderSettingsAll.bypass_rendering_project_settings:
        #     finalRes = props.getRenderResolutionForFinalOutput(
        #         resPercentage=props.renderSettingsAll.resolutionPercentage,
        #         useStampInfo=props.renderSettingsAll.useStampInfo,
        #     )
        #     finalRes = props.convertToSupportedRenderResolution(finalRes)

        infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
        infosStr += f"{fps} fps"
        row.label(text=infosStr)

        # TODO wkip
        if not props.use_project_settings and 100 != scene.render.resolution_percentage:
            row = col.row()
            row.alert = True
            row.label(text="*** Warning: Resolution Percentage is not 100% ***")
            infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
            row = col.row()
            row.alert = True
            row.separator(factor=sepFactor)
            row.label(text=infosStr)

        col.separator(factor=sepHeight)
        row = col.row()
        filePath = props.getCurrentShot().getOutputMediaPath("SH_VIDEO", provideName=False)
        row.separator(factor=sepFactor)
        row.label(text="Rendered in: " + filePath)
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath
        col.separator()

    # PLAYBLAST ###
    elif props.displayPlayblastProps:
        # if props.renderSettingsPlayblast.bypass_rendering_project_settings:
        # finalRes = props.getRenderResolutionForFinalOutput(
        #     resPercentage=props.renderSettingsPlayblast.resolutionPercentage,
        #     useStampInfo=props.renderSettingsPlayblast.useStampInfo,
        # )
        # finalRes = props.convertToSupportedRenderResolution(finalRes)

        infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
        infosStr += f"{fps} fps"
        row.label(text=infosStr)

        # prefs = config.getAddonPrefs()
        #   filePath = props.renderRootPath + "\\" + prefs.playblastFileName
        # filePath = props.renderRootPath
        # if not filePath.endswith("\\") and not filePath.endswith("/"):
        #     filePath += "\\"
        # filePath += f"_playblast_.{props.getOutputFileFormat()}"
        # if not props.isRenderRootPathValid():
        #     rowAlert = layout.row()
        #     rowAlert.alert = True
        #     rowAlert.label(text="*** Invalid Root Path ***")

        take = props.getCurrentTake()
        filePath = props.getOutputMediaPath("TK_PLAYBLAST", take, rootPath=props.renderRootPath)

        # # TODO wkip
        # if 100 != scene.render.resolution_percentage:
        #     row = col.row()
        #     row.alert = True
        #     row.label(text="*** Warning: Resolution Percentage is not 100% ***")
        #     infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
        #     row = col.row()
        #     row.alert = True
        #     row.separator(factor=sepFactor)
        #     row.label(text=infosStr)

        col.separator(factor=sepHeight)
        row = col.row()
        row.separator(factor=sepFactor)
        row.label(text="Playblast Video: " + filePath)
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = str(
            Path(bpy.path.abspath(filePath))
        )
        col.separator()


def draw3DRenderPanel(self, context):
    scene = context.scene
    props = config.getAddonProps(context.scene)
    iconExplorer = config.icons_col["General_Explorer_32"]

    stampInfoAvailable = props.isStampInfoAvailable()

    def _separatorRow(layout):
        itemsRow = layout.row()
        itemsRow.scale_y = 0.8
        itemsRow.separator()

    layout = self.layout
    # row = layout.row()
    # row.separator(factor=3)
    # if not props.useProjectRenderSettings:
    #     row.alert = True
    # row.prop(props, "useProjectRenderSettings")
    # row.operator("uas_shot_manager.render_restore_project_settings")
    # row.operator("uas_shot_manager.project_settings_prefs")
    # row.separator(factor=0.1)

    if config.devDebug:
        row = layout.row()
        row.label(text="Debug Mode:")
        subrow = row.row()
        # subrow.operator("uas_shot_manager.enable_debug", text="Off").enable_debug = True
        subrow.alert = config.devDebug
        subrow.operator("uas_shot_manager.enable_debug", text="On").enable_debug = False

    row = layout.row()

    if props.use_project_settings:
        row.alert = True
        row.alignment = "CENTER"
        row.label(text="***  Project Settings used: Scene render settings will be overwritten  *** ")

    if props.isStampInfoAllowed():
        row = layout.row()
        row.separator(factor=2)
        row.prop(props, "useStampInfoDuringRendering")

    row = layout.row(align=True)
    row.separator(factor=3)
    if not props.isRenderRootPathValid():
        row.alert = True
    row.prop(props, "renderRootPath")
    row.alert = False
    row.operator("uas_shot_manager.openpathbrowser", text="", icon="FILEBROWSER", emboss=True)
    row.separator()
    row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = props.renderRootPath
    row.separator()
    layout.separator()

    ##############
    # render engine
    ##############

    row = layout.row(align=False)
    subRow = row.row(align=False)
    subRow.alignment = "LEFT"
    subRow.prop(props.renderContext, "renderHardwareMode", text="Mode")

    if config.devDebug:
        # row.alignment = "LEFT"
        # row.separator(factor=2)
        subRow = row.row(align=False)
        subRow.alignment = "RIGHT"
        subRow.label(text="Iteration (dev.):")
        subRow.prop(props.renderContext, "renderFrameIterationMode", text="")

    # row.prop(bpy.context.scene.render, "engine", text="Engine")

    # row = layout.row(align=False)
    # row.separator()
    # box = row.box()
    box = layout.box()

    if "OPENGL" == props.renderContext.renderHardwareMode:
        grid = box.grid_flow(columns=2)

        row = grid.row(align=False)
        row.alignment = "LEFT"
        # row.label(text="GPU Engine:")
        row.prop(props.renderContext, "renderEngineOpengl", text="GPU Engine")
        # row.separator()

        row = grid.row(align=False)
        row.alignment = "RIGHT"
        row.label(text="Quality:")
        row.prop(props.renderContext, "renderQualityOpengl", text="")

        overlaysRow = box.row(align=True)
        overlaysSplit = overlaysRow.split(factor=0.4)
        overlaysRowLeft = overlaysSplit.row(align=True)
        overlaysRowLeft.prop(props.renderContext, "useOverlays", text="With Overlays")

        if props.renderContext.useOverlays:
            overlaysRowRight = overlaysSplit.row(align=True)
            overlaysRowRight.alert = True
            overlaysRowRight.alignment = "RIGHT"
            overlaysRowRight.label(text="Will use the settings of THIS viewport")

    else:
        grid = box.grid_flow(columns=2)

        row = grid.row(align=False)
        row.alignment = "RIGHT"
        # row.label(text="CPU Engine:")
        row.prop(props.renderContext, "renderEngine", text="CPU Engine")

        row = grid.row(align=False)
        row.alignment = "RIGHT"
        row.label(text="Quality:")
        row.prop(props.renderContext, "renderQuality", text="")

    layout.separator()

    row = layout.row(align=True)
    row.scale_y = 1.3
    # row.operator ( renderProps.UAS_PT_ShotManager_RenderDialog.bl_idname, text = "Render Active", icon = "RENDER_ANIMATION" ).only_active = True

    # row.use_property_split = True
    # row           = layout.row(align=True)
    # split = row.split ( align = True )
    row.scale_x = 1.2
    row.prop(props, "displayStillProps", text="", icon="IMAGE_DATA")
    row.operator("uas_shot_manager.render", text="Render Image").renderMode = "STILL"

    row.separator(factor=2)
    row.scale_x = 1.2
    row.prop(props, "displayAnimationProps", text="", icon="RENDER_ANIMATION")
    row.operator("uas_shot_manager.render", text="Render Current Shot").renderMode = "ANIMATION"

    row.separator(factor=2)
    row.scale_x = 1.2
    row.prop(props, "displayAllEditsProps", text="", icon="RENDERLAYERS")
    row.operator("uas_shot_manager.render", text="Render All").renderMode = "ALL"

    layout.separator(factor=0.3)
    row = layout.row(align=True)
    row.scale_y = 1.3
    row.scale_x = 1.2
    row.prop(props, "displayOtioProps", text="", icon="SEQ_STRIP_DUPLICATE")
    row.operator("uas_shot_manager.render", text="Edit File").renderMode = "OTIO"

    # row = layout.row()
    # row = layout.row(align=True)
    row.separator(factor=2)
    row.prop(props, "displayPlayblastProps", text="", icon="FILE_MOVIE")  # AUTO
    row.operator("uas_shot_manager.render", text="Playblast").renderMode = "PLAYBLAST"

    # scene warnings
    ################
    warningsList = props.getWarnings(scene)
    if len(warningsList):
        drawWarnings(context, layout, warningsList, panelType="RENDER")
    else:
        layout.separator(factor=0)

    # if config.devDebug:
    #     row = layout.row()
    #     row.label(text="Last Render Results:")
    #     subRow = row.row()
    #     if True:
    #         subRow.alert = True
    #         subRow.operator("uas_shot_manager.open_last_render_results", text="Errors")
    #     else:
    #         subRow.operator("uas_shot_manager.open_last_render_results", text="OK")
    #     row.operator("uas_shot_manager.clear_last_render_results")

    display_bypass_options = True
    subItemSeparator = 3

    # STILL ###
    if props.displayStillProps:
        titleRow = layout.row(align=False)
        titleLeftRow = titleRow.row()
        titleLeftRow.alignment = "RIGHT"
        titleLeftRow.label(text="Render Image:")
        # currentShot = props.getCurrentShot()
        # txt = currentShot.name if currentShot else "*** No Current Shot ***"
        txt = f"Frame {scene.frame_current}"
        titleRow.label(text=txt)

        box = layout.box()

        if props.use_project_settings:
            box.prop(props.renderSettingsStill, "bypass_rendering_project_settings")
            if props.renderSettingsStill.bypass_rendering_project_settings:
                subRow = box.row()
                subSubRow = subRow.row()
                subSubRow.separator(factor=2)
                subbox = subRow.box()
                bypassItemsCol = subbox.column()
            else:
                display_bypass_options = False
        else:
            bypassItemsCol = box.column_flow(columns=1)

        if display_bypass_options:
            itemsRow = bypassItemsCol.row()
            col = itemsRow.column()
            row = col.row()
            row.prop(props.renderSettingsStill, "writeToDisk", text="Write Image to Disk")

            _separatorRow(bypassItemsCol)

            itemsRow = bypassItemsCol.row()
            col = itemsRow.column()
            col.enabled = stampInfoAvailable
            row = col.row()
            row.prop(props.renderSettingsStill, "useStampInfo")
            if not stampInfoAvailable:
                row.label(text="*** Add-on not available ***")
            # if not props.use_project_settings:
            utils_ui.drawStampInfoBut(row)

            row = col.row()
            row.separator(factor=subItemSeparator)
            row.enabled = props.renderSettingsStill.useStampInfo
            row.prop(props.renderSettingsStill, "keepIntermediateFiles")

            col.separator(factor=0.5)

            row = col.row()
            row.label(text="Resolution %:")
            row.prop(props.renderSettingsStill, "resolutionPercentage", text="")

        drawRenderInfos(context, box)

    # ANIMATION ###
    elif props.displayAnimationProps:
        titleRow = layout.row(align=False)
        titleLeftRow = titleRow.row()
        titleLeftRow.alignment = "RIGHT"
        titleLeftRow.label(text="Render Current Shot:")
        currentShot = props.getCurrentShot()
        txt = currentShot.name if currentShot else "*** No Current Shot ***"
        titleRow.label(text=txt)

        box = layout.box()

        if props.use_project_settings:
            box.prop(props.renderSettingsAnim, "bypass_rendering_project_settings")
            if props.renderSettingsAnim.bypass_rendering_project_settings:
                subRow = box.row()
                subSubRow = subRow.row()
                subSubRow.separator(factor=2)
                subbox = subRow.box()
                bypassItemsCol = subbox.column()
            else:
                display_bypass_options = False
        else:
            bypassItemsCol = box.column_flow(columns=1)

        if display_bypass_options:
            itemsRow = bypassItemsCol.row()
            col = itemsRow.column()
            row = col.row()
            row.label(text="Output Media:")
            row.prop(props.renderSettingsAnim, "outputMediaMode", text="")

            _separatorRow(bypassItemsCol)

            itemsRow = bypassItemsCol.row()
            col = itemsRow.column()
            col.enabled = stampInfoAvailable
            row = col.row()
            row.prop(props.renderSettingsAnim, "useStampInfo")
            if not stampInfoAvailable:
                row.label(text="*** Add-on not available ***")
            # if not props.use_project_settings:
            utils_ui.drawStampInfoBut(row)

            row = col.row()
            row.separator(factor=subItemSeparator)
            row.enabled = props.renderSettingsAnim.useStampInfo
            row.prop(props.renderSettingsAnim, "keepIntermediateFiles")

            col.separator(factor=0.5)

            row = col.row()
            row.label(text="Resolution %:")
            row.prop(props.renderSettingsAnim, "resolutionPercentage", text="")

            _separatorRow(bypassItemsCol)

            itemsRow = bypassItemsCol.row()
            col = itemsRow.column()
            row = col.row()
            row.prop(props.renderSettingsAnim, "renderHandles")

        openButEnabled = not (display_bypass_options and "IMAGE_SEQ" == props.renderSettingsAnim.outputMediaMode)
        drawAfterRendering(props.renderSettingsAnim, box, openButEnabled=openButEnabled)

        drawRenderInfos(context, box)

    # ALL EDITS ###
    elif props.displayAllEditsProps:
        titleRow = layout.row(align=True)
        titleRow.separator(factor=0.5)
        titleRow.label(text="Render All:")
        box = layout.box()

        if props.use_project_settings:
            box.prop(props.renderSettingsAll, "bypass_rendering_project_settings")
            if props.renderSettingsAll.bypass_rendering_project_settings:
                subRow = box.row()
                subSubRow = subRow.row()
                subSubRow.separator(factor=2)
                subbox = subRow.box()
                bypassItemsCol = subbox.column()
            else:
                display_bypass_options = False
        else:
            bypassItemsCol = box.column_flow(columns=1)

        if display_bypass_options:
            itemsRow = bypassItemsCol.row()
            col = itemsRow.column()

            row = col.row()
            row.label(text="Output Media:")
            row.prop(props.renderSettingsAll, "outputMediaMode", text="")

            _separatorRow(bypassItemsCol)

            itemsRow = bypassItemsCol.row()
            col = itemsRow.column()
            col.enabled = stampInfoAvailable
            row = col.row()
            row.prop(props.renderSettingsAll, "useStampInfo")
            if not stampInfoAvailable:
                row.label(text="*** Add-on not available ***")
            # if not props.use_project_settings:
            utils_ui.drawStampInfoBut(row)

            row = col.row()
            row.separator(factor=subItemSeparator)
            row.enabled = props.renderSettingsAll.useStampInfo
            row.prop(props.renderSettingsAll, "keepIntermediateFiles")

            col.separator(factor=0.5)

            row = col.row()
            row.label(text="Resolution %:")
            row.prop(props.renderSettingsAll, "resolutionPercentage", text="")

            _separatorRow(bypassItemsCol)

            itemsRow = bypassItemsCol.row()
            col = itemsRow.column()

            row = col.row()
            row.enabled = "VIDEO" in props.renderSettingsAll.outputMediaMode
            split = row.split(factor=0.5)
            split.prop(props.renderSettingsAll, "renderOtioFile")
            subSplit = split.split(factor=0.3)
            subSplit.enabled = props.renderSettingsAll.renderOtioFile
            subSplit.label(text="Type:")
            subSplit.prop(props.renderSettingsAll, "otioFileType", text="")

        col = box.column()
        row = col.row()
        row.prop(props.renderSettingsAll, "rerenderExistingShotVideos")
        row.prop(props.renderSettingsAll, "generateEditVideo")

        row = col.row()
        row.prop(props.renderSettingsAll, "renderAllTakes")
        row.prop(props.renderSettingsAll, "renderAlsoDisabled")

        openButEnabled = not (display_bypass_options and "IMAGE_SEQ" == props.renderSettingsAll.outputMediaMode)
        openButEnabled = openButEnabled and not props.renderSettingsAll.renderAllTakes
        drawAfterRendering(props.renderSettingsAll, box, openButEnabled=openButEnabled)

        drawRenderInfos(context, box)

    # EDIT FILE ###
    elif props.displayOtioProps:
        titleRow = layout.row(align=True)
        titleRow.separator(factor=0.5)
        titleRow.label(text="Generate Edit File:")

        box = layout.box()

        row = box.row()
        row.label(text="Generate for:")
        if config.devDebug:
            row.prop(props.renderSettingsOtio, "outputMediaMode", text="")
        else:
            row.label(text="Videos (Only Supported Format)")

        row = box.row()
        row.label(text="File Type:")
        row.prop(props.renderSettingsOtio, "otioFileType", text="")

        row = box.row()

        take = props.getCurrentTake()
        filePath = (
            props.getOutputMediaPath("TK_EDIT_VIDEO", take, rootPath=props.renderRootPath, provideExtension=False)
            + f".{props.renderSettingsOtio.otioFileType.lower()}"
        )

        row.label(text="Current Take Edit: " + filePath)
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath

    # PLAYBLAST ###
    elif props.displayPlayblastProps:
        titleRow = layout.row(align=True)
        titleRow.separator(factor=0.5)
        titleRow.label(text="Playblast:")

        # video tracks available?
        versionStr = utils.addonVersion("Video Tracks")
        # if props.isStampInfoAvailable() and versionStr is not None:
        subRow = row.row()
        subRow.enabled = versionStr is not None
        subRow.operator(
            "uas_shot_manager.go_to_video_tracks", text="", icon="SEQ_STRIP_DUPLICATE"
        ).vseSceneName = "SM_CheckSequence"
        subRow.separator(factor=0.2)

        box = layout.box()

        bypassItemsCol = box.column_flow(columns=1)

        itemsRow = bypassItemsCol.row()
        col = itemsRow.column()

        row = col.row()
        split = row.split(factor=0.45)
        split.prop(props.renderSettingsPlayblast, "stampRenderInfo")
        if props.renderSettingsPlayblast.stampRenderInfo and (
            not stampInfoAvailable or not props.renderSettingsPlayblast.useStampInfo
        ):
            # row.alert = True
            splitRow = split.row()
            splitRow.alignment = "RIGHT"
            splitRow.label(text="(Scene Metadata will be used)")
        stampInfoRow = col.row()
        stampInfoRow.separator(factor=subItemSeparator)
        stampInfoRow.enabled = stampInfoAvailable and props.renderSettingsPlayblast.stampRenderInfo
        stampInfoRow.prop(props.renderSettingsPlayblast, "useStampInfo")
        if not stampInfoAvailable:
            stampInfoRow.label(text="*** Add-on not available ***")
        # if not props.use_project_settings:
        utils_ui.drawStampInfoBut(stampInfoRow)

        _separatorRow(bypassItemsCol)

        # col.separator(factor=0.5)

        row = box.row()
        row.label(text="Resolution %:")
        row.prop(props.renderSettingsPlayblast, "resolutionPercentage", text="")

        row = box.row()
        colFlow = row.column_flow(columns=2)
        col = colFlow.row()
        col.prop(props.renderSettingsPlayblast, "renderSound")
        col = colFlow.row()
        col.prop(props.renderSettingsPlayblast, "disableCameraBG")

        drawAfterRendering(props.renderSettingsPlayblast, box)

        drawRenderInfos(context, box)

    # ------------------------

    # renderWarnings = ""
    # if "" == bpy.data.filepath:
    #     renderWarnings = "*** Save file first ***"
    # elif "" == props.getRenderFileName():
    #     renderWarnings = "*** Invalid Output File Name ***"

    # if "" != renderWarnings or config.devDebug:
    #     box = self.layout.box()
    #     # box.use_property_split = True

    #     row = box.row()
    #     row.label(text=renderWarnings)

    #     row = box.row()
    #     row.prop(context.scene.render, "filepath")
    #     row.operator(
    #         "uas_shot_manager.open_explorer", text="", icon="FILEBROWSER"
    #     ).path = props.getRenderFileName()

    # wkip retrait temporaire
    # box = self.layout.box()
    # row = box.row()
    # # enabled=False
    # row.prop(props, "render_sequence_prefix")

    # row.separator()
    # row.operator("uas_shot_manager.open_explorer", emboss=True, icon='FILEBROWSER', text="")

    # ------------------------

    # if config.devDebug:
    #     debugCol = layout.column()
    #     debugCol.alert = True
    #     debugCol.label(text="Debug Infos:")

    #     currentRenderResStr = f"SM Render Res: {props.getRenderResolution()}"
    #     debugCol.label(text="  " + currentRenderResStr)

    self.layout.separator(factor=0.2)


def drawAfterRendering(renderPreset, layout, openButEnabled=True):
    col = layout.column()
    # col.scale_y = 0.8
    row = col.row()
    row.label(text="After Rendering:")
    row = col.row()
    row.separator(factor=2)
    subRow = row.row()
    subRow.enabled = openButEnabled
    subRow.prop(renderPreset, "openRenderedVideoInPlayer")
    subRow = row.row()
    subRow.enabled = False
    subRow.prop(renderPreset, "updatePlayblastInVSM", text="Open in Video Tracks")


_classes = (UAS_PT_ShotManagerRenderPanel, UAS_PT_ShotManagerRenderPanelStdalone)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
