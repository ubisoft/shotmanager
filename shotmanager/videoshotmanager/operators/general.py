import bpy
from bpy.types import Operator
from bpy.props import StringProperty, FloatProperty, IntProperty

from shotmanager.config import config
from shotmanager.utils import utils


class UAS_VideoShotManager_SelectedToActive(Operator):
    bl_idname = "uas_video_shot_manager.selected_to_active"
    bl_label = "Selected to Active"
    bl_description = "Set the first selected clip of a VSE as the active clip"
    bl_options = {"INTERNAL"}

    # @classmethod
    # def poll(cls, context):
    #     props = context.scene.UAS_shot_manager_props
    #     val = len(props.getTakes()) and len(props.get_shots())
    #     return val

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props

        return {"FINISHED"}

    # def execute(self, context):
    #     scene = context.scene
    #     props = scene.UAS_shot_manager_props
    #     return {"FINISHED"}


####################
# Markers
####################


class UAS_VideoShotManager_GoToMarker(Operator):
    bl_idname = "uas_video_shot_manager.go_to_marker"
    bl_label = "Go To Marker"
    bl_description = "Go to the specified marker"
    bl_options = {"INTERNAL"}

    goToMode: StringProperty(
        name="Go To Mode", description="Go to the specified marker. Can be FIRST, PREVIOUS, NEXT, LAST", default="NEXT"
    )

    def invoke(self, context, event):
        scene = context.scene
        prefs = context.preferences.addons["shotmanager"].preferences
        marker = None

        filterText = "" if not prefs.mnavbar_use_filter else prefs.mnavbar_filter_text

        if len(scene.timeline_markers):
            # print(self.goToMode)
            if "FIRST" == self.goToMode:
                marker = utils.getFirstMarker(scene, scene.frame_current, filter=filterText)
            elif "PREVIOUS" == self.goToMode:
                marker = utils.getMarkerBeforeFrame(scene, scene.frame_current, filter=filterText)
            elif "NEXT" == self.goToMode:
                marker = utils.getMarkerAfterFrame(scene, scene.frame_current, filter=filterText)
            elif "LAST" == self.goToMode:
                marker = utils.getLastMarker(scene, scene.frame_current, filter=filterText)

            if marker is not None:
                scene.frame_set(marker.frame)

        return {"FINISHED"}


class UAS_VideoShotManager_AddMarker(Operator):
    bl_idname = "uas_video_shot_manager.add_marker"
    bl_label = "Add / Rename Marker"
    bl_description = "Add or rename a marker at the specified frame"
    bl_options = {"INTERNAL", "UNDO"}

    markerName: StringProperty(name="New Marker Name", default="")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        utils.addMarkerAtFrame(context.scene, context.scene.frame_current, self.markerName)
        return {"FINISHED"}


class UAS_VideoShotManager_DeleteMarker(Operator):
    bl_idname = "uas_video_shot_manager.delete_marker"
    bl_label = "Delete Marker"
    bl_description = "Delete the marker at the specified frame"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        utils.deleteMarkerAtFrame(context.scene, context.scene.frame_current)
        return {"FINISHED"}


####################
# Track specific Select and Zoom
####################


class UAS_VideoShotManager_TrackSelectAndZoomView(Operator):
    bl_idname = "uas_video_shot_manager.track_select_and_zoom_view"
    bl_label = "Select and Zoom on Track Content"
    bl_description = "Select the track content and change zoom value to make all the track clips fit into the view.\n"
    bl_options = {"INTERNAL"}

    # Can be "TRACKCLIPS"
    actionMode: StringProperty(default="TRACKCLIPS")
    trackIndex: IntProperty(default=-1)

    @classmethod
    def description(self, context, properties):
        descr = "_"
        if "TRACKCLIPS" == properties.actionMode:
            descr = "Select the track content and change zoom value to make all the track clips fit into the view"
        return descr

    def execute(self, context):
        scene = context.scene
        vse_render = bpy.context.window_manager.UAS_vse_render

        start = scene.frame_preview_start if scene.use_preview_range else scene.frame_start
        end = scene.frame_preview_end if scene.use_preview_range else scene.frame_end
        activeClip = scene.sequence_editor.active_strip
        scene.sequence_editor.active_strip = None

        if "TRACKCLIPS" == self.actionMode:
            # bpy.ops.sequencer.select_all(action="DESELECT")
            vse_render.selectChannelClips(scene, self.trackIndex, mode="CLEARANDSELECT")
            bpy.ops.sequencer.view_selected()

        bpy.context.scene.sequence_editor.active_strip = activeClip
        return {"FINISHED"}


