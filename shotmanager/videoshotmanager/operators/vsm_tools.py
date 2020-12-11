import os
from pathlib import Path
from stat import S_IMODE, S_IWRITE

import bpy
from bpy.types import Operator, Menu
from bpy.props import StringProperty, BoolProperty, IntProperty

import opentimelineio
from shotmanager.otio import otio_wrapper as ow
from shotmanager.otio.imports import importToVSE

from shotmanager.rrs_specific.montage.montage_otio import MontageOtio

from shotmanager.utils import utils

from shotmanager.config import config

import logging

_logger = logging.getLogger(__name__)


class UAS_VideoShotManager_OT_Import_Edit_From_OTIO(Operator):
    bl_idname = "uas_video_shot_manager.importeditfromotio"
    bl_label = "Import Edit from EDL file"
    bl_description = "Open EDL file (Final Cut XML, OTIO...) to import its content"
    bl_options = {"INTERNAL", "UNDO"}

    otioFile: StringProperty()

    offsetTime: BoolProperty(
        name="Offset Time",
        description="Offset the imported part of edit to start at the specified time",
        default=False,
    )

    importAtFrame: IntProperty(
        name="Import at Frame",
        description="Make the imported edit start at the specified frame",
        soft_min=0,
        min=0,
        default=0,
    )

    useEditTimeRange: BoolProperty(
        name="Edit Time Range", description="Change the scene time range to match the edit one", default=True,
    )
    useEditFramerate: BoolProperty(
        name="Edit Framerate", description="Change the scene framerate to match the edit one", default=True,
    )
    useEditResolution: BoolProperty(
        name="Edit Resolution", description="Change the scene resolution to match the edit one", default=True,
    )

    importTimeRange: BoolProperty(
        name="Import Time Range", description="Part of the edit to be imported", default=False,
    )
    range_start: IntProperty(
        name="Range Start", description="Range Start", default=0,
    )
    range_end: IntProperty(
        name="Range End", description="Range End", default=250,
    )

    importVideoInVSE: BoolProperty(
        name="Import Video In VSE",
        description="Import video clips directly into the VSE of the current scene",
        default=True,
    )

    importAudioInVSE: BoolProperty(
        name="Import Sound In VSE",
        description="Import sound clips directly into the VSE of the current scene",
        default=True,
    )

    def invoke(self, context, event):
        wm = context.window_manager

        config.gMontageOtio = None
        if "" != self.otioFile and Path(self.otioFile).exists():
            config.gMontageOtio = MontageOtio()
            config.gMontageOtio.fillMontageInfoFromOtioFile(otioFile=self.otioFile, verboseInfo=True)

            # timeline = ow.get_timeline_from_file(self.otioFile)
            # if timeline is not None:
            #     config.gMontageOtio = otc.OtioTimeline()
            #     config.gMontageOtio.otioFile = self.otioFile
            #     config.gMontageOtio.timeline = timeline

        wm.invoke_props_dialog(self, width=500)
        #    res = bpy.ops.uasotio.openfilebrowser("INVOKE_DEFAULT")
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="OTIO File")
        box.prop(self, "otioFile", text="")

        if config.gMontageOtio is not None:
            timeline = config.gMontageOtio.timeline
            time = timeline.duration()
            rate = int(time.rate)

            if rate != context.scene.render.fps:
                box.alert = True
                box.label(
                    text="!!! Scene fps is " + str(context.scene.render.fps) + ", imported edit is " + str(rate) + "!!"
                )
                box.alert = False

        row = box.row(align=True)
        row.operator("uas_video_shot_manager.print_montage_info")
        row.separator()

        box = layout.box()
        row = box.row(align=True)
        row.prop(self, "useEditTimeRange")
        row.prop(self, "useEditFramerate")
        row.prop(self, "useEditResolution")

        box = layout.box()
        row = box.row(align=True)
        row.prop(self, "importTimeRange")
        subrow = row.row(align=False)
        subrow.enabled = self.importTimeRange
        subrow.prop(self, "range_start")
        subrow.prop(self, "range_end")

        row = box.row(align=True)
        row.prop(self, "offsetTime")
        subrow = row.row(align=True)
        subrow.enabled = self.offsetTime
        subrow.prop(self, "importAtFrame")

        layout.label(text="Video:")
        row = layout.row(align=True)
        box = row.box()
        row = box.row()
        row.prop(self, "importVideoInVSE")

        layout.label(text="Sound:")
        row = layout.row(align=True)
        box = row.box()
        row = box.row()
        row.prop(self, "importAudioInVSE")

        layout.separator()

    def execute(self, context):

        if config.gMontageOtio is None:
            return

        scene = context.scene

        # creation VSE si existe pas
        vse = utils.getSceneVSE(scene.name)
        # bpy.context.space_data.show_seconds = False
        bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]
        # bpy.context.window.space_data.show_seconds = False

        # configure scene
        if self.useEditTimeRange:
            # print(f" 02: config.gMontageOtio.seqCharacteristics: {config.gMontageOtio.seqCharacteristics}")
            scene.frame_start = 0
            # if config.gMontageOtio.characteristics is None:
            #     print(f" *** config.gMontageOtio.characteristics is None - EDL Edit duration cannot be set *** ")
            #     context.scene.frame_end = 40000
            # else:
            #     context.scene.frame_end = config.gMontageOtio.characteristics["duration"]
            scene.frame_end = config.gMontageOtio.get_frame_duration() - 1

        if self.useEditFramerate:
            # if config.gMontageOtio.characteristics is None:
            #     print(f" *** config.gMontageOtio.characteristics is None - EDL Edit framerate cannot be set *** ")
            # else:
            #     context.scene.render.fps = config.gMontageOtio.characteristics["rate"]["timebase"]
            scene.render.fps = config.gMontageOtio.get_fps()

        if self.useEditResolution:
            if config.gMontageOtio._characteristics is None:
                print(f" *** config.gMontageOtio._characteristics is None - EDL Edit resolution cannot be set *** ")
            else:
                characts = config.gMontageOtio.get_montage_characteristics()
                if "resolution_x" in characts:
                    context.scene.render.resolution_x = characts["resolution_x"]
                if "resolution_y" in characts:
                    context.scene.render.resolution_y = characts["resolution_y"]

        timeRange = None
        if self.importTimeRange:
            timeRange = [self.range_start, self.range_end]

        offsetFrameNumber = 0
        if self.offsetTime:
            if timeRange is None:
                offsetFrameNumber = self.importAtFrame
            else:
                offsetFrameNumber = self.importAtFrame - timeRange[0]

        # print(f"Import Otio File: {config.gMontageOtio.otioFile}, num clips: {len(clipList)}")
        if timeRange is not None:
            print(f"   from {timeRange[0]} to {timeRange[1]}")

        trackType = "ALL"
        if self.importVideoInVSE and not self.importAudioInVSE:
            trackType = "VIDEO"
        elif not self.importVideoInVSE and self.importAudioInVSE:
            trackType = "AUDIO"

        importToVSE(
            config.gMontageOtio.timeline,
            vse,
            timeRange=timeRange,
            offsetFrameNumber=offsetFrameNumber,
            track_type=trackType,
        )

        #    context.scene.UAS_vsm_props.updateTracksList(context.scene)

        return {"FINISHED"}


