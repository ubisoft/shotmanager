from pathlib import Path

import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, StringProperty

from .rendering import launchRender

from ..utils import utils


def get_media_path(out_path, take_name, shot_name):

    if out_path.startswith("//"):
        out_path = str(Path(bpy.data.filepath).parent.absolute()) + out_path[1:]
    return f"{out_path}/{take_name}/{bpy.context.scene.UAS_shot_manager_props.renderShotPrefix()}_{shot_name}.mp4"


##########
# Render
##########


class UAS_OT_OpenPathBrowser(Operator):
    bl_idname = "uas_shot_manager.openpathbrowser"
    bl_label = "Open"
    bl_description = (
        "Open a path browser to define the directory to use to render the images\n"
        "Relative path must be set directly in the text field and must start with ''//''"
    )

    # https://docs.blender.org/api/current/bpy.props.html
    #  filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory: StringProperty(subtype="DIR_PATH")

    # filter_glob : StringProperty(
    #     default = '*',
    #     options = {'HIDDEN'} )

    def invoke(self, context, event):  # See comments at end  [1]
        #  self.filepath = bpy.context.scene.UAS_shot_manager_props.renderRootPath
        # https://docs.blender.org/api/current/bpy.types.WindowManager.html
        self.directory = context.scene.UAS_shot_manager_props.renderRootPath
        context.window_manager.fileselect_add(self)

    def execute(self, context):
        """Open a path browser to define the directory to use to render the images"""
        context.scene.UAS_shot_manager_props.renderRootPath = self.directory
        return {"FINISHED"}

        return {"RUNNING_MODAL"}


class UAS_PT_ShotManager_Render(Operator):
    bl_idname = "uas_shot_manager.render"
    bl_label = "Render"
    bl_description = "Render."
    bl_options = {"INTERNAL"}

    renderMode: EnumProperty(
        name="Display Shot Properties Mode",
        description="Update the content of the Shot Properties panel either on the current shot\nor on the shot seleted in the shots list",
        items=(("STILL", "Still", ""), ("ANIMATION", "Animation", ""), ("ALL", "All Edits", ""), ("OTIO", "OTIO", ""),),
        default="STILL",
    )

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props

        # update UI
        if "STILL" == self.renderMode:
            props.displayStillProps = True
        elif "ANIMATION" == self.renderMode:
            props.displayAnimationProps = True
        elif "ALL" == self.renderMode:
            props.displayAllEditsProps = True
        elif "OTIO" == self.renderMode:
            props.displayOtioProps = True

        renderWarnings = ""
        if props.renderRootPath.startswith("//"):
            if "" == bpy.data.filepath:
                renderWarnings = "*** Save file first ***"
        elif "" == props.renderRootPath:
            renderWarnings = "*** Invalid Output File Name ***"

        if "" != renderWarnings:
            from ..utils.utils import ShowMessageBox

            ShowMessageBox(renderWarnings, "Render Aborted", "ERROR")
            print("Render aborted before start: " + renderWarnings)
            return {"CANCELLED"}

        if "OTIO" == self.renderMode:
            bpy.ops.uas_shot_manager.export_otio()
        else:
            filePath = props.renderRootPath
            bpy.path.abspath(filePath)
            if filePath.startswith("//"):
                filePath = bpy.path.abspath(filePath)
            if not (filePath.endswith("/") or filePath.endswith("\\")):
                filePath += "\\"

            # if props.isRenderRootPathValid():
            launchRender(self.renderMode, renderRootFilePath=filePath, useStampInfo=props.useStampInfoDuringRendering)

        return {"FINISHED"}


