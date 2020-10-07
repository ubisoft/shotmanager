import os
from pathlib import Path
import json
import time

import bpy

from shotmanager.config import config
from shotmanager.scripts.rrs.RRS_StampInfo import setRRS_StampInfoSettings

from shotmanager.utils import utils

import logging

_logger = logging.getLogger(__name__)


# def getCompositedMediaPath(rootPath, shot, specificFrame=None):
#     # props = shot.parentScene.UAS_shot_manager_props
#     takeName = shot.getParentTake().getName_PathCompliant()
#     #    outputFileFormat = props.getOutputFileFormat(isVideo=specificFrame is None)

#     compositedMediaPath = f"{rootPath}{takeName}\\{shot.getOutputFileName(fullPath=False)}"  # .{outputFileFormat}"
#     if specificFrame is not None:
#         compositedMediaPath = (
#             f"{rootPath}{takeName}\\{shot.getOutputFileName(fullPath=False, specificFrame=specificFrame)}"
#         )
#     return compositedMediaPath


def launchRenderWithVSEComposite(
    context,
    renderMode,
    takeIndex=-1,
    filePath="",
    useStampInfo=True,
    stampInfoCustomSettingsDict=None,
    rerenderExistingShotVideos=True,
    fileListOnly=False,
    generateSequenceVideo=True,
    specificShotList=None,
    specificFrame=None,
    render_handles=True,
    renderAlsoDisabled=False,
    area=None,
    override_all_viewports = False
):
    """ Generate the media for the specified take
        Return a dictionary with a list of all the created files and a list of failed ones
        filesDict = {"rendered_files": newMediaFiles, "failed_files": failedFiles}
        specificFrame: When specified, only this frame is rendered. Handles are ignored and the resulting media in an image, not a video
    """

    userRenderSettings = {}

    def _storeUserRenderSettings(context):
        #    userRenderSettings["show_overlays"] = bpy.context.space_data.overlay.show_overlays
        userRenderSettings["resolution_x"] = context.scene.render.resolution_x
        userRenderSettings["resolution_y"] = context.scene.render.resolution_y
        userRenderSettings["render_engine"] = context.scene.render.engine

        userRenderSettings["frame_start"] = scene.frame_start
        userRenderSettings["frame_end"] = scene.frame_end

        userRenderSettings["view_transform"] = bpy.context.scene.view_settings.view_transform

        userRenderSettings["render_use_compositing"] = bpy.context.scene.render.use_compositing
        userRenderSettings["render_use_sequencer"] = bpy.context.scene.render.use_sequencer

        # eevee
        ##############
        # if "BLENDER_EEVEE" == bpy.context.scene.render.engine:
        userRenderSettings["eevee_taa_render_samples"] = context.scene.eevee.taa_render_samples
        userRenderSettings["eevee_taa_samples"] = context.scene.eevee.taa_samples

        # workbench
        ##############
        # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
        userRenderSettings["workbench_render_aa"] = context.scene.display.render_aa
        userRenderSettings["workbench_viewport_aa"] = context.scene.display.viewport_aa

        # cycles
        ##############
        #  if "CYCLES" == bpy.context.scene.render.engine:
        userRenderSettings["cycles_samples"] = context.scene.cycles.samples
        userRenderSettings["cycles_preview_samples"] = context.scene.cycles.preview_samples

        return userRenderSettings

    def _restoreUserRenderSettings(context, userRenderSettings):
        # wkip bug here dans certaines conditions vse
        #    bpy.context.space_data.overlay.show_overlays = userRenderSettings["show_overlays"]

        context.scene.render.resolution_x = userRenderSettings["resolution_x"]
        context.scene.render.resolution_y = userRenderSettings["resolution_y"]
        context.scene.render.engine = userRenderSettings["render_engine"]

        scene.frame_start = userRenderSettings["frame_start"]
        scene.frame_end = userRenderSettings["frame_end"]

        bpy.context.scene.view_settings.view_transform = userRenderSettings["view_transform"]

        bpy.context.scene.render.use_compositing = userRenderSettings["render_use_compositing"]
        bpy.context.scene.render.use_sequencer = userRenderSettings["render_use_sequencer"]

        # eevee
        ##############
        #   if "BLENDER_EEVEE" == bpy.context.scene.render.engine:
        context.scene.eevee.taa_render_samples = userRenderSettings["eevee_taa_render_samples"]
        context.scene.eevee.taa_samples = userRenderSettings["eevee_taa_samples"]

        # workbench
        ##############
        # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
        context.scene.display.render_aa = userRenderSettings["workbench_render_aa"]
        context.scene.display.viewport_aa = userRenderSettings["workbench_viewport_aa"]

        # cycles
        ##############
        #        if "CYCLES" == bpy.context.scene.render.engine:
        context.scene.cycles.samples = userRenderSettings["cycles_samples"]
        context.scene.cycles.preview_samples = userRenderSettings["cycles_preview_samples"]

        return

    def _deleteTempFiles(dirPath):
        # delete unsused rendered frames
        if config.uasDebug:
            print(f"Cleaning shot temp dir: {dirPath}")

        if os.path.exists(dirPath):
            files_in_directory = os.listdir(dirPath)
            filtered_files = [file for file in files_in_directory if file.endswith(".png") or file.endswith(".wav")]

            for file in filtered_files:
                path_to_file = os.path.join(dirPath, file)
                try:
                    os.remove(path_to_file)
                except Exception as e:
                    _logger.exception(f"\n*** File locked (by system?): {path_to_file}")
                    print(f"\n*** File locked (by system?): {path_to_file}")
            try:
                os.rmdir(dirPath)
            except Exception:
                print("Cannot delete Dir: ", dirPath)

    # context = bpy.context
    scene = context.scene
    props = scene.UAS_shot_manager_props
    vse_render = context.window_manager.UAS_vse_render

    currentShot = props.getCurrentShot()

    # it is possible to have handles but not to render them (case of still frame),
    # it is also possible not to use the handles, whitch is different on stamp info
    useHandles = props.areShotHandlesUsed()
    handles = props.getHandlesDuration()

    # handles = 0
    # if useHandles:
    #     handles = props.project_shot_handle_duration if props.use_project_settings else props.handles
    #     handles = max(0, handles)

    # we verify anyway if handles are used
    renderHandles = render_handles and useHandles
    if specificFrame is not None:
        renderHandles = False

    viewportArea = area if area is not None else bpy.context.area

    startRenderintTime = time.monotonic()

    _logger.debug(f"Start Time: {startRenderintTime}")

    # _logger.info(f" *** launchRenderWithVSEComposite")
    # _logger.info(f"    render_shot_prefix: {props.renderShotPrefix()}")

    take = props.getCurrentTake() if -1 == takeIndex else props.getTakeByIndex(takeIndex)
    takeName = take.getName_PathCompliant()
    shotList = take.getShotList(ignoreDisabled=not renderAlsoDisabled) if specificShotList is None else specificShotList

    projectFps = scene.render.fps
    sequenceFileName = props.renderShotPrefix() + takeName

    if props.use_project_settings:
        props.restoreProjectSettings()
        scene.render.image_settings.file_format = props.project_images_output_format
        projectFps = scene.render.fps
        sequenceFileName = props.renderShotPrefix()

    newMediaFiles = []
    sequenceFiles = []  # only enabled shots

    rootPath = filePath if "" != filePath else os.path.dirname(bpy.data.filepath)
    # use absolute path
    rootPath = bpy.path.abspath(rootPath)

    if not rootPath.endswith("\\"):
        rootPath += "\\"

    preset_useStampInfo = False
    RRS_StampInfo = None

    if not fileListOnly:
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

        if preset_useStampInfo:  # framed output resolution is used only when StampInfo is used
            RRS_StampInfo.clearRenderHandlers()

        context.window_manager.UAS_shot_manager_shots_play_mode = False
        context.window_manager.UAS_shot_manager_display_timeline = False

    previousTakeRenderTime = time.monotonic()
    currentTakeRenderTime = previousTakeRenderTime

    previousShotRenderTime = time.monotonic()
    currentShotRenderTime = previousShotRenderTime

    context.scene.use_preview_range = False

    renderFrameByFrame = (
        "PLAYBLAST_LOOP" == props.renderContext.renderComputationMode
        or "ENGINE_LOOP" == props.renderContext.renderComputationMode
    )
    renderWithOpengl = (
        "PLAYBLAST_LOOP" == props.renderContext.renderComputationMode
        or "PLAYBLAST_ANIM" == props.renderContext.renderComputationMode
    )

    userRenderSettings = _storeUserRenderSettings(context)

    if renderWithOpengl:
        spaces = list ( )
        if override_all_viewports:
            for area in context.screen.areas:
                if area.type == "VIEW_3D":
                    for space_data in area.spaces:
                        if space_data.type == "VIEW_3D":
                            spaces.append ( space_data )
        else:
            spaces.append ( context.space_data )
        
        for space_data in spaces:
            if not "CUSTOM" == props.renderContext.renderEngineOpengl:
                context.scene.render.engine = props.renderContext.renderEngineOpengl
                if "BLENDER_EEVEE" == props.renderContext.renderEngineOpengl:
                    if space_data is not None:  # case where Blender is running in background
                        space_data.shading.type = "RENDERED"
                elif "BLENDER_WORKBENCH" == props.renderContext.renderEngineOpengl:
                    if space_data is not None:  # case where Blender is running in background
                        space_data.shading.type = "SOLID"
            if space_data is not None:  # case where Blender is running in background
                space_data.overlay.show_overlays = props.renderContext.useOverlays

                        

    else:
        # wkip hack rrs
        bpy.context.scene.render.use_compositing = False
        bpy.context.scene.render.use_sequencer = False

        if not "CUSTOM" == props.renderContext.renderEngine:
            context.scene.render.engine = props.renderContext.renderEngine

    props.renderContext.applyRenderQualitySettings(context)
    context.scene.view_settings.view_transform = "Standard"

    for i, shot in enumerate(shotList):
        # context.window_manager.UAS_shot_manager_progressbar = (i + 1) / len(shotList) * 100.0
        # bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=2)

        newTempRenderPath = rootPath + takeName + "\\" + shot.getName_PathCompliant() + "\\"
        # compositedMediaPath = shot.getCompositedMediaPath(rootPath, specificFrame=specificFrame)
        compositedMediaPath = shot.getOutputMediaPath(rootPath=rootPath, specificFrame=specificFrame)

        newMediaFiles.append(compositedMediaPath)
        if shot.enabled:
            sequenceFiles.append(compositedMediaPath)

        if not rerenderExistingShotVideos:
            if Path(compositedMediaPath).exists():
                print(f" - File {Path(compositedMediaPath).name} already computed")
                continue

        if not fileListOnly:
            print("\n----------------------------------------------------")
            print("\n  Rendering Shot: ", shot.name)
            print("  ---------------")
            print("\n     newTempRenderPath: ", newTempRenderPath)
            print("     compositedMediaPath: ", compositedMediaPath)

            _deleteTempFiles(newTempRenderPath)

            # set scene as current
            context.window.scene = scene
            #     props.setCurrentShotByIndex(i)
            #     props.setSelectedShotByIndex(i)

            if specificFrame is None:
                if renderHandles:
                    scene.frame_start = shot.start - handles
                    scene.frame_end = shot.end + handles
                else:
                    scene.frame_start = shot.start
                    scene.frame_end = shot.end
            else:
                scene.frame_start = specificFrame
                scene.frame_end = specificFrame

            scene.camera = shot.camera
            print("Scene.name:", scene.name)
            print("Scene.camera:", scene.camera.name)
            if override_all_viewports:
                for area in context.screen.areas:
                    utils.setCurrentCameraToViewport(context, area)
            else:
                utils.setCurrentCameraToViewport(context, viewportArea)
            # props.setCurrentShot(shot)

            numFramesInShot = scene.frame_end - scene.frame_start + 1
            previousFrameRenderTime = time.monotonic()
            currentFrameRenderTime = previousFrameRenderTime

            #######################
            # render image only
            #######################

            renderShotContent = True
            if renderShotContent and not fileListOnly:
                scene.render.resolution_x = 1280
                scene.render.resolution_y = 720

                if renderFrameByFrame:
                    for f, currentFrame in enumerate(range(scene.frame_start, scene.frame_end + 1)):
                        # scene.frame_current = currentFrame
                        scene.frame_set(currentFrame)

                        # scene.render.filepath = shot.getOutputFileName(
                        #     rootFilePath=rootPath, specificFrame=scene.frame_current, fullPath=True
                        # )
                        scene.render.filepath = shot.getOutputMediaPath(
                            rootPath=rootPath, specificFrame=scene.frame_current
                        )

                        print("      ------------------------------------------")
                        print(
                            f"      \nFrame: {currentFrame}    ( {f + 1} / {numFramesInShot} )    -     Shot: {shot.name}"
                        )

                        print("scene.render.filepath (frame by frame): ", scene.render.filepath)
                        if renderWithOpengl:
                            #     _logger.debug("ici loop playblast")

                            bpy.ops.render.opengl(animation=False, write_still=True)

                        else:
                            #     _logger.debug("ici loop pas playblast")
                            bpy.ops.render.render(animation=False, write_still=True)
                            # bpy.ops.render.render(animation=False, write_still=True)

                            currentFrameRenderTime = time.monotonic()
                            print(
                                f"      \nFrame render time: {(currentFrameRenderTime - previousFrameRenderTime):0.2f} sec."
                            )
                            previousFrameRenderTime = currentFrameRenderTime

                        # currentFrameRenderTime = time.monotonic()
                        # print(
                        #     f"      \nFrame render time: {(currentFrameRenderTime - previousFrameRenderTime):0.2f} sec."
                        # )
                        # previousFrameRenderTime = currentFrameRenderTime

                # render all in one anim pass
                else:
                    scene.render.filepath = (
                        shot.getOutputFileName(rootFilePath=rootPath, fullPath=True, noExtension=True) + "_"
                    )
                    print("scene.render.filepath (anim): ", scene.render.filepath)
                    #   _logger.debug("ici PAS loop")
                    if renderWithOpengl:
                        #    _logger.debug("ici PAS loop Playblast opengl")
                        # print(f"scene.frame_start: {scene.frame_start}")
                        # print(f"scene.frame_end: {scene.frame_end}")

                        bpy.ops.render.opengl(animation=True, write_still=False)

                    # _logger.debug("Render Opengl done")
                    else:
                        # _logger.debug("ici PAS loop pas playblast")
                        bpy.ops.render.render(animation=True, write_still=False)

            #######################
            # render stamped info
            #######################
            if preset_useStampInfo:
                renderStampedInfoForShot(
                    RRS_StampInfo,
                    props,
                    takeName,
                    shot,
                    rootPath,
                    newTempRenderPath,
                    handles,
                    render_handles=renderHandles,
                    specificFrame=specificFrame,
                    stampInfoCustomSettingsDict=stampInfoCustomSettingsDict,
                    verbose=False,
                )

            #######################
            # print info
            #######################

            currentShotRenderTime = time.monotonic()
            print(
                f"      \nShot render time (images only): {(currentShotRenderTime - previousShotRenderTime):0.2f} sec."
            )
            print("----------------------------------------")
            previousShotRenderTime = currentShotRenderTime

            if specificFrame is None:
                # render sound
                audioFilePath = (
                    newTempRenderPath + f"{props.renderShotPrefix()}_{shot.getName_PathCompliant()}" + ".wav"
                )
                print(f"\n Sound for shot {shot.name}:")
                print("    audioFilePath: ", audioFilePath)
                # bpy.ops.sound.mixdown(filepath=audioFilePath, relative_path=True, container='WAV', codec='PCM')
                # if my_file.exists():
                #     import os.path
                # os.path.exists(file_path)
                bpy.ops.sound.mixdown(filepath=audioFilePath, relative_path=False, container="WAV", codec="PCM")

            # use vse_render to store all the elements to composite

            # frameIndStr = "####" if specificFrame is None else f"{specificFrame:04}"
            # vse_render.clearMedia(scene)
            # vse_render.inputOverMediaPath = (
            #     newTempRenderPath
            #     + shot.getOutputFileName(fullPath=False, noExtension=True)
            #     + "_"
            #     + frameIndStr
            #     + ".png"
            # )
            if specificFrame is None:
                vse_render.inputOverMediaPath = newTempRenderPath + shot.getOutputMediaPath(
                    providePath=False, genericFrame=True
                )
            else:
                vse_render.inputOverMediaPath = newTempRenderPath + shot.getOutputMediaPath(
                    providePath=False, specificFrame=specificFrame
                )

            _logger.debug(f"\n - OverMediaPath: {vse_render.inputOverMediaPath}")
            vse_render.inputOverResolution = (1280, 720)

            if preset_useStampInfo:
                frameIndStr = "####" if specificFrame is None else f"{specificFrame:04}"
                _logger.debug(f"\n - specificFrame: {specificFrame}")
                vse_render.inputBGMediaPath = newTempRenderPath + "_tmp_StampInfo." + frameIndStr + ".png"
                _logger.debug(f"\n - BGMediaPath: {vse_render.inputBGMediaPath}")
                vse_render.inputBGResolution = (1280, 960)

            if specificFrame is None:
                vse_render.inputAudioMediaPath = audioFilePath

            if specificFrame is None:
                video_frame_end = shot.end - shot.start + 1
                if renderHandles:
                    video_frame_end += 2 * handles

                vse_render.compositeVideoInVSE(
                    projectFps, 1, video_frame_end, compositedMediaPath, shot.getName_PathCompliant(),
                )
            else:
                print(f"compositedMediaPath: {compositedMediaPath}")
                vse_render.compositeVideoInVSE(
                    projectFps, 1, 1, compositedMediaPath, shot.getName_PathCompliant(),
                )

            # bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=True)
            # bpy.ops.render.render('INVOKE_DEFAULT', animation = True)
            # bpy.ops.render.opengl ( animation = True )

            deleteTempFiles = not config.uasDebug_keepVSEContent
            if deleteTempFiles:
                _deleteTempFiles(newTempRenderPath)

    #######################
    # render sequence video
    #######################

    sequenceOutputFullPath = ""
    if generateSequenceVideo and specificFrame is None:
        sequenceOutputFullPath = f"{rootPath}{takeName}\\{sequenceFileName}.{props.getOutputFileFormat()}"
        print("  sequenceOutputFullPath: ", sequenceOutputFullPath)

        if not fileListOnly:
            print(f"sequenceFiles: {sequenceFiles}")
            vse_render.buildSequenceVideo(sequenceFiles, sequenceOutputFullPath, handles, projectFps)

            currentTakeRenderTime = time.monotonic()
            print(f"      \nTake render time: {(currentTakeRenderTime - previousTakeRenderTime):0.2f} sec.")
            print("----------------------------------------")
            previousTakeRenderTime = currentTakeRenderTime

        newMediaFiles.append(sequenceOutputFullPath)

    failedFiles = []

    filesDict = {
        "rendered_files": newMediaFiles,
        "failed_files": failedFiles,
        "sequence_video_file": sequenceOutputFullPath,
    }
    _restoreUserRenderSettings(context, userRenderSettings)
    props.setCurrentShot(currentShot, changeTime=False)

    return filesDict


