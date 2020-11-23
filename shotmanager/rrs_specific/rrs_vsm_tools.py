from pathlib import Path

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

from shotmanager.config import config
from shotmanager.utils import utils

from shotmanager.rrs_specific.montage.montage_otio import MontageOtio


import logging

_logger = logging.getLogger(__name__)


class UAS_VideoShotManager_OT_RRS_ExportShotsFromEdit(Operator):
    bl_idname = "uas_video_shot_manager.rrs_export_shots_from_edit"
    bl_label = "Export Shots From Previz Edit..."
    bl_description = "Open the specified animatic edit video and import it with markers added at each shot"
    bl_options = {"INTERNAL"}

    overlayFile: StringProperty(default=r"C:\_UAS_ROOT\RRSpecial\00_Common\Images\RRS_EditPreviz_Overlay.png")
    editVideoFile: StringProperty(default=r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.mp4")
    otioFile: StringProperty(default=r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.xml")
    # editVideoFile: StringProperty(
    #     default=r"C:\_UAS_ROOT\RRSpecial\_Sandbox\Julien\Fixtures_Montage\PrevizAct01_Seq0060\Act01_Seq0060_Main_Take_ModifsRename.mp4"
    # )
    # otioFile: StringProperty(
    #     default=r"C:\_UAS_ROOT\RRSpecial\_Sandbox\Julien\Fixtures_Montage\PrevizAct01_Seq0060\Act01_Seq0060_Main_Take_ModifsRename.xml"
    # )
    useOverlayFrame: BoolProperty(name="Use Overlay Frame", default=False)

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        props = scene.UAS_shot_manager_props

        # if "" != self.opArgs:
        #     argsDict = json.loads(self.opArgs)
        #     print(f" argsDict: {argsDict}")
        #     print(f" argsDict['otioFile']: {argsDict['otioFile']}")
        #     if "otioFile" in argsDict:
        #         self.otioFile = argsDict["otioFile"]
        #     if "conformMode" in argsDict:
        #         self.conformMode = argsDict["conformMode"]
        #     if "mediaHaveHandles" in argsDict:
        #         self.mediaHaveHandles = argsDict["mediaHaveHandles"]
        #     if "mediaHandlesDuration" in argsDict:
        #         self.mediaHandlesDuration = argsDict["mediaHandlesDuration"]

        config.gMontageOtio = None
        if "" != self.otioFile and Path(self.otioFile).exists():
            config.gMontageOtio = MontageOtio()
            config.gMontageOtio.fillMontageInfoFromOtioFile(
                otioFile=self.otioFile, refVideoTrackInd=1, verboseInfo=False
            )

            config.gSeqEnumList = list()
            print(f"config.gMontageOtio name: {config.gMontageOtio.get_name()}")
            for i, seq in enumerate(config.gMontageOtio.sequencesList):
                print(f"- seqList: i:{i}, seq: {seq.get_name()}")
                config.gSeqEnumList.append((str(i), seq.get_name(), f"Import sequence {seq.get_name()}", i + 1))

            self.sequenceList = config.gSeqEnumList[0][0]

        wm.invoke_props_dialog(self, width=500)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        # selSeq = config.gMontageOtio.sequencesList[int(self.sequenceList)] if config.gMontageOtio is not None else None

        layout = self.layout
        row = layout.row(align=True)

        box = row.box()
        box.label(text="OTIO File")
        box.prop(self, "otioFile", text="")

        if "" == self.otioFile or not Path(self.otioFile).exists():
            row = box.row()
            row.alert = True
            row.label(text="Specified EDL file not found! - Verify your local depot")  # wkip rrs specific
            row.alert = False

        box.prop(self, "useOverlayFrame")

        if config.gMontageOtio is not None:
            numVideoTracks = len(config.gMontageOtio.timeline.video_tracks())
            numAudioTracks = len(config.gMontageOtio.timeline.audio_tracks())

            row = box.row()
            row.label(text=f"Timeline: {config.gMontageOtio.timeline.name}")
            # row = box.row()
            row.label(text=f"Video Tracks: {numVideoTracks},  Audio Tracks: {numAudioTracks}")
            row = box.row()
            row.label(
                text=f"Duration: {config.gMontageOtio.get_frame_duration()} frames at {config.gMontageOtio.get_fps()} fps"
            )
            row.separator(factor=3)
            row.label(text=f"Num. Sequences: {len(config.gMontageOtio.sequencesList)}")

            row = box.row()
            if config.gMontageOtio.get_fps() != scene.render.fps:
                row.alert = True
                row.label(text=f"!! Scene has a different framerate: {scene.render.fps} fps !!")
                row.alert = False

        #     # if config.uasDebug:
        #     #     row.operator("uas_shot_manager.montage_sequences_to_json")  # uses config.gMontageOtio

        #     subRow = box.row()
        #     subRow.enabled = selSeq is not None
        #     row.operator("uasshotmanager.compare_otio_and_current_montage").sequenceName = selSeq.get_name()

        # row = layout.row(align=True)
        # box = row.box()
        # box.separator(factor=0.2)
        # box.prop(self, "sequenceList")

        # # print("self.sequenceList: ", self.sequenceList)
        # if selSeq is not None:
        #     labelText = f"Start: {selSeq.get_frame_start()}, End: {selSeq.get_frame_end()}, Duration: {selSeq.get_frame_duration()}, Num Shots: {len(selSeq.shotsList)}"

        #     # sm_montage.printInfo()

        # else:
        #     labelText = f"Start: {-1}, End: {-1}, Num Shots: {0}"

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        if not Path(self.otioFile).exists():
            return

        vse_render = bpy.context.window_manager.UAS_vse_render

        editVideoClip = vse_render.createNewClip(scene, self.editVideoFile, 1, 0, importAudio=True)

        if self.useOverlayFrame:
            overlayClip = vse_render.createNewClip(scene, self.overlayFile, 2, 0, offsetEnd=-60000)
            scene.sequence_editor.sequences_all[overlayClip.name].blend_type = "ALPHA_OVER"

        scene.timeline_markers.clear()

        for i, seq in enumerate(config.gMontageOtio.get_sequences()):
            print(f"seq name: {seq.get_name()}")
            for j, sh in enumerate(seq.getEditShots()):
                print(
                    f"    shot name: {sh.get_name()}, starts at: {sh.get_frame_final_start()}"
                )  # , from media {sh.get_med}
                marker_name = Path(sh.get_name()).stem
                scene.timeline_markers.new(marker_name, frame=sh.get_frame_final_start())

                # last marker
                if len(config.gMontageOtio.get_sequences()) - 1 == i and len(seq.getEditShots()) - 1 == j:
                    scene.timeline_markers.new("Edit End", frame=sh.get_frame_final_end())

        vsm_props = context.scene.UAS_vsm_props
        vsm_props.updateTracksList(scene)

        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
        scene.render.ffmpeg.gopsize = 5  # keyframe interval
        scene.render.ffmpeg.audio_codec = "AAC"

        #       scene.render.filepath = output_filepath
        scene.render.use_file_extension = False

        # scene.render.resolution_percentage = 75.0

        return {"FINISHED"}


class UAS_VideoShotManager_OT_RRS_CheckSequence(Operator):
    bl_idname = "uas_video_shot_manager.rrs_check_sequence"
    bl_label = "Check Sequence..."
    bl_description = "Bla bla"
    bl_options = {"INTERNAL", "UNDO"}

    overlayFile: StringProperty(default=r"C:\_UAS_ROOT\RRSpecial\00_Common\Images\RRS_EditPreviz_Overlay.png")
    editVideoFile: StringProperty(default=r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.mp4")
    otioFile: StringProperty(default=r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.xml")
    # editVideoFile: StringProperty(
    #     default=r"C:\_UAS_ROOT\RRSpecial\_Sandbox\Julien\Fixtures_Montage\PrevizAct01_Seq0060\Act01_Seq0060_Main_Take_ModifsRename.mp4"
    # )
    # otioFile: StringProperty(
    #     default=r"C:\_UAS_ROOT\RRSpecial\_Sandbox\Julien\Fixtures_Montage\PrevizAct01_Seq0060\Act01_Seq0060_Main_Take_ModifsRename.xml"
    # )
    useOverlayFrame: BoolProperty(name="Use Overlay Frame", default=False)
    importMarkers: BoolProperty(name="Import Markers", default=True)

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        props = scene.UAS_shot_manager_props

        # if "" != self.opArgs:
        #     argsDict = json.loads(self.opArgs)
        #     print(f" argsDict: {argsDict}")
        #     print(f" argsDict['otioFile']: {argsDict['otioFile']}")
        #     if "otioFile" in argsDict:
        #         self.otioFile = argsDict["otioFile"]
        #     if "conformMode" in argsDict:
        #         self.conformMode = argsDict["conformMode"]
        #     if "mediaHaveHandles" in argsDict:
        #         self.mediaHaveHandles = argsDict["mediaHaveHandles"]
        #     if "mediaHandlesDuration" in argsDict:
        #         self.mediaHandlesDuration = argsDict["mediaHandlesDuration"]

        config.gMontageOtio = None
        if self.importMarkers and "" != self.otioFile and Path(self.otioFile).exists():
            config.gMontageOtio = MontageOtio()
            config.gMontageOtio.fillMontageInfoFromOtioFile(
                otioFile=self.otioFile, refVideoTrackInd=1, verboseInfo=False
            )

            config.gSeqEnumList = list()
            print(f"config.gMontageOtio name: {config.gMontageOtio.get_name()}")
            for i, seq in enumerate(config.gMontageOtio.sequencesList):
                print(f"- seqList: i:{i}, seq: {seq.get_name()}")
                config.gSeqEnumList.append((str(i), seq.get_name(), f"Import sequence {seq.get_name()}", i + 1))

            self.sequenceList = config.gSeqEnumList[0][0]

        if False:
            return {wm.invoke_props_dialog(self, width=500)}
            # return {"RUNNING_MODAL"}
        return self.execute(context)

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        # selSeq = config.gMontageOtio.sequencesList[int(self.sequenceList)] if config.gMontageOtio is not None else None

        layout = self.layout
        row = layout.row(align=True)

        box = row.box()
        box.label(text="OTIO File")
        box.prop(self, "otioFile", text="")

        if "" == self.otioFile or not Path(self.otioFile).exists():
            row = box.row()
            row.alert = True
            row.label(text="Specified EDL file not found! - Verify your local depot")  # wkip rrs specific
            row.alert = False

        # box.prop(self, "useOverlayFrame")
        #  box.prop(self, "importMarkers")

        if config.gMontageOtio is not None:
            numVideoTracks = len(config.gMontageOtio.timeline.video_tracks())
            numAudioTracks = len(config.gMontageOtio.timeline.audio_tracks())

            row = box.row()
            row.label(text=f"Timeline: {config.gMontageOtio.timeline.name}")
            # row = box.row()
            row.label(text=f"Video Tracks: {numVideoTracks},  Audio Tracks: {numAudioTracks}")
            row = box.row()
            row.label(
                text=f"Duration: {config.gMontageOtio.get_frame_duration()} frames at {config.gMontageOtio.get_fps()} fps"
            )
            row.separator(factor=3)
            row.label(text=f"Num. Sequences: {len(config.gMontageOtio.sequencesList)}")

            row = box.row()
            if config.gMontageOtio.get_fps() != scene.render.fps:
                row.alert = True
                row.label(text=f"!! Scene has a different framerate: {scene.render.fps} fps !!")
                row.alert = False

        #     # if config.uasDebug:
        #     #     row.operator("uas_shot_manager.montage_sequences_to_json")  # uses config.gMontageOtio

        #     subRow = box.row()
        #     subRow.enabled = selSeq is not None
        #     row.operator("uasshotmanager.compare_otio_and_current_montage").sequenceName = selSeq.get_name()

        # row = layout.row(align=True)
        # box = row.box()
        # box.separator(factor=0.2)
        # box.prop(self, "sequenceList")

        # # print("self.sequenceList: ", self.sequenceList)
        # if selSeq is not None:
        #     labelText = f"Start: {selSeq.get_frame_start()}, End: {selSeq.get_frame_end()}, Duration: {selSeq.get_frame_duration()}, Num Shots: {len(selSeq.shotsList)}"

        #     # sm_montage.printInfo()

        # else:
        #     labelText = f"Start: {-1}, End: {-1}, Num Shots: {0}"

    def execute(self, context):

        playblastInfos = dict()
        from shotmanager.scripts.rrs.rrs_playblast import rrs_playblast_to_vsm, rrs_animatic_to_vsm

        rrs_animatic_to_vsm(
            editVideoFile=self.editVideoFile, montageOtio=config.gMontageOtio, importMarkers=self.importMarkers,
        )

        # rrs_playblast_to_vsm(
        #     playblastInfo=None,
        #     editVideoFile=self.editVideoFile,
        #     montageOtio=config.gMontageOtio,
        #     importMarkers=self.importMarkers,
        # )
        return {"FINISHED"}


class UAS_VideoShotManager_GoToSequenceScene(Operator):
    bl_idname = "uas_video_shot_manager.go_to_sequence_scene"
    bl_label = "Go To Sequence Scene"
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
    UAS_VideoShotManager_OT_RRS_ExportShotsFromEdit,
    UAS_VideoShotManager_OT_RRS_CheckSequence,
    UAS_VideoShotManager_GoToSequenceScene,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
