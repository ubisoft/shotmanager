import logging

_logger = logging.getLogger(__name__)

import os
from pathlib import Path

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, IntProperty, EnumProperty, PointerProperty
from bpy_extras.io_utils import ImportHelper

import opentimelineio
from .exports import exportOtio

# from shotmanager.otio import imports
from .imports import createShotsFromOtio, importOtioToVSE
from .imports import getSequenceListFromOtioTimeline, getSequenceClassListFromOtioTimeline
from .imports import createShotsFromOtioTimelineClass

from shotmanager.utils import utils

from shotmanager.config import config

from shotmanager.rrs_specific.montage.montage_otio import MontageOtio


from . import otio_wrapper as ow


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
            exportOtio(context.scene, filePath=props.renderRootPath, fps=context.scene.render.fps)
        else:
            from ..utils.utils import ShowMessageBox

            ShowMessageBox("Render root path is invalid", "OpenTimelineIO Export Aborted", "ERROR")
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


class UAS_ShotManager_OT_Create_Shots_From_OTIO_RRS(Operator):
    bl_idname = "uasshotmanager.createshotsfromotio_rrs"
    bl_label = "Import/Update Shots from EDL File"
    bl_description = "Open EDL file (Final Cut XML, OTIO...) to import a set of shots"
    bl_options = {"INTERNAL", "UNDO"}

    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.xml;*.otio", options={"HIDDEN"})

    otioFile: StringProperty()

    sequenceList: EnumProperty(
        name="Sequence",
        description="Sequences available in the specified EDL file",
        # items=(("NO_SEQ", "No Sequence Found", ""),),
        items=(list_sequences_from_edl),
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

        config.gMontageOtio = None
        if "" != self.otioFile and Path(self.otioFile).exists():
            # config.gMontageOtio = getSequenceClassListFromOtioTimeline(self.otioFile, verbose=False)

            config.gMontageOtio = MontageOtio()
            config.gMontageOtio.fillMontageInfoFromOtioFile(self.otioFile, verboseInfo=False)

            # config.gMontageOtio.printInfo()

            config.gSeqEnumList = list()
            for i, seq in enumerate(config.gMontageOtio.sequencesList):
                config.gSeqEnumList.append((str(i), seq.get_name(), f"Import sequence {seq.get_name()}", i + 1))

            self.sequenceList = config.gSeqEnumList[0][0]

        #    seqList = getSequenceListFromOtioTimeline(config.gMontageOtio)
        #  self.sequenceList.items = list_sequences_from_edl(context, seqList)

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

            if config.gMontageOtio.get_fps() != context.scene.render.fps:
                row.alert = True
                row.label(text=f"!! Scene has a different framerate: {context.scene.render.fps} fps !!")
                row.alert = False

            row = box.row()
            row.label(text=f"Num. Sequences: {len(config.gMontageOtio.sequencesList)}")

        row = layout.row(align=True)
        box = row.box()
        box.separator(factor=0.2)
        box.prop(self, "sequenceList")

        # print("self.sequenceList: ", self.sequenceList)
        if config.gMontageOtio is not None:
            selSeq = config.gMontageOtio.sequencesList[int(self.sequenceList)]
            labelText = f"Start: {selSeq.get_frame_start()}, End: {selSeq.get_frame_end()}, Duration: {selSeq.get_frame_duration()}, Num Shots: {len(selSeq.shotsList)}"
        else:
            labelText = f"Start: {-1}, End: {-1}, Num Shots: {0}"

        row = box.row(align=True)
        row.label(text=labelText)

        row = box.row(align=True)
        row.prop(self, "offsetTime")
        # row.separator(factor=3)
        subrow = row.row(align=True)
        subrow.enabled = self.offsetTime
        subrow.prop(self, "importAtFrame")

        box.prop(self, "reformatShotNames")
        box.prop(self, "createCameras")

        if self.createCameras:
            layout.label(text="Camera Background:")
            row = layout.row(align=True)
            box = row.box()
            box.prop(self, "useMediaAsCameraBG")

            row = box.row()
            row.enabled = self.useMediaAsCameraBG
            row.separator(factor=3)
            row.prop(self, "mediaHaveHandles")

            subrow = row.row(align=True)
            # subrow.separator(factor=3)
            subrow.enabled = self.useMediaAsCameraBG and self.mediaHaveHandles
            subrow.prop(self, "mediaHandlesDuration")

        layout.label(text="Sound:")
        row = layout.row(align=True)
        box = row.box()
        row = box.row()
        # if 0 != self.mediaHandlesDuration and
        #     row.enabled = False
        row.prop(self, "importAudioInVSE")
        row = box.row()
        row.enabled = self.importAudioInVSE
        row.separator(factor=3)
        row.prop(self, "importAudio_HumanVoices")
        row.prop(self, "importAudio_RabbidVoices")
        row = box.row()
        row.enabled = self.importAudioInVSE
        row.separator(factor=3)
        row.prop(self, "importAudio_Sounds")
        row.prop(self, "importAudio_Music")

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
        selSeq = config.gMontageOtio.sequencesList[int(self.sequenceList)]

        useTimeRange = True
        timeRange = [selSeq.get_frame_start(), selSeq.get_frame_end()] if useTimeRange else None

        # track indices are starting from 1, not 0!!
        videoTracksToImport = [1]
        audioTracksToImport = []
        if self.importAudio_HumanVoices:
            audioTracksToImport.extend(list(range(1, 6)))
        if self.importAudio_RabbidVoices:
            audioTracksToImport.extend(list(range(6, 13)))
        if self.importAudio_Sounds:
            audioTracksToImport.extend(list(range(14, 26)))
        if self.importAudio_Music:
            audioTracksToImport.extend(list(range(28, 30)))

        audioTracksToImport = [19, 20]

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
            importSoundInVSE=self.importAudioInVSE,
            videoTracksList=videoTracksToImport,
            audioTracksList=audioTracksToImport,
        )

        return {"FINISHED"}


class UAS_ShotManager_OT_Create_Shots_From_OTIO(Operator):
    bl_idname = "uasshotmanager.createshotsfromotio"
    bl_label = "Import/Update Shots from EDL File"
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
        print("ex File name:", filename)
        print("ex File extension:", extension)

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
    UAS_OTIO_OpenFileBrowser,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