def renderStampedInfoForFrame(scene, shot):
    pass


def renderStampedInfoForShot(
    stampInfoSettings,
    shotManagerProps,
    takeName,
    shot,
    rootPath,
    newTempRenderPath,
    handles,
    render_handles=True,
    specificFrame=None,
    stampInfoCustomSettingsDict=None,
    verbose=False,
):
    _logger.debug("\n - * - *renderStampedInfoForShot *** ")
    props = shotManagerProps
    scene = props.parentScene

    if stampInfoCustomSettingsDict is not None:
        # print(f"*** customFileFullPath: {stampInfoCustomSettingsDict['customFileFullPath']}")
        if "customFileFullPath" in stampInfoCustomSettingsDict:
            stampInfoSettings.customFileFullPath = stampInfoCustomSettingsDict["customFileFullPath"]

    stampInfoSettings.takeName = takeName

    stampInfoSettings.notesUsed = shot.hasNotes()
    stampInfoSettings.notesLine01 = shot.note01
    stampInfoSettings.notesLine02 = shot.note02
    stampInfoSettings.notesLine03 = shot.note03

    stampInfoSettings.cornerNoteUsed = not shot.enabled
    if not shot.enabled:
        stampInfoSettings.cornerNote = " *** Shot Muted in the take ***"
    else:
        stampInfoSettings.cornerNote = ""

    stampInfoSettings.shotHandles = handles

    # wkipwkipwkip faux!!!!!!!!!
    stampInfoSettings.edit3DTotalNumber = props.getEditDuration()

    ##############
    # save scene state
    ##############

    previousCam = scene.camera
    previousFrameStart = scene.frame_start
    previousFrameEnd = scene.frame_end

    previousResX = scene.render.resolution_x
    previousResY = scene.render.resolution_y

    ##############
    # change scene state
    ##############

    scene.camera = shot.camera

    scene.frame_start = shot.start - handles
    scene.frame_end = shot.end + handles

    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960

    numFramesInShot = scene.frame_end - scene.frame_start + 1

    if props.use_project_settings:
        scene.render.resolution_x = props.project_resolution_framed_x
        scene.render.resolution_y = props.project_resolution_framed_y

    render_frame_start = scene.frame_start
    if specificFrame is not None:
        render_frame_start = specificFrame
    elif not render_handles:
        render_frame_start = shot.start

    render_frame_end = scene.frame_end
    if specificFrame is not None:
        render_frame_end = specificFrame
    elif not render_handles:
        render_frame_end = shot.end

    for f, currentFrame in enumerate(range(render_frame_start, render_frame_end + 1)):

        # to do
        renderStampedInfoForFrame(scene, currentFrame)

        # scene.frame_current = currentFrame
        scene.frame_set(currentFrame)

        # scene.render.filepath = shot.getOutputFileName(
        #     rootFilePath=rootPath, fullPath=True, specificFrame=scene.frame_current
        # )
        scene.render.filepath = shot.getOutputMediaPath(rootPath=rootPath, specificFrame=scene.frame_current)

        if verbose:
            print("      ------------------------------------------")
            print(
                f"      \nStamp Info Frame: {currentFrame}    ( {f + 1} / {numFramesInShot} )    -     Shot: {shot.name}"
            )

        stampInfoSettings.shotName = f"{props.renderShotPrefix()}_{shot.name}"
        # stampInfoSettings.shotName = f"{shot.name}"

        if stampInfoCustomSettingsDict is not None:
            if True or "asset_tracking_step" in stampInfoCustomSettingsDict:
                stampInfoSettings.bottomNoteUsed = True
                stampInfoSettings.bottomNote = "Step: " + stampInfoCustomSettingsDict["asset_tracking_step"]
            else:
                stampInfoSettings.bottomNoteUsed = False
                stampInfoSettings.bottomNote = ""

        stampInfoSettings.cameraName = shot.camera.name
        stampInfoSettings.edit3DFrame = props.getEditTime(shot, currentFrame)
        stampInfoSettings.renderRootPath = newTempRenderPath
        stampInfoSettings.renderTmpImageWithStampedInfo(scene, currentFrame)

    ##############
    # restore scene state
    ##############

    scene.camera = previousCam
    scene.frame_start = previousFrameStart
    scene.frame_end = previousFrameEnd

    scene.render.resolution_x = previousResX
    scene.render.resolution_y = previousResY


