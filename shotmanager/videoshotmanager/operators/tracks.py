import bpy
from bpy.types import Operator, Menu
from bpy.props import StringProperty, BoolProperty, FloatVectorProperty, PointerProperty, EnumProperty

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
        print(f"_list_takes: {item}")
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
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(name="Name")

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
            ("RENDERED_SHOTS", "Rendered Shots", ""),
            ("SHOT_CAMERAS", "Shot Cameras", ""),
            ("CAM_FROM_SCENE", "Camera From Scene", ""),
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
        col.label(text="Color:")
        col = grid_flow.column(align=False)
        col.prop(self, "color", text="")

        col.separator()

        col = grid_flow.column(align=False)
        col.label(text="Track Type:")
        col = grid_flow.column(align=False)
        col.prop(self, "trackType", text="")

        if "CUSTOM" != self.trackType:
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
        selectedTrackInd = vsm_props.getSelectedTrackIndex()
        newTrackInd = selectedTrackInd + 1

        col = [self.color[0], self.color[1], self.color[2], 1]

        vsm_props.addTrack(
            atIndex=newTrackInd,
            name=vsm_props.getUniqueTrackName(self.name),
            color=col,
            trackType=self.trackType,
            sceneName=self.sceneName,
            sceneTakeName=self.sceneTakeName,
        )

        vsm_props.setCurrentTrackByIndex(newTrackInd)
        vsm_props.setSelectedTrackByIndex(newTrackInd)

        return {"FINISHED"}


class UAS_VideoShotManager_TrackDuplicate(Operator):
    bl_idname = "uas_video_shot_manager.duplicate_track"
    bl_label = "Duplicate Selected Track"
    bl_description = "Duplicate the track selected in the track list." "\nThe new track is put after the selected track"
    bl_options = {"REGISTER", "UNDO"}

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

        vsm_props.setCurrentTrackByIndex(newTrackInd)
        vsm_props.setSelectedTrackByIndex(newTrackInd)

        return {"FINISHED"}

    def invoke(self, context, event):
        #    currentTrack = context.scene.uas_video_shot_manager_props.getCurrentTrack()
        selectedTrack = context.scene.UAS_vsm_props.getSelectedTrack()
        if selectedTrack is None:
            return {"CANCELLED"}
        self.name = selectedTrack.name + "_copy"
        return context.window_manager.invoke_props_dialog(self)


class UAS_VideoShotManager_RemoveTrack(Operator):
    bl_idname = "uas_video_shot_manager.remove_track"
    bl_label = "Remove Selected Track"
    bl_description = "Remove the track selected in the track list."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        tracks = context.scene.UAS_vsm_props.getTracks()
        if len(tracks) <= 0:
            return False

        return True

    def invoke(self, context, event):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props
        tracks = vsm_props.getTracks()
        currentTrackInd = vsm_props.current_track_index
        selectedTrackInd = vsm_props.getSelectedTrackIndex()

        try:
            item = tracks[selectedTrackInd]
        except IndexError:
            pass
        else:
            #    print(" current: " + str(currentTrackInd) + ", len(tracks): " + str(len(tracks)) + ", selectedTrackInd: " + str(selectedTrackInd))

            # case of the last track
            if selectedTrackInd == len(tracks) - 1:
                if currentTrackInd == selectedTrackInd:
                    vsm_props.setCurrentTrackByIndex(selectedTrackInd - 1)

                tracks.remove(selectedTrackInd)
                #  vsm_props.selected_track_index = selectedTrackInd - 1
                vsm_props.setSelectedTrackByIndex(selectedTrackInd - 1)
            else:
                if currentTrackInd >= selectedTrackInd:
                    vsm_props.setCurrentTrackByIndex(-1)
                tracks.remove(selectedTrackInd)

                if currentTrackInd == selectedTrackInd:
                    vsm_props.setCurrentTrackByIndex(vsm_props.selected_track_index)
                elif currentTrackInd > selectedTrackInd:
                    vsm_props.setCurrentTrackByIndex(min(currentTrackInd - 1, len(tracks) - 1))

                if selectedTrackInd < len(tracks):
                    vsm_props.setSelectedTrackByIndex(selectedTrackInd)
                else:
                    vsm_props.setSelectedTrackByIndex(selectedTrackInd - 1)

        return {"FINISHED"}


