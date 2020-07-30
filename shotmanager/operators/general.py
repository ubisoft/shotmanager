import os

import bpy
from bpy.types import Operator

from ..utils.utils import getSceneVSE


class UAS_ShotManager_GoToVideoShotManager(Operator):
    bl_idname = "uas_shot_manager.go_to_video_shot_manager"
    bl_label = "Go To Video Shot Manager"
    bl_description = "Go to Video Shot Manager"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):

        vsm_scene = None
        vsm_scene = getSceneVSE("VideoShotManger")

        # startup_blend = os.path.join(
        #     bpy.utils.resource_path("LOCAL"),
        #     "scripts",
        #     "startup",
        #     "bl_app_templates_system",
        #     "Video_Editing",
        #     "startup.blend",
        # )

        # bpy.context.window.scene = vsm_scene
        # if "Video Editing" not in bpy.data.workspaces:
        #     bpy.ops.workspace.append_activate(idname="Video Editing", filepath=startup_blend)
        bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]

        return {"FINISHED"}


_classes = (UAS_ShotManager_GoToVideoShotManager,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
