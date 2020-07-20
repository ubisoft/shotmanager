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
        row.operator("uas_shot_manager.render_openexplorer", text="", icon="FILEBROWSER").path = props.renderRootPath
        row.separator()
        layout.separator()

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
        row.prop(props, "displayProjectProps", text="", icon="RENDERLAYERS")
        row.operator("uas_shot_manager.render", text="Render All").renderMode = "PROJECT"

        row = layout.row()
        row = layout.row(align=True)
        row.prop(props, "displayOtioProps", text="", icon="SEQ_STRIP_DUPLICATE")
        row.operator("uas_shot_manager.export_otio")

        layout.separator(factor=1)

        # STILL ###
        if props.displayStillProps:
            row = layout.row()
            row.label(text="Render Image:")

            box = layout.box()
            row = box.row()
            row.prop(props.renderSettingsStill, "writeToDisk")

            row = box.row()
            filePath = props.getCurrentShot().getOutputFileName(
                frameIndex=bpy.context.scene.frame_current, fullPath=True
            )
            row.label(text="Current Image: " + filePath)
            row.operator("uas_shot_manager.render_openexplorer", text="", icon="FILEBROWSER").path = filePath

        # ANIMATION ###
        elif props.displayAnimationProps:
            row = layout.row()
            row.label(text="Render Current Shot:")

            box = layout.box()
            row = box.row()
            row.prop(props.renderSettingsAnim, "renderWithHandles")

            row = box.row()
            filePath = props.getCurrentShot().getOutputFileName(fullPath=True)
            row.label(text="Current Video: " + filePath)
            row.operator("uas_shot_manager.render_openexplorer", text="", icon="FILEBROWSER").path = filePath

        # PROJECT ###
        elif props.displayProjectProps:
            row = layout.row()
            row.label(text="Render All:")

            box = layout.box()
            row = box.row()
            row.prop(props.renderSettingsProject, "renderAllTakes")
            row.prop(props.renderSettingsProject, "renderAlsoDisabled")

        layout.separator(factor=1)

        # ------------------------

        renderWarnings = ""
        if "" == bpy.data.filepath:
            renderWarnings = "*** Save file first ***"
        elif "" == props.getRenderFileName():
            renderWarnings = "*** Invalid Output File Name ***"

        if "" != renderWarnings or config.uasDebug:
            box = self.layout.box()
            # box.use_property_split = True

            row = box.row()
            row.label(text=renderWarnings)

            row = box.row()
            row.prop(context.scene.render, "filepath")
            row.operator(
                "uas_shot_manager.render_openexplorer", text="", icon="FILEBROWSER"
            ).path = props.getRenderFileName()

        # wkip retrait temporaire
        # box = self.layout.box()
        # row = box.row()
        # # enabled=False
        # row.prop(props, "render_shot_prefix")

        # row.separator()
        # row.operator("uas_shot_manager.render_openexplorer", emboss=True, icon='FILEBROWSER', text="")

        self.layout.separator(factor=1)


_classes = (UAS_PT_ShotManagerRenderPanel,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
