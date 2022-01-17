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
To do: module description here.
"""

from pathlib import Path

import bpy
from bpy.types import Panel

from ..config import config
from ..utils import utils

from shotmanager.ui.warnings_ui import drawWarnings


class UAS_PT_ShotManagerRenderPanelStdalone(Panel):
    bl_label = "Shot Manager - Render"
    bl_idname = "UAS_PT_ShotManagerRenderPanelStdalone"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng - Render"

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences
        displayPanel = context.preferences.addons["shotmanager"].preferences.separatedRenderPanel

        displayPanel = displayPanel and props.getCurrentShot() is not None

        return displayPanel and prefs.display_render_in_properties

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


class UAS_PT_ShotManagerRenderPanel(Panel):
    bl_label = "Rendering"
    bl_idname = "UAS_PT_ShotManagerRenderPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences
        displayPanel = context.preferences.addons["shotmanager"].preferences.separatedRenderPanel
        val = not props.dontRefreshUI() and len(props.takes) and len(props.get_shots())
        val = val and not context.preferences.addons["shotmanager"].preferences.separatedRenderPanel
        return val and prefs.display_render_in_properties

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
    # row.menu("UAS_MT_Shot_Manager_prefs_mainmenu", icon="PREFERENCES", text="")
    row.operator("uas_shot_manager.render_prefs", icon="PREFERENCES", text="")
    row.separator(factor=1.0)


def drawRenderInfos(context, layout):
    scene = context.scene
    props = context.scene.UAS_shot_manager_props
    iconExplorer = config.icons_col["General_Explorer_32"]

    # layout.separator(factor=-2.5)
    col = layout.column()
    col.scale_y = 0.8

    row = col.row()
    row.alignment = "CENTER"
    row.label(text="_____________________")

    sepFactor = 1
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
        fps = scene.render.fps

    row = col.row()
    row.separator(factor=sepFactor)

    #     infosStr = f"Image Res: {props.project_resolution_x} x {props.project_resolution_y}, "
    #     infosStr += f"Final Res: {props.project_resolution_framed_x} x {props.project_resolution_framed_y}, "
    #     infosStr += f"{props.project_fps} fps"
    # else:
    #     infosStr = f"Image Res: {scene.render.resolution_x} x {scene.render.resolution_y}, "
    #     infosStr += f"Final Res: {props.project_resolution_framed_x} x {props.project_resolution_framed_y}, "
    #     infosStr = f"{scene.render.fps} fps"

    imgRes = props.getRenderResolution()
    finalRes = props.getRenderResolutionForFinalOutput(resPercentage=100)

    def _getResText(imgRes_x, imgRes_y, finalRes_x, finalRes_y):
        infosStr = f"Image Res: {imgRes_x} x {imgRes_x},  "
        infosStr += f"Final Res: {finalRes_x} x {finalRes_y},  "
        return infosStr

    ### still
    if props.displayStillProps:
        if props.renderSettingsStill.bypass_rendering_project_settings:
            finalRes = props.getRenderResolutionForFinalOutput(
                resPercentage=100, useStampInfo=props.renderSettingsStill.useStampInfo
            )

        infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
        infosStr += f"{fps} fps"
        row.label(text=infosStr)

        if 100 != scene.render.resolution_percentage:
            row = col.row()
            row.alert = True
            row.label(text="*** Warning: Resolution Percentage is not 100% ***")
            infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
            row = col.row()
            row.alert = True
            row.separator(factor=sepFactor)
            row.label(text=infosStr)

        col.separator()
        row = col.row()
        filePath = props.getCurrentShot().getOutputMediaPath(specificFrame=bpy.context.scene.frame_current)
        row.separator(factor=sepFactor)
        row.label(text="Current Image: " + filePath)
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath
        col.separator()

    ### animation
    if props.displayAnimationProps:
        if props.renderSettingsAnim.bypass_rendering_project_settings:
            finalRes = props.getRenderResolutionForFinalOutput(
                resPercentage=100, useStampInfo=props.renderSettingsAnim.useStampInfo
            )

        infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
        infosStr += f"{fps} fps"
        row.label(text=infosStr)

        col.separator()
        row = col.row()
        filePath = props.getCurrentShot().getOutputMediaPath()
        row.separator(factor=sepFactor)
        row.label(text="Current Video: " + filePath)
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath
        col.separator()

    ### all edits
    elif props.displayAllEditsProps:
        if props.renderSettingsAll.bypass_rendering_project_settings:
            finalRes = props.getRenderResolutionForFinalOutput(
                resPercentage=100, useStampInfo=props.renderSettingsAll.useStampInfo
            )

        infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
        infosStr += f"{fps} fps"
        row.label(text=infosStr)

        col.separator()
        row = col.row()
        # filePath = props.getTakeOutputFilePath()
        filePath = props.getCurrentShot().getOutputMediaPath(provideName=False, provideExtension=False)
        row.separator(factor=sepFactor)
        row.label(text="Rendering Folder: " + filePath)
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath
        col.separator()

    ### playblast
    elif props.displayPlayblastProps:
        # if props.renderSettingsPlayblast.bypass_rendering_project_settings:
        finalRes = props.getRenderResolutionForFinalOutput(
            resPercentage=props.renderSettingsPlayblast.resolutionPercentage,
            useStampInfo=props.renderSettingsPlayblast.useStampInfo,
        )

        infosStr = _getResText(imgRes[0], imgRes[1], finalRes[0], finalRes[1])
        infosStr += f"{fps} fps"
        row.label(text=infosStr)

        # prefs = context.preferences.addons["shotmanager"].preferences
        #   filePath = props.renderRootPath + "\\" + prefs.playblastFileName
        filePath = props.renderRootPath
        if not filePath.endswith("\\") and not filePath.endswith("/"):
            filePath += "\\"
        filePath += f"_playblast_.{props.getOutputFileFormat()}"
        if not props.isRenderRootPathValid():
            rowAlert = box.row()
            rowAlert.alert = True
            rowAlert.label(text="*** Invalid Root Path ***")

        col.separator()
        row = col.row()
        row.separator(factor=sepFactor)
        row.label(text="Playblast Video: " + filePath)
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = str(
            Path(bpy.path.abspath(filePath))
        )
        col.separator()


def draw3DRenderPanel(self, context):
    scene = context.scene
    props = context.scene.UAS_shot_manager_props
    iconExplorer = config.icons_col["General_Explorer_32"]

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

    # scene warnings
    ################
    warningsList = props.getWarnings(scene)
    drawWarnings(context, layout, warningsList, panelType="RENDERING")

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

        row = box.row(align=False)
        row.prop(props.renderContext, "useOverlays", text="With Overlays")
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
    row.prop(props, "displayOtioProps", text="", icon="SEQ_STRIP_DUPLICATE")
    row.operator("uas_shot_manager.render", text="Render Edit File").renderMode = "OTIO"

    # row = layout.row()
    # row = layout.row(align=True)
    row.separator(factor=2)
    # row.scale_x = 1.2
    row.prop(props, "displayPlayblastProps", text="", icon="FILE_MOVIE")  # AUTO
    row.operator("uas_shot_manager.render", text="Playblast").renderMode = "PLAYBLAST"

    layout.separator(factor=1)

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

    # STILL ###
    if props.displayStillProps:
        row = layout.row()
        row.label(text="Render Image:")
        box = layout.box()

        if props.use_project_settings:
            box.prop(props.renderSettingsStill, "bypass_rendering_project_settings")
            if props.renderSettingsStill.bypass_rendering_project_settings:
                subRow = box.row()
                subSubRow = subRow.row()
                subSubRow.separator(factor=2)
                subbox = subRow.box()
                row = subbox.row()
            else:
                display_bypass_options = False
        else:
            row = box.row()

        if display_bypass_options:
            row.prop(props.renderSettingsStill, "writeToDisk")
            row.prop(props.renderSettingsStill, "useStampInfo")

        drawRenderInfos(context, box)

    # ANIMATION ###
    elif props.displayAnimationProps:
        row = layout.row()
        row.label(text="Render Current Shot:")
        box = layout.box()

        if props.use_project_settings:
            box.prop(props.renderSettingsAnim, "bypass_rendering_project_settings")
            if props.renderSettingsAnim.bypass_rendering_project_settings:
                subRow = box.row()
                subSubRow = subRow.row()
                subSubRow.separator(factor=2)
                subbox = subRow.box()
                row = subbox.row()
            else:
                display_bypass_options = False
        else:
            row = box.row()

        if display_bypass_options:
            row.prop(props.renderSettingsAnim, "renderHandles")
            row.prop(props.renderSettingsAnim, "useStampInfo")

        drawRenderInfos(context, box)

    # ALL EDITS ###
    elif props.displayAllEditsProps:
        row = layout.row()
        row.label(text="Render All:")
        box = layout.box()

        row = box.row()
        row.prop(props.renderSettingsAll, "rerenderExistingShotVideos")
        row = box.row()
        row.prop(props.renderSettingsAll, "generateEditVideo")

        if props.use_project_settings:
            box.prop(props.renderSettingsAll, "bypass_rendering_project_settings")
            if props.renderSettingsAll.bypass_rendering_project_settings:
                subRow = box.row()
                subSubRow = subRow.row()
                subSubRow.separator(factor=2)
                subbox = subRow.box()
                row = subbox.row()
            else:
                display_bypass_options = False
        else:
            row = box.row()

        if display_bypass_options:
            row.prop(props.renderSettingsAll, "renderAlsoDisabled")
            row.prop(props.renderSettingsAll, "useStampInfo")
            if props.use_project_settings:
                row = subbox.row()
            else:
                row = box.row()
            row.prop(props.renderSettingsAll, "renderAllTakes")
            row.prop(props.renderSettingsAll, "renderOtioFile")

        drawRenderInfos(context, box)

    # Edit file ###
    elif props.displayOtioProps:
        row = layout.row()
        row.label(text="Render Edit File:")

        box = layout.box()
        row = box.row()

        row.prop(props.renderSettingsOtio, "otioFileType")

        row = box.row()

        take = props.getCurrentTake()
        take_name = take.getName_PathCompliant()

        filePath = props.renderRootPath
        if filePath.startswith("//"):
            filePath = bpy.path.abspath(filePath)
        if not (filePath.endswith("/") or filePath.endswith("\\")):
            filePath += "\\"

        # if addTakeNameToPath:

        # take folder
        filePath += take_name + "\\"

        # if "" == fileName:

        # edit file name
        filePath += take_name

        # file extension
        filePath += f".{props.renderSettingsOtio.otioFileType.lower()}"
        # + ".xml"
        # else:
        #     otioRenderPath += fileName
        #     if Path(fileName).suffix == "":
        #         otioRenderPath += ".otio"

        row.label(text="Current Take Edit: " + filePath)
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath

    # PLAYBLAST ###
    elif props.displayPlayblastProps:
        row = layout.row()
        row.label(text="Playblast:")

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

        # # prefs = context.preferences.addons["shotmanager"].preferences
        # #   filePath = props.renderRootPath + "\\" + prefs.playblastFileName
        # filePath = props.renderRootPath
        # if not filePath.endswith("\\") and not filePath.endswith("/"):
        #     filePath += "\\"
        # filePath += f"_playblast_.{props.getOutputFileFormat()}"
        # if not props.isRenderRootPathValid():
        #     rowAlert = box.row()
        #     rowAlert.alert = True
        #     rowAlert.label(text="*** Invalid Root Path ***")

        row = box.row()
        row.prop(props.renderSettingsPlayblast, "stampRenderInfo")
        subRow = row.row()
        subRow.enabled = props.renderSettingsPlayblast.stampRenderInfo
        subRow.prop(props.renderSettingsPlayblast, "useStampInfo")
        box.separator(factor=0.3)

        row = box.row()
        colFlow = row.column_flow(columns=3)
        col = colFlow.row()
        col.prop(props.renderSettingsPlayblast, "renderSound")
        col = colFlow.row()
        col.prop(props.renderSettingsPlayblast, "disableCameraBG")
        col = colFlow.row()
        col.label(text="Resolution %:")
        col.prop(props.renderSettingsPlayblast, "resolutionPercentage", text="")
        # row.use_property_split = False

        row = box.row()
        # # if config.devDebug:
        # row.label(text="After Rendering:")

        # row = box.row()
        # row.separator(factor=1)
        row.label(text="After Rendering:")
        row = box.row()
        row.separator(factor=2)
        subRow = row.row()
        subRow.prop(props.renderSettingsPlayblast, "openPlayblastInPlayer")
        subRow = row.row()
        subRow.enabled = False
        subRow.prop(props.renderSettingsPlayblast, "updatePlayblastInVSM", text="Open in Video Tracks")

        # row = box.row()
        # row.prop(props.renderSettingsPlayblast, "renderCameraBG")

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
    # row.prop(props, "render_shot_prefix")

    # row.separator()
    # row.operator("uas_shot_manager.open_explorer", emboss=True, icon='FILEBROWSER', text="")

    # ------------------------

    # if config.devDebug:
    #     debugCol = layout.column()
    #     debugCol.alert = True
    #     debugCol.label(text="Debug Infos:")

    #     currentRenderResStr = f"SM Render Res: {props.getRenderResolution()}"
    #     debugCol.label(text="  " + currentRenderResStr)

    self.layout.separator(factor=1)


_classes = (UAS_PT_ShotManagerRenderPanel, UAS_PT_ShotManagerRenderPanelStdalone)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
