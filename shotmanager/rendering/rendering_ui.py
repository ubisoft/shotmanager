from pathlib import Path

import bpy
from bpy.types import Panel

from ..config import config


class UAS_PT_ShotManagerRenderPanel(Panel):
    bl_label = "Rendering"
    bl_idname = "UAS_PT_ShotManagerRenderPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        val = not props.dontRefreshUI() and len(props.takes) and len(props.get_shots())
        return val

    # def check(self, context):
    #     # should we redraw when a button is pressed?
    #     if True:
    #         return True
    #     return False

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props
        iconExplorer = config.icons_col["General_Explorer_32"]

        layout = self.layout
        row = layout.row()
        # row.separator(factor=3)
        # if not props.useProjectRenderSettings:
        #     row.alert = True
        # row.prop(props, "useProjectRenderSettings")
        # row.operator("uas_shot_manager.render_restore_project_settings")
        # row.operator("uas_shot_manager.project_settings_prefs")
        # row.separator(factor=0.1)

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
        row.operator(
            "uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id
        ).path = props.renderRootPath
        row.separator()
        layout.separator()

        ##############
        # render engine
        ##############
        row = layout.row(align=False)
        # row.label(text="Mode:")
        row.prop(props.renderContext, "renderComputationMode", text="Mode")
        row.separator()
        row.prop(props.renderContext, "renderQuality", text="Quality")

        # row.prop(bpy.context.scene.render, "engine", text="Engine")

        box = layout.box()
        row = box.row(align=False)
        renderWithOpengl = (
            "PLAYBLAST_LOOP" == props.renderContext.renderComputationMode
            or "PLAYBLAST_ANIM" == props.renderContext.renderComputationMode
        )
        if renderWithOpengl:
            row.label(text="Playblast Engine")
            row.prop(props.renderContext, "renderEngineOpengl", text="")
            row.separator(factor=1)
            row.prop(props.renderContext, "useOverlays", text="With Overlays")
        else:
            row.label(text="Render Engine")
            row.prop(props.renderContext, "renderEngine", text="")

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
        row.operator("uas_shot_manager.render", text="Render EDL File").renderMode = "OTIO"

        # row = layout.row()
        # row = layout.row(align=True)
        row.separator(factor=2)
        # row.scale_x = 1.2
        row.prop(props, "displayPlayblastProps", text="", icon="FILE_MOVIE")  # AUTO
        row.operator("uas_shot_manager.render", text="Playblast").renderMode = "PLAYBLAST"

        layout.separator(factor=1)

        # if config.uasDebug:
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

            row = box.row()
            filePath = props.getCurrentShot().getOutputMediaPath(specificFrame=bpy.context.scene.frame_current)
            row.label(text="Current Image: " + filePath)
            row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath

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

            row = box.row()
            filePath = props.getCurrentShot().getOutputMediaPath()
            row.label(text="Current Video: " + filePath)
            row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath

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

            row = box.row()
            # filePath = props.getTakeOutputFilePath()
            filePath = props.getCurrentShot().getOutputMediaPath(provideName=False, provideExtension=False)
            row.label(text="Rendering Folder: " + filePath)
            row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath

        # EDL ###
        elif props.displayOtioProps:
            row = layout.row()
            row.label(text="Render EDL File:")

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
            filePath += take_name + "\\"
            # if "" == fileName:
            filePath += take_name + ".xml"
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

            box = layout.box()

            prefs = context.preferences.addons["shotmanager"].preferences
            #   filePath = props.renderRootPath + "\\" + prefs.playblastFileName
            filePath = props.renderRootPath
            if not filePath.endswith("\\") and not filePath.endswith("/"):
                filePath += "\\"
            filePath += f"_playblast_.{props.getOutputFileFormat()}"
            if not props.isRenderRootPathValid():
                rowAlert = box.row()
                rowAlert.alert = True
                rowAlert.label(text="*** Invalid Root Path ***")

            row = box.row()
            colFlow = row.column_flow(columns=2)
            col = colFlow.row()
            col.prop(props.renderSettingsPlayblast, "useStampInfo")
            col = colFlow.row()
            col.label(text="Resolution %")
            col.prop(props.renderSettingsPlayblast, "resolutionPercentage", text="")
            # row.use_property_split = False

            row = box.row()
            row.label(text="Playblast Video: " + filePath)
            row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = str(
                Path(bpy.path.abspath(filePath))
            )

        # ------------------------

        # renderWarnings = ""
        # if "" == bpy.data.filepath:
        #     renderWarnings = "*** Save file first ***"
        # elif "" == props.getRenderFileName():
        #     renderWarnings = "*** Invalid Output File Name ***"

        # if "" != renderWarnings or config.uasDebug:
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

        self.layout.separator(factor=1)


_classes = (UAS_PT_ShotManagerRenderPanel,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
