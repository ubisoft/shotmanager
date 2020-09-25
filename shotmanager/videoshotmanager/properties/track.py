import bpy

from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, FloatVectorProperty, EnumProperty

from shotmanager.properties.take import UAS_ShotManager_Take

from shotmanager.utils.utils import findFirstUniqueName


class UAS_VideoShotManager_Track(PropertyGroup):

    parentScene: PointerProperty(type=Scene, description="Scene to which this track belongs to")

    # deprecated? Use self.parentScene.UAS_vsm_props instead
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
        """ Set a unique name to the track
        """
        tracks = self.videoShotManager().getTracksList()

        # newName = value
        # foundDuplicateName = False
        # for track in tracks:
        #     if track != self and newName == track.name:
        #         foundDuplicateName = True
        # if foundDuplicateName:
        #     newName += "_1"

        newName = findFirstUniqueName(self, value, tracks)

        self["name"] = newName

    name: StringProperty(name="Name", get=get_name, set=set_name)

    def _update_enabled(self, context):
        selectedTrackIndex = context.scene.UAS_vsm_props.getTrackIndex(self)
        for item in bpy.context.scene.sequence_editor.sequences:
            # print(f"Item Channel: {item.channel}, selectedTrackIndex: {selectedTrackIndex}")
            if (len(context.scene.UAS_vsm_props.tracks) - selectedTrackIndex) == item.channel:
                item.mute = not self.enabled

        context.scene.UAS_vsm_props.selected_track_index = selectedTrackIndex

    enabled: BoolProperty(
        name="Enabled", description="Use - or not - the track in the edit", update=_update_enabled, default=True
    )

    color: FloatVectorProperty(
        subtype="COLOR", min=0.0, max=1.0, size=4, default=(1.0, 1.0, 1.0, 1.0), options=set(),
    )

    def _get_vseTrackIndex(self):
        ind = len(self.parentScene.UAS_vsm_props.tracks) - self.parentScene.UAS_vsm_props.getTrackIndex(self)
        val = self.get("vseTrackIndex", ind)
        return val

    def _set_vseTrackIndex(self, value):
        self["vseTrackIndex"] = value

    vseTrackIndex: IntProperty(
        name="VSE Track Index",
        description="Index of the track to use in the VSE",
        min=1,
        get=_get_vseTrackIndex,
        set=_set_vseTrackIndex,
        default=1,
        options=set(),
    )

    trackType: EnumProperty(
        name="Track Type",
        description="Type of the track",
        items=(
            ("STANDARD", "Standard", ""),
            ("RENDERED_SHOTS", "Rendered Shots", ""),
            ("SHOT_CAMERAS", "Shot Cameras", ""),
            ("CAM_FROM_SCENE", "Camera From Scene", ""),
            ("CAM_BG", "Camera Backgrounds", ""),
            ("CUSTOM", "Custom", ""),
        ),
        default="STANDARD",
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

        if self.shotManagerScene is not None:
            props = self.shotManagerScene.UAS_shot_manager_props
            for i, take in enumerate([t.name for t in props.takes]):
                res.append((take, take, "", i))

        if not len(res):
            # res = None
            res.append(("NOTAKE", "No Take Found", ""))
        #     print("Toto")

        return res

    # def _current_take_changed(self, context):
    #     self.setCurrentShotByIndex(0)
    #     self.setSelectedShotByIndex(0)

    sceneTakeName: EnumProperty(
        items=_list_takes, name="Takes", description="Select a take"  # update=_current_take_changed
    )

    def regenerateTrackContent(self):
        print("regenerateTrackContent: " + self.name)

        props = self.shotManagerScene.UAS_shot_manager_props
        takeInd = props.getTakeIndex(props.takes[self.sceneTakeName])
        shotsList = props.getShotsList(ignoreDisabled=True, takeIndex=takeInd)

        self.clearContent()

        if "CAM_BG" == self.trackType:
            for shot in shotsList:
                print("\nShot:", shot.name)

                if len(shot.camera.data.background_images):
                    print("Cam BG found")
                    clip = shot.camera.data.background_images[0].clip
                    offsetEnd = clip.frame_duration + shot.bgImages_offset - shot.getDuration()
                    print("OffsetEnd:", offsetEnd)
                    print(
                        f"dur: {clip.frame_duration}, off: {shot.bgImages_offset}, end - start:{shot.end - shot.start}"
                    )
                    mediaPath = bpy.path.abspath(clip.filepath)
                    print(f"mediaPath: {mediaPath}, duration: {clip.frame_duration}")
                    bpy.context.window_manager.UAS_vse_render.createNewClip(
                        self.parentScene,
                        mediaPath,
                        self.vseTrackIndex,
                        clip.frame_start,
                        offsetStart=-1 * shot.bgImages_offset,
                        offsetEnd=offsetEnd,
                    )

        elif "CAM_FROM_SCENE":

            for shot in shotsList:
                print("\nShot:", shot.name)
                print(f"Start: {shot.start}, Edit Start: {shot.getEditStart()}")
                bpy.context.window_manager.UAS_vse_render.createNewClip(
                    self.parentScene,
                    "",
                    self.vseTrackIndex,
                    -1 * shot.start + shot.getEditStart(),
                    offsetStart=shot.start,  # + shot.getEditStart(),
                    offsetEnd=shot.end,
                    cameraScene=self.shotManagerScene,
                    cameraObject=shot.camera,
                )

            # self.shotManagerScene.frame_start = 14  # OriRangeStart
            # self.shotManagerScene.frame_end = OriRangeEnd

        elif "RENDERED_SHOTS":
            pass

    def clearContent(self):
        bpy.context.window_manager.UAS_vse_render.clearChannel(self.parentScene, self.vseTrackIndex)

    # wkip rajouter un range?
    def getClips(self):
        return bpy.context.window_manager.UAS_vse_render.getChannelClips(self.parentScene, self.vseTrackIndex)

    def getClipsNumber(self):
        return bpy.context.window_manager.UAS_vse_render.getChannelClipsNumber(self.parentScene, self.vseTrackIndex)

    def changeClipsTrack(self, targetTrackIndex):
        return bpy.context.window_manager.UAS_vse_render.changeClipsChannel(
            self.parentScene, self.vseTrackIndex, targetTrackIndex
        )

