import bpy

from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, FloatVectorProperty, FloatProperty

from shotmanager.utils.utils import findFirstUniqueName


class UAS_ShotManager_Shot(PropertyGroup):
    # def _get_parentScene(self):
    #     val = self.get("parentScene", None)
    #     if val is None:
    #         matches = [
    #             s for s in bpy.data.scenes if "UAS_shot_manager_props" in s and self == s["UAS_shot_manager_props"]
    #         ]
    #         self["parentScene"] = matches[0] if len(matches) > 0 else None
    #     return self["parentScene"]

    # def _set_parentScene(self, value):
    #     self["parentScene"] = value

    # parentScene: PointerProperty(type=Scene, get=_get_parentScene, set=_set_parentScene)
    parentScene: PointerProperty(type=Scene)
    parentTakeIndex: IntProperty(name="Parent Take Index", default=-1)

    # for backward compatibility - before V1.2.21
    # used by data version patches.
    # For general purpose use the property self.parentScene
    def getParentScene(self):
        if self.parentScene is not None:
            return self.parentScene

        for scn in bpy.data.scenes:
            if "UAS_shot_manager_props" in scn:
                props = scn.UAS_shot_manager_props
                for take in props.takes:
                    #    print("Take name: ", take.name)
                    for shot in take.shots:
                        #        print("  Shot name: ", shot.name)
                        if shot.name == self.name:
                            self.parentScene = scn
                            return scn
        return None

    # def shotManager(self):
    #     """Return the shot manager properties instance the shot is belonging to.
    #     """
    #     parentShotManager = None
    #     parentScene = self.getParentScene()

    #     if parentScene is not None:
    #         parentShotManager = parentScene.UAS_shot_manager_props
    #     return parentShotManager

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
        """ Set a unique name to the shot
        """
        # shots = self.getParentScene().UAS_shot_manager_props.getShotsList(takeIndex=self.parentTakeIndex)
        shots = self.parentScene.UAS_shot_manager_props.getShotsList(takeIndex=self.parentTakeIndex)
        newName = findFirstUniqueName(self, value, shots)
        self["name"] = newName

    name: StringProperty(name="Name", get=get_name, set=set_name)

    #############
    # start #####
    #############

    def _get_start(self):
        val = self.get("start", 25)
        return val

    def _set_start(self, value):
        duration = self.getDuration()
        self["start"] = value
        if self.durationLocked:
            self["end"] = self.start + duration - 1
        else:
            if self.start > self.end:
                self["end"] = self.start

    def _update_start(self, context):
        if self.camera is not None and len(self.camera.data.background_images):
            bgClip = self.camera.data.background_images[0].clip
            if bgClip is not None and self.bgImages_linkToShotStart:
                bgClip.frame_start = self.start + self.bgImages_offset
                # print("  Value: ", value)

    start: IntProperty(
        name="Start",
        description="Index of the first included frame of the shot",
        get=_get_start,
        set=_set_start,
        update=_update_start,
    )

    #############
    # end #####
    #############

    def _get_end(self):
        val = self.get("end", 30)
        return val

    def _set_end(self, value):
        duration = self.getDuration()
        self["end"] = value
        if self.durationLocked:
            self["start"] = self.end - duration + 1
        else:
            if self.start > self.end:
                self["start"] = self.end

    def _update_end(self, context):
        pass

    end: IntProperty(
        name="End",
        description="Index of the last included frame of the shot",
        get=_get_end,
        set=_set_end,
        update=_update_end,
    )

    #############
    # duration #####
    #############

    def _get_duration_fp(self):
        print("\n*** _get_duration_fp: New state: ", self.duration_fp)

        # not used
        fakeVal = self.get("_get_duration_fp", -1)

        realVal = self.getDuration()
        return realVal

    def _set_duration_fp(self, value):
        print("\n*** _update_duration_fp: New state: ", self.duration_fp)
        self["_set_duration_fp"] = value
        self.end = self.start + max(value, 1) - 1

    def _update_duration_fp(self, context):
        print("\n*** _update_duration_fp: New state: ", self.duration_fp)

    # fake property: value never used in itself, its purpose is to update ofher properties
    duration_fp: IntProperty(
        name="Shot Duration",
        description="Duration is a frame number given by end - start + 1",
        min=1,
        get=_get_duration_fp,
        set=_set_duration_fp,
        update=_update_duration_fp,
        options=set(),
    )

    durationLocked: BoolProperty(
        name="Lock Duration",
        description="Lock - or not - the shot duration.\nWhen locked, changing one boundary will also affect the other",
        default=False,
        options=set(),
    )

    def _update_enabled(self, context):
        context.scene.UAS_shot_manager_props.selected_shot_index = context.scene.UAS_shot_manager_props.getShotIndex(
            self
        )

    enabled: BoolProperty(
        name="Enabled",
        description="Use - or not - the shot in the edit",
        update=_update_enabled,
        default=True,
        options=set(),
    )

    camera: PointerProperty(
        name="Camera",
        description="Select a Camera",
        type=bpy.types.Object,
        poll=lambda self, obj: True if obj.type == "CAMERA" else False,
    )

    def get_color(self):
        defaultVal = [1.0, 1.0, 1.0, 1.0]
        props = self.parentScene.UAS_shot_manager_props

        if props.use_camera_color:
            if self.camera is not None:
                defaultVal[0] = self.camera.color[0]
                defaultVal[1] = self.camera.color[1]
                defaultVal[2] = self.camera.color[2]

        val = self.get("color", defaultVal)

        if props.use_camera_color:
            if self.camera is not None:
                val[0] = self.camera.color[0]
                val[1] = self.camera.color[1]
                val[2] = self.camera.color[2]
            else:
                val = [0.0, 0.0, 0.0, 1.0]

        return val

    def set_color(self, value):
        self["color"] = value
        props = self.parentScene.UAS_shot_manager_props
        if props.use_camera_color and self.camera is not None:
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

    def updateClipLinkToShotStart(self):
        if self.camera is not None and len(self.camera.data.background_images):
            bgClip = self.camera.data.background_images[0].clip
            if bgClip is not None:
                if self.bgImages_linkToShotStart:
                    bgClip.frame_start = self.start + self.bgImages_offset
                else:
                    bgClip.frame_start = self.bgImages_offset

    ##############
    # background images
    ##############

    def _get_bgImages_linkToShotStart(self):
        val = self.get("bgImages_linkToShotStart", True)
        return val

    def _set_bgImages_linkToShotStart(self, value):
        self["bgImages_linkToShotStart"] = value
        self.updateClipLinkToShotStart()

    # def _update_bgImages_linkToShotStart(self, context):
    #     if self.camera is not None and len(self.camera.data.background_images):
    #         bgClip = self.camera.data.background_images[0].clip
    #         if bgClip is not None:
    #             if self._update_bgImages_linkToShotStart:
    #                 bgClip.frame_start = self.start + self.bgImages_offset
    #             else:
    #                 bgClip.frame_start = self.bgImages_offset

    bgImages_linkToShotStart: BoolProperty(
        name="Link BG to Start",
        description="Link the background image clip to the shot start.\n"
        "If linked the background clip start frame is relative to the shot start.\n"
        "If not linked the clip starts at frame 0 + offset",
        default=True,
        get=_get_bgImages_linkToShotStart,
        set=_set_bgImages_linkToShotStart,
        # update=_update_bgImages_linkToShotStart,
        options=set(),
    )

    def _get_bgImages_offset(self):
        val = self.get("bgImages_offset", 0)
        return val

    def _set_bgImages_offset(self, value):
        self["bgImages_offset"] = value
        self.updateClipLinkToShotStart()
        # if self.camera is not None and len(self.camera.data.background_images):
        #     bgClip = self.camera.data.background_images[0].clip
        #     if bgClip is not None:
        #         if self.bgImages_linkToShotStart:
        #             bgClip.frame_start = self.start + self.bgImages_offset
        #         else:
        #             bgClip.frame_start = self.bgImages_offset

    bgImages_offset: IntProperty(
        name="BG Clip Offset",
        description="Time offset for the clip used as background for the camera",
        soft_min=-20,
        soft_max=20,
        get=_get_bgImages_offset,
        set=_set_bgImages_offset,
        default=0,
    )
