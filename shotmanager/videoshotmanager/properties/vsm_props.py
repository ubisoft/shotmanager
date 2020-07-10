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

    tracks: CollectionProperty(type=UAS_VideoShotManager_Track)

    current_track_index: IntProperty(default=-1)

    selected_track_index: IntProperty(default=-1)

    display_color_in_tracklist: BoolProperty(name="Display Color in Track List", default=True, options=set())

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
        trackType=None,
        sceneName="",
        sceneTakeName="",
    ):
        """ Add a new track after the current track if possible or at the end of the track list otherwise
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
            trackList.move(len(trackList) - 1, atIndex)

        return newTrack

    def copyTrack(self, track, atIndex=-1):
        """ Copy a track after the current track if possible or at the end of the track list otherwise
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

    def setCurrentTrackByIndex(self, currentTrackIndex):
        """ Changing the current track doesn't affect the selected one
        """
        #  print(" setCurrentTrackByIndex")
        scene = bpy.context.scene
        vsm_props = scene.UAS_vsm_props

        trackList = self.getTracks()
        self.current_track_index = currentTrackIndex

    def setCurrentTrack(self, currentTrack):
        trackInd = self.getTrackIndex(currentTrack)
        #    print("setCurrentTrack: trackInd:", trackInd)
        self.setCurrentTrackByIndex(trackInd)

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

    def getCurrentTrackIndex(self, ignoreDisabled=False):
        """ Return the index of the current track in the enabled track list
            Use this function instead of a direct call to self.current_track_index
            
            if ignoreDisabled is false (default) then the track index is relative to the whole track list,
               otherwise it is relative to the list of the enabled tracks
            can return -1 if all the tracks are disabled!!
        """
        #   print(" *** getCurrentTrackIndex")

        currentTrackInd = -1

        if ignoreDisabled and 0 < len(self.tracks):
            # for i, track in enumerate ( self.context.scene.UAS_track_manager_props.takes[self.context.scene.UAS_track_manager_props.sceneTakeName].tracks ):
            currentTrackInd = self.current_track_index
            for i in range(self.current_track_index + 1):
                if not self.tracks[i].enabled:
                    currentTrackInd -= 1
        #      print("  in ignoreDisabled, currentTrackInd: ", currentTrackInd)
        else:
            if 0 < len(self.tracks):

                if len(self.tracks) > self.current_track_index:
                    #          print("    in 01")
                    currentTrackInd = self.current_track_index
                else:
                    #          print("    in 02")
                    currentTrackInd = len(self.tracks) - 1
                    self.setCurrentTrackByIndex(currentTrackInd)

        # print("  NOT in ignoreDisabled, currentTrackInd: ", currentTrackInd)

        return currentTrackInd

    def getCurrentTrack(self, ignoreDisabled=False):
        currentTrackInd = -1

        currentTrackInd = self.getCurrentTrackIndex(ignoreDisabled=ignoreDisabled)
        #   print("getCurrentTrack: currentTrackInd: ", currentTrackInd)
        currentTrack = None
        if -1 != currentTrackInd:
            currentTrack = self.tracks[currentTrackInd]

        return currentTrack

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


_classes = (
    UAS_VideoShotManager_Track,
    UAS_VSM_Props,
)


def register():
    print("\n *** *** Resistering Video Shot Manager *** *** \n")
    for cls in _classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.UAS_vsm_props = PointerProperty(type=UAS_VSM_Props)


def unregister():

    del bpy.types.Scene.UAS_vsm_props

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
