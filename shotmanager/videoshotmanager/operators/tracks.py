import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, FloatVectorProperty, EnumProperty, IntProperty

from ..properties.track import UAS_VideoShotManager_Track

from random import uniform


def _list_scenes(self, context):
    res = list()
    # print("Self: ", self)
    for i, scn in enumerate([c for c in bpy.data.scenes]):
        if "UAS_shot_manager_props" in scn:
            # if scn is not context.scene:  # required for camera clips use
            res.append((scn.name, scn.name, "", i))
    # if not len(res):
    #     res.append(("", "", "", 0))
    return res


def _list_takes(self, context):
    res = list()
    # print("*** self.sceneName: ", self.sceneName)
    for i, take in enumerate([c for c in bpy.data.scenes[self.sceneName].UAS_shot_manager_props.takes]):
        item = (take.name, take.name, "")
        res.append(item)
    if not len(res):
        # res = None
        res.append(("NOTAKE", "No Take Found", ""))
    #     print("Toto")
    return res


class UAS_VideoShotManager_TrackAdd(Operator):
    bl_idname = "uas_video_shot_manager.add_track"
    bl_label = "Add New Track"
    bl_description = "Add a new track starting at the current frame" "\nThe new track is put after the selected track"
    bl_options = {"INTERNAL", "UNDO"}

    name: StringProperty(name="Name", default="New Track")
    insertAtChannel: IntProperty(name="Insert at Channel", default=1)

    color: FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        size=3,
        description="Track Color",
        min=0.0,
        max=1.0,
        precision=2,
        # default=(uniform(0, 1), uniform(0, 1), uniform(0, 1)),
        default=(1.0, 1.0, 1.0),
    )

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
        default="STANDARD",
        options=set(),
    )

    sceneName: EnumProperty(
        items=_list_scenes, name="Takes", description="Select a take",  # update=_current_take_changed
    )

    sceneTakeName: EnumProperty(
        items=_list_takes, name="Takes", description="Select a take",  # update=_current_take_changed
    )

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        vsm_props = scene.UAS_vsm_props

        vsm_props.updateTracksList(scene)

        # print("vsm_props.selected_track_index: ", vsm_props.selected_track_index)
        self.insertAtChannel = vsm_props.selected_track_index + 1 if -1 < vsm_props.selected_track_index else 1

        self.name = "New Track"
        self.color = (uniform(0, 1), uniform(0, 1), uniform(0, 1))

        sceneNames = _list_scenes(self, context)
        if len(sceneNames):
            self.sceneName = sceneNames[0][0]

        takeNames = _list_takes(self, context)
        if len(takeNames):
            self.sceneTakeName = (takeNames[0])[0]

        # if takeNames is not None and len(takeNames):
        #     self.sceneTakeName = takeNames[0][0]
        # else:
        #     takeNames = None

        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, row_major=True, columns=2, even_columns=False)

        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="New Track Name:")
        col = grid_flow.column(align=False)
        col.prop(self, "name", text="")

        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="Insert at Channel:")
        col = grid_flow.column(align=False)
        col.prop(self, "insertAtChannel", text="")

        col = grid_flow.column(align=False)
        col.label(text="Color:")
        col = grid_flow.column(align=False)
        col.prop(self, "color", text="")

        col.separator()

        col = grid_flow.column(align=False)
        col.label(text="Track Type:")
        col = grid_flow.column(align=False)
        col.prop(self, "trackType", text="")

        if "CUSTOM" != self.trackType and "STANDARD" != self.trackType:

            col.separator(factor=1.5)
            col = grid_flow.column(align=False)
            col.label(text="Scene:")
            col = grid_flow.column(align=False)
            col.prop(self, "sceneName", text="")

            col = grid_flow.column(align=False)
            col.label(text="Take:")
            col = grid_flow.column(align=False)
            #  if self.sceneTakeName == "":
            # col.alert = True
            col.prop(self, "sceneTakeName", text="")

        layout.separator()

    def execute(self, context):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props
        # selectedTrackInd = vsm_props.getSelectedTrackIndex()
        # newTrackInd = vsm_props.numTracks - selectedTrackInd + 1
        newTrackInd = self.insertAtChannel

        col = [self.color[0], self.color[1], self.color[2], 1]

        vsm_props.addTrack(
            atIndex=newTrackInd,
            name=vsm_props.getUniqueTrackName(self.name),
            color=col,
            trackType=self.trackType,
            sceneName=self.sceneName,
            sceneTakeName=self.sceneTakeName,
        )

        vsm_props.setSelectedTrackByIndex(newTrackInd)

        return {"FINISHED"}


