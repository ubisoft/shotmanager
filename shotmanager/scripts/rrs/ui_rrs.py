from ...config import config

from bpy.types import Panel


class UAS_PT_ShotManager_RRS_Debug(Panel):
    bl_label = "ShotManager_RRS_Debug"
    bl_idname = "UAS_PT_Shot_Manager_rrs_debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        return not props.dontRefreshUI()

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props

        layout = self.layout
        row = layout.row(align=False)
        row.label(text="RRS Specific (debug temp):")
        row.prop(props, "rrs_useRenderRoot")
        row = layout.row(align=False)
        row.alert = True
        row.operator("uas_shot_manager.initialize_rrs_project", text="Debug - RRS Initialyze")
        row.operator("uas_shot_manager.lauch_rrs_render", text="Debug - RRS Publish").prodFilePath = (
            "c:\\tmpRezo\\" + context.scene.name + "\\"
        )
        row.alert = False

        # if config.uasDebug:
        #     row = layout.row(align=False)
        #     # row.enabled = False
        #     row.prop(context.window_manager, "UAS_shot_manager_progressbar", text="Rendering...")

        layout.separator(factor=1)

