from pathlib import Path

import bpy
from bpy.types import Operator, Panel
from bpy.props import StringProperty, BoolProperty, EnumProperty

from shotmanager.config import config
from shotmanager.utils import utils

from shotmanager.rrs_specific.montage.montage_otio import MontageOtio


import logging

_logger = logging.getLogger(__name__)


######
# RRS VSE panel #
######


class UAS_PT_RRSVSMTools(Panel):
    bl_idname = "UAS_PT_RRSVSMTools"
    bl_label = "RR Special VSE Tools"
    bl_description = "RRS Options"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "UAS Video Shot Man"
    #  bl_parent_id = "UAS_PT_Video_Shot_Manager"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        val = not (
            scene.name.startswith("Act01_Seq")
            or scene.name.startswith("Act02_Seq")
            or scene.name.startswith("Act03_Seq")
        )
        return val

    def draw(self, context):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props
        layout = self.layout

        #########################################
        # RRS Specific
        #########################################

        layout.separator(factor=1)

        # wkip conditions dégueu
        if not (
            scene.name.startswith("Act01_Seq")
            or scene.name.startswith("Act02_Seq")
            or scene.name.startswith("Act03_Seq")
        ):
            layout.label(text="RR-Special: Visual Check:")
            box = layout.box()
            box.separator(factor=0.2)
            row = box.row()
            row.scale_y = 1
            row.operator("uas_video_shot_manager.rrs_check_sequence", text="Import Previz Montage Act 01")

            if (
                bpy.data.scenes[0].name.startswith("Act01_Seq")
                or bpy.data.scenes[0].name.startswith("Act02_Seq")
                or bpy.data.scenes[0].name.startswith("Act03_Seq")
            ) and bpy.data.scenes[0] is not scene:
                box.separator(factor=0.1)
                row = box.row()
                row.operator(
                    "uas_video_shot_manager.import_published_sequence"
                )  # , text="Import Previz Montage Act 01")
                layout.separator()
                row = layout.row()
                row.scale_y = 1.4
                row.operator(
                    "uas_video_shot_manager.go_to_sequence_scene", text="Go to Sequence Scene", icon="SCENE_DATA"
                ).sceneName = bpy.data.scenes[0].name

            box.separator(factor=0.2)

        layout.separator(factor=1)

        layout.label(text="For Montages and Confos:")
        box = layout.box()
        row = box.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator(
            "uas_video_shot_manager.export_content_between_markers", text="   Batch Export Content Between Markers..."
        ).outputDir = r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\_OutputShots"

        layout.separator(factor=1)


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


def list_sequences_from_markers(self, context):
    res = config.gSeqEnumList
    # res = list()
    nothingList = list()
    nothingList.append(("NO_SEQ", "No Sequence Found", "No sequence found in the specified EDL file", 0))

    # seqList = getSequenceListFromOtioTimeline(config.gMontageOtio)
    # for i, item in enumerate(seqList):
    #     res.append((item, item, "My seq", i + 1))

    # res = getSequenceListFromOtio()
    # res.append(("NEW_CAMERA", "New Camera", "Create new camera", 0))
    # for i, cam in enumerate([c for c in context.scene.objects if c.type == "CAMERA"]):
    #     res.append(
    #         (cam.name, cam.name, 'Use the exising scene camera named "' + cam.name + '"\nfor the new shot', i + 1)
    #     )

    if res is None or 0 == len(res):
        res = nothingList
    return res