class UAS_VideoShotManager_TrackDuplicate(Operator):
    bl_idname = "uas_video_shot_manager.duplicate_track"
    bl_label = "Duplicate Selected Track"
    bl_description = "Duplicate the track selected in the track list." "\nThe new track is put after the selected track"
    bl_options = {"INTERNAL", "UNDO"}

    name: StringProperty(name="Name")
    addToEndOfList: BoolProperty(name="Add At The End Of The List")

    @classmethod
    def poll(cls, context):
        trackList = context.scene.UAS_vsm_props.getTracks()
        if len(trackList) <= 0:
            return False

        return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, row_major=True, columns=2, even_columns=False)

        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="New Track Name:")
        col = grid_flow.column(align=False)
        col.prop(self, "name", text="")

        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, row_major=True, columns=1, even_columns=False)
        # grid_flow.separator( factor=0.5)
        grid_flow.use_property_split = True
        grid_flow.prop(self, "startAtCurrentTime")
        grid_flow.prop(self, "addToEndOfList")

        layout.separator()

    def execute(self, context):
        vsm_props = context.scene.UAS_vsm_props
        selectedTrack = vsm_props.getSelectedTrack()
        selectedTrackInd = vsm_props.getSelectedTrackIndex()

        if selectedTrack is None:
            return {"CANCELLED"}

        newTrackInd = len(vsm_props.getTracks()) if self.addToEndOfList else selectedTrackInd + 1
        newTrack = vsm_props.copyTrack(selectedTrack, atIndex=newTrackInd)

        newTrack.name = vsm_props.getUniqueTrackName(self.name)

        vsm_props.setSelectedTrackByIndex(newTrackInd)

        return {"FINISHED"}

    def invoke(self, context, event):
        #    currentTrack = context.scene.uas_video_shot_manager_props.getCurrentTrack()
        selectedTrack = context.scene.UAS_vsm_props.getSelectedTrack()
        if selectedTrack is None:
            return {"CANCELLED"}
        self.name = selectedTrack.name + "_copy"
        return context.window_manager.invoke_props_dialog(self)


class UAS_VideoShotManager_MoveTrackUpDown(Operator):
    """Move items up and down in the list
    """

    bl_idname = "uas_video_shot_manager.move_treack_up_down"
    bl_label = "Move Track Up of Down"
    bl_description = "Move track up or down in the track stack"
    bl_options = {"INTERNAL", "UNDO"}

    action: bpy.props.EnumProperty(items=(("UP", "Up", ""), ("DOWN", "Down", "")))

    @classmethod
    def description(self, context, properties):
        descr = "_"
        if "UP" == properties.action:
            descr = "Move track up in the track stack"
        elif "DOWN" == properties.action:
            descr = "Move track down in the track stack"
        return descr

    def execute(self, context):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props
        tracks = vsm_props.getTracks()
        numTracks = len(tracks)

        selectedTrackInd = vsm_props.getSelectedTrackIndex()

        if self.action == "DOWN" and selectedTrackInd > 1:
            movedTrack = vsm_props.moveTrackFromIndexToIndex(selectedTrackInd, selectedTrackInd - 1)
            print(f"MovedTrack: {movedTrack.name}")
            # context.window_manager.UAS_vse_render.swapChannels(
            #     scene, numTracks - selectedTrackInd, numTracks - selectedTrackInd - 1
            # )
            # tracks.move(selectedTrackInd, selectedTrackInd + 1)
            vsm_props.setSelectedTrackByIndex(selectedTrackInd - 1)

        elif self.action == "UP" and selectedTrackInd < numTracks:
            movedTrack = vsm_props.moveTrackFromIndexToIndex(selectedTrackInd, selectedTrackInd + 1)
            print(f"MovedTrack: {movedTrack.name}")
            # context.window_manager.UAS_vse_render.swapChannels(
            #     scene, numTracks - selectedTrackInd, numTracks - selectedTrackInd + 1
            # )
            # tracks.move(selectedTrackInd, selectedTrackInd - 1)
            vsm_props.setSelectedTrackByIndex(selectedTrackInd + 1)

        return {"FINISHED"}


