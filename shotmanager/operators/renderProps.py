import os
import json
from pathlib import Path

import bpy
from bpy.types import Panel, Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

from ..utils import utils

from ..scripts.RRS_StampInfo import setRRS_StampInfoSettings

# for file browser:
# from bpy_extras.io_utils import ImportHelper


def get_media_path(out_path, take_name, shot_name):

    if out_path.startswith("//"):
        out_path = str(Path(bpy.data.filepath).parent.absolute()) + out_path[1:]
    return f"{out_path}/{take_name}/{bpy.context.scene.UAS_shot_manager_props.render_shot_prefix + shot_name}.mp4"


##########
# Render
##########
class UAS_PT_ShotManagerRenderPanel(Panel):
    bl_label = "Rendering"
    bl_idname = "UAS_PT_ShotManagerRenderPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props

        layout = self.layout
        layout.separator()
        row = layout.row()
        row.separator(factor=3)
        if not props.useProjectRenderSettings:
            row.alert = True
        row.prop(props, "useProjectRenderSettings")
        row.operator("uas_shot_manager.render_restore_project_settings")
        row.operator("uas_shot_manager.render_display_project_settings")
        row.separator(factor=0.1)

        row = layout.row()
        row.separator(factor=3)
        row.prop(props, "useStampInfoDuringRendering")

        row = layout.row(align=True)
        row.separator(factor=3)
        if not props.isRenderRootPathValid():
            row.alert = True
        row.prop(props, "renderRootPath")
        row.alert = False
        row.operator("uas_shot_manager.openpathbrowser", text="", icon="FILEBROWSER", emboss=True)
        row.separator()
        row.operator("uas_shot_manager.render_openexplorer", text="", icon="FILEBROWSER").path = props.renderRootPath
        row.separator()
        layout.separator()

        row = layout.row(align=True)
        row.scale_y = 1.6
        # row.operator ( renderProps.UAS_PT_ShotManager_RenderDialog.bl_idname, text = "Render Active", icon = "RENDER_ANIMATION" ).only_active = True

        # row.use_property_split = True
        # row           = layout.row(align=True)
        # split = row.split ( align = True )
        row.scale_x = 1.2
        row.prop(props, "displayStillProps", text="", icon="IMAGE_DATA")
        row.operator("uas_shot_manager.render", text="Render Image").renderMode = "STILL"
        row.separator(factor=2)

        row.scale_x = 1.2
        row.prop(props, "displayAnimationProps", text="", icon="RENDER_ANIMATION")
        row.operator("uas_shot_manager.render", text="Render Current Shot").renderMode = "ANIMATION"

        row.separator(factor=4)
        row.scale_x = 1.2
        row.prop(props, "displayProjectProps", text="", icon="RENDERLAYERS")
        row.operator("uas_shot_manager.render", text="Render All").renderMode = "PROJECT"

        row = layout.row()
        row.alert = True
        row.operator("uas_shot_manager.lauchrrsrender")
        row.operator("uas_shot_manager.export_otio")
        row.alert = False

        layout.separator(factor=1)

        # STILL ###
        if props.displayStillProps:
            row = layout.row()
            row.label(text="Render Image:")

            box = layout.box()
            row = box.row()
            row.prop(props.renderSettingsStill, "writeToDisk")

            row = box.row()
            filePath = props.getCurrentShot().getOutputFileName(
                frameIndex=bpy.context.scene.frame_current, fullPath=True
            )
            row.label(text="Current Image: " + filePath)
            row.operator("uas_shot_manager.render_openexplorer", text="", icon="FILEBROWSER").path = filePath

        # ANIMATION ###
        elif props.displayAnimationProps:
            row = layout.row()
            row.label(text="Render Current Shot:")

            box = layout.box()
            row = box.row()
            row.prop(props.renderSettingsAnim, "renderWithHandles")

            row = box.row()
            filePath = props.getCurrentShot().getOutputFileName(fullPath=True)
            row.label(text="Current Video: " + filePath)
            row.operator("uas_shot_manager.render_openexplorer", text="", icon="FILEBROWSER").path = filePath

        # PROJECT ###
        elif props.displayProjectProps:
            row = layout.row()
            row.label(text="Render All:")

            box = layout.box()
            row = box.row()
            row.prop(props.renderSettingsProject, "renderAllTakes")
            row.prop(props.renderSettingsProject, "renderAlsoDisabled")

        layout.separator(factor=2)

        # ------------------------

        box = self.layout.box()
        # box.use_property_split = True

        row = box.row()
        if "" == bpy.data.filepath:
            row.alert = True
            row.label(text="*** Save file first ***")
        # elif None == (props.getInfoFileFullPath(context.scene, -1)[0]):
        #     row.alert = True
        #     row.label ( text = "*** Invalid Output Path ***" )
        elif "" == props.getRenderFileName():
            row.alert = True
            row.label(text="*** Invalid Output File Name ***")
        else:
            row.label(text="Ready to render")

        row = box.row()
        row.prop(context.scene.render, "filepath")
        row.operator(
            "uas_shot_manager.render_openexplorer", text="", icon="FILEBROWSER"
        ).path = props.getRenderFileName()

        box = self.layout.box()
        row = box.row()
        # enabled=False
        row.prop(props, "render_shot_prefix")

        # row.separator()
        # row.operator("uas_shot_manager.render_openexplorer", emboss=True, icon='FILEBROWSER', text="")

        self.layout.separator(factor=1)

    def check(self, context):
        # should we redraw when a button is pressed?
        if True:
            return True
        return False

    @classmethod
    def poll(cls, context):
        return len(context.scene.UAS_shot_manager_props.takes) and context.scene.UAS_shot_manager_props.get_shots()


