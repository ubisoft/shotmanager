import bpy
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


class UAS_VSM_Props(PropertyGroup):
    def _get_numTracks(self):
        val = self.get("numTracks", 0)
        val = len(self.tracks)
        return val

    def _set_numTracks(self, value):
        # new tracks are added at the top
        if value > len(self.tracks):
            v = value
            while v > len(self.tracks):
                self.addTrack(trackType="STANDARD", atIndex=(len(self.tracks) + 1))
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
        print("\n*** _update_selected_track_index_inverted updated. New state: ", self.selected_track_index_inverted)

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
        print("\n*** _update_selected_track_index updated. New state: ", self.selected_track_index)
        if self.selected_track_index_inverted != len(self.tracks) - self["selected_track_index"]:
            self.selected_track_index_inverted = len(self.tracks) - self["selected_track_index"]

    # Works from len(self.track) to 1
    selected_track_index: IntProperty(
        name="Selected Track Index",
        get=_get_selected_track_index,
        set=_set_selected_track_index,
        update=_update_selected_track_index,
        default=-1,
    )

    display_color_in_tracklist: BoolProperty(name="Display Color in Track List", default=True, options=set())
    display_opacity_in_tracklist: BoolProperty(name="Display Opacity in Track List", default=True, options=set())

    def getTracks(self):
        return self.tracks

    def getParentScene(self):
        for scene in bpy.data.scenes:
            if "UAS_vsm_props" in scene and self == scene["UAS_vsm_props"]:
                return scene
        return None

    ####################
    # tracks
    ####################

    def getUniqueTrackName(self, nameToMakeUnique):
        uniqueName = nameToMakeUnique

        trackList = self.getTracksList(ignoreDisabled=False)

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
        color=(0.2, 0.6, 0.8, 1),
        enabled=True,
        trackType="STANDARD",
        sceneName="",
        sceneTakeName="",
    ):
        """ Add a new track after the selected track if possible or at the end of the track list otherwise
            Return the newly added track
        """

        newTrack = None

        trackList = self.getTracks()

        newTrack = trackList.add()  # track is added at the end
        newTrack.parentScene = self.getParentScene()
        newTrack.name = name
        newTrack.enabled = enabled
        newTrack.color = color

        newTrack.trackType = trackType

        if "" != sceneName:
            newTrack.shotManagerScene = bpy.data.scenes[sceneName]
        if "" != sceneTakeName:
            newTrack.sceneTakeName = sceneTakeName

        if -1 != atIndex:  # move track at specified index
            trackList.move(len(trackList) - 1, len(trackList) - atIndex)

        #  self.numTracks += 1

        return newTrack

    def copyTrack(self, track, atIndex=-1):
        """ Copy a track after the selected track if possible or at the end of the track list otherwise
            Return the newly added track
        """

        newTrack = None

        trackList = self.getTracks()

        newTrack = trackList.add()  # track is added at the end
        newTrack.name = track.name
        newTrack.enabled = track.enabled
        newTrack.color = track.color

        if -1 != atIndex:  # move track at specified index
            trackList.move(len(trackList) - 1, atIndex)
            newTrack = trackList[atIndex]

        return newTrack

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
        """

        trackList = self.getTracks()

        track = trackList[len(trackList) - trackIndex]

        if name is not None:
            track.name = name

        if enabled is not None:
            track.enabled = enabled

        if color is not None:
            track.color = color

        if trackType is not None:
            track.trackType = trackType

        # if "" != sceneName:
        #     newTrack.shotManagerScene = bpy.data.scenes[sceneName]
        # if "" != sceneTakeName:
        #     newTrack.sceneTakeName = sceneTakeName

        # if -1 != atIndex:  # move track at specified index
        #     trackList.move(len(trackList) - 1, len(trackList) - atIndex)

        # #  self.numTracks += 1

        return

    def getTrackIndex(self, track):
        trackInd = -1

        trackList = self.getTracksList(ignoreDisabled=False)

        trackInd = 0
        while trackInd < len(trackList) and track != trackList[trackInd]:  # wkip mettre trackList[trackInd].name?
            trackInd += 1
        if trackInd == len(trackList):
            trackInd = -1

        return trackInd

    def getTrack(self, trackIndex, ignoreDisabled=False):
        track = None

        trackList = self.getTracksList(ignoreDisabled=ignoreDisabled)

        # if ignoreDisabled:
        #     if 0 < len(trackList) and trackIndex < len(trackList):
        #         track = trackList[trackIndex]
        # else if 0 < trackNumber and trackIndex < trackNumber:
        #     track = self.tracks[trackIndex]

        if 0 < len(trackList) and trackIndex < len(trackList):
            track = trackList[trackIndex]

        return track

    def getTracksList(self, ignoreDisabled=False):
        trackList = []

        for track in self.tracks:
            if not ignoreDisabled or track.enabled:
                trackList.append(track)

        return trackList

    def getSelectedTrackIndex(self):
        """ Return the index of the selected track in the enabled track list
            Use this function instead of a direct call to self.selected_track_index
        """
        if 0 >= len(self.getTracks()):
            self.selected_track_index = -1

        return self.selected_track_index

    def getSelectedTrack(self):
        selectedTrackInd = self.getSelectedTrackIndex()
        selectedTrack = None
        if -1 != selectedTrackInd:
            selectedTrack = (self.getTracks())[selectedTrackInd]

        return selectedTrack

    def setSelectedTrackByIndex(self, selectedTrackIndex):
        # print("setSelectedTrackByIndex: selectedTrackIndex:", selectedTrackIndex)
        self.selected_track_index = selectedTrackIndex

    def setSelectedTrack(self, selectedTrack):
        trackInd = self.getTrackIndex(selectedTrack)
        self.setSelectedTrackByIndex(trackInd)

    def updateTracksList(self, scene):
        """Add new track at the top of the list
        """
        numChannels = self.getNumUsedChannels(scene)

        if self.numTracks < numChannels:
            self.numTracks = numChannels

    ####################
    # channels
    ####################

    def getNumUsedChannels(self, scene):
        numChannels = 0
        for i, seq in enumerate(scene.sequence_editor.sequences):
            numChannels = max(seq.channel, numChannels)
        return numChannels


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
