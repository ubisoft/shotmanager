import bpy
from bpy.types import Operator

from . import publishRRS


class UAS_InitializeRRSProject(Operator):
    bl_idname = "uas_shot_manager.initialize_rrs_project"
    bl_label = "Initialize scene for RRS project"
    bl_description = "Initialize scene for RRS project"

    def execute(self, context):
        print(" UAS_InitializeRRSProject")

        publishRRS.initializeForRRS()

        return {"FINISHED"}


class UAS_LaunchRRSRender(Operator):
    bl_idname = "uas_shot_manager.lauch_rrs_render"
    bl_label = "RRS Render Script"
    bl_description = "Run the RRS Render Script"

    def execute(self, context):
        """Launch RRS Publish script"""
        print(" UAS_LaunchRRSRender")

        # publishRRS.publishRRS( context.scene.UAS_shot_manager_props.renderRootPath )
        takeInd = 0
        publishRRS.publishRRS("c:\\tmpRezo\\" + context.scene.name + "\\", verbose=True, takeIndex=takeInd)
        print("End of Publish")
        return {"FINISHED"}
