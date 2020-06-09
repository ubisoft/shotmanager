import bpy

from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, FloatVectorProperty, EnumProperty

from shotmanager.properties.take import UAS_ShotManager_Take


class UAS_VideoShotManager_Track(PropertyGroup):

    parentScene: PointerProperty(type=Scene, description="Scene to which this track belongs to")

    def videoShotManager(self):
        """Return the video shot manager properties instance the shot is belonging to.
        """
        parentVideoShotManager = None

        # wkip dirty if self.parentScene is not None
        if self.parentScene is None:
            self.parentScene = bpy.context.scene

        if self.parentScene is not None and "UAS_vsm_props" in self.parentScene:
            parentVideoShotManager = self.parentScene.UAS_vsm_props
        return parentVideoShotManager

    def getName_PathCompliant(self):
        trackName = self.name.replace(" ", "_")
        return trackName

    def get_name(self):
        val = self.get("name", "-")
        return val

    def set_name(self, value):
        newName = value
        foundDuplicateName = False

        tracks = self.videoShotManager().getTracksList()

        for track in tracks:
            if track != self and newName == track.name:
                foundDuplicateName = True
        if foundDuplicateName:
            newName += "_1"

        self["name"] = newName

    name: StringProperty(name="Name", get=get_name, set=set_name)

    def _update_enabled(self, context):
        context.scene.UAS_vsm_props.selected_track_index = context.scene.UAS_vsm_props.getTrackIndex(self)

    enabled: BoolProperty(
        name="Enabled", description="Use - or not - the track in the edit", update=_update_enabled, default=True
    )

    color: FloatVectorProperty(
        subtype="COLOR", min=0.0, max=1.0, size=4, default=(1.0, 1.0, 1.0, 1.0), options=set(),
    )

    # wkip readonly?
    vseTrackIndex: IntProperty(
        name="VSE Track Index", description="Index of the track to use in the VSE", options=set(),
    )

    trackType: EnumProperty(
        name="Track Type",
        description="Type of the track",
        items=(
            ("RENDERED_SHOTS", "Rendered Shots", ""),
            ("3D_CAMERAS", "3D Cameras", ""),
            ("CAM_BG", "Camera Backgrounds", ""),
        ),  # adding CUSTOM ?
        default="CAM_BG",
        options=set(),
    )

    def _filter_ShotManagerScenes(self, object):
        """ Return only scenes with a ShotManager instance
        """
        #   print("object", str(object))
        # print("self", str(self))
        #   print("self.parentScene ", str(self.parentScene))
        sceneWithValidSM = "UAS_shot_manager_props" in object and object is not self.parentScene
        return sceneWithValidSM
        # return "SceneRace" == object.name  # "SceneRace" in bpy.data.scenes

    shotManagerScene: PointerProperty(
        type=bpy.types.Scene,
        poll=_filter_ShotManagerScenes,
        name="Shot Manager Scene",
        description="Scene with a Shot Manager instance.\nCurrent scene cannot be used",
    )

    # shotManagerTake: PointerProperty(
    #     type=UAS_ShotManager_Take,
    #     name="Shot Manager Take",
    #     description="Scene with a Shot Manager instance.\nCurrent scene cannot be used",
    # )

    def _list_takes(self, context):
        res = list()
        props = self.shotManagerScene.UAS_shot_manager_props
        for i, take in enumerate([t.name for t in props.takes]):
            res.append((take, take, "", i))

        return res

    # def _current_take_changed(self, context):
    #     self.setCurrentShotByIndex(0)
    #     self.setSelectedShotByIndex(0)

    current_take_name: EnumProperty(
        items=_list_takes, name="Takes", description="Select a take",  # update=_current_take_changed
    )

    def regenerateTrackContent(self):
        print("regenerateTrackContent: " + self.name)

        props = self.shotManagerScene.UAS_shot_manager_props
        takeInd = props.getTakeIndex(props.takes[self.current_take_name])
        shotsList = props.getShotsList(ignoreDisabled=True, takeIndex=takeInd)
        for shot in shotsList:
            print("Shot:", shot.name)
            if "CAM_BG" == self.trackType:
                if len(shot.camera.data.background_images):
                    print("Cam BG found")
                    mediaPath = bpy.path.abspath(shot.camera.data.background_images[0].clip.filepath)
                    print("mediaPath:", mediaPath)
                    bpy.context.window_manager.UAS_vse_render.createNewClip(
                        self.parentScene, mediaPath, self.vseTrackIndex, 2, offsetStart=0, offsetEnd=0
                    )
