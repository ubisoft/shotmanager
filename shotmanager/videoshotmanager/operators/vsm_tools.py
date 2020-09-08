import logging

_logger = logging.getLogger(__name__)

import os
from pathlib import Path

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, IntProperty, EnumProperty, PointerProperty
from bpy_extras.io_utils import ImportHelper

import opentimelineio
from shotmanager.otio import otio_wrapper as ow
from shotmanager.otio.exports import exportOtio
from shotmanager.otio.imports import importToVSE

from shotmanager.utils import utils

from shotmanager.config import config


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

    useTimeRange: BoolProperty(
        name="Use Time Range", description="Part of the edit to be importer", default=False,
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
            timeline = ow.get_timeline_from_file(self.otioFile)
            if timeline is not None:
                config.gMontageOtio = otc.OtioTimeline()
                config.gMontageOtio.otioFile = self.otioFile
                config.gMontageOtio.timeline = timeline

        wm.invoke_props_dialog(self, width=500)
        #    res = bpy.ops.uasotio.openfilebrowser("INVOKE_DEFAULT")
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)

        box = row.box()
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
        row.prop(self, "useTimeRange")
        subrow = row.row(align=False)
        subrow.enabled = self.useTimeRange
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

        # creation VSE si existe pas
        vse = utils.getSceneVSE(context.scene.name)
        # bpy.context.space_data.show_seconds = False
        bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]
        # bpy.context.window.space_data.show_seconds = False

        timeRange = None
        if self.useTimeRange:
            timeRange = [self.range_start, self.range_end]

        offsetFrameNumber = 0
        if self.offsetTime:
            if timeRange is None:
                offsetFrameNumber = importAtFrame
            else:
                offsetFrameNumber = importAtFrame - timeRange[0]

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


_classes = (
    UAS_VideoShotManager_OT_Import_Edit_From_OTIO,
    UAS_VideoShotManager_OT_Parse_Edit_From_OTIO,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