class UAS_VideoShotManager_OT_Parse_Edit_From_OTIO(Operator):
    bl_idname = "uas_video_shot_manager.parseeditfromotio"
    bl_label = "Parse Edit from EDL file"
    bl_description = "Open EDL file (Final Cut XML, OTIO...) to import its content"
    bl_options = {"INTERNAL"}

    otioFile: StringProperty()

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, width=500)
        #    res = bpy.ops.uasotio.openfilebrowser("INVOKE_DEFAULT")
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)

        box = row.box()
        box.label(text="OTIO File")
        box.prop(self, "otioFile", text="")

        from pathlib import Path

        if "" != self.otioFile and Path(self.otioFile).exists():
            timeline = opentimelineio.adapters.read_from_file(self.otioFile)
            time = timeline.duration()
            rate = int(time.rate)

            if rate != context.scene.render.fps:
                box.alert = True
                box.label(
                    text="!!! Scene fps is " + str(context.scene.render.fps) + ", imported edit is " + str(rate) + "!!"
                )
                box.alert = False

        # layout.label(text="Video:")
        # row = layout.row(align=True)
        # box = row.box()
        # row = box.row()
        # row.prop(self, "importVideoInVSE")

        layout.separator()

    def execute(self, context):
        ow.parseOtioFile(self.otioFile)
        return {"FINISHED"}