class UAS_PT_ShotManager_RenderDialog(Operator):
    bl_idname = "uas_shot_manager.renderdialog"
    bl_label = "Render"
    bl_description = "Render"
    bl_options = {"INTERNAL"}

    only_active: BoolProperty(name="Render Only Active", default=False)

    renderer: EnumProperty(
        items=(("BLENDER_EEVEE", "Eevee", ""), ("CYCLES", "Cycles", ""), ("OPENGL", "OpenGL", "")),
        default="BLENDER_EEVEE",
    )

    def execute(self, context):

        print("*** uas_shot_manager.renderDialog ***")

        scene = context.scene
        context.space_data.region_3d.view_perspective = "CAMERA"
        handles = context.scene.UAS_shot_manager_props.handles
        props = scene.UAS_shot_manager_props

        with utils.PropertyRestoreCtx(
            (scene.render, "filepath"),
            (scene, "frame_start"),
            (scene, "frame_end"),
            (scene.render.image_settings, "file_format"),
            (scene.render.ffmpeg, "format"),
            (scene.render, "engine"),
            (scene.render, "resolution_x"),
            (scene.render, "resolution_y"),
        ):

            scene.render.image_settings.file_format = "FFMPEG"
            scene.render.ffmpeg.format = "MPEG4"

            if self.renderer != "OPENGL":
                scene.render.engine = self.renderer

            context.window_manager.UAS_shot_manager_shots_play_mode = False
            context.window_manager.UAS_shot_manager_display_timeline = False

            out_path = scene.render.filepath
            shots = props.get_shots()
            take = props.getCurrentTake()
            if take is None:
                take_name = ""
            else:
                take_name = take.name

            if self.only_active:
                shot = scene.UAS_shot_manager_props.getCurrentShot()
                if shot is None:
                    return {"CANCELLED"}
                scene.frame_start = shot.start - handles
                scene.frame_end = shot.end + handles
                scene.render.filepath = get_media_path(out_path, take_name, shot.name)
                print("      scene.render.filepath: ", scene.render.filepath)

                scene.camera = shot.camera

                if getattr(scene, "UAS_StampInfo_Settings", None) is not None:
                    RRS_StampInfo.setRRS_StampInfoSettings(scene)

                if self.renderer == "OPENGL":
                    bpy.ops.render.opengl(animation=True)
                else:
                    bpy.ops.render.render(animation=True)

                if getattr(scene, "UAS_StampInfo_Settings", None) is not None:
                    scene.UAS_StampInfo_Settings.stampInfoUsed = False
            else:
                for shot in shots:
                    if shot.enabled:
                        scene.frame_start = shot.start - handles
                        scene.frame_end = shot.end + handles
                        scene.render.filepath = get_media_path(out_path, take_name, shot.name)
                        scene.camera = shot.camera
                        if getattr(scene, "UAS_StampInfo_Settings", None) is not None:
                            scene.UAS_StampInfo_Settings.stampInfoUsed = True
                            scene.UAS_StampInfo_Settings.shotName = shot.name

                        if self.renderer == "OPENGL":
                            bpy.ops.render.opengl(animation=True)
                        else:
                            bpy.ops.render.render(animation=True)

                        if getattr(scene, "UAS_StampInfo_Settings", None) is not None:
                            scene.UAS_StampInfo_Settings.stampInfoUsed = False

            scene.UAS_StampInfo_Settings.restorePreviousValues(scene)
            print(" --- RRS Settings Restored ---")

        return {"FINISHED"}

    def draw(self, context):
        l = self.layout
        row = l.row()
        row.prop(self, "renderer")

    # def invoke ( self, context, event ):
    #     wm = context.window_manager
    #     return wm.invoke_props_dialog ( self )


###########
# utils
###########


class UAS_ShotManager_Render_RestoreProjectSettings(Operator):
    bl_idname = "uas_shot_manager.render_restore_project_settings"
    bl_label = "Restore Project Settings"
    bl_description = "Restore Project Settings"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.scene.UAS_shot_manager_props.restoreProjectSettings()
        return {"FINISHED"}


_classes = (
    UAS_PT_ShotManager_Render,
    UAS_PT_ShotManager_RenderDialog,
    UAS_OT_OpenPathBrowser,
    #    UAS_ShotManager_Explorer,
    UAS_ShotManager_Render_RestoreProjectSettings,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
