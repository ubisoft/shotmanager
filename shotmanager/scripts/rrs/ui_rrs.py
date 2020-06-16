import bpy

from bpy.types import Panel


class UAS_PT_ShotManager_RRS_Debug(Panel):
    bl_label = "ShotManager_RRS_Debug"
    bl_idname = "UAS_PT_Shot_Manager_rrs_debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=False)
        row.alert = True
        row.label(text="RRS Specific (debug temp):")
        row.operator("uas_shot_manager.initialize_rrs_project", text="Debug - RRS Initialyze")
        row.operator("uas_shot_manager.lauch_rrs_render", text="Debug - RRS Publish").prodFilePath = (
            "c:\\tmpRezo\\" + context.scene.name + "\\"
        )
        row.alert = False
        layout.separator(factor=1)
