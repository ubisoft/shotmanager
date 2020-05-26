import bpy

from bpy.types import PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, FloatVectorProperty


class UAS_ShotManager_Shot(PropertyGroup):
    def getDuration(self):
        """ Returns the shot duration in frames
            in Blender - and in Shot Manager - the last frame of the shot is included in the rendered images
        """
        duration = self.end - self.start + 1
        return duration

    def getOutputFileName(self, frameIndex=-1, fullPath=False, fullPathOnly=False, rootFilePath=""):
        return bpy.context.scene.UAS_shot_manager_props.getShotOutputFileName(
            self, frameIndex=frameIndex, fullPath=fullPath, fullPathOnly=fullPathOnly, rootFilePath=rootFilePath
        )

    def getName_PathCompliant(self):
        shotName = self.name.replace(" ", "_")
        return shotName

    def _shot_name_changed(self, context):
        dup_name = False

        # wkip fix rename
        # ownerTakeInd = context.scene.UAS_shot_manager_props.getShotOwnerTake(self)  or ownertakeind?
        shots = context.scene.UAS_shot_manager_props.getShotsList(takeIndex=self.parentTakeIndex)

        for shot in shots:
            if shot != self and self.name == shot.name:
                dup_name = True

        if dup_name:
            self.name = f"{self.name}_1"

    def _start_frame_changed(self, context):
        if self.start > self.end:
            self.end = self.start

    def _end_frame_changed(self, context):
        if self.start > self.end:
            self.start = self.end

    def _enabled_changed(self, context):
        context.scene.UAS_shot_manager_props.selected_shot_index = context.scene.UAS_shot_manager_props.getShotIndex(
            self
        )

    parentTakeIndex: IntProperty(name="Parent Take Index", default=-1)
    name: StringProperty(name="Name", update=_shot_name_changed)
    start: IntProperty(name="Start", update=_start_frame_changed)
    end: IntProperty(name="End", update=_end_frame_changed)
    enabled: BoolProperty(
        name="Enabled", description="Use - or not - the shot in the edit", update=_enabled_changed, default=True
    )

    camera: PointerProperty(
        name="Camera",
        description="Select a Camera",
        type=bpy.types.Object,
        poll=lambda self, obj: True if obj.type == "CAMERA" else False,
    )

    color: FloatVectorProperty(subtype="COLOR", min=0.0, max=1.0, size=4, default=(1.0, 1.0, 1.0, 1.0), options=set())

    def getEditStart(self, scene):
        return scene.UAS_shot_manager_props.getEditTime(self, self.start)

    def getEditEnd(self, scene):
        return scene.UAS_shot_manager_props.getEditTime(self, self.end)