class UAS_VideoShotManager_Actions(Operator):
    """Move items up and down, add and remove"""

    bl_idname = "uas_video_shot_manager.list_action"
    bl_label = "List Actions 02"
    bl_description = "Move items up and down, add and remove"
    bl_options = {"REGISTER", "UNDO"}

    action: bpy.props.EnumProperty(items=(("UP", "Up", ""), ("DOWN", "Down", "")))

    def execute(self, context):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props
        tracks = vsm_props.getTracks()
        numTracks = len(tracks)
        currentTrackInd = vsm_props.getCurrentTrackIndex()
        selectedTrackInd = vsm_props.getSelectedTrackIndex()

        try:
            item = tracks[currentTrackInd]
        except IndexError:
            print(" *** Error in actions *** ")
            pass
        else:
            if self.action == "DOWN" and selectedTrackInd < len(tracks) - 1:
                bpy.context.window_manager.UAS_vse_render.swapChannels(
                    scene, numTracks - selectedTrackInd, numTracks - selectedTrackInd - 1
                )
                tracks.move(selectedTrackInd, selectedTrackInd + 1)
                if currentTrackInd == selectedTrackInd:
                    vsm_props.setCurrentTrackByIndex(currentTrackInd + 1)
                elif currentTrackInd == selectedTrackInd + 1:
                    vsm_props.setCurrentTrackByIndex(selectedTrackInd)
                vsm_props.setSelectedTrackByIndex(selectedTrackInd + 1)

            elif self.action == "UP" and selectedTrackInd >= 1:
                bpy.context.window_manager.UAS_vse_render.swapChannels(
                    scene, numTracks - selectedTrackInd, numTracks - selectedTrackInd + 1
                )
                tracks.move(selectedTrackInd, selectedTrackInd - 1)
                if currentTrackInd == selectedTrackInd:
                    vsm_props.setCurrentTrackByIndex(currentTrackInd - 1)
                elif currentTrackInd == selectedTrackInd - 1:
                    vsm_props.setCurrentTrackByIndex(selectedTrackInd)

                vsm_props.setSelectedTrackByIndex(selectedTrackInd - 1)

        return {"FINISHED"}


class UAS_VideoShotManager_TrackRemoveMultiple(Operator):
    bl_idname = "uas_video_shot_manager.remove_multiple_tracks"
    bl_label = "Remove Tracks"
    bl_description = "Remove the specified tracks from the list"
    bl_options = {"REGISTER", "UNDO"}

    action: bpy.props.EnumProperty(items=(("ALL", "ALL", ""), ("DISABLED", "DISABLED", "")))

    def invoke(self, context, event):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props
        currentTrackInd = vsm_props.current_track_index
        selectedTrackInd = vsm_props.getSelectedTrackIndex()

        tracks = vsm_props.getTracks()

        vsm_props.setCurrentTrackByIndex(-1)

        try:
            item = tracks[selectedTrackInd]
        except IndexError:
            pass
        else:
            if self.action == "ALL":
                vsm_props.setCurrentTrackByIndex(-1)
                i = len(tracks) - 1
                while i > -1:
                    tracks.remove(i)
                    i -= 1
                vsm_props.setSelectedTrackByIndex(-1)
            elif self.action == "DISABLED":
                i = len(tracks) - 1
                while i > -1:
                    if not tracks[i].enabled:
                        if currentTrackInd == len(tracks) - 1 and currentTrackInd == selectedTrackInd:
                            pass
                        tracks.remove(i)
                    i -= 1
                if 0 < len(tracks):  # wkip pas parfait, on devrait conserver la sel currente
                    vsm_props.setCurrentTrackByIndex(0)
                    vsm_props.setSelectedTrackByIndex(0)

        return {"FINISHED"}


class UAS_VideoShotManager_UpdateVSETrack(Operator):
    bl_idname = "uas_video_shot_manager.update_vse_track"
    bl_label = "Update VSE Track"
    bl_description = "Update VSE Track"
    bl_options = {"REGISTER", "UNDO"}

    trackName: StringProperty()

    def invoke(self, context, event):

        print("trackName: ", self.trackName)
        context.scene.UAS_vsm_props.tracks[self.trackName].regenerateTrackContent()

        return {"FINISHED"}


class UAS_VideoShotManager_ClearVSETrack(Operator):
    bl_idname = "uas_video_shot_manager.clear_vse_track"
    bl_label = "Clear VSE Track"
    bl_description = "Clear VSE Track"
    bl_options = {"REGISTER", "UNDO"}

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


class UAS_VideoShotManager_ClearAll(Operator):
    bl_idname = "uas_video_shot_manager.clear_all"
    bl_label = "Clear All"
    bl_description = "Clear all channels"
    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    def invoke(self, context, event):
        # vsm_sceneName = "VideoShotManger"
        # vsm_scene = bpy.data.scenes[vsm_sceneName]
        vsm_scene = bpy.context.scene
        vsm_scene.sequence_editor_clear()
        vsm_scene.sequence_editor_create()

        for area in bpy.context.screen.areas:
            if area.type == "SEQUENCE_EDITOR":
                area.tag_redraw()
        #     space_data = area.spaces.active
        # bpy.context.scene.sequence_editor.tag_redraw()
        return {"FINISHED"}


_classes = (
    UAS_VideoShotManager_TrackAdd,
    UAS_VideoShotManager_TrackDuplicate,
    UAS_VideoShotManager_RemoveTrack,
    UAS_VideoShotManager_Actions,
    UAS_VideoShotManager_TrackRemoveMultiple,
    UAS_VideoShotManager_UpdateVSETrack,
    UAS_VideoShotManager_ClearVSETrack,
    UAS_VideoShotManager_GoToSpecifedScene,
    # UAS_VideoShotManager_SetCurrentTrack,
    UAS_VideoShotManager_ClearAll,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