class UAS_VideoShotManager_SelectTrackFromClipSelection(Operator):
    bl_idname = "uas_video_shot_manager.select_track_from_clip_selection"
    bl_label = "Select Track"
    bl_description = (
        "Select the track corresponding to the last clip of the selection (usually the active one),\n"
        "or the active clip if the selection is empty."
    )
    bl_options = {"INTERNAL"}

    def execute(self, context):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props
        if len(context.selected_sequences):
            if scene.sequence_editor.active_strip is not None and scene.sequence_editor.active_strip.select:
                vsm_props.setSelectedTrackByIndex(scene.sequence_editor.active_strip.channel)
            else:
                vsm_props.setSelectedTrackByIndex(context.selected_sequences[0].channel)
        elif scene.sequence_editor.active_strip is not None:
            vsm_props.setSelectedTrackByIndex(scene.sequence_editor.active_strip.channel)
        return {"FINISHED"}


####################
# Zoom
####################


class UAS_VideoShotManager_ZoomView(Operator):
    bl_idname = "uas_video_shot_manager.zoom_view"
    bl_label = "Zoom VSE View"
    bl_description = "Change VSE zoom value to make all the clips fit into the view.\nCurrent selection and time range are not modified"
    bl_options = {"INTERNAL"}

    # Can be "TIMERANGE", "ALLCLIPS", "SELECTEDCLIPS", "TOCURRENTFRAME", "TRACKCLIPS"
    zoomMode: StringProperty(default="TIMERANGE")
    trackIndex: IntProperty(default=-1)

    @classmethod
    def description(self, context, properties):
        descr = "_"
        if "TIMERANGE" == properties.zoomMode:
            descr = "Set zoom to frame time range"
        elif "ALLCLIPS" == properties.zoomMode:
            descr = "Set zoom to frame all clips"
        elif "SELECTEDCLIPS" == properties.zoomMode:
            descr = "Set zoom to frame selected clips"
        elif "TOCURRENTFRAME" == properties.zoomMode:
            descr = "Center view to current frame"
        elif "TRACKCLIPS" == properties.zoomMode:
            descr = "Set zoom to frame clips of the selected track"
        return descr

    def execute(self, context):
        """
            Dev notes:
            - view_all / vie_all_preview: zoom on the max range beteen time range and all clips
            - selection nor time range are modified
        """
        # bpy.ops.sequencer.view_selected()
        # bpy.ops.sequencer.view_all_preview()
        scene = context.scene
        vse_render = bpy.context.window_manager.UAS_vse_render

        start = scene.frame_preview_start if scene.use_preview_range else scene.frame_start
        end = scene.frame_preview_end if scene.use_preview_range else scene.frame_end
        activeClip = scene.sequence_editor.active_strip
        scene.sequence_editor.active_strip = None

        if "TOCURRENTFRAME" == self.zoomMode:
            bpy.ops.sequencer.view_frame()

        elif "TIMERANGE" == self.zoomMode:
            # doesn't work directly cause they include the active clip !!!
            # bpy.ops.sequencer.view_all_preview()
            # bpy.ops.sequencer.view_all()
            # if context.scene.use_preview_range:
            #     bpy.ops.sequencer.view_all_preview()
            # else:
            #     bpy.ops.sequencer.view_all()

            # backup and clear selection
            selArr = []
            numSel = 0
            for clip in scene.sequence_editor.sequences:
                selArr.append(clip.select)
                if clip.select:
                    numSel += 1

            #     bpy.ops.sequencer.select_all(action="SELECT")
            bpy.ops.sequencer.select_all(action="DESELECT")
            #     bpy.context.scene.sequence_editor.active_strip = None

            vse_render.changeClipsChannel(scene, 1, 32)

            tmpClip = scene.sequence_editor.sequences.new_effect(
                "_tmp_clip-to_delete", "COLOR", 1, frame_start=start, frame_end=end
            )
            #  print("tmpClip: ", tmpClip)
            tmpClip.select = True
            #     bpy.ops.sequencer.select_all(action="DESELECT")
            #     tmpClip.select = True

            bpy.ops.sequencer.view_selected()
            scene.sequence_editor.sequences.remove(tmpClip)
            vse_render.changeClipsChannel(scene, 32, 1)

            # restore selection
            for i, clip in enumerate(scene.sequence_editor.sequences):
                clip.select = selArr[i]

        elif "SELECTEDCLIPS" == self.zoomMode:
            bpy.ops.sequencer.view_selected()

        elif "ALLCLIPS" == self.zoomMode:
            # by default view_all is the max range between all clips and the time range. We modify
            # it so that only the clips are framed

            bpy.ops.sequencer.select_all(action="SELECT")
            if context.scene.use_preview_range:
                #   bpy.ops.sequencer.set_range_to_strips(preview=True)
                bpy.ops.sequencer.set_range_to_strips(preview=True)
                bpy.ops.sequencer.view_all_preview()
                scene.frame_preview_start = start
                scene.frame_preview_end = end
            else:
                #  bpy.ops.sequencer.set_range_to_strips(preview=False)
                bpy.ops.sequencer.set_range_to_strips(preview=False)
                bpy.ops.sequencer.view_all()
                scene.frame_start = start
                scene.frame_end = end

        elif "TRACKCLIPS" == self.zoomMode:
            # backup and clear selection
            selArr = []
            numSel = 0
            for clip in scene.sequence_editor.sequences:
                selArr.append(clip.select)
                if clip.select:
                    numSel += 1

            bpy.ops.sequencer.select_all(action="DESELECT")

            # select only track clip
            for clip in scene.sequence_editor.sequences:
                clip.select = self.trackIndex == clip.channel
            bpy.ops.sequencer.view_selected()

            # restore selection
            for i, clip in enumerate(scene.sequence_editor.sequences):
                clip.select = selArr[i]

        # for test only
        # filedit = bpy.context.window_manager.UAS_vse_render.getMediaList(context.scene, listVideo=False, listAudio=True)
        # print(f"filedit: \n{filedit}")

        # if context.scene.use_preview_range:
        #     bpy.ops.sequencer.set_range_to_strips(preview=True)
        # else:
        #     bpy.ops.sequencer.set_range_to_strips(preview=False)

        bpy.context.scene.sequence_editor.active_strip = activeClip
        return {"FINISHED"}