class UAS_VideoShotManager_ImportPublishedSequence(Operator):
    bl_idname = "uas_video_shot_manager.import_published_sequence"
    bl_label = "Import a Published Sequence"
    bl_description = "Import a specified sequence generated by the Publish"
    bl_options = {"INTERNAL", "UNDO"}

    sequenceList: EnumProperty(
        name="Sequence",
        description="Sequences available from the markers list",
        # items=(("NO_SEQ", "No Sequence Found", ""),),
        items=(list_sequences_from_markers),
    )

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        props = scene.UAS_shot_manager_props

        return wm.invoke_props_dialog(self, width=500)

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        # selSeq = (
        #     config.gMontageOtio.sequencesList[int(self.sequenceList)]
        #     if config.gMontageOtio is not None and len(config.gMontageOtio.sequencesList)
        #     else None
        # )

        row = layout.row(align=True)
        box = row.box()
        box.separator(factor=0.2)
        box.prop(self, "sequenceList")

        # # print("self.sequenceList: ", self.sequenceList)
        # if selSeq is not None:
        #     labelText = f"Start: {selSeq.get_frame_start()}, End: {selSeq.get_frame_end()}, Duration: {selSeq.get_frame_duration()}, Num Shots: {len(selSeq.shotsList)}"

        #     # display the shots infos
        #     # sm_montage.printInfo()

        # else:
        #     labelText = f"Start: {-1}, End: {-1}, Num Shots: {0}"

    def execute(self, context):
        scene = context.scene
        vse_render = bpy.context.window_manager.UAS_vse_render
        props = scene.UAS_shot_manager_props
        vsm_props = scene.UAS_vsm_props

        sequenceClip = None
        sequenceName = bpy.data.scenes[0].name
        # wkip mettre un RE match ici
        act = sequenceName[0:5]
        filePath = (
            r"C:\_UAS_ROOT\RRSpecial\05_Acts\\"
            + act
            + r"\\"
            + sequenceName
            + r"\Shots\Main_Take\\"
            + sequenceName
            + ".mp4"
        )

        print(f" *** Seq filePath: {filePath}")

        importSequenceAtFrame = 0

        # find if a marker exists with the name of the first shot
        markers = utils.sortMarkers(scene.timeline_markers, sequenceName)
        if len(markers):
            # if firstShotMarker is not None:
            importSequenceAtFrame = markers[0].frame

        if not Path(filePath).exists():
            print(f" *** Sequence video file not found: {Path(filePath)}")
        else:
            sequence_AudioTrack_name = f"{sequenceName} (audio)"
            sequence_VideoTrack_name = f"{sequenceName} (video)"
            sequence_AudioTrack = None
            sequence_VideoTrack = None

            channelInd = 2

            sequence_AudioTrack = vsm_props.getTrackByName(sequence_AudioTrack_name)
            if sequence_AudioTrack is not None:
                sequence_AudioTrack.clearContent()
            sequence_VideoTrack = vsm_props.getTrackByName(sequence_VideoTrack_name)
            if sequence_VideoTrack is not None:
                sequence_VideoTrack.clearContent()

            channelInd_audio = channelInd + 1
            importSound = True
            if importSound:
                # create audio clip
                if sequence_AudioTrack is not None:
                    channelInd_audio = vsm_props.getTrackIndex(sequence_AudioTrack)
                sequenceAudioClip = vse_render.createNewClip(
                    scene,
                    filePath,
                    channelInd=channelInd_audio,
                    atFrame=importSequenceAtFrame,
                    importVideo=False,
                    importAudio=True,
                    clipName=sequence_AudioTrack_name,
                )
                vsm_props.updateTracksList(scene)
                sequence_AudioTrack = vsm_props.setTrackInfo(
                    channelInd_audio, trackType="AUDIO", name=sequence_AudioTrack_name, color=(0.1, 0.5, 0.2, 1),
                )

            # create video clip
            channelInd_video = channelInd + 1
            if sequence_AudioTrack is not None:
                channelInd_video = channelInd_audio + 1

            if sequence_VideoTrack is not None:
                channelInd_video = vsm_props.getTrackIndex(sequence_VideoTrack)

            sequenceClip = vse_render.createNewClip(
                scene,
                filePath,
                channelInd=channelInd_video,
                atFrame=importSequenceAtFrame,
                importAudio=False,
                clipName=sequence_VideoTrack_name,
            )

            if sequenceClip is not None:
                res_x = 1280
                res_y = 960
                vse_render.cropClipToCanvas(
                    res_x, res_y, sequenceClip, 1280, 960, mode="FIT_WIDTH",
                )

                scene.sequence_editor.active_strip = sequenceClip

            # vsm_props.addTrack(atIndex=3, trackType="STANDARD", name="Sequence", color=(0.5, 0.4, 0.6, 1))
            vsm_props.updateTracksList(scene)
            sequence_VideoTrack = vsm_props.setTrackInfo(
                channelInd_video, trackType="VIDEO", name=sequence_VideoTrack_name, color=(0.6, 0.3, 0.3, 1),
            )
            vsm_props.setSelectedTrackByIndex(channelInd_video)

        # works on selection
        #  bpy.ops.sequencer.set_range_to_strips(preview=False)

        bpy.ops.sequencer.select_all(action="DESELECT")

        if sequenceClip is not None:
            sequenceClip.select = True
        # scene.sequence_editor.sequences[2].select = Tru

        scene.frame_set(importSequenceAtFrame)

        # wkip works but applies the modifs on every sequence editor occurence of the file
        edSeqWksp = bpy.data.workspaces["Video Editing"]
        for screen in edSeqWksp.screens:
            #   print(f"Screen type: {screen.name}")
            for area in screen.areas:
                #      print(f"Area type: {area.type}")
                if area.type == "SEQUENCE_EDITOR":
                    #         print("Area seq ed")
                    override = bpy.context.copy()
                    override["area"] = area
                    override["region"] = area.regions[-1]

                    bpy.ops.sequencer.view_selected(override)
                    # bpy.context.space_data.show_seconds = False

        return {"FINISHED"}


_classes = (
    UAS_VideoShotManager_OT_RRS_ExportShotsFromEdit,
    UAS_VideoShotManager_OT_RRS_CheckSequence,
    UAS_VideoShotManager_GoToSequenceScene,
    UAS_VideoShotManager_ImportPublishedSequence,
    UAS_PT_RRSVSMTools,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
