import os
from pathlib import Path
import json
import subprocess, platform

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, IntProperty, EnumProperty, PointerProperty
from bpy_extras.io_utils import ImportHelper

from shotmanager.config import config
from shotmanager.utils import utils

import opentimelineio
from .exports import exportShotManagerEditToOtio

# from shotmanager.otio import imports
from .imports import createShotsFromOtio, importOtioToVSE
from .imports import getSequenceListFromOtioTimeline
from .imports import createShotsFromOtioTimelineClass, conformToRefMontage

from shotmanager.rrs_specific.montage.montage_otio import MontageOtio

from . import otio_wrapper as ow

import logging

_logger = logging.getLogger(__name__)


class UAS_ShotManager_Export_OTIO(Operator):
    bl_idname = "uas_shot_manager.export_otio"
    bl_label = "Export otio"
    bl_description = "Export otio"
    bl_options = {"INTERNAL"}

    file: StringProperty()

    # def invoke ( self, context, event ):
    #     props = context.scene.UAS_shot_manager_props

    #     if not props.isRenderRootPathValid():
    #         from ..utils.utils import ShowMessageBox
    #         ShowMessageBox( "Render root path is invalid", "OpenTimelineIO Export Aborted", 'ERROR')
    #         print("OpenTimelineIO Export aborted before start: Invalid Root Path")

    #     return {'RUNNING_MODAL'}

    # wkip a remettre plus tard pour définir des chemins alternatifs de sauvegarde.
    # se baser sur
    # wm = context.window_manager
    # self.fps = context.scene.render.fps
    # out_path = context.scene.render.filepath
    # if out_path.startswith ( "//" ):

    #     out_path = str ( Path ( props.renderRootPath ).parent.absolute ( ) ) + out_path[ 1 : ]
    # out_path = Path ( out_path)

    # take = context.scene.UAS_shot_manager_props.getCurrentTake ()
    # if take is None:
    #     take_name = ""
    # else:
    #     take_name = take.getName_PathCompliant()

    # if out_path.suffix == "":
    #     self.file = f"{out_path.absolute ( )}/{take_name}/export.xml"
    # else:
    #     self.file = f"{out_path.parent.absolute ( )}/{take_name}/export.xml"

    # return wm.invoke_props_dialog ( self )

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props

        if props.isRenderRootPathValid():
            exportShotManagerEditToOtio(
                context.scene,
                filePath=props.renderRootPath,
                fps=context.scene.render.fps,
                # montageCharacteristics=props.get_montage_characteristics(),
            )
        else:
            utils.ShowMessageBox("Render root path is invalid", "OpenTimelineIO Export Aborted", "ERROR")
            print("OpenTimelineIO Export aborted before start: Invalid Root Path")

        return {"FINISHED"}


# def list_sequences_from_edl(context, itemList):
def list_sequences_from_edl(self, context):
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


def list_video_tracks_from_edl(self, context):
    res = config.gTracksEnumList
    nothingList = list()
    nothingList.append(("1 -", "1 ---", "", 0))

    if res is None or 0 == len(res):
        res = nothingList
    return res


