import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty, IntProperty

from . import publish_rrs


# To call the operator:
# bpy.ops.uas_shot_manager.initialize_rrs_project(override_existing = True, verbose = True)
class UAS_InitializeRRSProject(Operator):
    bl_idname = "uas_shot_manager.initialize_rrs_project"
    bl_label = "Initialize scene for RRS project"
    bl_description = "Initialize scene for RRS project"

    override_existing: BoolProperty(default=False)
    verbose: BoolProperty(default=False)

    def execute(self, context):
        print(" UAS_InitializeRRSProject")

        publish_rrs.initializeForRRS(self.override_existing, verbose=self.verbose)

        return {"FINISHED"}


# To call the operator:
# bpy.ops.uas_shot_manager.lauch_rrs_render(prodFilePath = "c:\\tmpRezo\\" + context.scene.name + "\\",
# verbose = True, takeIndex = -1)
# use takeIndex = -1 to render the current take
class UAS_LaunchRRSRender(Operator):
    bl_idname = "uas_shot_manager.lauch_rrs_render"
    bl_label = "RRS Render Script"
    bl_description = "Run the RRS Render Script used for the scene publish"

    prodFilePath: StringProperty(default="")
    takeIndex: IntProperty(default=-1)
    verbose: BoolProperty(default=False)
    useCache: BoolProperty(default=False)

    def execute(self, context):
        """Launch RRS Publish script"""
        print(" UAS_LaunchRRSRender")

        props = context.scene.UAS_shot_manager_props

        if not props.sceneIsReady():
            return {"CANCELLED"}

        if props.rrs_useRenderRoot:  # used in SM UI in the debug panel
            print("Publish at render root")
            publish_rrs.publishRRS(
                bpy.path.abspath(props.renderRootPath),
                verbose=True,
                takeIndex=self.takeIndex,
                useCache=False,
                fileListOnly=props.rrs_fileListOnly,
            )
        else:
            publish_rrs.publishRRS(
                self.prodFilePath,
                verbose=self.verbose,
                takeIndex=self.takeIndex,
                useCache=self.useCache,
                fileListOnly=props.rrs_fileListOnly,
            )

        print("End of Publish")

        return {"FINISHED"}
