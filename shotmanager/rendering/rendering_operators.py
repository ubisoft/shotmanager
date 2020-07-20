import os
import re
import json
from pathlib import Path

import bpy
from bpy.types import Panel, Operator
from bpy.props import EnumProperty, BoolProperty


from ..utils import utils

from ..scripts.rrs.RRS_StampInfo import setRRS_StampInfoSettings

# import opentimelineio as otio

# for file browser:
# from bpy_extras.io_utils import ImportHelper


def get_media_path(out_path, take_name, shot_name):

    if out_path.startswith("//"):
        out_path = str(Path(bpy.data.filepath).parent.absolute()) + out_path[1:]
    return f"{out_path}/{take_name}/{bpy.context.scene.UAS_shot_manager_props.render_shot_prefix}_{shot_name}.mp4"


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
    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    # filter_glob : StringProperty(
    #     default = '*',
    #     options = {'HIDDEN'} )

    def execute(self, context):
        """Open a path browser to define the directory to use to render the images"""
        bpy.context.scene.UAS_shot_manager_props.renderRootPath = self.directory
        return {"FINISHED"}

    def invoke(self, context, event):  # See comments at end  [1]
        #  self.filepath = bpy.context.scene.UAS_shot_manager_props.renderRootPath
        # https://docs.blender.org/api/current/bpy.types.WindowManager.html
        self.directory = bpy.context.scene.UAS_shot_manager_props.renderRootPath
        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}


# class UAS_ShotManager_Explorer ( Operator ):
#     bl_idname = "uas_shot_manager.explorer"
#     bl_label = "Open Explorer"
#     bl_description = "Open Explorer"
#     bl_options = { "INTERNAL" }

#     folder: StringProperty ( )

#     def execute ( self, context ):
#         pathToOpen = self.folder
#         absPathToOpen = bpy.path.abspath(pathToOpen)
#         #wkip pouvoir ouvrir path relatif

#         if Path ( pathToOpen ).exists():
#             subprocess.Popen ( f"explorer \"{bpy.path.abspath(pathToOpen)}\"" )
#         else:
#             print("Open Explorer failed: Path not found: \"" + bpy.path.abspath(pathToOpen) + "\"")

#         return { "FINISHED" }


class UAS_PT_ShotManager_Render(Operator):
    bl_idname = "uas_shot_manager.render"
    bl_label = "Render"
    bl_description = "Render."
    bl_options = {"INTERNAL"}

    renderMode: bpy.props.EnumProperty(
        name="Display Shot Properties Mode",
        description="Update the content of the Shot Properties panel either on the current shot\nor on the shot seleted in the shots list",
        items=(("STILL", "Still", ""), ("ANIMATION", "Animation", ""), ("PROJECT", "Project", "")),
        default="STILL",
    )

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props

        # update UI
        if "STILL" == self.renderMode:
            props.displayStillProps = True
        elif "ANIMATION" == self.renderMode:
            props.displayAnimationProps = True
        elif "PROJECT" == self.renderMode:
            props.displayProjectProps = True
        else:
            props.displayOtioProps = True

        rootPath = props.renderRootPath
        if "" == rootPath:
            rootPath = os.path.dirname(bpy.data.filepath)
        if props.isRenderRootPathValid():
            launchRender(self.renderMode, renderRootFilePath=rootPath, useStampInfo=props.useStampInfoDuringRendering)
        else:
            from ..utils.utils import ShowMessageBox

            ShowMessageBox("Render root path is invalid", "Render Aborted", "ERROR")
            print("Render aborted before start: Invalid Root Path")

        return {"FINISHED"}


