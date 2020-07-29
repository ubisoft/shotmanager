import os

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ImportHelper

import opentimelineio
from .exports import exportOtio

# from shotmanager.otio import imports
from .imports import createShotsFromOtio, importSound


class UAS_ShotManager_Export_OTIO(Operator):
    bl_idname = "uas_shot_manager.export_otio"
    bl_label = "Export otio"
    bl_description = "Export otio"
    bl_options = {"INTERNAL"}

    file: StringProperty()

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props

        if props.isRenderRootPathValid():
            exportOtio(context.scene, filePath=props.renderRootPath, fps=context.scene.render.fps)
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


class UAS_ShotManager_OT_Create_Shots_From_OTIO(Operator):
    bl_idname = "uasshotmanager.createshotsfromotio"
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
        name="Media Have Handles", description="Do imported media use the project handles?", default=False,
    )
    mediaHandlesDuration: IntProperty(
        name="Handles Duration", description="", soft_min=0, min=0, default=10,
    )

    importSoundInVSE: BoolProperty(
        name="Import sound In VSE",
        description="Import sound clips directly into the VSE of the current scene",
        default=True,
    )

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, width=500)
        #    res = bpy.ops.uasotio.openfilebrowser("INVOKE_DEFAULT")

        # print("Res: ", res)

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
        row.prop(self, "importSoundInVSE")

        layout.separator()

    def execute(self, context):
        #   import opentimelineio as otio
        # from random import uniform
        # from math import radians

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
            importSoundInVSE=self.importSoundInVSE,
        )

        return {"FINISHED"}


class UAS_ShotManager_OT_ImportSound_OTIO(Operator):
    bl_idname = "uasshotmanager.importsoundotio"
    bl_label = "Import sound tracks from OTIO File"
    bl_description = "Import sound tracks from OTIO File"
    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    pathProp: StringProperty()
    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.xml;*.otio", options={"HIDDEN"})

    def invoke(self, context, event):

        # if self.pathProp in context.window_manager.UAS_vse_render:
        #     self.filepath = context.window_manager.UAS_vse_render[self.pathProp]
        # else:
        self.filepath = ""
        # https://docs.blender.org/api/current/bpy.types.WindowManager.html
        #    self.directory = bpy.context.scene.UAS_shot_manager_props.renderRootPath

        # to popup the window
        context.window_manager.fileselect_add(self)
        # return {"FINISHED"}
        return {"RUNNING_MODAL"}

    def execute(self, context):
        """Open OTIO file to import a set of shots"""
        filename, extension = os.path.splitext(self.filepath)
        print("Selected file:", self.filepath)
        print("File name:", filename)
        print("File extension:", extension)

        # pathOtio = r"Z:\EvalSofts\Blender\DevPython_Data\UAS_ShotManager_Data\ImportSounds\ExportSounds.xml"
        # importSound(context.scene, pathOtio)
        # or:
        importSound(context.scene, self.filepath)

        # import_otio(
        #     context.scene,
        #     self.filepath,
        #     "",
        #     # "D:/Work/EvalSofts/Blender/DevPython_Data/UAS_ShotManager_Data/ImportSounds/",
        #     r"C:/_UAS_ROOT/RRSpecial/04_ActsPredec/Act01/Act01_Seq0010_Intro/Act01_Seq0010_Exports/",
        # )

        return {"FINISHED"}


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_OTIO_OpenFileBrowser(Operator, ImportHelper):  # from bpy_extras.io_utils import ImportHelper
    bl_idname = "uasotio.openfilebrowser"
    bl_label = "Open Otio File"
    bl_description = "Open OTIO file to import a set of shots"

    pathProp: StringProperty()
    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.xml;*.otio", options={"HIDDEN"})

    def invoke(self, context, event):

        # if self.pathProp in context.window_manager.UAS_vse_render:
        #     self.filepath = context.window_manager.UAS_vse_render[self.pathProp]
        # else:
        self.filepath = ""
        # https://docs.blender.org/api/current/bpy.types.WindowManager.html
        #    self.directory = bpy.context.scene.UAS_shot_manager_props.renderRootPath
        context.window_manager.fileselect_add(self)

        # return {"FINISHED"}
        return {"RUNNING_MODAL"}

    def execute(self, context):
        """Open OTIO file to import a set of shots"""
        filename, extension = os.path.splitext(self.filepath)
        print("Selected file:", self.filepath)
        print("File name:", filename)
        print("File extension:", extension)

        bpy.ops.uasshotmanager.createshotsfromotio("INVOKE_DEFAULT", otioFile=self.filepath)

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_Export_OTIO,
    UAS_ShotManager_OT_Create_Shots_From_OTIO,
    UAS_ShotManager_OT_ImportSound_OTIO,
    UAS_OTIO_OpenFileBrowser,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
