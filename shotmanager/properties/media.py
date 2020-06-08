import bpy

from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, FloatVectorProperty


class UAS_ShotManager_Media(PropertyGroup):

    parentScene: PointerProperty(type=Scene)

    parentTakeIndex: IntProperty(name="Parent Take Index", default=-1)

    def shotManager(self):
        """Return the shot manager properties instance the shot is belonging to.
        """
        parentShotManager = None

        # wkip dirty if self.parentScene is not None
        if self.parentScene is None:
            self.parentScene = bpy.context.scene

        if self.parentScene is not None and "UAS_shot_manager_props" in self.parentScene:
            parentShotManager = self.parentScene.UAS_shot_manager_props
        return parentShotManager

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

    def get_name(self):
        val = self.get("name", "-")
        return val

    def set_name(self, value):
        newName = value
        foundDuplicateName = False

        shots = self.shotManager().getShotsList(takeIndex=self.parentTakeIndex)

        for shot in shots:
            if shot != self and newName == shot.name:
                foundDuplicateName = True
        if foundDuplicateName:
            newName += "_1"

        self["name"] = newName

    name: StringProperty(name="Name", get=get_name, set=set_name)

    def _update_start(self, context):
        if self.start > self.end:
            self.end = self.start

    start: IntProperty(name="Start", description="Index of the first included frame of the shot", update=_update_start)

    def _update_end(self, context):
        if self.start > self.end:
            self.start = self.end

    end: IntProperty(name="End", description="Index of the last included frame of the shot", update=_update_end)

    def _update_enabled(self, context):
        context.scene.UAS_shot_manager_props.selected_shot_index = context.scene.UAS_shot_manager_props.getShotIndex(
            self
        )

    enabled: BoolProperty(
        name="Enabled", description="Use - or not - the shot in the edit", update=_update_enabled, default=True
    )

    camera: PointerProperty(
        name="Camera",
        description="Select a Camera",
        type=bpy.types.Object,
        poll=lambda self, obj: True if obj.type == "CAMERA" else False,
    )

    def get_color(self):
        defaultVal = [1.0, 1.0, 1.0, 1.0]
        if self.shotManager() is not None and self.shotManager().use_camera_color:
            if self.camera is not None:
                defaultVal[0] = self.camera.color[0]
                defaultVal[1] = self.camera.color[1]
                defaultVal[2] = self.camera.color[2]

        val = self.get("color", defaultVal)

        if self.shotManager() is not None and self.shotManager().use_camera_color:
            if self.camera is not None:
                val[0] = self.camera.color[0]
                val[1] = self.camera.color[1]
                val[2] = self.camera.color[2]
            else:
                val = [0.0, 0.0, 0.0, 1.0]

        return val

    def set_color(self, value):
        self["color"] = value
        if self.shotManager() is not None and self.shotManager().use_camera_color:
            if self.camera is not None:
                self.camera.color[0] = self["color"][0]
                self.camera.color[1] = self["color"][1]
                self.camera.color[2] = self["color"][2]
                self.camera.color[3] = self["color"][3]

    color: FloatVectorProperty(
        subtype="COLOR",
        min=0.0,
        max=1.0,
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        get=get_color,
        set=set_color,
        options=set(),
    )

    def getEditStart(self, scene):
        return scene.UAS_shot_manager_props.getEditTime(self, self.start)

    def getEditEnd(self, scene):
        return scene.UAS_shot_manager_props.getEditTime(self, self.end)
