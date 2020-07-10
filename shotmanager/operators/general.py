import os

import bpy
from bpy.types import Operator


class UAS_ShotManager_GoToVideoShotManager(Operator):
    bl_idname = "uas_shot_manager.go_to_video_shot_manager"
    bl_label = "Go To Video Shot Manager"
    bl_description = "Go to Video Shot Manager"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):

        vsm_sceneName = "VideoShotManger"
        vsm_scene = None

        if vsm_sceneName in bpy.data.scenes:
            vsm_scene = bpy.data.scenes[vsm_sceneName]
        else:
            vsm_scene = bpy.data.scenes.new(name=vsm_sceneName)
            vsm_scene.render.fps = context.scene.render.fps

            if not vsm_scene.sequence_editor:
                vsm_scene.sequence_editor_create()

        startup_blend = os.path.join(
            bpy.utils.resource_path("LOCAL"),
            "scripts",
            "startup",
            "bl_app_templates_system",
            "Video_Editing",
            "startup.blend",
        )

        bpy.context.window.scene = vsm_scene
        if "Video Editing" not in bpy.data.workspaces:
            bpy.ops.workspace.append_activate(idname="Video Editing", filepath=startup_blend)
        bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]

        return {"FINISHED"}


_classes = (UAS_ShotManager_GoToVideoShotManager,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
