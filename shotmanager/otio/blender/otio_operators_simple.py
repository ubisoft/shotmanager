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
Blender operators to import and export otio files
"""

import os
from pathlib import Path

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, IntProperty

# paths are relative in order to make the package not dependent on an add-on name
from ...utils import utils

import opentimelineio

from ..montage_otio import MontageOtio

from shotmanager.config import config
from ...config import sm_logging

_logger = sm_logging.getLogger(__name__)


def createShotsFromOtio(
    scene,
    otioFile,
    importAtFrame=0,
    reformatShotNames=False,
    createCameras=True,
    useMediaAsCameraBG=False,
    mediaHaveHandles=False,
    mediaHandlesDuration=0,
    importAudioInVSE=True,
):
    # filePath="", fileName=""):

    print("Import Otio File createShotsFromOtio: ", otioFile)
    from random import uniform
    from math import radians

    props = config.getAddonProps(scene)
    if len(props.getCurrentTake().getShotList()) != 0:
        bpy.ops.uas_shot_manager.take_add(name=Path(otioFile).stem)

    handlesDuration = 0
    if mediaHaveHandles:
        handlesDuration = mediaHandlesDuration

    try:
        timeline = opentimelineio.adapters.read_from_file(otioFile)
        if len(timeline.video_tracks()):
            track = timeline.video_tracks()[0]  # Assume the first one contains the shots.

            cam = None
            if not createCameras:  # Create Default Camera
                cam_ob = utils.create_new_camera("Camera", location=[0, 0, 0])
                cam = cam_ob.data

            shot_re = re.compile(r"sh_?(\d+)", re.IGNORECASE)
            atLeastOneVideoFailed = False
            for i, clip in enumerate(track.each_clip()):
                clipName = clip.name
                if createCameras:
                    if reformatShotNames:
                        match = shot_re.search(clipName)
                        if match:
                            clipName = props.naming_shot_format + match.group(1)

                    cam_ob = utils.create_new_camera("Cam_" + clipName, location=[0.0, i, 0.0])
                    cam = cam_ob.data
                    cam_ob.color = [uniform(0, 1), uniform(0, 1), uniform(0, 1), 1]
                    cam_ob.rotation_euler = (radians(90), 0.0, radians(90))

                    # add media as camera background
                    if useMediaAsCameraBG:
                        print("Import Otio clip.media_reference.target_url: ", clip.media_reference.target_url)
                        media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
                        print("Import Otio media_path: ", media_path)
                        if not media_path.exists():
                            # Lets find it inside next to the xml
                            media_path = Path(otioFile).parent.joinpath(media_path.name)
                            print("** not found, so Path(self.otioFile).parent: ", Path(otioFile).parent)
                            print("   and new media_path: ", media_path)

                        # start frame of the background video is not set here since it will be linked to the shot start frame
                        videoAdded = utils.add_background_video_to_cam(
                            cam, str(media_path), 0, alpha=props.shotsGlobalSettings.backgroundAlpha
                        )
                        if videoAdded is None:
                            atLeastOneVideoFailed = True

                shot = props.addShot(
                    name=clipName,
                    start=opentimelineio.opentime.to_frames(clip.range_in_parent().start_time) + importAtFrame,
                    end=opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame,
                    camera=cam_ob,
                    color=cam_ob.color,
                )
                # bpy.ops.uas_shot_manager.shot_add(
                #     name=clipName,
                #     start=opentimelineio.opentime.to_frames(clip.range_in_parent().start_time) + importAtFrame,
                #     end=opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame,
                #     cameraName=cam.name,
                #     color=(cam_ob.color[0], cam_ob.color[1], cam_ob.color[2]),
                # )
                shot.bgImages_linkToShotStart = True
                shot.bgImages_offset = -1 * handlesDuration

                # wkip maybe to remove
                scene.frame_start = importAtFrame
                scene.frame_end = (
                    opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame
                )

            if importAudioInVSE:
                # creation VSE si existe pas
                vse = utils.getSceneVSE(scene.name)
                # bpy.context.space_data.show_seconds = False
                bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]
                importOtioToVSE(otioFile, vse, importAtFrame=importAtFrame, importVideoTracks=False)

            # TOFIX wkip message don't appear...
            if createCameras and atLeastOneVideoFailed:
                utils.ShowMessageBox(
                    message=f"At least one video import failed...",
                    title="Missing Media\n   {media_path}",
                    icon="WARNING",
                )

    except opentimelineio.exceptions.NoKnownAdapterForExtensionError:
        from ...utils.utils import ShowMessageBox

        ShowMessageBox("File not recognized", f"{otioFile} could not be understood by Opentimelineio", "ERROR")


class UAS_ShotManager_OT_Create_Shots_From_OTIO_Simple(Operator):
    bl_idname = "uasshotmanager.createshotsfromotio_simple"
    bl_label = "Import / Update Shots from Edit File - Simple Mode"
    bl_description = "Open edit file (Final Cut XML, OTIO...) to import a set of shots"
    bl_options = {"REGISTER", "UNDO"}

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
        name="Reformat Shot Names",
        description="Keep only the shot name part for the name of the shots",
        default=True,
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
        name="Media Have Handles",
        description="Do imported media use the project handles?",
        default=False,
    )
    mediaHandlesDuration: IntProperty(
        name="Handles Duration",
        description="",
        soft_min=0,
        min=0,
        default=10,
    )

    importAudioInVSE: BoolProperty(
        name="Import sound In VSE",
        description="Import sound clips directly into the VSE of the current scene",
        default=True,
    )

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, width=500)

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

            # if rate != context.scene.render.fps:
            sceneFps = utils.getSceneEffectiveFps(context.scene)
            if rate != sceneFps:
                box.alert = True
                box.label(text=f"!!! Scene fps is {sceneFps}, imported edit is {rate} !!!")
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
            importAudioInVSE=self.importAudioInVSE,
        )

        return {"FINISHED"}


_classes = (UAS_ShotManager_OT_Create_Shots_From_OTIO_Simple,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
