import bpy
from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import (
    CollectionProperty,
    IntProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    PointerProperty,
)

from .track import UAS_VideoShotManager_Track

from shotmanager.utils import utils_vse

import logging

_logger = logging.getLogger(__name__)


class UAS_VSM_Props(PropertyGroup):
    def initialize_video_shot_manager(self):
        print(f"\nInitializing Video Shot Manager... Scene: {bpy.context.scene.name}")
        # self.parentScene = self.getParentScene()

        if self.parentScene is None:
            self.parentScene = self.findParentScene()
        # _logger.info(f"\n  self.parentScene : {self.parentScene}")

        # self.initialize()
        # self.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
        # self.createDefaultTake()
        # self.createRenderSettings()
        self.updateTracksList(self.parentScene)  # bad context

        self.isInitialized = True

    def get_isInitialized(self):
        #    print(" get_isInitialized")
        val = self.get("isInitialized", False)

        if not val:
            self.initialize_video_shot_manager()

        return val

    def set_isInitialized(self, value):
        #  print(" set_isInitialized: value: ", value)
        self["isInitialized"] = value

    isInitialized: BoolProperty(get=get_isInitialized, set=set_isInitialized, default=False)

    parentScene: PointerProperty(type=Scene,)  # get=_get_parentScene, set=_set_parentScene,

    def getParentScene(self):
        parentScn = None
        try:
            parentScn = self.parentScene
        except Exception:  # as e
            print("Error - parentScene property is None in vsm_props.getParentScene():", sys.exc_info()[0])

        # if parentScn is not None:
        #     return parentScn
        if parentScn is None:
            _logger.error("\n\n WkError: parentScn in None in Props !!! *** ")
            self.parentScene = self.findParentScene()
        else:
            self.parentScene = parentScn

        if self.parentScene is None:
            print("\n\n Re WkError: self.parentScene in still None in Props !!! *** ")
        # findParentScene is done in initialize function

        return self.parentScene

    def findParentScene(self):
        for scn in bpy.data.scenes:
            if "UAS_vsm_props" in scn:
                props = scn.UAS_vsm_props
                if self == props:
                    #    print("findParentScene: Scene found")
                    return scn
        # print("findParentScene: Scene NOT found")
        return None

    def _get_numTracks(self):
        val = self.get("numTracks", 0)
        val = len(self.tracks)
        return val

    def _set_numTracks(self, value):
        # new tracks are added at the top
        if value > len(self.tracks):
            v = value
            while v > len(self.tracks):
                atIndex = len(self.tracks) + 1
                self.addTrack(name=f"Track {atIndex}", trackType="STANDARD", atIndex=atIndex)
            self["numTracks"] = value
        else:
            self["numTracks"] = len(self.tracks)

    def _update_numTracks(self, context):

        # while self.numTracks > len(self.tracks):
        #     self.addTrack(trackType="STANDARD",)
        pass

    numTracks: IntProperty(
        name="Num Tracks",
        min=0,
        soft_max=20,
        max=32,
        get=_get_numTracks,
        set=_set_numTracks,
        update=_update_numTracks,
        default=5,
    )

    tracks: CollectionProperty(type=UAS_VideoShotManager_Track)

    # property used by the template_list component in an inverted order than selected_track_index in order
    # to reflect the VSE channels stack
    def _get_selected_track_index_inverted(self):
        val = self.get("selected_track_index_inverted", -1)
        return val

    def _set_selected_track_index_inverted(self, value):
        self["selected_track_index_inverted"] = value

    # self.selected_track_index = len(self.tracks) - self["selected_track_index_inverted"]

    def _update_selected_track_index_inverted(self, context):
        if self.selected_track_index != len(self.tracks) - self["selected_track_index_inverted"]:
            self.selected_track_index = len(self.tracks) - self["selected_track_index_inverted"]

    #    print("\n*** _update_selected_track_index_inverted updated. New state: ", self.selected_track_index_inverted)

    # Works from 0 to len(self.track) - 1
    selected_track_index_inverted: IntProperty(
        name="Selected Track Index Inverted",
        get=_get_selected_track_index_inverted,
        set=_set_selected_track_index_inverted,
        update=_update_selected_track_index_inverted,
        default=-1,
    )

    def _get_selected_track_index(self):
        val = self.get("selected_track_index", -1)
        return val

    def _set_selected_track_index(self, value):
        self["selected_track_index"] = value

    def _update_selected_track_index(self, context):
        #    print("\n*** _update_selected_track_index updated. New state: ", self.selected_track_index)
        if self.selected_track_index_inverted != len(self.tracks) - self["selected_track_index"]:
            self.selected_track_index_inverted = len(self.tracks) - self["selected_track_index"]

    # Really represent the track (or channel) index. Then goes from 1 to number of tracks
    selected_track_index: IntProperty(
        name="Selected Track Index",
        get=_get_selected_track_index,
        set=_set_selected_track_index,
        update=_update_selected_track_index,
        default=-1,
    )

    display_color_in_tracklist: BoolProperty(name="Display Color in Track List", default=True, options=set())
    display_opacity_or_volume_in_tracklist: BoolProperty(
        name="Display Opacity in Track List", default=True, options=set()
    )
    display_track_type_in_tracklist: BoolProperty(name="Display Track Type in Track List", default=False, options=set())

    def _filter_jumpToScene(self, object):
        """ Return true only for cameras from the same scene as the shot
        """
        # print("self", str(self))  # this shot
        # print("object", str(object))  # all the objects of the property type

        # if object.type == "SCENE" and object.name in self.parentScene.objects:
        if object is bpy.context.scene:
            return False
        else:
            return True

    jumpToScene: PointerProperty(
        name="Jump To Scene", description="Scene to go to", type=bpy.types.Scene, poll=_filter_jumpToScene,
    )

    ####################
    # tracks
    ####################

    def getUniqueTrackName(self, nameToMakeUnique):
        uniqueName = nameToMakeUnique

        trackList = self.getTracks()

        dup_name = False
        for track in trackList:
            if uniqueName == track.name:
                dup_name = True
        if dup_name:
            uniqueName = f"{uniqueName}_1"

        return uniqueName

    def addTrack(
        self,
        atIndex=-1,
        name="defaultTrack",
        start=10,
        end=20,
        camera=None,
        color=None,
        enabled=True,
        trackType="STANDARD",
        sceneName="",
        sceneTakeName="",
    ):
        """ Add a new track after the selected track if possible or at the end of the track list otherwise
            Return the newly added track
        """

        newTrack = None

        trackListInverted = self.tracks

        newTrack = trackListInverted.add()  # track is added at the end
        newTrack.parentScene = self.getParentScene()
        # print(f"****Add Track: newTrack.parentScene: {newTrack.parentScene}")
        newTrack.name = name
        newTrack.enabled = enabled
        newTrack.trackType = trackType

        if color is None:
            newTrack.setColorFromTrackType()

        else:
            newTrack.color = color

        if "" != sceneName:
            newTrack.shotManagerScene = bpy.data.scenes[sceneName]
        if "" != sceneTakeName:
            newTrack.sceneTakeName = sceneTakeName

        if -1 != atIndex:  # move track at specified index
            # trackListInverted.move(len(trackList) - 1, len(trackList) - atIndex)
            trackListInverted.move(len(trackListInverted) - 1, len(trackListInverted) - atIndex)
            newTrack = trackListInverted[len(trackListInverted) - atIndex]

        return newTrack

    def copyTrack(self, track, atIndex=-1):
        """ Copy a track after the selected track if possible or at the end of the track list otherwise
            Return the newly added track
        """

        newTrack = None
        trackListInverted = self.tracks

        newTrack = trackListInverted.add()  # track is added at the end
        newTrack.name = track.name
        newTrack.enabled = track.enabled
        newTrack.color = track.color

        if -1 != atIndex:  # move track at specified index
            # trackList.move(len(trackListInverted) - 1, atIndex)
            trackListInverted.move(len(trackListInverted) - 1, len(trackListInverted) - atIndex)
            newTrack = trackListInverted[len(trackListInverted) - atIndex]

        return newTrack

    def removeTrack(self, track):
        trackInd = self.getTrackIndex(track)
        print(f"Remove TRack: Name: {track.name} at {trackInd}")
        utils_vse.clearChannel(self.parentScene, trackInd)
        trackListInverted = self.tracks
        trackListInverted.remove(len(trackListInverted) - trackInd)

    def setTrackInfo(
        self,
        trackIndex,
        name=None,
        start=None,
        end=None,
        camera=-1,
        color=None,
        enabled=None,
        trackType=None,
        sceneName=None,
        sceneTakeName=None,
    ):
        """ Set the information of an existing track
            Returns the track
        """
        track = None
        trackList = self.getTracks()

        if not 0 <= trackIndex - 1 < len(trackList):
            return track
        track = trackList[trackIndex - 1]

        if name is not None:
            track.name = name

        if enabled is not None:
            track.enabled = enabled

        if trackType is not None:
            track.trackType = trackType

        if color is not None:
            track.color = color

        # if "" != sceneName:
        #     newTrack.shotManagerScene = bpy.data.scenes[sceneName]
        # if "" != sceneTakeName:
        #     newTrack.sceneTakeName = sceneTakeName

        # if -1 != atIndex:  # move track at specified index
        #     trackList.move(len(trackList) - 1, len(trackList) - atIndex)

        # #  self.numTracks += 1

        return track

    def getTrackIndex(self, track):
        trackList = self.getTracks()
        for i in range(len(trackList)):
            if track == trackList[i]:
                return i + 1
        return -1
        # trackInd = -1

        # trackList = self.getTracks()

        # trackInd = 0
        # while trackInd < len(trackList) and track != trackList[trackInd]:  # wkip mettre trackList[trackInd].name?
        #     trackInd += 1
        # if trackInd == len(trackList):
        #     trackInd = -1

        # return trackInd

    def moveTrackFromIndexToIndex(self, fromIndex, toIndex):
        utils_vse.swapChannels(self.parentScene, fromIndex, toIndex)
        newTrack = None
        trackListInverted = self.tracks
        trackListInverted.move(len(trackListInverted) - fromIndex, len(trackListInverted) - toIndex)
        newTrack = trackListInverted[len(trackListInverted) - toIndex]
        return newTrack

    def getTrackByIndex(self, trackIndex):
        if not (0 < trackIndex <= len(self.tracks)):
            return None
        return self.getTracks()[trackIndex - 1]

    def getTrackByName(self, trackName):
        for t in self.tracks:
            if t.name == trackName:
                return t
        return None

    def getTracks(self, ignoreDisabled=False):
        """Return a list of tracks inverted from the one stored internally. This is because tracks are directly used by the
            template list ui component.
            The list starts at 0 and ends at number of channels - 1
        """
        return [t for t in reversed(self.tracks) if not ignoreDisabled or t.enabled]

    # def getTracksList(self, ignoreDisabled=False):
    #     trackList = []

    #     for track in self.tracks:
    #         if not ignoreDisabled or track.enabled:
    #             trackList.append(track)

    #     return trackList

    def getSelectedTrackIndex(self):
        """ Return the index of the selected track in the enabled track list
            Use this function instead of a direct call to self.selected_track_index
        """
        if 0 >= len(self.getTracks()):
            self.selected_track_index = -1

        return self.selected_track_index

    def getSelectedTrack(self):
        selTrackInd = self.getSelectedTrackIndex()
        if 0 >= selTrackInd:
            return None
        trackList = self.getTracks()
        return trackList[selTrackInd - 1]
        # selectedTrackInd = self.getSelectedTrackIndex()
        # selectedTrack = None
        # if -1 != selectedTrackInd:
        #     selectedTrack = (self.getTracks())[selectedTrackInd]

        # return selectedTrack

    def setSelectedTrackByIndex(self, selectedTrackIndex):
        # print("setSelectedTrackByIndex: selectedTrackIndex:", selectedTrackIndex)
        self.selected_track_index = selectedTrackIndex

    def setSelectedTrack(self, selectedTrack):
        trackInd = self.getTrackIndex(selectedTrack)
        self.setSelectedTrackByIndex(trackInd)

    def updateTracksList(self, scene):
        """Add new track at the top of the list
        """
        # numChannels = utils_vse.getNumUsedChannels(self.parentScene)

        # if self.numTracks < numChannels:
        #     self.numTracks = numChannels

        if 32 > self.numTracks:
            self.numTracks = 32

    ####################
    # channels
    ####################

    def getChannelClips(self, channelIndex):
        clipsList = list()
        for seq in self.parentScene.sequence_editor.sequences:
            if channelIndex == seq.channel:
                clipsList.append(seq)

        return clipsList

    def getChannelClipsNumber(self, channelIndex):
        clipsList = self.getChannelClips(channelIndex)
        return len(clipsList)


_classes = (
    UAS_VideoShotManager_Track,
    UAS_VSM_Props,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.UAS_vsm_props = PointerProperty(type=UAS_VSM_Props)


def unregister():

    del bpy.types.Scene.UAS_vsm_props

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