class UAS_VideoShotManager_OT_PrintMontageInfo(Operator):
    bl_idname = "uas_video_shot_manager.print_montage_info"
    bl_label = "Print Montage Info"
    bl_description = "Print montage information in the console"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        config.gMontageOtio.printInfo()

        # sm_montage = MontageShotManager()
        # sm_montage.initialize(scene, props.getCurrentTake())

        # props.printInfo()
        # dictMontage = dict()
        # dictMontage["sequence"] = context.scene.name
        # props.getInfoAsDictionnary(dictMontage=dictMontage)

        # import json

        # print(json.dumps(dictMontage, indent=4))

        return {"FINISHED"}


class UAS_VideoShotManager_OT_ExportContentbetweenMarkers(Operator):
    bl_idname = "uas_video_shot_manager.export_content_between_markers"
    bl_label = "Batch Export Content Between Markers..."
    bl_description = "Export all the segments defined by the markers as separated videos"
    bl_options = {"INTERNAL"}

    outputDir: StringProperty(default=r"-- Copy Output Directory Here ---")

    start: IntProperty(name="Start", default=10)
    end: IntProperty(name="end", default=150)

    exportAsVideoFiles: BoolProperty(name="Export as Video Files", default=True)
    exportVideosWithSound: BoolProperty(name="With Sound", default=True)
    exportAsAudioFiles: BoolProperty(name="Export as Audio Files", default=True)
    exportEditSoundtracks: BoolProperty(name="Export Edit Sound Tracks", default=True)

    def invoke(self, context, event):

        self.start = context.scene.frame_start
        self.end = context.scene.frame_end

        wm = context.window_manager
        wm.invoke_props_dialog(self, width=500)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "outputDir")
        row = layout.row()
        row.prop(self, "start")
        row.prop(self, "end")
        row = layout.row()
        row.prop(self, "exportAsVideoFiles")
        row.prop(self, "exportVideosWithSound")
        row = layout.row()
        row.prop(self, "exportAsAudioFiles")
        row = layout.row()
        row.prop(self, "exportEditSoundtracks")

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        vse_render = bpy.context.window_manager.UAS_vse_render

        if not Path(self.outputDir).exists():
            print(f" *** Cannot export VSE content, path does not exist: {self.outputDir}")
            return {"FINISHED"}

        ######
        # Export videos

        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
        scene.render.ffmpeg.gopsize = 5  # keyframe interval
        scene.render.ffmpeg.audio_codec = "AAC" if self.exportVideosWithSound else "NONE"

        #       scene.render.filepath = output_filepath
        scene.render.use_file_extension = False

        markers = utils.sortMarkers(scene.timeline_markers)

        # print(f"markers: {markers}")
        if self.exportAsVideoFiles:
            print(f"\n * Exporting video files:")
            for i, mrk in enumerate(markers):
                if self.start <= markers[i].frame <= self.end:
                    if i < len(markers) - 1:
                        if self.start <= markers[i + 1].frame <= self.end:
                            #    print(f"{i} Marker name: {mrk.name}")
                            scene.frame_start = markers[i].frame
                            scene.frame_end = markers[i + 1].frame - 1
                            scene.render.filepath = self.outputDir + "/" + mrk.name + ".mp4"
                            bpy.ops.render.opengl(animation=True, sequencer=True)

        ######
        # Export audios

        if self.exportAsAudioFiles:
            for i, mrk in enumerate(markers):
                if self.start <= markers[i].frame <= self.end:
                    #   print(f"{i} if 01 - Marker name: {mrk.name}")
                    if i < len(markers) - 1:
                        #       print(f"{i} if 02 - Marker name: {mrk.name}, {self.start}, {markers[i + 1].frame}, {self.end}")
                        if self.start <= markers[i + 1].frame <= self.end:
                            #    print(f"{i} Marker name: {mrk.name}")
                            scene.frame_start = markers[i].frame
                            scene.frame_end = markers[i + 1].frame - 1
                            # https://blenderartists.org/t/scripterror-mixdown-operstor/548056/4
                            # bpy.ops.sound.mixdown(filepath=str(audioFilePath), relative_path=False, container="WAV", codec="PCM", bitrate=192)
                            audioFilePath = self.outputDir + "/" + mrk.name + ".mp3"
                            bpy.ops.sound.mixdown(
                                filepath=audioFilePath, relative_path=False, container="MP3", codec="MP3"
                            )

        ######
        # Export Sound Tracks

        if self.exportEditSoundtracks:
            vsm_props = context.scene.UAS_vsm_props
            tracks = vsm_props.getTracks()
            for t in tracks:
                t.enabled = False

            for t in tracks:
                if (
                    t.get_name() == "SFX"
                    or t.get_name() == "Rabbids"
                    or t.get_name() == "Humans_Rabbids"
                    or t.get_name() == "Humans"
                ):
                    t.enabled = True

                    # print(f" Len markers: {len(markers)}")
                    for i, mrk in enumerate(markers):
                        if self.start <= markers[i].frame <= self.end:
                            #       print(f"{i} if 01 - Marker name: {mrk.name}")
                            if i < len(markers) - 1:
                                # print(
                                #     f"{i} if 02 - Marker name: {mrk.name}, {self.start}, {markers[i + 1].frame}, {self.end}"
                                # )
                                if self.start <= markers[i + 1].frame <= self.end + 1:
                                    #   print(f"{i} Marker 3 name: {mrk.name}")
                                    scene.frame_start = markers[i].frame
                                    scene.frame_end = markers[i + 1].frame - 1
                                    # https://blenderartists.org/t/scripterror-mixdown-operstor/548056/4
                                    # bpy.ops.sound.mixdown(filepath=str(audioFilePath), relative_path=False, container="WAV", codec="PCM", bitrate=192)
                                    seqName = mrk.name[0:13]
                                    audioFile = f"C:/_UAS_ROOT/RRSpecial/05_Acts/Act01/{seqName}/_Exports/Sound/{mrk.name}_{t.get_name()}.wav"

                                    audioFilePath = Path(audioFile).parent
                                    if Path(audioFilePath).exists():
                                        # print(f"Path Ok: {audioFilePath}")
                                        pass
                                        if Path(audioFile).exists():
                                            stat = Path(audioFile).stat()
                                            #   print(f"Blender file Stats: {stat.st_mode}")
                                            fileIsReadOnly = S_IMODE(stat.st_mode) & S_IWRITE == 0
                                            if fileIsReadOnly:
                                                os.chmod(audioFile, 0o666)

                                    else:
                                        # print(f"Path not found: {audioFilePath}")
                                        try:
                                            os.makedirs(audioFilePath)
                                        except OSError:
                                            print("Creation of the directory %s failed" % audioFilePath)
                                        else:
                                            # print("Successfully created the directory %s" % audioFilePath)
                                            pass

                                    print(f"Exporting audioFile: {audioFile}")

                                    bpy.ops.sound.mixdown(
                                        filepath=audioFile, relative_path=False, container="WAV",
                                    )

                    print("")
                    t.enabled = False

        context.scene.frame_start = self.start
        context.scene.frame_end = self.end
        print(f"\n * Export content between markers done to {self.outputDir}\n")

        return {"FINISHED"}