def launchRenderWithVSEComposite(renderMode, takeIndex=-1, filePath="", useStampInfo=True):
    """ Generate the media for the specified take
        Return a dictionary with a list of all the created files and a list of failed ones
        filesDict = {"rendered_files": newMediaFiles, "failed_files": failedFiles}
    """
    context = bpy.context
    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props

    projectFps = scene.render.fps

    if props.useProjectRenderSettings:
        props.restoreProjectSettings()
        scene.render.image_settings.file_format = "PNG"
        projectFps = scene.render.fps

    newMediaFiles = []

    rootPath = filePath if "" != filePath else os.path.dirname(bpy.data.filepath)
    if not rootPath.endswith("\\"):
        rootPath += "\\"

    preset_useStampInfo = False
    RRS_StampInfo = None
    if getattr(scene, "UAS_StampInfo_Settings", None) is not None:
        RRS_StampInfo = scene.UAS_StampInfo_Settings

        # remove handlers and compo!!!
        RRS_StampInfo.clearRenderHandlers()
        RRS_StampInfo.clearInfoCompoNodes(scene)

        preset_useStampInfo = useStampInfo
        if not useStampInfo:
            RRS_StampInfo.stampInfoUsed = False
        else:
            RRS_StampInfo.renderRootPathUsed = True
            RRS_StampInfo.renderRootPath = rootPath
            setRRS_StampInfoSettings(scene)

    take = props.getCurrentTake() if -1 == takeIndex else props.getTakeByIndex(takeIndex)
    shotList = take.getShotList(ignoreDisabled=True)

    # sequence composite scene
    sequenceScene = bpy.data.scenes.new(name="VSE_SequenceRenderScene")
    if not sequenceScene.sequence_editor:
        sequenceScene.sequence_editor_create()
    sequenceScene.render.fps = projectFps
    sequenceScene.render.resolution_x = 1280
    sequenceScene.render.resolution_y = 960
    sequenceScene.frame_start = 1
    sequenceScene.frame_end = props.getEditDuration()
    sequenceScene.render.image_settings.file_format = "FFMPEG"
    sequenceScene.render.ffmpeg.format = "MPEG4"
    sequenceScene.render.filepath = f"{rootPath}{take.getName_PathCompliant()}\\{props.render_shot_prefix}.mp4"

    context.window_manager.UAS_shot_manager_handler_toggle = False
    context.window_manager.UAS_shot_manager_display_timeline = False

    if preset_useStampInfo:  # framed output resolution is used only when StampInfo is used
        if "UAS_PROJECT_RESOLUTIONFRAMED" in os.environ.keys():
            resolution = json.loads(os.environ["UAS_PROJECT_RESOLUTIONFRAMED"])
            scene.render.resolution_x = resolution[0]
            scene.render.resolution_y = resolution[1]

    # if props.useProjectRenderSettings:
    #     scene.render.image_settings.file_format = "FFMPEG"
    #     scene.render.ffmpeg.format = "MPEG4"
    if preset_useStampInfo:
        RRS_StampInfo.clearRenderHandlers()
    for i, shot in enumerate(shotList):
        if shot.enabled:
            print("\n----------------------------------------------------")
            print("\n  Shot rendered: ", shot.name)

            # set scene as current
            bpy.context.window.scene = scene
            #     props.setCurrentShotByIndex(i)
            #     props.setSelectedShotByIndex(i)

            newTempRenderPath = ""

            # render stamped info
            if preset_useStampInfo:
                RRS_StampInfo.takeName = take.getName_PathCompliant()
                #    print("RRS_StampInfo.takeName: ", RRS_StampInfo.takeName)
            #        RRS_StampInfo.shotName = f"{props.render_shot_prefix}_{shot.name}"
            #        print("RRS_StampInfo.renderRootPath: ", RRS_StampInfo.renderRootPath)
            # RRS_StampInfo.renderRootPath = (
            #     rootPath + "\\" + take.getName_PathCompliant() + "\\" + shot.getName_PathCompliant() + "\\"
            # )
            # newTempRenderPath = (
            #     rootPath + "\\" + take.getName_PathCompliant() + "\\" + shot.getName_PathCompliant() + "\\"
            # )
            # print("newTempRenderPath: ", newTempRenderPath)

            scene.frame_start = shot.start - props.handles
            scene.frame_end = shot.end + props.handles

            newTempRenderPath = rootPath + take.getName_PathCompliant() + "\\" + shot.getName_PathCompliant() + "\\"
            print("newTempRenderPath: ", newTempRenderPath)

            for currentFrame in range(scene.frame_start, scene.frame_end + 1):
                scene.camera = shot.camera
                scene.frame_start = shot.start - props.handles
                scene.frame_end = shot.end + props.handles
                scene.frame_current = currentFrame
                scene.render.filepath = shot.getOutputFileName(
                    frameIndex=scene.frame_current, fullPath=True, rootFilePath=rootPath
                )
                print("      ------------------------------------------")
                print("      \nFrame: ", currentFrame)
                print("      \nscene.render.filepath: ", scene.render.filepath)
                print("      Current Scene:", scene.name)

                if preset_useStampInfo:
                    RRS_StampInfo.shotName = f"{props.render_shot_prefix}_{shot.name}"
                    RRS_StampInfo.cameraName = shot.camera.name
                    scene.render.resolution_x = 1280
                    scene.render.resolution_y = 960
                    RRS_StampInfo.edit3DFrame = props.getEditTime(shot, currentFrame)

                    print("RRS_StampInfo.takeName: ", RRS_StampInfo.takeName)
                    print("RRS_StampInfo.renderRootPath: ", RRS_StampInfo.renderRootPath)
                    RRS_StampInfo.renderRootPath = newTempRenderPath

                    RRS_StampInfo.renderTmpImageWithStampedInfo(scene, currentFrame)

                # area.spaces[0].region_3d.view_perspective = 'CAMERA'

                scene.render.resolution_x = 1280
                scene.render.resolution_y = 720

                bpy.ops.render.render(animation=False, write_still=True)

            vse_render = context.window_manager.UAS_vse_render
            vse_render.inputOverMediaPath = (scene.render.filepath)[0:-8] + "####" + ".png"
            print("inputOverMediaPath: ", vse_render.inputOverMediaPath)
            vse_render.inputOverResolution = (1280, 720)
            vse_render.inputBGMediaPath = newTempRenderPath + "_tmp_StampInfo.####.png"
            vse_render.inputBGResolution = (1280, 960)

            # compositedMediaPath = shot.getOutputFileName(fullPath=True, rootFilePath=rootPath)     # if we use that the shot .mp4 is rendered in the shot dir
            # here we render in the take dir
            compositedMediaPath = f"{rootPath}{take.getName_PathCompliant()}\\{shot.getOutputFileName(fullPath=False)}"

            vse_render.compositeVideoInVSE(
                projectFps,
                1,
                shot.end - shot.start + 2 * props.handles + 1,
                compositedMediaPath,
                shot.getName_PathCompliant(),
            )
            newMediaFiles.append(compositedMediaPath)

            # bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=True)
            # bpy.ops.render.render('INVOKE_DEFAULT', animation = True)
            # bpy.ops.render.opengl ( animation = True )

            # delete unsused rendered frames
            files_in_directory = os.listdir(newTempRenderPath)
            filtered_files = [file for file in files_in_directory if file.endswith(".png")]

            for file in filtered_files:
                path_to_file = os.path.join(newTempRenderPath, file)
                os.remove(path_to_file)
            try:
                os.rmdir(newTempRenderPath)
            except Exception:
                print("Cannot delete Dir: ", newTempRenderPath)

            vse_render.createNewClip(
                sequenceScene,
                compositedMediaPath,
                1,
                shot.getEditStart() - props.handles,
                offsetStart=props.handles,
                offsetEnd=props.handles,
            )

    # render full sequence
    # Note that here we are back to the sequence scene, not anymore in the shot scene
    bpy.context.window.scene = sequenceScene
    bpy.ops.render.opengl(animation=True, sequencer=True)
    newMediaFiles.append(sequenceScene.render.filepath)
    failedFiles = []

    filesDict = {"rendered_files": newMediaFiles, "failed_files": failedFiles}
    return filesDict