def launchRender(context, renderMode, rootPath, useStampInfo=True):
    """
        rootPath: directory to render the files
    """
    context = bpy.context
    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props
    renderDisplayInfo = ""

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

    renderDisplayInfo += "\n\n*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***\n"
    renderDisplayInfo += "\n                                 *** UAS Shot Manager V " + props.version()[0] + " - "

    preset = None
    # renderDisplayInfo += "     - Render mode: "
    if "STILL" == renderMode:
        preset = props.renderSettingsStill
        # renderDisplayInfo += f"   STILL, preset: {preset.name}\n"
        renderDisplayInfo += f"   Render Image"
    elif "ANIMATION" == renderMode:
        preset = props.renderSettingsAnim
        # renderDisplayInfo += f"   ANIMATION, preset: {preset.name}\n"
        renderDisplayInfo += f"   Render Current Shot"
    elif "ALL" == renderMode:
        preset = props.renderSettingsAll
        # renderDisplayInfo += f"   ALL, preset: {preset.name}\n"
        renderDisplayInfo += f"   Render All"
    else:
        preset = props.renderSettingsOtio
        # renderDisplayInfo += f"   EDL, preset: {preset.name}\n"
        renderDisplayInfo += f"   Render EDL File"

    renderDisplayInfo += "  ***"
    renderDisplayInfo += "\n\n*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***\n\n"

    from datetime import datetime

    now = datetime.now()
    renderDisplayInfo += f"   Date: {now.strftime('%b-%d-%Y')}  -  {now.strftime('%H:%M:%S')}\n"

    renderDisplayInfo += f"   - File: {bpy.data.filepath}\n"
    renderDisplayInfo += f"   - Scene: {scene.name}\n"
    renderDisplayInfo += f"   - RootPath: {rootPath}\n"

    renderDisplayInfo += f"\n"
    print(renderDisplayInfo)

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

        context.window_manager.UAS_shot_manager_shots_play_mode = False
        context.window_manager.UAS_shot_manager_display_timeline = False

        # if props.use_project_settings:
        #     props.restoreProjectSettings()

        #     if preset_useStampInfo:  # framed output resolution is used only when StampInfo is used
        #         if "UAS_PROJECT_RESOLUTIONFRAMED" in os.environ.keys():
        #             resolution = json.loads(os.environ["UAS_PROJECT_RESOLUTIONFRAMED"])
        #             scene.render.resolution_x = resolution[0]
        #             scene.render.resolution_y = resolution[1]

        # render window
        if "STILL" == preset.renderMode:
            _logger.debug("Render Animation")

            shot = props.getCurrentShot()

            # get the list of files to write, delete them is they exists, stop everithing if the delete cannot be done
            #            shotFileName = shot.

            willBeRenderedFilesDict = launchRenderWithVSEComposite(
                context,
                "PROJECT",
                filePath=props.renderRootPath,
                generateSequenceVideo=False,
                specificShotList=[shot],
                specificFrame=scene.frame_current,
                fileListOnly=True,
            )
            # willBeRenderedFilesDict

            renderedFilesDict = launchRenderWithVSEComposite(
                context,
                "PROJECT",
                filePath=props.renderRootPath,
                generateSequenceVideo=False,
                specificShotList=[shot],
                specificFrame=scene.frame_current,
            )
            print(json.dumps(renderedFilesDict, indent=4))

        elif "ANIMATION" == preset.renderMode:
            _logger.debug("Render Animation")

            shot = props.getCurrentShot()

            renderedFilesDict = launchRenderWithVSEComposite(
                context,
                "PROJECT",
                filePath=props.renderRootPath,
                generateSequenceVideo=False,
                specificShotList=[shot],
                render_handles=preset.renderHandles if preset.bypass_rendering_project_settings else True,
            )
            print(json.dumps(renderedFilesDict, indent=4))

        elif "ALL" == preset.renderMode:
            print(f"Render All:" + str(props.renderSettingsAll.renderAllTakes))
            print(f"Render All, preset.renderAllTakes: {preset.renderAllTakes}")

            takesToRender = [-1]
            if preset.renderAllTakes:
                print("Render All takes")
                takesToRender = [i for i in range(0, len(props.takes))]

            for takeInd in takesToRender:
                renderedFilesDict = launchRenderWithVSEComposite(
                    context,
                    "PROJECT",
                    takeIndex=takeInd,
                    filePath=props.renderRootPath,
                    fileListOnly=False,
                    rerenderExistingShotVideos=preset.rerenderExistingShotVideos,
                    generateSequenceVideo=preset.generateEditVideo,
                    renderAlsoDisabled=preset.renderAlsoDisabled,
                )

                if preset.renderOtioFile:
                    from shotmanager.otio.exports import exportOtio

                    bpy.context.window.scene = scene
                    renderedOtioFile = exportOtio(
                        scene, takeIndex=takeInd, filePath=props.renderRootPath, fileListOnly=False
                    )
                    # renderedFilesDict["edl_files"] = [renderedOtioFile]
            print(json.dumps(renderedFilesDict, indent=4))

        else:
            pass

        print("Render done\n")