#################
# general tools
#################

# class UAS_MT_VideoShotManager_Prefs_MainMenu(Menu):
#     bl_idname = "UAS_MT_Video_Shot_Manager_prefs_mainmenu"


class UAS_MT_VideoShotManager_Clear_Menu(Menu):
    bl_idname = "UAS_MT_Video_Shot_Manager_clear_menu"
    bl_label = "Clear Tools"
    bl_description = "Clear Tools"

    def draw(self, context):

        # Copy menu entries[ ---
        layout = self.layout
        row = layout.row(align=True)

        # row.label(text="Tools for Tracks:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_video_shot_manager.remove_multiple_tracks", text="Remove Disabled Tracks").action = "DISABLED"

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_video_shot_manager.remove_multiple_tracks", text="Remove All Tracks").action = "ALL"

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_video_shot_manager.clear_clips", text="Remove All Clips")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_video_shot_manager.clear_markers", text="Remove All Markers")


#        layout.separator()


class UAS_VideoShotManager_OT_ClearAll(Operator):
    bl_idname = "uas_video_shot_manager.clear_all"
    bl_label = "Clear All"
    bl_description = "Clear all channels"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        vsm_props = context.scene.UAS_vsm_props
        # print("Clear all ici")
        bpy.ops.uas_video_shot_manager.remove_multiple_tracks(action="ALL")
        bpy.ops.uas_video_shot_manager.clear_clips()
        bpy.ops.uas_video_shot_manager.clear_markers()

        vsm_props.updateTracksList(context.scene)

        return {"FINISHED"}


