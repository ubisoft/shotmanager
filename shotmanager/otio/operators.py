import os
import re
import json
from pathlib import Path

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ImportHelper

from ..utils import utils


import opentimelineio as otio


class UAS_ShotManager_Export_OTIO(Operator):
    bl_idname = "uas_shot_manager.export_otio"
    bl_label = "Export otio"
    bl_description = "Export otio"
    bl_options = {"INTERNAL"}

    file: StringProperty()

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props

        if props.isRenderRootPathValid():
            exportOtio(context.scene, renderRootFilePath=props.renderRootPath, fps=context.scene.render.fps)
        else:
            from ..utils.utils import ShowMessageBox

            ShowMessageBox("Render root path is invalid", "OpenTimelineIO Export Aborted", "ERROR")
            print("OpenTimelineIO Export aborted before start: Invalid Root Path")

        return {"FINISHED"}

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


class UAS_ShotManager_OT_Import_OTIO(Operator):
    bl_idname = "uasshotmanager.importotio"
    bl_label = "Import/Update Shots from OTIO File"
    bl_description = "Open OTIO file to import a set of shots"
    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

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
        name="Media Have Handles", description="Do imported media use the project handles?", default=True,
    )

    mediaHandlesDuration: IntProperty(
        name="Handles Duration", description="", soft_min=0, min=0, default=10,
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)

        box = row.box()
        box.prop(self, "otioFile", text="OTIO File")

        timeline = otio.adapters.read_from_file(self.otioFile)
        time = timeline.duration()
        rate = int(time.rate)

        if rate != context.scene.render.fps:
            box.alert = True
            box.label(
                text="!!! Scene fps is " + str(context.scene.render.fps) + ", imported edit is " + str(rate) + "!!"
            )
            box.alert = False

        box.separator(factor=0.2)
        box.prop(self, "importAtFrame")
        box.prop(self, "reformatShotNames")
        box.prop(self, "createCameras")
        if self.createCameras:
            layout.label(text="Camera Background:")
            row = layout.row(align=True)
            box = row.box()
            box.prop(self, "useMediaAsCameraBG")
            if self.useMediaAsCameraBG:
                box.prop(self, "mediaHaveHandles")
                if self.mediaHaveHandles:
                    box.prop(self, "mediaHandlesDuration")

        layout.separator()

    def execute(self, context):
        #   import opentimelineio as otio
        from random import uniform
        from math import radians

        # print("Otio File: ", self.otioFile)
        props = context.scene.UAS_shot_manager_props
        if len(props.getCurrentTake().getShotList()) != 0:
            bpy.ops.uas_shot_manager.add_take(name=Path(self.otioFile).stem)

        try:
            timeline = otio.adapters.read_from_file(self.otioFile)
            if len(timeline.video_tracks()):
                track = timeline.video_tracks()[0]  # Assume the first one contains the shots.

                cam = None
                if not self.createCameras:  # Create Default Camera
                    # bpy.ops.object.camera_add(location=[0, 0, 0], rotation=[0, 0, 0])  # doesn't return a cam...
                    cam = bpy.data.cameras.new("Camera")
                    cam_ob = bpy.data.objects.new(cam.name, cam)
                    bpy.context.collection.objects.link(cam_ob)
                    bpy.data.cameras[cam.name].lens = 40
                    cam_ob.location = (0.0, 0.0, 0.0)
                    cam_ob.rotation_euler = (radians(90), 0.0, radians(90))

                shot_re = re.compile(r"sh_?(\d+)", re.IGNORECASE)
                for i, clip in enumerate(track.each_clip()):
                    clipName = clip.name
                    if self.createCameras:
                        if self.reformatShotNames:
                            match = shot_re.search(clipName)
                            if match:
                                clipName = context.scene.UAS_shot_manager_props.new_shot_prefix + match.group(1)

                        cam = bpy.data.cameras.new("Cam_" + clipName)
                        cam_ob = bpy.data.objects.new(cam.name, cam)
                        bpy.context.collection.objects.link(cam_ob)
                        bpy.data.cameras[cam.name].lens = 40
                        cam_ob.color = [uniform(0, 1), uniform(0, 1), uniform(0, 1), 1]
                        cam_ob.location = (0.0, i, 0.0)
                        cam_ob.rotation_euler = (radians(90), 0.0, radians(90))

                        # add media as camera background
                        if self.useMediaAsCameraBG:
                            print("Import Otio clip.media_reference.target_url: ", clip.media_reference.target_url)
                            media_path = Path(utils.file_path_from_uri(clip.media_reference.target_url))
                            print("Import Otio media_path: ", media_path)
                            if not media_path.exists():
                                # Lets find it inside next to the xml
                                media_path = Path(self.otioFile).parent.joinpath(media_path.name)
                                print("** not found, so Path(self.otioFile).parent: ", Path(self.otioFile).parent)
                                print("   and new media_path: ", media_path)

                            handlesDuration = 0
                            if self.mediaHaveHandles:
                                handlesDuration = self.mediaHandlesDuration

                            # start frame of the background video is not set here since it will be linked to the shot start frame
                            utils.add_background_video_to_cam(
                                cam, str(media_path), 0, alpha=props.shotsGlobalSettings.backgroundAlpha
                            )

                    shot = props.addShot(
                        name=clipName,
                        start=otio.opentime.to_frames(clip.range_in_parent().start_time) + self.importAtFrame,
                        end=otio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + self.importAtFrame,
                        camera=cam_ob,
                        color=cam_ob.color,  # (cam_ob.color[0], cam_ob.color[1], cam_ob.color[2]),
                    )
                    # bpy.ops.uas_shot_manager.add_shot(
                    #     name=clipName,
                    #     start=otio.opentime.to_frames(clip.range_in_parent().start_time) + self.importAtFrame,
                    #     end=otio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + self.importAtFrame,
                    #     cameraName=cam.name,
                    #     color=(cam_ob.color[0], cam_ob.color[1], cam_ob.color[2]),
                    # )
                    shot.bgImages_linkToShotStart = True
                    shot.bgImages_offset = -1 * handlesDuration

                    # wkip maybe to remove
                    context.scene.frame_start = self.importAtFrame
                    context.scene.frame_end = (
                        otio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + self.importAtFrame
                    )

        except otio.exceptions.NoKnownAdapterForExtensionError:
            from ..utils.utils import ShowMessageBox

            ShowMessageBox("File not recognized", f"{self.otioFile} could not be understood by Opentimelineio", "ERROR")

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, width=500)
        #    res = bpy.ops.uasotio.openfilebrowser("INVOKE_DEFAULT")

        # print("Res: ", res)

        return {"RUNNING_MODAL"}


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_OTIO_OpenFileBrowser(Operator, ImportHelper):  # from bpy_extras.io_utils import ImportHelper
    bl_idname = "uasotio.openfilebrowser"
    bl_label = "Open Otio File"
    bl_description = "Open OTIO file to import a set of shots"

    pathProp: StringProperty()
    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.xml;*.otio", options={"HIDDEN"})

    def execute(self, context):
        """Open OTIO file to import a set of shots"""
        filename, extension = os.path.splitext(self.filepath)
        print("Selected file:", self.filepath)
        print("File name:", filename)
        print("File extension:", extension)

        bpy.ops.uasshotmanager.importotio("INVOKE_DEFAULT", otioFile=self.filepath)

        return {"FINISHED"}

    def invoke(self, context, event):

        # if self.pathProp in context.window_manager.UAS_vse_render:
        #     self.filepath = context.window_manager.UAS_vse_render[self.pathProp]
        # else:
        self.filepath = ""
        # https://docs.blender.org/api/current/bpy.types.WindowManager.html
        #    self.directory = bpy.context.scene.UAS_shot_manager_props.renderRootPath
        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}


_classes = (
    UAS_ShotManager_Export_OTIO,
    UAS_ShotManager_OT_Import_OTIO,
    UAS_OTIO_OpenFileBrowser,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
