import bpy
from bpy.types import Operator
from bpy.props import StringProperty, FloatProperty

from shotmanager.config import config
from shotmanager.utils import utils


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


####################
# Markers
####################


class UAS_VideoShotManager_GoToMarker(Operator):
    bl_idname = "uas_video_shot_manager.go_to_marker"
    bl_label = "Go To Marker"
    bl_description = "Go to the specified marker"
    bl_options = {"INTERNAL"}

    goToMode: StringProperty(
        name="Go To Mode", description="Go to the specified marker. Can be FIRST, PREVIOUS, NEXT, LAST", default="NEXT"
    )

    def invoke(self, context, event):
        scene = context.scene
        marker = None
        if len(scene.timeline_markers):
            print(self.goToMode)
            if "FIRST" == self.goToMode:
                marker = utils.getFirstMarker(scene, scene.frame_current)
            elif "PREVIOUS" == self.goToMode:
                marker = utils.getMarkerBeforeFrame(scene, scene.frame_current)
            elif "NEXT" == self.goToMode:
                marker = utils.getMarkerAfterFrame(scene, scene.frame_current)
            elif "LAST" == self.goToMode:
                marker = utils.getLastMarker(scene, scene.frame_current)

            if marker is not None:
                scene.frame_set(marker.frame)

        return {"FINISHED"}


class UAS_VideoShotManager_AddMarker(Operator):
    bl_idname = "uas_video_shot_manager.add_marker"
    bl_label = "Add / Rename Marker"
    bl_description = "Add or rename a marker at the specified frame"
    bl_options = {"INTERNAL", "UNDO"}

    markerName: StringProperty(name="New Marker Name", default="")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        utils.addMarkerAtFrame(context.scene, context.scene.frame_current, self.markerName)
        return {"FINISHED"}


class UAS_VideoShotManager_DeleteMarker(Operator):
    bl_idname = "uas_video_shot_manager.delete_marker"
    bl_label = "Delete Marker"
    bl_description = "Delete the marker at the specified frame"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        utils.deleteMarkerAtFrame(context.scene, context.scene.frame_current)
        return {"FINISHED"}


####################
# Time range framing
####################


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
    UAS_VideoShotManager_GoToMarker,
    UAS_VideoShotManager_AddMarker,
    UAS_VideoShotManager_DeleteMarker,
    UAS_VideoShotManager_FrameAllClips,
    UAS_VideoShotManager_FrameTimeRange,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
