
import bpy
from bpy.types import Operator, Menu
from bpy.props import StringProperty, BoolProperty, FloatVectorProperty, PointerProperty

from ..properties.track import UAS_VideoShotManager_Track


class UAS_VideoShotManager_TrackAdd(Operator):
    bl_idname = "uas_video_shot_manager.add_track"
    bl_label = "Add New Track"
    bl_description = (
        "Add a new track starting at the current frame"
        "\nThe new track is put after the selected track"
    )
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

    def invoke(self, context, event):
        wm = context.window_manager

        self.name = "New Track"
        ev = []
        if event.ctrl:
            ev.append("Ctrl")
        if event.shift:
            ev.append("Shift")
        if event.alt:
            ev.append("Alt")
        if event.oskey:
            ev.append("OS")
        ev.append("Click")

        self.report({'INFO'}, "+".join(ev))

        return wm.invoke_props_dialog(self)

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
        col = grid_flow.column(align=True)
        col.prop(self, "color", text="")

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

    def invoke(self, context, event):
        scene = context.scene
        print("ici")
        vsm_props = scene.UAS_vsm_props
        tracks = vsm_props.getTracks()
        currentTrackInd = vsm_props.getCurrentTrackIndex()
        selectedTrackInd = vsm_props.getSelectedTrackIndex()
        
        try:
            item = tracks[currentTrackInd]
        except IndexError:
            print(" *** Error in actions *** ")
            pass
        else:
            if self.action == "DOWN" and selectedTrackInd < len(tracks) - 1:
                tracks.move(selectedTrackInd, selectedTrackInd + 1)
                if currentTrackInd == selectedTrackInd:
                    vsm_props.setCurrentTrackByIndex(currentTrackInd + 1)
                elif currentTrackInd == selectedTrackInd + 1:
                    vsm_props.setCurrentTrackByIndex(selectedTrackInd)
                vsm_props.setSelectedTrackByIndex(selectedTrackInd + 1)

            elif self.action == "UP" and selectedTrackInd >= 1:
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
    bl_options = {"INTERNAL"}

    trackName: StringProperty()

    def invoke(self, context, event):

        print("trackName: ", self.trackName)
        context.scene.UAS_vsm_props.tracks[self.trackName].regenerateTrackContent()

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


_classes = (
    UAS_VideoShotManager_TrackAdd,
    UAS_VideoShotManager_TrackDuplicate,
    UAS_VideoShotManager_RemoveTrack,
    UAS_VideoShotManager_Actions,
    UAS_VideoShotManager_TrackRemoveMultiple,
    UAS_VideoShotManager_UpdateVSETrack,
    UAS_VideoShotManager_GoToSpecifedScene,
    # UAS_VideoShotManager_SetCurrentTrack,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
