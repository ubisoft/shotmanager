# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
To do: module description here.
"""

from pathlib import Path

import bpy
from bpy.types import Operator, Panel
from bpy.props import StringProperty, BoolProperty, EnumProperty

from shotmanager.config import config
from shotmanager.utils import utils

from shotmanager.otio.montage_otio import MontageOtio
from shotmanager.scripts.rrs import utils_rrs

from shotmanager.scripts.rrs.rrs_playblast import (
    rrs_playblast_to_vsm,
    rrs_animatic_to_vsm,
    rrs_sequence_to_vsm,
    getSoundFilesForEachShot,
)

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


######
# RRS VSE panel #
######


class UAS_PT_RRSVSMTools(Panel):
    bl_idname = "UAS_PT_RRSVSMTools"
    bl_label = "RR Special VSE Tools"
    bl_description = "RRS Options"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Video Shot Mng"
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
            row.label(text="On Tracks 1 (audio) and 2 (video)")

            if (
                not (
                    bpy.data.scenes[0].name.startswith("Act01_Seq")
                    or bpy.data.scenes[0].name.startswith("Act02_Seq")
                    or bpy.data.scenes[0].name.startswith("Act03_Seq")
                )
                or "SM_CheckSequence" == scene.name
            ):
                box.separator(factor=0.1)
                row = box.row()
                row.operator("uas_video_shot_manager.import_published_sequence")
                row.label(text="On Tracks 3 (audio) and 4 (video)")
                layout.separator()

            if (
                bpy.data.scenes[0].name.startswith("Act01_Seq")
                or bpy.data.scenes[0].name.startswith("Act02_Seq")
                or bpy.data.scenes[0].name.startswith("Act03_Seq")
            ) and bpy.data.scenes[0] is not scene:
                row = layout.row()
                row.scale_y = 1.4
                row.operator(
                    "uas_video_shot_manager.go_to_sequence_scene", text="Go to Sequence Scene", icon="SCENE_DATA"
                ).sceneName = bpy.data.scenes[0].name

            box.label(text="Playblast Tracks: 5 (audio) and 6 (video)")
            box.separator(factor=0.2)

        layout.separator(factor=1)

        layout.label(text="For Montages and Confos:")
        box = layout.box()
        row = box.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator(
            "uas_video_shot_manager.export_content_between_markers", text="   Batch Export Content Between Markers..."
        ).outputDir = r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\_OutputShots"

        row = box.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        #   row.operator("uas_video_shot_manager.rrs_export_sounds_per_shot")
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
        props = config.getAddonProps(scene)

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
                otioFile=self.otioFile, refVideoTrackInd=0, verboseInfo=False
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
        props = config.getAddonProps(scene)

        # selSeq = config.gMontageOtio.sequencesList[int(self.sequenceList)] if config.gMontageOtio is not None else None

        layout = self.layout
        row = layout.row(align=True)

        box = row.box()
        box.label(text="OTIO File")
        box.prop(self, "otioFile", text="")

        if "" == self.otioFile or not Path(self.otioFile).exists():
            row = box.row()
            row.alert = True
            row.label(text="Specified edit file not found! - Verify your local depot")  # wkip rrs specific
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
            # if config.gMontageOtio.get_fps() != scene.render.fps:
            sceneFps = utils.getSceneEffectiveFps(scene)
            if config.gMontageOtio.get_fps() != sceneFps:
                row.alert = True
                row.label(text=f"!! Scene has a different framerate: {sceneFps} fps !!")
                row.alert = False

        #     # if config.devDebug:
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
        props = config.getAddonProps(scene)

        if not Path(self.otioFile).exists():
            return

        vse_render = bpy.context.window_manager.UAS_vse_render

        editVideoClip = vse_render.createNewClip(scene, self.editVideoFile, 1, 0, importAudio=True)

        if self.useOverlayFrame:
            overlayClip = vse_render.createNewClip(scene, self.overlayFile, 2, 0, offsetEnd=-60000)
            scene.sequence_editor.sequences_all[overlayClip.name].blend_type = "ALPHA_OVER"

        scene.timeline_markers.clear()
        importShotMarkersFromMontage(scene, config.gMontageOtio)

        vsm_props = context.scene.UAS_vsm_props
        vsm_props.updateTracksList(scene)

        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
        scene.render.ffmpeg.gopsize = 5  # keyframe interval
        scene.render.ffmpeg.audio_codec = "AAC"

        #       scene.render.filepath = output_filepath
        scene.render.use_file_extension = False

        # scene.render.resolution_percentage = 75

        return {"FINISHED"}


class UAS_VideoShotManager_OT_SM_CheckSequence(Operator):
    bl_idname = "uas_video_shot_manager.rrs_check_sequence"
    bl_label = "Check Sequence..."
    bl_description = "Import the animatic of the scpecified act into the VSE"
    bl_options = {"REGISTER", "UNDO"}

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
        props = config.getAddonProps(scene)

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
                otioFile=self.otioFile, refVideoTrackInd=0, verboseInfo=False
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
        props = config.getAddonProps(scene)

        # selSeq = config.gMontageOtio.sequencesList[int(self.sequenceList)] if config.gMontageOtio is not None else None

        layout = self.layout
        row = layout.row(align=True)

        box = row.box()
        box.label(text="OTIO File")
        box.prop(self, "otioFile", text="")

        if "" == self.otioFile or not Path(self.otioFile).exists():
            row = box.row()
            row.alert = True
            row.label(text="Specified edit file not found! - Verify your local depot")  # wkip rrs specific
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
            # if config.gMontageOtio.get_fps() != scene.render.fps:
            sceneFps = utils.getSceneEffectiveFps(scene)
            if config.gMontageOtio.get_fps() != sceneFps:
                row.alert = True
                row.label(text=f"!! Scene has a different framerate: {sceneFps} fps !!")
                row.alert = False

        #     # if config.devDebug:
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

        rrs_animatic_to_vsm(
            editVideoFile=self.editVideoFile,
            montageOtio=config.gMontageOtio,
            importMarkers=self.importMarkers,
        )

        bpy.ops.uas_video_shot_manager.zoom_view(zoomMode="SELECTEDCLIPS")

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
    nothingList.append(("NO_SEQ", "No Sequence Found", "No sequence found in the specified edit file", 0))

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
    bl_options = {"REGISTER", "UNDO"}

    sequenceList: EnumProperty(
        name="Sequence",
        description="Sequences available from the markers list",
        # items=(("NO_SEQ", "No Sequence Found", ""),),
        items=(list_sequences_from_markers),
    )

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        props = config.getAddonProps(scene)

        # parse the markers to get the shots list
        previzMarkers = scene.timeline_markers
        seqNames = list()
        currentSeqName = ""
        # if bpy.data.scenes[0].name.startswith("Act"):  # wkip re match
        if utils_rrs.start_with_act(bpy.data.scenes[0].name):  # wkip re match
            currentSeqName = (bpy.data.scenes[0].name)[6:13]
        print(f"Current seq name: {currentSeqName}")
        currentSeqIndex = -1
        seqInd = -1
        config.gSeqEnumList = list()
        for i, m in enumerate(previzMarkers):
            if utils_rrs.start_with_seq(m.name):
                seqName = m.name[0:13]
                seqNameShort = m.name[6:13]
                if seqName not in seqNames:
                    seqNames.append(seqName)
                    seqInd += 1
                    # config.gSeqEnumList.append((str(seqInd), seqName, f"Import sequence {seqName}", seqInd + 1))
                    config.gSeqEnumList.append((seqName, seqNameShort, f"Import sequence {seqName}", seqInd + 1))
                    if seqName == currentSeqName:
                        currentSeqIndex = seqInd
                        # strDebug += " - Is current sequence !"

        if not len(config.gSeqEnumList):
            config.gSeqEnumList.append(
                (str(0), " ** No Sequence in the markers list **", f"No sequence found in the markers list", 1)
            )

        if -1 != currentSeqIndex:
            self.sequenceList = config.gSeqEnumList[currentSeqIndex][0]
        else:
            self.sequenceList = config.gSeqEnumList[0][0]
        _logger.debug(f"self.sequenceList: {self.sequenceList}")

        return wm.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = config.getAddonProps(scene)

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
        seqToImport = self.sequenceList
        # seqToImport = config.gSeqEnumList[self.sequenceList][1]
        print("seq list to import:", seqToImport)
        success = rrs_sequence_to_vsm(context.scene, seqToImport)
        if not success:
            utils.ShowMessageBox(f"Sequence {seqToImport} cannot be loaded", "Cannot load sequence", "ERROR")
            return {"CANCELLED"}
        return {"FINISHED"}


# class UAS_VideoShotManager_OT_RRS_ExportAllSoundsPerShot(Operator):
#     bl_idname = "uas_video_shot_manager.rrs_export_sounds_per_shot"
#     bl_label = "Export Sounds Per Shot"
#     bl_description = "Bla bla"
#     bl_options = {"REGISTER", "UNDO"}

#     def execute(self, context):
#         soundsPerShot = getSoundFilesForEachShot(config.gMontageOtio, "Act01_Seq0100", otioFile)
#         print("soundsPerShot: ", soundsPerShot)

#         return {"FINISHED"}


_classes = (
    UAS_VideoShotManager_OT_RRS_ExportShotsFromEdit,
    UAS_VideoShotManager_OT_SM_CheckSequence,
    UAS_VideoShotManager_GoToSequenceScene,
    UAS_VideoShotManager_ImportPublishedSequence,
    UAS_PT_RRSVSMTools,
    # UAS_VideoShotManager_OT_RRS_ExportAllSoundsPerShot,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
