import bpy
from bpy.types import Operator
from bpy.props import StringProperty, FloatProperty

from shotmanager.config import config


class UAS_VideoShotManager_SelectedToActive(Operator):
    bl_idname = "uas_video_shot_manager.selected_to_active"
    bl_label = "Selected to Active"
    bl_description = "Set the first selected clip of a VSE as the active clip"
    bl_options = {"INTERNAL"}

    # @classmethod
    # def poll(cls, context):
    #     props = context.scene.UAS_shot_manager_props
    #     val = len(props.getTakes()) and len(props.get_shots())
    #     return val

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props

        return {"FINISHED"}

    # def execute(self, context):
    #     scene = context.scene
    #     props = scene.UAS_shot_manager_props
    #     return {"FINISHED"}


class UAS_VideoShotManager_FrameAllClips(Operator):
    bl_idname = "uas_video_shot_manager.frame_all_clips"
    bl_label = "Frame All Clips"
    bl_description = "Change the VSE zoom value to make all the clips fit into the view"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        # bpy.ops.sequencer.view_selected()
        # bpy.ops.sequencer.view_all_preview()

        bpy.ops.sequencer.view_all()
        # bpy.ops.time.view_all()

        # for test only
        # filedit = bpy.context.window_manager.UAS_vse_render.getMediaList(context.scene, listVideo=False, listAudio=True)
        # print(f"filedit: \n{filedit}")

        return {"FINISHED"}


class UAS_VideoShotManager_FrameTimeRange(Operator):
    bl_idname = "uas_video_shot_manager.frame_time_range"
    bl_label = "Frame Time Range"
    bl_description = "Change the VSE zoom value to fit the scene time range"
    bl_options = {"INTERNAL"}

    spacerPercent: FloatProperty(
        description="Range of time, in percentage, before and after the time range", min=0.0, max=40.0, default=5
    )

    def execute(self, context):
        scene = context.scene

        # bpy.ops.sequencer.view_selected()
        # bpy.ops.sequencer.view_all_preview()

        if scene.use_preview_range:
            beforeStart = scene.frame_preview_start
            beforeEnd = scene.frame_preview_end
            framesToAdd = int((beforeEnd - beforeStart + 1) * self.spacerPercent)
            scene.frame_preview_start = beforeStart - framesToAdd
            scene.frame_preview_end = beforeEnd + framesToAdd
            bpy.ops.sequencer.view_all()
            scene.frame_preview_start = beforeStart
            scene.frame_preview_end = beforeEnd

        else:
            beforeStart = scene.frame_start
            beforeEnd = scene.frame_end
            framesToAdd = int((beforeEnd - beforeStart + 1) * self.spacerPercent)
            scene.frame_start = beforeStart - framesToAdd
            scene.frame_end = beforeEnd + framesToAdd
            bpy.ops.sequencer.view_all()
            scene.frame_start = beforeStart
            scene.frame_end = beforeEnd

        # bpy.ops.time.view_all()
        return {"FINISHED"}


_classes = (
    UAS_VideoShotManager_SelectedToActive,
    UAS_VideoShotManager_FrameAllClips,
    UAS_VideoShotManager_FrameTimeRange,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