class UAS_VideoShotManager_OT_ClearMarkers(Operator):
    bl_idname = "uas_video_shot_manager.clear_markers"
    bl_label = "Clear Markers"
    bl_description = "Clear all markers"
    bl_options = {"INTERNAL", "UNDO"}

    def execute(self, context):
        context.scene.timeline_markers.clear()
        return {"FINISHED"}


# class UAS_VideoShotManager_OT_ClearTracks(Operator):
#     bl_idname = "uas_video_shot_manager.clear_tracks"
#     bl_label = "Clear Clips"
#     bl_description = "Clear all tracks"
#     bl_options = {"INTERNAL", "UNDO"}

#     def invoke(self, context, event):
#         # vsm_sceneName = "VideoShotManager"
#         # vsm_scene = bpy.data.scenes[vsm_sceneName]
#         vsm_scene = bpy.context.scene
#         vsm_scene.sequence_editor_clear()
#         vsm_scene.sequence_editor_create()

#         for area in bpy.context.screen.areas:
#             if area.type == "SEQUENCE_EDITOR":
#                 area.tag_redraw()
#         #     space_data = area.spaces.active
#         # bpy.context.scene.sequence_editor.tag_redraw()
#         return {"FINISHED"}


class UAS_VideoShotManager_OT_ClearClips(Operator):
    bl_idname = "uas_video_shot_manager.clear_clips"
    bl_label = "Clear Clips"
    bl_description = "Clear all clips"
    bl_options = {"INTERNAL", "UNDO"}

    def execute(self, context):
        vsm_scene = bpy.context.scene
        vsm_scene.sequence_editor_clear()
        vsm_scene.sequence_editor_create()

        for area in bpy.context.screen.areas:
            if area.type == "SEQUENCE_EDITOR":
                area.tag_redraw()

        return {"FINISHED"}


class UAS_VideoShotManager_OT_GoToScene(Operator):
    bl_idname = "uas_video_shot_manager.go_to_scene"
    bl_label = "Go To Specified Scene"
    bl_description = "Go to specified scene"
    bl_options = {"INTERNAL"}

    sceneName: StringProperty()

    def invoke(self, context, event):

        # print("trackName: ", self.trackName)
        # Make track scene the current one
        # bpy.context.window.scene = context.scene.UAS_vsm_props.tracks[self.trackName].shotManagerScene
        bpy.context.window.scene = bpy.data.scenes[self.sceneName]
        bpy.context.window.workspace = bpy.data.workspaces["Layout"]

        return {"FINISHED"}


_classes = (
    UAS_VideoShotManager_OT_Import_Edit_From_OTIO,
    UAS_VideoShotManager_OT_Parse_Edit_From_OTIO,
    UAS_VideoShotManager_OT_PrintMontageInfo,
    UAS_VideoShotManager_OT_ExportContentbetweenMarkers,
    UAS_MT_VideoShotManager_Clear_Menu,
    UAS_VideoShotManager_OT_ClearAll,
    UAS_VideoShotManager_OT_ClearMarkers,
    # UAS_VideoShotManager_OT_ClearTracks,
    UAS_VideoShotManager_OT_ClearClips,
    UAS_VideoShotManager_OT_GoToScene,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
