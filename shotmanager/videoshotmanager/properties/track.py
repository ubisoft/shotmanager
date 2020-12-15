import bpy

from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    IntProperty,
    BoolProperty,
    PointerProperty,
    FloatVectorProperty,
    EnumProperty,
    FloatProperty,
)

from shotmanager.properties.take import UAS_ShotManager_Take

from shotmanager.utils.utils import findFirstUniqueName
from shotmanager.utils import utils_vse

# ("STANDARD", "Standard", ""),
# ("AUDIO", "Audio", ""),
# ("VIDEO", "Video", ""),
# ("CAM_FROM_SCENE", "Camera From Scene", ""),
# ("SHOT_CAMERAS", "Shot Manager Cameras", "Cameras from Shot Manager"),
# ("RENDERED_SHOTS", "Rendered Shots", ""),
# ("CAM_BG", "Camera Backgrounds", ""),
# ("CUSTOM", "Custom", ""),


class UAS_VideoShotManager_Track(PropertyGroup):

    parentScene: PointerProperty(type=Scene, description="Scene to which this track belongs to")

    def getName_PathCompliant(self):
        trackName = self.name.replace(" ", "_")
        return trackName

    def get_name(self):
        val = self.get("name", "-")
        return val

    def set_name(self, value):
        """ Set a unique name to the track
        """
        tracks = self.parentScene.UAS_vsm_props.getTracks()

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
        if 0 < self.vseTrackIndex:
            utils_vse.muteChannel(self.parentScene, self.vseTrackIndex, not self.enabled)
        self.parentScene.UAS_vsm_props.setSelectedTrack(self)

    enabled: BoolProperty(
        name="Enabled", description="Use - or not - the track in the edit", update=_update_enabled, default=True
    )

    def _get_opacity(self):
        val = self.get("opacity", 100)
        return val

    def _set_opacity(self, value):
        self["opacity"] = value

    def _update_opacity(self, context):
        utils_vse.setChannelAlpha(self.parentScene, self.vseTrackIndex, self.opacity * 0.01)
        self.parentScene.UAS_vsm_props.setSelectedTrack(self)

    opacity: IntProperty(
        name="Opacity",
        description="Track opacity",
        min=0,
        max=100,
        get=_get_opacity,
        set=_set_opacity,
        update=_update_opacity,
        default=100,
        subtype="PERCENTAGE",
        options=set(),
    )

    def _get_volume(self):
        val = self.get("volume", 1.0)
        return val

    def _set_volume(self, value):
        self["volume"] = value

    def _update_volume(self, context):
        utils_vse.setChannelVolume(self.parentScene, self.vseTrackIndex, self.volume)
        self.parentScene.UAS_vsm_props.setSelectedTrack(self)

    volume: FloatProperty(
        name="Volume",
        description="Track volume",
        min=0.0,
        soft_max=2,
        max=5,
        get=_get_volume,
        set=_set_volume,
        update=_update_volume,
        default=1.0,
        subtype="FACTOR",
        options=set(),
    )

    def _update_color(self, context):
        self.parentScene.UAS_vsm_props.setSelectedTrack(self)

    color: FloatVectorProperty(
        subtype="COLOR", min=0.0, max=1.0, size=4, update=_update_color, default=(1.0, 1.0, 1.0, 1.0), options=set(),
    )

    def _get_vseTrackIndex(self):
        ind = self.parentScene.UAS_vsm_props.getTrackIndex(self)
        val = self.get("vseTrackIndex", ind)
        return val

    def _set_vseTrackIndex(self, value):
        self["vseTrackIndex"] = value

    vseTrackIndex: IntProperty(
        name="VSE Track Index",
        description="Index of the track to use in the VSE. Starts at 1",
        min=1,
        get=_get_vseTrackIndex,
        set=_set_vseTrackIndex,
        default=1,
        options=set(),
    )

    def _update_trackType(self, context):
        self.setColorFromTrackType()
        self.parentScene.UAS_vsm_props.setSelectedTrack(self)

    trackType: EnumProperty(
        name="Track Type",
        description="Type of the track",
        items=(
            ("STANDARD", "Standard", ""),
            ("AUDIO", "Audio", ""),
            ("VIDEO", "Video", ""),
            ("CAM_FROM_SCENE", "Camera From Scene", ""),
            ("SHOT_CAMERAS", "Shot Manager Cameras", "Cameras from Shot Manager"),
            ("RENDERED_SHOTS", "Rendered Shots", ""),
            ("CAM_BG", "Camera Backgrounds", ""),
            ("CUSTOM", "Custom", ""),
        ),
        update=_update_trackType,
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
        print(f"\nregenerateTrackContent: {self.name}, type: {self.trackType}")

        if "CAM_FROM_SCENE" == self.trackType:
            # wkip to do
            return

        if self.shotManagerScene is None:
            return

        props = self.shotManagerScene.UAS_shot_manager_props
        vse_render = bpy.context.window_manager.UAS_vse_render
        takeInd = props.getTakeIndex(props.takes[self.sceneTakeName])
        shotsList = props.getShotsList(ignoreDisabled=True, takeIndex=takeInd)

        trackScene_resolution_x = self.shotManagerScene.render.resolution_x
        trackScene_resolution_y = self.shotManagerScene.render.resolution_y

        self.clearContent()

        if "SHOT_CAMERAS" == self.trackType:
            for shot in shotsList:
                print("\nShot:", shot.name)
                print(f"Start: {shot.start}, Edit Start: {shot.getEditStart()}")
                newClip = vse_render.createNewClip(
                    self.parentScene,
                    "",
                    self.vseTrackIndex,
                    -1 * shot.start + shot.getEditStart(),
                    offsetStart=shot.start,  # + shot.getEditStart(),
                    offsetEnd=shot.end,
                    cameraScene=self.shotManagerScene,
                    cameraObject=shot.camera,
                    clipName=shot.name,
                )

                res_x = 1280
                res_y = 960
                clip_x = trackScene_resolution_x
                clip_y = trackScene_resolution_y
                vse_render.cropClipToCanvas(
                    res_x, res_y, newClip, clip_x, clip_y, mode="FIT_WIDTH",
                )
                # newClip.use_crop = True
                # newClip.crop.min_x = -1 * int((1280 - trackScene_resolution_x) / 2)
                # newClip.crop.max_x = newClip.crop.min_x
                # newClip.crop.min_y = -1 * int((960 - trackScene_resolution_y) / 2)
                # newClip.crop.max_y = newClip.crop.min_y

        elif "CAM_BG" == self.trackType:
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

        elif "RENDERED_SHOTS" == self.trackType:
            pass

    def clearContent(self):
        bpy.context.window_manager.UAS_vse_render.clearChannel(self.parentScene, self.vseTrackIndex)

    # wkip rajouter un range?
    def getClips(self):
        # return bpy.context.window_manager.UAS_vse_render.getChannelClips(self.parentScene, self.vseTrackIndex)
        return self.parentScene.UAS_vsm_props.getChannelClips(self.parentScene, self.vseTrackIndex)

    def getClipsNumber(self):
        return bpy.context.window_manager.UAS_vse_render.getChannelClipsNumber(self.parentScene, self.vseTrackIndex)

    def changeClipsTrack(self, targetTrackIndex):
        return bpy.context.window_manager.UAS_vse_render.changeClipsChannel(
            self.parentScene, self.vseTrackIndex, targetTrackIndex
        )

    def setColorFromTrackType(self):
        if "STANDARD" == self.trackType:
            self.color = (0.15, 0.06, 0.25, 1)
        elif "AUDIO" == self.trackType:
            self.color = (0.1, 0.5, 0.2, 1)
        elif "VIDEO" == self.trackType:
            self.color = (0.1, 0.2, 0.8, 1)
        elif "CAM_FROM_SCENE" == self.trackType:
            self.color = (0.6, 0.5, 0.0, 1)
        elif "SHOT_CAMERAS" == self.trackType:
            self.color = (0.6, 0.2, 0.0, 1)
        elif "RENDERED_SHOTS" == self.trackType:
            self.color = (0.4, 0.7, 0.0, 1)
        elif "CAM_BG" == self.trackType:
            self.color = (0.7, 0.0, 0.2, 1)
        elif "CUSTOM" == self.trackType:
            self.color = (0.3, 0.5, 0.4, 1)