class UAS_VideoShotManager_RemoveTrack(Operator):
    bl_idname = "uas_video_shot_manager.remove_track"
    bl_label = "Remove Selected Track"
    bl_description = "Remove the track selected in the track list."
    bl_options = {"INTERNAL", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.UAS_vsm_props.getTracks()

    def invoke(self, context, event):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props
        selectedTrackInd = vsm_props.getSelectedTrackIndex()
        if 0 < selectedTrackInd:
            track = vsm_props.getTrackByIndex(selectedTrackInd)
            vsm_props.removeTrack(track)
            vsm_props.setSelectedTrackByIndex(selectedTrackInd - 1)

        return {"FINISHED"}


class UAS_VideoShotManager_TrackRemoveMultiple(Operator):
    bl_idname = "uas_video_shot_manager.remove_multiple_tracks"
    bl_label = "Remove Tracks"
    bl_description = "Remove the specified tracks from the list"
    bl_options = {"INTERNAL", "UNDO"}

    action: bpy.props.EnumProperty(items=(("ALL", "ALL", ""), ("DISABLED", "DISABLED", "")))

    def execute(self, context):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props
        selectedTrackInd = vsm_props.getSelectedTrackIndex()

        if "ALL" == self.action:
            print("ALL in remove multiple")
            tracks = vsm_props.getTracks()
            # tracks = vsm_props.tracks
            print(f"tracks: {tracks}")
            for t in tracks:
                vsm_props.removeTrack(t)
                tracksCheck = vsm_props.getTracks()

            vsm_props.setSelectedTrackByIndex(-1)

        elif "DISABLED" == self.action:
            print("DISABLED")
            tracks = vsm_props.getTracks()
            for t in tracks:
                if not t.enabled:
                    vsm_props.removeTrack(t)
            vsm_props.setSelectedTrackByIndex(1)
        # try:
        #     item = tracks[selectedTrackInd]
        # except IndexError:
        #     pass
        # else:
        #     if self.action == "ALL":
        #         i = len(tracks) - 1
        #         while i > -1:
        #             tracks.remove(i)
        #             i -= 1
        #         vsm_props.setSelectedTrackByIndex(-1)
        #     elif self.action == "DISABLED":
        #         i = len(tracks) - 1
        #         while i > -1:
        #             if not tracks[i].enabled:
        #                 tracks.remove(i)
        #             i -= 1
        #         if 0 < len(tracks):  # wkip pas parfait, on devrait conserver la sel currente
        #             vsm_props.setSelectedTrackByIndex(0)

        return {"FINISHED"}


class UAS_VideoShotManager_UpdateVSETrack(Operator):
    bl_idname = "uas_video_shot_manager.update_vse_track"
    bl_label = "Update VSE Track"
    bl_description = "Update VSE Track"
    bl_options = {"INTERNAL", "UNDO"}

    trackName: StringProperty()

    def invoke(self, context, event):

        print("trackName: ", self.trackName)
        context.scene.UAS_vsm_props.tracks[self.trackName].regenerateTrackContent()

        return {"FINISHED"}


class UAS_VideoShotManager_ClearVSETrack(Operator):
    bl_idname = "uas_video_shot_manager.clear_vse_track"
    bl_label = "Clear VSE Track"
    bl_description = "Clear VSE Track"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        vsm_props = context.scene.UAS_vsm_props
        print("trackName: ", vsm_props.tracks[vsm_props.selected_track_index].name)
        vsm_props.tracks[vsm_props.selected_track_index].clearContent()

        return {"FINISHED"}


class UAS_VideoShotManager_GoToSpecifedScene(Operator):
    bl_idname = "uas_video_shot_manager.go_to_specified_scene"
    bl_label = "Go To Scene"
    bl_description = "Go to specified scene"
    bl_options = {"INTERNAL"}

    trackName: StringProperty()

    def invoke(self, context, event):

        print("trackName: ", self.trackName)
        # Make track scene the current one
        bpy.context.window.scene = context.scene.UAS_vsm_props.tracks[self.trackName].shotManagerScene
        bpy.context.window.workspace = bpy.data.workspaces["Layout"]

        return {"FINISHED"}


class UAS_VideoShotManager_UpdateTracksList(Operator):
    bl_idname = "uas_video_shot_manager.update_tracks_list"
    bl_label = "Update Tracks List"
    bl_description = "Set a number of tracks matching the number of used channels"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        context.scene.UAS_vsm_props.updateTracksList(context.scene)
        return {"FINISHED"}


_classes = (
    UAS_VideoShotManager_TrackAdd,
    UAS_VideoShotManager_TrackDuplicate,
    UAS_VideoShotManager_RemoveTrack,
    UAS_VideoShotManager_MoveTrackUpDown,
    UAS_VideoShotManager_TrackRemoveMultiple,
    UAS_VideoShotManager_UpdateVSETrack,
    UAS_VideoShotManager_ClearVSETrack,
    UAS_VideoShotManager_GoToSpecifedScene,
    # UAS_VideoShotManager_SetCurrentTrack,
    UAS_VideoShotManager_UpdateTracksList,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