class UAS_ShotManager_OT_Create_Shots_From_OTIO_RRS(Operator):
    bl_idname = "uasshotmanager.createshotsfromotio_rrs"
    bl_label = "Import/Update Shots from EDL File"
    bl_description = "Open EDL file (Final Cut XML, OTIO...) to import a set of shots"
    bl_options = {"INTERNAL", "UNDO"}

    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.xml;*.otio", options={"HIDDEN"})

    # opArgs is a dictionary containing this operator properties and dumped to a json string
    opArgs: StringProperty(default="")

    otioFile: StringProperty()

    refVideoTrackList: EnumProperty(
        name="Shots Video Track",
        description="Track to use in the EDL to get the shot list",
        # items=(("NO_SEQ", "No Sequence Found", ""),),
        items=(list_video_tracks_from_edl),
    )

    ############
    # EDL edit settings
    ############
    mediaInEDLHaveHandles: BoolProperty(
        name="Media In EDL Have Handles", description="Do media used in the EDL edit have handles?", default=False,
    )
    mediaInEDLHandlesDuration: IntProperty(
        name="EDL Handles Duration",
        description="Duration of the handles in the EDL edit",
        soft_min=0,
        min=0,
        default=0,
    )

    # starts at 0, not 1!
    refVideoTrackInd: IntProperty(
        name="Reference Track",
        description="Track to get the shots list from (starts at 0)",
        soft_min=0,
        min=0,
        default=0,
    )

    sequenceList: EnumProperty(
        name="Sequence",
        description="Sequences available in the specified EDL file",
        # items=(("NO_SEQ", "No Sequence Found", ""),),
        items=(list_sequences_from_edl),
    )

    # can be "PREDEC" or "PREVIZ"
    importStepMode: StringProperty(default="PREDEC")

    conformMode: EnumProperty(
        name="Conform Mode",
        description="Type of conformation to apply to the current scene",
        items=(
            (
                "CREATE",
                "Create New Shots From EDL",
                "Create new shots into the current scene. They are added to the current take if the take is empty,\nto a new take otherwise.",
            ),
            (
                "UPDATE",
                "Update Existing Shots From EDL",
                "Update the existing shots of the current scene (order, time, background image...).\nNew shots may be added.",
            ),
        ),
        default="UPDATE",
    )

    offsetTime: BoolProperty(
        name="Offset Time", description="Offset the imported part of edit to start at the specified time", default=True,
    )
    importAtFrame: IntProperty(
        name="Import at Frame",
        description="Frame at which the imported edit has to start",
        soft_min=0,
        min=0,
        default=25,
    )

    ############
    # Create mode UI only
    ############

    reformatShotNames: BoolProperty(
        name="Reformat Shot Names", description="Keep only the shot name part for the name of the shots", default=True,
    )

    ############
    # Update mode UI only
    ############

    changeShotsTiming: BoolProperty(
        name="Update Timing of Existing Shots",
        description="Update the timing of the existing shots to match the reference edit",
        default=True,
    )

    createMissingShots: BoolProperty(
        name="Create Missing Shots",
        description="Create shots in the current take for shots exisiting only in the reference edit",
        default=True,
    )

    ############
    # VSE
    ############
    clearVSE: BoolProperty(
        name="Clear VSE From Previous Sounds and Videos",
        description="Clear VSE From Previous Sounds and Videos to avoid conflics",
        default=True,
    )
    clearCameraBG: BoolProperty(
        name="Clear Existing Camera Backgrounds",
        description="Clear existing camera backgrounds to avoid conflics",
        default=True,
    )
    videoShotsFolder: StringProperty()

    ############
    # common UI
    ############

    createCameras: BoolProperty(
        name="Create Camera for New Shots",
        description="Create a camera for each new shot or use the same camera for all shots",
        default=True,
    )

    useMediaAsCameraBG: BoolProperty(
        name="Use Clips as Camera Backgrounds",
        description="Use the clips and videos from the edit file as background for the cameras",
        default=True,
    )
    useMediaSoundtrackForCameraBG: BoolProperty(
        name="Use Media Soundtrack for Camera Backgrounds",
        description="Use the clip and video soundtracks from the edit file as sound associated to the camera backgrounds",
        default=True,
    )

    mediaHaveHandles: BoolProperty(
        name="Media Have Handles", description="Do imported media use the project handles?", default=False,
    )
    mediaHandlesDuration: IntProperty(
        name="Handles Duration", description="", soft_min=0, min=0, default=0,
    )

    compare3DAndAnimaticInVSE: BoolProperty(
        name="Compare Animatic and 3D Shots In VSE",
        description="Import the video and mixed sounds from the animatic into a new scene VSE and compare them with the 3D cameras",
        default=True,
    )

    importAnimaticInVSE: BoolProperty(
        name="Import Animatic In VSE",
        description="Import the video and mixed sounds from the animatic into the VSE of the current scene",
        default=True,
    )
    animaticFile: StringProperty(name="Animatic")

    importVideoInVSE: BoolProperty(
        name="Import Shot Videos In VSE",
        description="Import shot videos as clips directly into the VSE of the current scene",
        default=True,
    )

    importAudioInVSE: BoolProperty(
        name="Import Original Sound Tracks In VSE",
        description="Import all original edit sounds as clips directly into the VSE of the current scene",
        default=True,
    )

    # -Pistes sons 1 à 3 : voix humaines
    # -Pistes sons 4 à 7 : voix lapins
    # -Piste 8 : vide
    # -Pistes 9 à 15 : bruitages
    # -Piste 16 : vide
    # -Pistes 17 et 18 : musiques

    importAudio_HumanVoices: BoolProperty(
        name="Human Voices", description="Import tracks (1 to 3)", default=True,
    )
    importAudio_RabbidVoices: BoolProperty(
        name="Rabbid Voices", description="Import tracks (4 to 7)", default=True,
    )
    importAudio_Sounds: BoolProperty(
        name="Sounds", description="Import tracks (9 to 15)", default=True,
    )
    importAudio_Music: BoolProperty(
        name="Music", description="Import tracks (17 to 18)", default=False,
    )

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        props = scene.UAS_shot_manager_props

        # if "PREVIZ" == self.importStepMode:
        #     self.mediaHaveHandles = props.areShotHandlesUsed()
        #     self.mediaHandlesDuration = props.getHandlesDuration()
        # else:
        #     self.mediaHaveHandles = False
        #     self.mediaHandlesDuration = 0

        if "" != self.opArgs:
            argsDict = json.loads(self.opArgs)
            # print(f" argsDict: {argsDict}")
            # print(f" argsDict['otioFile']: {argsDict['otioFile']}")

            # PREDEC or PREVIZ
            if "importStepMode" in argsDict:
                self.importStepMode = argsDict["importStepMode"]

                # we need to put this code here again to cover all the cases
                # if "PREVIZ" == self.importStepMode:
                #     self.mediaHaveHandles = props.areShotHandlesUsed()
                #     self.mediaHandlesDuration = props.getHandlesDuration()
                # else:
                #     self.mediaHaveHandles = False
                #     self.mediaHandlesDuration = 0

            if "otioFile" in argsDict:
                self.otioFile = argsDict["otioFile"]
            if "animaticFile" in argsDict:
                self.animaticFile = argsDict["animaticFile"]

            # not used
            if "refVideoTrackInd" in argsDict:
                self.refVideoTrackInd = argsDict["refVideoTrackInd"]

            if "conformMode" in argsDict:
                self.conformMode = argsDict["conformMode"]

            if "videoShotsFolder" in argsDict:
                self.videoShotsFolder = argsDict["videoShotsFolder"]

            if "mediaInEDLHaveHandles" in argsDict:
                self.mediaInEDLHaveHandles = argsDict["mediaInEDLHaveHandles"]
                if "mediaInEDLHandlesDuration" in argsDict:
                    self.mediaInEDLHandlesDuration = argsDict["mediaInEDLHandlesDuration"]

            if "mediaHaveHandles" in argsDict:
                self.mediaHaveHandles = argsDict["mediaHaveHandles"]
                if "mediaHandlesDuration" in argsDict:
                    self.mediaHandlesDuration = argsDict["mediaHandlesDuration"]

        config.gMontageOtio = None

        if "" == self.otioFile:
            print(f"*** Otio file not defined - Cannot open EDL file ***")
            return {"CANCELLED"}
        if not Path(self.otioFile).exists():
            print(f"*** Otio file not found - Cannot open EDL file ***")
            print(f"***      Otio file: {self.otioFile}")
            return {"CANCELLED"}

        if "" != self.otioFile and Path(self.otioFile).exists():
            config.gMontageOtio = MontageOtio()
            config.gMontageOtio.initialize(self.otioFile)

            config.gTracksEnumList = list()
            numVideoTracks = len(config.gMontageOtio.timeline.video_tracks())
            for i in range(0, numVideoTracks):
                config.gTracksEnumList.append((str(i), str(i + 1), "", i))

            self.refVideoTrackInd = 0
            if "PREVIZ" == self.importStepMode:
                self.refVideoTrackInd = min(numVideoTracks - 1, 0)
            print(
                f"**** self.importStepMode: {self.importStepMode}, self.refVideoTrackInd: {self.refVideoTrackInd}, numVideoTracks: {numVideoTracks}"
            )

            self.refVideoTrackList = str(self.refVideoTrackInd)  # config.gTracksEnumList[0][0]

            config.gMontageOtio.fillMontageInfoFromOtioFile(
                refVideoTrackInd=int(self.refVideoTrackList), verboseInfo=False
            )
            print(f"config.gMontageOtio name: {config.gMontageOtio.get_name()}")

            # wkip not very context generic...
            currentSeqName = (scene.name)[6:]
            print(f"Current seq name: {currentSeqName}")
            currentSeqIndex = -1
            config.gSeqEnumList = list()
            if len(config.gMontageOtio.sequencesList):
                for i, seq in enumerate(config.gMontageOtio.sequencesList):
                    strDebug = f"- seqList: i:{i}, seq: {seq.get_name()}"
                    if seq.get_name() == currentSeqName:
                        currentSeqIndex = i
                        strDebug += " - Is current sequence !"
                    _logger.debug(strDebug)
                    config.gSeqEnumList.append((str(i), seq.get_name(), f"Import sequence {seq.get_name()}", i + 1))
            else:
                config.gSeqEnumList.append(
                    (str(0), " ** No Sequence in Ref Track **", f"No sequence found in the specifed reference track", 1)
                )

            if -1 != currentSeqIndex:
                self.sequenceList = config.gSeqEnumList[currentSeqIndex][0]
            else:
                self.sequenceList = config.gSeqEnumList[0][0]
            _logger.debug(f"self.sequenceList: {self.sequenceList}")

        #    seqList = getSequenceListFromOtioTimeline(config.gMontageOtio)
        #  self.sequenceList.items = list_sequences_from_edl(context, seqList)

        wm.invoke_props_dialog(self, width=500)
        #    res = bpy.ops.uasotio.openfilebrowser("INVOKE_DEFAULT")

        # print("Res: ", res)
        # return wm.invoke_props_dialog(self, width=500)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        #########################
        #########################

        # # print(f"self.refVideoTrackList: {self.refVideoTrackList}")
        # config.gMontageOtio.fillMontageInfoFromOtioFile(refVideoTrackInd=int(self.refVideoTrackList), verboseInfo=False)

        # config.gSeqEnumList = list()
        # for i, seq in enumerate(config.gMontageOtio.sequencesList):
        #     # print(f"- seqList: i:{i}, seq: {seq.get_name()}")
        #     config.gSeqEnumList.append((str(i), seq.get_name(), f"Import sequence {seq.get_name()}", i + 1))

        # # self.sequenceList = config.gSeqEnumList[0][0]
        # #        print(f"Import Sequence: {self.sequenceList}, {config.gSeqEnumList[int(self.sequenceList)]}")
        # # if len(config.gSeqEnumList) <= int(self.sequenceList):
        # if "" == self.sequenceList:
        #     self.sequenceList = config.gSeqEnumList[0][0]

        # #########################
        #########################

        selSeq = (
            config.gMontageOtio.sequencesList[int(self.sequenceList)]
            if config.gMontageOtio is not None and len(config.gMontageOtio.sequencesList)
            else None
        )

        layout = self.layout
        box = layout.box()

        if config.uasDebug:
            row = box.row()
            row.label(text=self.importStepMode)
            row.prop(self, "refVideoTrackList")

        box.label(text="EDL File (Otio, XML...):")
        row = box.row()
        row.separator(factor=3)
        row.prop(self, "otioFile", text="")

        if "" == self.otioFile or not Path(self.otioFile).exists():
            row = box.row()
            row.alert = True
            row.label(text="Specified EDL file not found! - Verify your local depot")  # wkip rrs specific
            row.alert = False

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

            if config.uasDebug:
                box.prop(self, "refVideoTrackList")

            if config.uasDebug:
                row = box.row()
                # row.enabled = self.useMediaAsCameraBG
                row.separator(factor=3)
                row.prop(self, "mediaInEDLHaveHandles")

                subrow = row.row(align=True)
                # subrow.separator(factor=3)
                subrow.enabled = self.mediaInEDLHaveHandles
                subrow.prop(self, "mediaInEDLHandlesDuration")

            row = box.row()
            if config.gMontageOtio.get_fps() != context.scene.render.fps:
                row.alert = True
                row.label(text=f"!! Scene has a different framerate: {context.scene.render.fps} fps !!")
                row.alert = False

            # if config.uasDebug:
            #     row.operator("uas_shot_manager.montage_sequences_to_json")  # uses config.gMontageOtio

            if selSeq is not None:
                subRow = box.row()
                subRow.enabled = selSeq is not None
                row.operator("uasshotmanager.compare_otio_and_current_montage").sequenceName = selSeq.get_name()

        row = layout.row(align=True)
        box = row.box()
        box.separator(factor=0.2)
        box.prop(self, "sequenceList")

        # print("self.sequenceList: ", self.sequenceList)
        if selSeq is not None:
            labelText = f"Start: {selSeq.get_frame_start()}, End: {selSeq.get_frame_end()}, Duration: {selSeq.get_frame_duration()}, Num Shots: {len(selSeq.shotsList)}"

            # display the shots infos
            # sm_montage.printInfo()

        else:
            labelText = f"Start: {-1}, End: {-1}, Num Shots: {0}"

        row = box.row(align=True)
        row.label(text=labelText)

        if config.uasDebug:
            row = box.row(align=True)
            row.prop(self, "conformMode")

        if "CREATE" == self.conformMode or config.uasDebug:
            row = box.row(align=True)
            row.prop(self, "offsetTime")
            # row.separator(factor=3)
            subrow = row.row(align=True)
            subrow.enabled = self.offsetTime
            subrow.prop(self, "importAtFrame")

        row = layout.row(align=True)
        if "CREATE" == self.conformMode:
            row.label(text="Create Settings:")
        else:
            row.label(text="Update Settings:")

        if selSeq is None:
            return None

        box = layout.box()

        ############
        # Create UI
        ############
        if "CREATE" == self.conformMode:
            box.prop(self, "createCameras")
            box.prop(self, "reformatShotNames")

        ############
        # Update UI
        ############
        else:
            boxRow = box.row(align=True)
            boxRow.prop(self, "changeShotsTiming")
            # boxRow = box.row(align=True)
            # boxRow.prop(self, "clearCameraBG")

            box.prop(self, "createMissingShots")
            boxRow = box.row(align=True)
            boxRow.separator(factor=3)
            boxRow.enabled = self.createMissingShots
            boxRow.prop(self, "createCameras")

        if self.createCameras:
            box.prop(self, "useMediaAsCameraBG")

            if config.uasDebug:
                row = box.row()
                row.enabled = self.useMediaAsCameraBG
                row.separator(factor=3)
                row.prop(self, "mediaHaveHandles")

                subrow = row.row(align=True)
                # subrow.separator(factor=3)
                subrow.enabled = self.useMediaAsCameraBG and self.mediaHaveHandles
                subrow.prop(self, "mediaHandlesDuration")

            boxRow = box.row(align=True)
            boxRow.separator(factor=3)
            boxRow.enabled = self.useMediaAsCameraBG
            boxRow.prop(self, "useMediaSoundtrackForCameraBG")

        layout.label(text="Scene VSE:")
        box = layout.box()

        row = box.row()
        row.prop(self, "clearVSE")

        # if config.uasDebug:
        #     row = box.row()
        #     row.prop(self, "importAnimaticInVSE")
        #     row = box.row()
        #     row.separator(factor=3)
        #     row.enabled = self.importAnimaticInVSE
        #     row.prop(self, "animaticFile", text="")

        # row = box.row()
        # row.prop(self, "importVideoInVSE")
        # row = box.row()
        # row.prop(self, "importAudioInVSE")
        # row = box.row()
        # row.enabled = self.importAudioInVSE
        # row.separator(factor=3)
        # itemText = "Human Voices (1 to 6)" if "CREATE" == self.conformMode else "Human Voices (1 to 3)"
        # row.prop(self, "importAudio_HumanVoices", text=itemText)
        # itemText = "Rabbid Voices (7 to 14)" if "CREATE" == self.conformMode else "Rabbid Voices (4 to 7)"
        # row.prop(self, "importAudio_RabbidVoices", text=itemText)
        # row = box.row()
        # row.enabled = self.importAudioInVSE
        # row.separator(factor=3)
        # itemText = "Sounds (15 to 29)" if "CREATE" == self.conformMode else "Sounds (9 to 15)"
        # row.prop(self, "importAudio_Sounds", text=itemText)
        # itemText = "Music (30 to 33)" if "CREATE" == self.conformMode else "Music (17 to 18)"
        # row.prop(self, "importAudio_Music", text=itemText)

        layout.separator()

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props
        print(f"\n--------------------")
        print(
            f"\nCreateshotsfromotio Import Sequence Exec: {self.sequenceList}, {config.gSeqEnumList[int(self.sequenceList)]}"
        )
        print(f"\n--------")

        # filename, extension = os.path.splitext(self.filepath)
        # print("ex Selected file:", self.filepath)
        # print("ex File name:", filename)
        # print("ex File extension:", extension)

        if not len(config.gMontageOtio.sequencesList):
            return {"CANCELLED"}

        selSeq = config.gMontageOtio.sequencesList[int(self.sequenceList)]

        selSeq.printInfo()

        useTimeRange = True
        # timeRange end is inclusive, meaning that clips overlaping this value will be imported
        timeRange = [selSeq.get_frame_start(), selSeq.get_frame_end() - 1] if useTimeRange else None

        # track indices are starting from 1, not 0!!
        videoTracksToImport = []
        audioTracksToImport = []

        # audioTracksToImport = [19, 20]

        if "CREATE" == self.conformMode:
            # track indices are starting from 1, not 0!!
            videoTracksToImport = [1]

            if self.importAudio_HumanVoices:
                audioTracksToImport.extend(list(range(1, 4)))
            if self.importAudio_RabbidVoices:
                audioTracksToImport.extend(list(range(4, 7)))
            if self.importAudio_Sounds:
                audioTracksToImport.extend(list(range(9, 16)))
            if self.importAudio_Music:
                audioTracksToImport.extend(list(range(17, 19)))

            createShotsFromOtioTimelineClass(
                context.scene,
                config.gMontageOtio,
                selSeq.get_name(),
                config.gMontageOtio.sequencesList[int(self.sequenceList)].shotsList,
                timeRange=timeRange,
                offsetTime=self.offsetTime,
                importAtFrame=self.importAtFrame,
                reformatShotNames=self.reformatShotNames,
                createCameras=self.createCameras,
                useMediaAsCameraBG=self.useMediaAsCameraBG,
                mediaHaveHandles=self.mediaHaveHandles,
                mediaHandlesDuration=self.mediaHandlesDuration,
                useMediaSoundtrackForCameraBG=self.useMediaSoundtrackForCameraBG,
                importVideoInVSE=self.importVideoInVSE,
                importAudioInVSE=self.importAudioInVSE,
                videoTracksList=videoTracksToImport,
                audioTracksList=audioTracksToImport,
                animaticFile=self.animaticFile if self.importAnimaticInVSE else None,
            )

            props.setCurrentShotByIndex(0)
            props.setSelectedShotByIndex(0)
            props.display_camerabgtools_in_properties = True
            props.shotsGlobalSettings.backgroundAlpha = 1
            props.renderContext.useOverlays = True

            try:
                bpy.context.space_data.overlay.show_overlays = True
            except Exception as e:
                print("Cannot set Overlay")

        else:
            # track indices are starting from 1, not 0!!
            videoTracksToImport = [2]

            if self.importAudio_HumanVoices:
                audioTracksToImport.extend(list(range(1, 6)))
            if self.importAudio_RabbidVoices:
                audioTracksToImport.extend(list(range(6, 13)))
            if self.importAudio_Sounds:
                audioTracksToImport.extend(list(range(14, 26)))
            if self.importAudio_Music:
                audioTracksToImport.extend(list(range(28, 30)))

            if config.uasDebug:
                bpy.ops.uasshotmanager.compare_otio_and_current_montage(sequenceName=selSeq.get_name())

            textFile = conformToRefMontage(
                context.scene,
                config.gMontageOtio,
                selSeq.get_name(),
                mediaInEDLHaveHandles=self.mediaInEDLHaveHandles,
                mediaInEDLHandlesDuration=self.mediaInEDLHandlesDuration,
                clearVSE=self.clearVSE,
                clearCameraBG=self.clearCameraBG,
                changeShotsTiming=self.changeShotsTiming,
                createMissingShots=self.createMissingShots,
                createCameras=self.createCameras,
                useMediaAsCameraBG=self.useMediaAsCameraBG,
                videoShotsFolder=self.videoShotsFolder,
                mediaHaveHandles=self.mediaHaveHandles,
                mediaHandlesDuration=self.mediaHandlesDuration,
                useMediaSoundtrackForCameraBG=self.useMediaSoundtrackForCameraBG,
                #########
                # VSE - No imports anymore
                # importVideoInVSE=self.importVideoInVSE,
                # importAudioInVSE=self.importAudioInVSE,
                # videoTracksList=videoTracksToImport,
                # audioTracksList=audioTracksToImport,
                # animaticFile=self.animaticFile if self.importAnimaticInVSE else None,
            )
            props.setCurrentShotByIndex(0)
            props.setSelectedShotByIndex(0)
            props.display_camerabgtools_in_properties = True
            # props.renderContext.useOverlays = True

            try:
                bpy.context.space_data.overlay.show_overlays = True
            except Exception as e:
                print("Cannot set Overlay")

            props.display_notes_in_properties = True

            # update track list in VSM
            #            context.scene.uas_video_shot_manager.update_tracks_list()

            # open notes
            # import subprocess, os, platform
            if platform.system() == "Darwin":  # macOS
                subprocess.call(("open", textFile))
            elif platform.system() == "Windows":  # Windows
                os.startfile(textFile)
            else:  # linux variants
                subprocess.call(("xdg-open", textFile))

        return {"FINISHED"}