####################
# Time range framing
####################


class UAS_VideoShotManager_FrameTimeRange(Operator):
    bl_idname = "uas_video_shot_manager.frame_time_range"
    bl_label = "Frame Time Range"
    bl_description = "Change the VSE zoom value to fit the scene time range"
    bl_options = {"INTERNAL", "UNDO"}

    spacerPercent: FloatProperty(
        description="Range of time, in percentage, before and after the time range", min=0.0, max=40.0, default=5
    )

    # Can be "TIMERANGE", "ALLCLIPS", "SELECTEDCLIPS", "TOCURRENTFRAME"
    frameMode: StringProperty(default="TIMERANGE")

    @classmethod
    def description(self, context, properties):
        descr = "_"
        if "SELECTEDCLIPS" == properties.frameMode:
            descr = "Set time range to frame selected clips"
        elif "ALLCLIPS" == properties.frameMode:
            descr = "Set time range to frame all clips"
        return descr

    def execute(self, context):
        scene = context.scene

        start = scene.frame_preview_start if context.scene.use_preview_range else scene.frame_start
        end = scene.frame_preview_end if context.scene.use_preview_range else scene.frame_end
        activeClip = bpy.context.scene.sequence_editor.active_strip
        # print(f"Active Clip: {activeClip.name}")
        bpy.context.scene.sequence_editor.active_strip = None

        # for area in bpy.context.screen.areas:
        #     if area.type == "SEQUENCE_EDITOR":
        #         area.tag_redraw()

        # print(f"Active Clip 2: {bpy.context.scene.sequence_editor.active_strip}")

        # backup and clear selection
        selArr = []
        numSel = 0
        for clip in scene.sequence_editor.sequences:
            selArr.append(clip.select)
            if clip.select:
                numSel += 1

        if "SELECTEDCLIPS" == self.frameMode:
            # uncomment this to be able to frame the active clip
            # if 0 == numSel and activeClip is not None:
            #     activeClip.select = True
            if context.scene.use_preview_range:
                bpy.ops.sequencer.set_range_to_strips(preview=True)
            else:
                bpy.ops.sequencer.set_range_to_strips(preview=False)

        elif "ALLCLIPS" == self.frameMode:
            # by default view_all is the max range between all clips and the time range. We modify
            # it so that only the clips are framed

            bpy.ops.sequencer.select_all(action="SELECT")
            if context.scene.use_preview_range:
                bpy.ops.sequencer.set_range_to_strips(preview=True)
            #    bpy.ops.sequencer.view_all_preview()
            else:
                bpy.ops.sequencer.set_range_to_strips(preview=False)
            #    bpy.ops.sequencer.view_all()

            bpy.ops.sequencer.select_all(action="DESELECT")

            # restore selection
            for i, clip in enumerate(scene.sequence_editor.sequences):
                clip.select = selArr[i]

        # # bpy.ops.sequencer.view_selected()
        # # bpy.ops.sequencer.view_all_preview()

        # # bpy.ops.sequencer.view_zoom_ratio(ratio=1.0)

        # if scene.use_preview_range:
        #     beforeStart = scene.frame_preview_start
        #     beforeEnd = scene.frame_preview_end
        #     framesToAdd = int((beforeEnd - beforeStart + 1) * self.spacerPercent)
        #     scene.frame_preview_start = beforeStart - framesToAdd
        #     scene.frame_preview_end = beforeEnd + framesToAdd
        #     bpy.ops.sequencer.view_all_preview()
        #     scene.frame_preview_start = beforeStart
        #     scene.frame_preview_end = beforeEnd

        # else:
        #     beforeStart = scene.frame_start
        #     beforeEnd = scene.frame_end
        #     framesToAdd = 0  # int((beforeEnd - beforeStart + 1) * self.spacerPercent)
        #     scene.frame_start = beforeStart - framesToAdd
        #     scene.frame_end = beforeEnd + framesToAdd
        #     bpy.ops.sequencer.view_all()
        #     # bpy.ops.sequencer.view_selected()
        #     scene.frame_start = beforeStart
        #     scene.frame_end = beforeEnd

        # bpy.ops.time.view_all()

        bpy.context.scene.sequence_editor.active_strip = activeClip
        return {"FINISHED"}


_classes = (
    UAS_VideoShotManager_SelectedToActive,
    UAS_VideoShotManager_GoToMarker,
    UAS_VideoShotManager_AddMarker,
    UAS_VideoShotManager_DeleteMarker,
    UAS_VideoShotManager_TrackSelectAndZoomView,
    UAS_VideoShotManager_SelectTrackFromClipSelection,
    UAS_VideoShotManager_ZoomView,
    UAS_VideoShotManager_FrameTimeRange,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