class UAS_OT_OpenPathBrowser(Operator):
    bl_idname = "uas_shot_manager.openpathbrowser"
    bl_label = "Open"
    bl_description = (
        "Open a path browser to define the directory to use to render the images"
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


class UAS_LaunchRRSRender(Operator):
    bl_idname = "uas_shot_manager.lauchrrsrender"
    bl_label = "RRS Render Script"
    bl_description = "Run the RRS Render Script"

    def execute(self, context):
        """Launch RRS Publish script"""
        print(" UAS_LaunchRRSRender")

        from ..scripts import publishRRS

        # publishRRS.publishRRS( context.scene.UAS_shot_manager_props.renderRootPath )
        publishRRS.publishRRS("c:\\tmpRezo\\", verbose=True)
        print("End of Publish")
        return {"FINISHED"}


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


def launchRenderWithVSEComposite(renderMode, renderRootFilePath="", useStampInfo=True):
    """ Generate the media for the specified take
        Return a list of all the created files
    """
    context = bpy.context
    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props

    projectFps = scene.render.fps

    newMediaFiles = []

    rootPath = renderRootFilePath if "" != renderRootFilePath else os.path.dirname(bpy.data.filepath)
    if not rootPath.endswith("\\"):
        rootPath += "\\"

    preset_useStampInfo = False
    if "UAS_StampInfo_Settings" in scene:
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

    take = props.getCurrentTake()
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
    sequenceScene.render.filepath = rootPath + props.render_shot_prefix + ".mp4"

    context.window_manager.UAS_shot_manager_handler_toggle = False
    context.window_manager.UAS_shot_manager_display_timeline = False

    if props.useProjectRenderSettings:
        props.restoreProjectSettings()
        scene.render.image_settings.file_format = "PNG"

    if preset_useStampInfo:  # framed output resolution is used only when StampInfo is used
        if "UAS_PROJECT_RESOLUTIONFRAMED" in os.environ.keys():
            resolution = json.loads(os.environ["UAS_PROJECT_RESOLUTIONFRAMED"])
            scene.render.resolution_x = resolution[0]
            scene.render.resolution_y = resolution[1]

    # if props.useProjectRenderSettings:
    #     scene.render.image_settings.file_format = "FFMPEG"
    #     scene.render.ffmpeg.format = "MPEG4"
    RRS_StampInfo.clearRenderHandlers()
    for i, shot in enumerate(shotList):
        if shot.enabled:
            print("\n----------------------------------------------------")
            print("\n  Shot rendered: ", shot.name)

            # set scene as current
            bpy.context.window.scene = scene
            #     props.setCurrentShotByIndex(i)
            #     props.setSelectedShotByIndex(i)

            # render stamped info
            if preset_useStampInfo:
                RRS_StampInfo.shotName = shot.name
                RRS_StampInfo.takeName = take.getName_PathCompliant()
                print("RRS_StampInfo.takeName: ", RRS_StampInfo.takeName)
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
                    RRS_StampInfo.shotName = shot.name
                    RRS_StampInfo.cameraName = shot.camera.name
                    scene.render.resolution_x = 1280
                    scene.render.resolution_y = 960
                    RRS_StampInfo.edit3DFrame = props.getEditTime(shot, currentFrame)

                    print("RRS_StampInfo.takeName: ", RRS_StampInfo.takeName)
                    print("RRS_StampInfo.renderRootPath: ", RRS_StampInfo.renderRootPath)
                    newTempRenderPath = (
                        rootPath + take.getName_PathCompliant() + "\\" + shot.getName_PathCompliant() + "\\"
                    )
                    print("newTempRenderPath: ", newTempRenderPath)
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

            compositedMediaPath = shot.getOutputFileName(fullPath=True, rootFilePath=rootPath)
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

            vse_render.createNewClip(
                sequenceScene,
                compositedMediaPath,
                1,
                shot.getEditStart(scene) - props.handles,
                offsetStart=props.handles,
                offsetEnd=props.handles,
            )

        # render full sequence
        bpy.context.window.scene = sequenceScene
        bpy.ops.render.opengl(animation=True, sequencer=True)

    return newMediaFiles


def launchRender(renderMode, renderRootFilePath="", useStampInfo=True):
    print("\n\n*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***")
    print("\n*** uas_shot_manager launchRender ***\n")
    context = bpy.context
    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props

    rootPath = renderRootFilePath if "" != renderRootFilePath else os.path.dirname(bpy.data.filepath)
    print("   rootPath: ", rootPath)

    # wkip for debug only:
    #   props.createRenderSettings()
    # tester le chemin

    preset_useStampInfo = False
    if "UAS_StampInfo_Settings" in scene:
        RRS_StampInfo = scene.UAS_StampInfo_Settings
        preset_useStampInfo = useStampInfo
        if not useStampInfo:
            RRS_StampInfo.stampInfoUsed = False
        #    RRS_StampInfo.activateStampInfo = False
        #    props.useStampInfoDuringRendering = False

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
            take_name = ""
        else:
            take_name = take.name

        context.window_manager.UAS_shot_manager_handler_toggle = False
        context.window_manager.UAS_shot_manager_display_timeline = False

        #    shot = props.getCurrentShot()
        # wkip use handles
        # scene.frame_start = shot.start + props.handles
        # scene.frame_end = shot.end + props.handles

        if props.useProjectRenderSettings:
            props.restoreProjectSettings()

            if preset_useStampInfo:  # framed output resolution is used only when StampInfo is used
                if "UAS_PROJECT_RESOLUTIONFRAMED" in os.environ.keys():
                    resolution = json.loads(os.environ["UAS_PROJECT_RESOLUTIONFRAMED"])
                    scene.render.resolution_x = resolution[0]
                    scene.render.resolution_y = resolution[1]

        #   if preset_useStampInfo:
        ################
        #     scene.UAS_StampInfo_Settings.clearRenderHandlers()

        #     #stamper.clearInfoCompoNodes(context.scene)
        #         ### wkip to remove !!! ###
        #     #clear all nodes
        #     allCompoNodes = scene.node_tree
        #     for currentNode in allCompoNodes.nodes:
        #         allCompoNodes.nodes.remove(currentNode)
        #         scene.use_nodes = False

        #     scene.UAS_StampInfo_Settings.registerRenderHandlers()
        # ################

        # props.useStampInfoDuringRendering = False
        #    RRS_StampInfo.stampInfoUsed = False
        #      RRS_StampInfo.activateStampInfo = False
        # setRRS_StampInfoSettings(scene, shot.name)
        #    RRS_StampInfo.activateStampInfo = True
        #    RRS_StampInfo.stampInfoUsed = True
        # props.useStampInfoDuringRendering = True

        #     RRS_StampInfo.projectName = os.environ['UAS_PROJECT_NAME']  #"RR Special"

        print("hEre un 01")

        # render window
        if "STILL" == preset.renderMode:
            print("hEre un 02 still")
            shot = props.getCurrentShot()
            # take = props.getCurrentTake()

            if preset_useStampInfo:
                #       RRS_StampInfo.stampInfoUsed = False
                #      RRS_StampInfo.activateStampInfo = False
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

            #        RRS_StampInfo.activateStampInfo = True
            #      RRS_StampInfo.stampInfoUsed = True

            if props.useProjectRenderSettings:
                scene.render.image_settings.file_format = "PNG"

            # bpy.ops.render.opengl ( animation = True )
            scene.render.filepath = shot.getOutputFileName(
                frameIndex=scene.frame_current, fullPath=True, rootFilePath=rootPath
            )

            print("hEre un 03 still")

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
                RRS_StampInfo.stampInfoUsed = False
                RRS_StampInfo.activateStampInfo = False
                setRRS_StampInfoSettings(scene)
                RRS_StampInfo.activateStampInfo = True
                RRS_StampInfo.stampInfoUsed = True

                RRS_StampInfo.shotName = shot.name
                RRS_StampInfo.takeName = take_name

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
                RRS_StampInfo.stampInfoUsed = False
                RRS_StampInfo.activateStampInfo = False
                setRRS_StampInfoSettings(scene)
                RRS_StampInfo.activateStampInfo = True
                RRS_StampInfo.stampInfoUsed = True

            # if preset.render

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
                        RRS_StampInfo.shotName = shot.name
                        RRS_StampInfo.takeName = take_name
                        print("RRS_StampInfo.takeName: ", RRS_StampInfo.takeName)

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

                if "UAS_StampInfo_Settings" in scene:
                    RRS_StampInfo.setRRS_StampInfoSettings(scene)

                if self.renderer == "OPENGL":
                    bpy.ops.render.opengl(animation=True)
                else:
                    bpy.ops.render.render(animation=True)

                if "UAS_StampInfo_Settings" in scene:
                    scene.UAS_StampInfo_Settings.stampInfoUsed = False
            else:
                for shot in shots:
                    if shot.enabled:
                        scene.frame_start = shot.start - handles
                        scene.frame_end = shot.end + handles
                        scene.render.filepath = get_media_path(out_path, take_name, shot.name)
                        scene.camera = shot.camera
                        if "UAS_StampInfo_Settings" in scene:
                            scene.UAS_StampInfo_Settings.stampInfoUsed = True
                            scene.UAS_StampInfo_Settings.shotName = shot.name

                        if self.renderer == "OPENGL":
                            bpy.ops.render.opengl(animation=True)
                        else:
                            bpy.ops.render.render(animation=True)

                        if "UAS_StampInfo_Settings" in scene:
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


class UAS_ShotManager_Render_DisplayProjectSettings(Operator):
    bl_idname = "uas_shot_manager.render_display_project_settings"
    bl_label = "Project Settings"
    bl_description = "Display Project Settings"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.UAS_shot_manager_props

        settingsList = props.restoreProjectSettings(settingsListOnly=True)

        box = layout.box()

        # grid_flow = row.grid_flow(align=True, row_major=True, columns=2, even_columns=False)

        # col = grid_flow.column(align=False)
        # col.scale_x = 0.6
        # col.label(text="New Shot Name:")

        for prop in settingsList:
            row = box.row(align=True)
            row.label(text=prop[0] + ":")
            row.label(text=str(prop[1]))

        # col = grid_flow.column(align=False)
        # col.prop ( self, "name", text="" )

    def execute(self, context):

        return {"FINISHED"}


######
# IO #
######

# wkip donner en parametre un nom ou indice de take!!!!
def exportOtio(scene, renderRootFilePath="", fps=-1):
    """ Create an OpenTimelineIO XML file for the specified take
        Return the file path of the created file
    """
    print("  ** -- ** exportOtio")
    props = scene.UAS_shot_manager_props

    sceneFps = fps if fps != -1 else scene.render.fps

    import opentimelineio as otio

    take = props.getCurrentTake()
    if take is None:
        print("   *** No Take found - Export OTIO aborted")
        return ""
    else:
        take_name = take.getName_PathCompliant()

    shotList = props.get_shots()

    # wkip note: scene.frame_start probablement à remplacer par start du premier shot enabled!!!
    startFrame = 0
    timeline = otio.schema.Timeline(
        name=scene.name + "_" + take_name, global_start_time=otio.opentime.from_frames(startFrame, sceneFps)
    )
    track = otio.schema.Track()
    timeline.tracks.append(track)

    renderPath = renderRootFilePath if "" != renderRootFilePath else props.renderRootPath
    renderPath += take_name + "\\" + take_name + ".xml"
    if Path(renderPath).suffix == "":
        renderPath += ".otio"

    print("   OTIO renderPath:", renderPath)

    clips = list()
    playhead = 0
    for shot in shotList:
        if shot.enabled:

            # media
            media_duration = shot.end - shot.start + 1 + 2 * props.handles
            start_time, end_time_exclusive = (
                otio.opentime.from_frames(0, sceneFps),
                otio.opentime.from_frames(media_duration, sceneFps),
            )

            available_range = otio.opentime.range_from_start_end_time(start_time, end_time_exclusive)

            shotFilePath = shot.getOutputFileName(fullPath=True)
            shotFileName = shot.getOutputFileName()
            print("    shotFilePath: ", shotFilePath, shotFileName)

            media_reference = otio.schema.ExternalReference(target_url=shotFilePath, available_range=available_range)

            # clip
            clip_start_time, clip_end_time_exclusive = (
                otio.opentime.from_frames(props.handles, sceneFps),
                otio.opentime.from_frames(shot.end - shot.start + 1 + props.handles, sceneFps),
            )
            source_range = otio.opentime.range_from_start_end_time(clip_start_time, clip_end_time_exclusive)
            newClip = otio.schema.Clip(name=shotFileName, source_range=source_range, media_reference=media_reference)
            newClip.metadata = {"clip_name": shot["name"], "camera_name": shot["camera"].name_full}

            clips.append(newClip)
            playhead += media_duration

    track.extend(clips)

    Path(renderPath).parent.mkdir(parents=True, exist_ok=True)
    if renderPath.endswith(".xml"):
        otio.adapters.write_to_file(timeline, renderPath, adapter_name="fcp_xml")
    else:
        otio.adapters.write_to_file(timeline, renderPath)

    return renderPath


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
    createCameras: BoolProperty(
        name="Create Camera for New Shots",
        description="Create a camera for each new shot or use the same camera for all shots",
        default=True,
    )
    reformatShotNames: BoolProperty(
        name="Reformat Shot Names", description="Keep only the shot name part for the name of the shots", default=True,
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)

        box = row.box()
        box.prop(self, "otioFile", text="OTIO File")

        box.separator(factor=0.2)
        box.prop(self, "createCameras")
        box.prop(self, "reformatShotNames")

        layout.separator()

    def execute(self, context):
        import opentimelineio as otio
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
                if not self.createCameras:
                    # bpy.ops.object.camera_add(location=[0, 0, 0], rotation=[0, 0, 0])  # doesn't return a cam...
                    cam = bpy.data.cameras.new("Camera")
                    cam_ob = bpy.data.objects.new(cam.name, cam)
                    bpy.context.collection.objects.link(cam_ob)
                    bpy.data.cameras[cam.name].lens = 40
                    cam_ob.location = (0.0, 0.0, 0.0)
                    cam_ob.rotation_euler = (radians(90), 0.0, radians(90))

                for i, clip in enumerate(track.each_clip()):
                    if self.createCameras:
                        clipName = clip.name
                        if self.reformatShotNames:
                            clipName = clipName.split("_")[2]
                            if clipName[1] == "H":
                                clipName[1] = "h"
                            if clipName[2] == "0":
                                clipName = clipName[0:2] + clipName[3:]

                        cam = bpy.data.cameras.new("Cam_" + clipName)
                        cam_ob = bpy.data.objects.new(cam.name, cam)
                        bpy.context.collection.objects.link(cam_ob)
                        bpy.data.cameras[cam.name].lens = 40
                        cam_ob.color = [uniform(0, 1), uniform(0, 1), uniform(0, 1), 1]
                        cam_ob.location = (0.0, i, 0.0)
                        cam_ob.rotation_euler = (radians(90), 0.0, radians(90))

                    bpy.ops.uas_shot_manager.add_shot(
                        name=clipName,
                        start=otio.opentime.to_frames(clip.range_in_parent().start_time),
                        end=otio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()),
                        cameraName=cam.name,
                        color=(cam_ob.color[0], cam_ob.color[1], cam_ob.color[2]),
                    )

        except otio.exceptions.NoKnownAdapterForExtensionError:
            from ..utils.utils import ShowMessageBox

            ShowMessageBox("File not recognized", f"{self.otioFile} could not be understood by Opentimelineio", "ERROR")

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, width=400)
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
    UAS_PT_ShotManagerRenderPanel,
    UAS_PT_ShotManager_Render,
    UAS_PT_ShotManager_RenderDialog,
    UAS_OT_OpenPathBrowser,
    #    UAS_ShotManager_Explorer,
    UAS_LaunchRRSRender,
    UAS_ShotManager_Render_RestoreProjectSettings,
    UAS_ShotManager_Render_DisplayProjectSettings,
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