class UAS_ShotManager_OT_CompareOtioAndCurrentMontage(Operator):
    bl_idname = "uasshotmanager.compare_otio_and_current_montage"
    bl_label = "Print Comparison"
    bl_description = (
        "Print the differences between the current sequence in the scene and the imported EDL file into the console"
    )
    bl_options = {"INTERNAL"}

    sequenceName: StringProperty(default="")

    def execute(self, context):
        context.scene.UAS_shot_manager_props.compareWithMontage(config.gMontageOtio, self.sequenceName)
        return {"FINISHED"}


class UAS_ShotManager_OT_Create_Shots_From_OTIO(Operator):
    bl_idname = "uasshotmanager.createshotsfromotio"
    bl_label = "Import/Update Shots from EDL File - deprec"
    bl_description = "Open EDL file (Final Cut XML, OTIO...) to import a set of shots"
    bl_options = {"INTERNAL", "UNDO"}

    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.xml;*.otio", options={"HIDDEN"})

    otioFile: StringProperty()
    importAtFrame: IntProperty(
        name="Import at Frame",
        description="Make the imported edit start at the specified frame",
        soft_min=0,
        min=0,
        default=25,
    )

    reformatShotNames: BoolProperty(
        name="Reformat Shot Names", description="Keep only the shot name part for the name of the shots", default=True,
    )
    createCameras: BoolProperty(
        name="Create Camera for New Shots",
        description="Create a camera for each new shot or use the same camera for all shots",
        default=True,
    )
    useMediaAsCameraBG: BoolProperty(
        name="Use Clips as Camera Backgrounds",
        description="Use the clips and videos from the edit file as background for the cameras",
        default=True,
    )
    mediaHaveHandles: BoolProperty(
        name="Media Have Handles", description="Do imported media use the project handles?", default=False,
    )
    mediaHandlesDuration: IntProperty(
        name="Handles Duration", description="", soft_min=0, min=0, default=10,
    )

    importAudioInVSE: BoolProperty(
        name="Import sound In VSE",
        description="Import sound clips directly into the VSE of the current scene",
        default=True,
    )

    def invoke(self, context, event):
        wm = context.window_manager

        from ..otio.imports import getSequenceListFromOtio

        wm.invoke_props_dialog(self, width=500)
        #    res = bpy.ops.uasotio.openfilebrowser("INVOKE_DEFAULT")

        # print("Res: ", res)
        # return wm.invoke_props_dialog(self, width=500)
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

        row = layout.row(align=True)
        box = row.box()
        box.separator(factor=0.2)
        box.prop(self, "importAtFrame")
        box.prop(self, "reformatShotNames")
        box.prop(self, "createCameras")

        if self.createCameras:
            layout.label(text="Camera Background:")
            row = layout.row(align=True)
            box = row.box()
            box.prop(self, "useMediaAsCameraBG")
            row = box.row()
            row.enabled = self.useMediaAsCameraBG
            row.separator()
            row.prop(self, "mediaHaveHandles")
            row = box.row()
            row.enabled = self.useMediaAsCameraBG and self.mediaHaveHandles
            row.separator(factor=4)
            row.prop(self, "mediaHandlesDuration")
        #                if self.mediaHaveHandles:

        layout.label(text="Sound:")
        row = layout.row(align=True)
        box = row.box()
        row = box.row()
        # if 0 != self.mediaHandlesDuration and
        #     row.enabled = False
        row.prop(self, "importAudioInVSE")

        layout.separator()

    def execute(self, context):
        #   import opentimelineio as otio
        # from random import uniform
        # from math import radians
        print("Exec uasshotmanager.createshotsfromotio")
        # filename, extension = os.path.splitext(self.filepath)
        # print("ex Selected file:", self.filepath)
        # print("ex File name:", filename)
        # print("ex File extension:", extension)

        # importOtio(
        createShotsFromOtio(
            context.scene,
            self.otioFile,
            importAtFrame=self.importAtFrame,
            reformatShotNames=self.reformatShotNames,
            createCameras=self.createCameras,
            useMediaAsCameraBG=self.useMediaAsCameraBG,
            mediaHaveHandles=self.mediaHaveHandles,
            mediaHandlesDuration=self.mediaHandlesDuration,
            importSoundInVSE=self.importAudioInVSE,
        )

        return {"FINISHED"}


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_OTIO_OpenFileBrowser(Operator, ImportHelper):  # from bpy_extras.io_utils import ImportHelper
    bl_idname = "uasotio.openfilebrowser"
    bl_label = "Open EDL File"
    bl_description = "Open EDL file (Final Cut XML, OTIO...) to import a set of shots"

    importMode: EnumProperty(
        name="Import Mode",
        description="Import Mode",
        items=(
            ("CREATE_SHOTS", "Create Shots", ""),
            ("IMPORT_EDIT", "Import Edit", ""),
            ("PARSE_EDIT", "Parse Edit", ""),
        ),
        default="CREATE_SHOTS",
    )

    # otioFile: StringProperty()
    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.xml;*.otio", options={"HIDDEN"})

    def invoke(self, context, event):

        # if self.otioFile in context.window_manager.UAS_vse_render:
        #     self.filepath = context.window_manager.UAS_vse_render[self.otioFile]
        # else:
        self.filepath = ""
        # https://docs.blender.org/api/current/bpy.types.WindowManager.html
        #    self.directory = bpy.context.scene.UAS_shot_manager_props.renderRootPath
        context.window_manager.fileselect_add(self)
        # wm = bpy.context.window_manager
        # operat = bpy.ops.uasshotmanager.createshotsfromotio
        # operat = type(UAS_ShotManager_OT_Create_Shots_From_OTIO)
        # operat = wm.operators["uasshotmanager.createshotsfromotio"]
        # operator = [op for op in wm.operators if op.name == "uasshotmanager.createshotsfromotio"]

        # if operator:
        #     print(" -- found op:", operator[-1].otioFile)

        #  context.window_manager.fileselect_add(operat)

        # return {"FINISHED"}
        return {"RUNNING_MODAL"}

    def execute(self, context):
        """Open EDL file (Final Cut XML, OTIO...) to import a set of shots"""
        filename, extension = os.path.splitext(self.filepath)
        print("ex Selected file:", self.filepath)
        # print("ex File name:", filename)
        # print("ex File extension:", extension)

        if "CREATE_SHOTS" == self.importMode:
            # bpy.ops.uasshotmanager.createshotsfromotio("INVOKE_DEFAULT", otioFile=self.filepath)
            bpy.ops.uasshotmanager.createshotsfromotio_rrs("INVOKE_DEFAULT", otioFile=self.filepath)
        elif "IMPORT_EDIT" == self.importMode:
            bpy.ops.uas_video_shot_manager.importeditfromotio("INVOKE_DEFAULT", otioFile=self.filepath)
        elif "PARSE_EDIT" == self.importMode:
            bpy.ops.uas_video_shot_manager.parseeditfromotio("INVOKE_DEFAULT", otioFile=self.filepath)

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_Export_OTIO,
    UAS_ShotManager_OT_Create_Shots_From_OTIO,
    UAS_ShotManager_OT_Create_Shots_From_OTIO_RRS,
    UAS_ShotManager_OT_CompareOtioAndCurrentMontage,
    UAS_OTIO_OpenFileBrowser,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