def launchRender(renderMode, renderRootFilePath="", useStampInfo=True):
    print("\n\n*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***")
    print("\n*** uas_shot_manager launchRender ***\n")
    context = bpy.context
    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props

    rootPath = renderRootFilePath if "" != renderRootFilePath else os.path.dirname(bpy.data.filepath)
    print("   rootPath: ", rootPath)

    stampInfoSettings = None
    preset_useStampInfo = False

    if props.use_project_settings and props.isStampInfoAvailable() and useStampInfo:
        stampInfoSettings = scene.UAS_StampInfo_Settings
        preset_useStampInfo = useStampInfo
        #       stampInfoSettings.stampInfoUsed = False
        stampInfoSettings.activateStampInfo = True
    elif props.stampInfoUsed() and useStampInfo:
        stampInfoSettings = scene.UAS_StampInfo_Settings
        stampInfoSettings.activateStampInfo = True
    elif props.isStampInfoAvailable():
        scene.UAS_StampInfo_Settings.activateStampInfo = False

    preset = None
    if "STILL" == renderMode:
        preset = props.renderSettingsStill
        print("   STILL, preset: ", preset.name)
    elif "ANIMATION" == renderMode:
        preset = props.renderSettingsAnim
        print("   ANIMATION, preset: ", preset.name)
    else:
        preset = props.renderSettingsProject
        print("   PROJECT, preset: ", preset.name)

    # with utils.PropertyRestoreCtx ( (scene.render, "filepath"),
    #                         ( scene, "frame_start"),
    #                         ( scene, "frame_end" ),
    #                                 ( scene.render.image_settings, "file_format" ),
    #                                 ( scene.render.ffmpeg, "format" )
    #                               ):
    if True:
        # prepare render settings
        # camera
        # range
        # takes

        take = props.getCurrentTake()
        if take is None:
            print("Shot Manager Rendering: No current take found - Rendering aborted")
            return False
        else:
            take_name = take.name

        context.window_manager.UAS_shot_manager_handler_toggle = False
        context.window_manager.UAS_shot_manager_display_timeline = False

        if props.useProjectRenderSettings:
            props.restoreProjectSettings()

            if preset_useStampInfo:  # framed output resolution is used only when StampInfo is used
                if "UAS_PROJECT_RESOLUTIONFRAMED" in os.environ.keys():
                    resolution = json.loads(os.environ["UAS_PROJECT_RESOLUTIONFRAMED"])
                    scene.render.resolution_x = resolution[0]
                    scene.render.resolution_y = resolution[1]

        # render window
        if "STILL" == preset.renderMode:
            shot = props.getCurrentShot()

            if preset_useStampInfo:
                setRRS_StampInfoSettings(scene)

                # set current cam
                # if None != shot.camera:
            #    props.setCurrentShot(shot)

            # editingCurrentTime = props.getEditCurrentTime( ignoreDisabled = False )
            # editingDuration = props.getEditDuration( ignoreDisabled = True )
            # set_StampInfoShotSettings(  scene, shot.name, take.name,
            #                             #shot.notes,
            #                             shot.camera.name, scene.camera.data.lens,
            #                             edit3DFrame = editingCurrentTime,
            #                             edit3DTotalNumber = editingDuration )

            #        stampInfoSettings.activateStampInfo = True
            #      stampInfoSettings.stampInfoUsed = True

            if props.useProjectRenderSettings:
                scene.render.image_settings.file_format = props.project_images_output_format

            # bpy.ops.render.opengl ( animation = True )
            scene.render.filepath = shot.getOutputFileName(
                frameIndex=scene.frame_current, fullPath=True, rootFilePath=rootPath
            )

            bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=preset.writeToDisk)
        #                bpy.ops.render.view_show()
        #                bpy.ops.render.render(animation=False, use_viewport=True, write_still = preset.writeToDisk)

        elif "ANIMATION" == preset.renderMode:

            shot = props.getCurrentShot()

            if props.renderSettingsAnim.renderWithHandles:
                scene.frame_start = shot.start - props.handles
                scene.frame_end = shot.end + props.handles
            else:
                scene.frame_start = shot.start
                scene.frame_end = shot.end

            print("shot.start: ", shot.start)
            print("scene.frame_start: ", scene.frame_start)

            if preset_useStampInfo:
                stampInfoSettings.stampInfoUsed = False
                stampInfoSettings.activateStampInfo = False
                setRRS_StampInfoSettings(scene)
                stampInfoSettings.activateStampInfo = True
                stampInfoSettings.stampInfoUsed = True

                stampInfoSettings.shotName = shot.name
                stampInfoSettings.takeName = take_name

            # wkip
            if props.useProjectRenderSettings:
                scene.render.image_settings.file_format = "FFMPEG"
                scene.render.ffmpeg.format = "MPEG4"

                scene.render.filepath = shot.getOutputFileName(fullPath=True, rootFilePath=rootPath)
                print("scene.render.filepath: ", scene.render.filepath)

            bpy.ops.render.render("INVOKE_DEFAULT", animation=True)

        else:
            #   wkip to remove
            shot = props.getCurrentShot()
            if preset_useStampInfo:
                stampInfoSettings.stampInfoUsed = False
                stampInfoSettings.activateStampInfo = False
                setRRS_StampInfoSettings(scene)
                stampInfoSettings.activateStampInfo = True
                stampInfoSettings.stampInfoUsed = True

            shots = props.get_shots()

            if props.useProjectRenderSettings:
                scene.render.image_settings.file_format = "FFMPEG"
                scene.render.ffmpeg.format = "MPEG4"

            for i, shot in enumerate(shots):
                if shot.enabled:
                    print("\n  Shot rendered: ", shot.name)
                    #     props.setCurrentShotByIndex(i)
                    #     props.setSelectedShotByIndex(i)

                    scene.camera = shot.camera

                    if preset_useStampInfo:
                        stampInfoSettings.shotName = shot.name
                        stampInfoSettings.takeName = take_name
                        print("stampInfoSettings.takeName: ", stampInfoSettings.takeName)

                    # area.spaces[0].region_3d.view_perspective = 'CAMERA'
                    scene.frame_current = shot.start
                    scene.frame_start = shot.start - props.handles
                    scene.frame_end = shot.end + props.handles
                    scene.render.filepath = shot.getOutputFileName(fullPath=True, rootFilePath=rootPath)
                    print("scene.render.filepath: ", scene.render.filepath)
                    # bpy.ops.render.render('INVOKE_DEFAULT', animation = True)
                    bpy.ops.render.render(animation=True)
                    # bpy.ops.render.opengl ( animation = True )

        # xwkip to remove
        if preset_useStampInfo:
            # scene.UAS_StampInfo_Settings.stampInfoUsed = False
            #  props.useStampInfoDuringRendering = False
            pass


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

            context.window_manager.UAS_shot_manager_handler_toggle = False
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
