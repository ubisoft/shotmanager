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
        row = layout.row(align=True)
        row.prop(props, "renderComputationMode", text="Mode")
        row.separator()
        row.prop(bpy.context.scene.render, "engine", text="Engine")
        # row = layout.row(align=True)
        # row.prop(props, "renderComputationMode", text="Comput. Mode")

        row = layout.row(align=True)
        row.separator(factor=5)
        row.prop(props, "useOverlays", text="With Overlays")
        row.prop(props.renderContext, "renderQuality", text="Quality")

        row = layout.row(align=True)
        row.scale_y = 1.6
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

        row = layout.row()
        row = layout.row(align=True)
        row.prop(props, "displayOtioProps", text="", icon="SEQ_STRIP_DUPLICATE")
        row.operator("uas_shot_manager.render", text="Render EDL File").renderMode = "OTIO"

        layout.separator(factor=1)

        display_bypass_options = True

        # STILL ###
        if props.displayStillProps:
            row = layout.row()
            row.label(text="Render Image:")
            box = layout.box()

            if props.use_project_settings:
                box.prop(props, "bypass_rendering_project_settings")
                if props.bypass_rendering_project_settings:
                    subbox = box.box()
                    row = subbox.row()
                else:
                    display_bypass_options = False
            else:
                row = box.row()

            if display_bypass_options:
                row.prop(props.renderSettingsStill, "writeToDisk")

            row = box.row()
            filePath = props.getCurrentShot().getOutputFileName(
                frameIndex=bpy.context.scene.frame_current, fullPath=True
            )
            row.label(text="Current Image: " + filePath)
            row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath

        # ANIMATION ###
        elif props.displayAnimationProps:
            row = layout.row()
            row.label(text="Render Current Shot:")
            box = layout.box()

            if props.use_project_settings:
                box.prop(props, "bypass_rendering_project_settings")
                if props.bypass_rendering_project_settings:
                    subbox = box.box()
                    row = subbox.row()
                else:
                    display_bypass_options = False
            else:
                row = box.row()

            if display_bypass_options:
                row.prop(props.renderSettingsAnim, "renderWithHandles")

            row = box.row()
            filePath = props.getCurrentShot().getOutputFileName(fullPath=True)
            row.label(text="Current Video: " + filePath)
            row.operator("uas_shot_manager.open_explorer", text="", icon_value=iconExplorer.icon_id).path = filePath

        # ALL EDITS ###
        elif props.displayAllEditsProps:
            row = layout.row()
            row.label(text="Render All:")
            box = layout.box()

            row = box.row()
            box.prop(props.renderSettingsAll, "generateEditVideo")

            if props.use_project_settings:
                box.prop(props, "bypass_rendering_project_settings")
                if props.bypass_rendering_project_settings:
                    subbox = box.box()
                    row = subbox.row()
                else:
                    display_bypass_options = False
            else:
                row = box.row()

            if display_bypass_options:
                row.prop(props.renderSettingsAll, "renderAllTakes")
                row.prop(props.renderSettingsAll, "renderAlsoDisabled")
                row.prop(props.renderSettingsAll, "renderOtioFile")

            row = box.row()
            filePath = props.getTakeOutputFilePath()
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
