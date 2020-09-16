import logging

_logger = logging.getLogger(__name__)

import os
import json

import bpy

from ..config import config
from ..scripts.rrs.RRS_StampInfo import setRRS_StampInfoSettings

from shotmanager.utils import utils


def launchRenderWithVSEComposite_old(
    renderMode,
    takeIndex=-1,
    filePath="",
    useStampInfo=True,
    fileListOnly=False,
    generateSequenceVideo=True,
    specificShotList=None,
    handles=0,
):
    """ Generate the media for the specified take
        Return a dictionary with a list of all the created files and a list of failed ones
        filesDict = {"rendered_files": newMediaFiles, "failed_files": failedFiles}
    """
    context = bpy.context
    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props
    videoFileFormat = "mp4"

    fileListOnly = False
    import time

    startRenderintTime = time.monotonic()

    print(f"Start Time: {startRenderintTime}")

    _logger.info(f" *** launchRenderWithVSEComposite")
    _logger.info(f"    render_shot_prefix: {props.renderShotPrefix()}")

    take = props.getCurrentTake() if -1 == takeIndex else props.getTakeByIndex(takeIndex)
    takeName = take.getName_PathCompliant()
    shotList = take.getShotList(ignoreDisabled=True) if specificShotList is None else specificShotList

    projectFps = scene.render.fps
    sequenceFileName = props.renderShotPrefix() + takeName
    print("  sequenceFileName 1: ", sequenceFileName)

    if props.use_project_settings:
        props.restoreProjectSettings()
        scene.render.image_settings.file_format = "PNG"
        projectFps = scene.render.fps
        sequenceFileName = props.renderShotPrefix()

    print("  sequenceFileName 2: ", sequenceFileName)
    newMediaFiles = []

    rootPath = filePath if "" != filePath else os.path.dirname(bpy.data.filepath)
    # use absolute path
    rootPath = bpy.path.abspath(rootPath)

    if not rootPath.endswith("\\"):
        rootPath += "\\"

    sequenceOutputFullPath = f"{rootPath}{takeName}\\{sequenceFileName}.{videoFileFormat}"
    print("  sequenceOutputFullPath: ", sequenceOutputFullPath)

    preset_useStampInfo = False
    RRS_StampInfo = None

    sequenceScene = None

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

        sequenceScene = None
        if generateSequenceVideo:
            # sequence composite scene
            sequenceScene = bpy.data.scenes.new(name="VSE_SequenceRenderScene")
            if not sequenceScene.sequence_editor:
                sequenceScene.sequence_editor_create()
            sequenceScene.render.fps = projectFps
            sequenceScene.render.resolution_x = 1280
            sequenceScene.render.resolution_y = 960
            sequenceScene.frame_start = 0
            sequenceScene.frame_end = props.getEditDuration() - 1
            sequenceScene.render.image_settings.file_format = "FFMPEG"
            sequenceScene.render.ffmpeg.format = "MPEG4"
            sequenceScene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
            sequenceScene.render.ffmpeg.gopsize = 5  # keyframe interval
            sequenceScene.render.ffmpeg.audio_codec = "AC3"
            sequenceScene.render.filepath = sequenceOutputFullPath

        context.window_manager.UAS_shot_manager_shots_play_mode = False
        context.window_manager.UAS_shot_manager_display_timeline = False

    previousTakeRenderTime = time.monotonic()
    currentTakeRenderTime = previousTakeRenderTime

    previousShotRenderTime = time.monotonic()
    currentShotRenderTime = previousShotRenderTime

    bpy.context.scene.use_preview_range = False

    renderFrameByFrame = (
        "PLAYBLAST_LOOP" == props.renderContext.renderComputationMode
        or "ENGINE_LOOP" == props.renderContext.renderComputationMode
    )
    renderWithOpengl = (
        "PLAYBLAST_LOOP" == props.renderContext.renderComputationMode
        or "PLAYBLAST_ANIM" == props.renderContext.renderComputationMode
    )

    if (
        "PLAYBLAST_LOOP" == props.renderContext.renderComputationMode
        or "PLAYBLAST_ANIM" == props.renderContext.renderComputationMode
    ):
        if not "CUSTOM" == props.renderContext.renderEngineOpengl:
            bpy.context.scene.render.engine = props.renderContext.renderEngineOpengl
    else:
        if not "CUSTOM" == props.renderContext.renderEngine:
            bpy.context.scene.render.engine = props.renderContext.renderEngine

    userRenderSettings = {}

    def _storeUserRenderSettings():
        userRenderSettings["show_overlays"] = bpy.context.space_data.overlay.show_overlays
        userRenderSettings["resolution_x"] = bpy.context.scene.render.resolution_x
        userRenderSettings["resolution_y"] = bpy.context.scene.render.resolution_y
        userRenderSettings["render_engine"] = bpy.context.scene.render.engine

        # eevee
        ##############
        # if "BLENDER_EEVEE" == bpy.context.scene.render.engine:
        userRenderSettings["eevee_taa_render_samples"] = bpy.context.scene.eevee.taa_render_samples
        userRenderSettings["eevee_taa_samples"] = bpy.context.scene.eevee.taa_samples

        # workbench
        ##############
        # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
        userRenderSettings["workbench_render_aa"] = bpy.context.scene.display.render_aa
        userRenderSettings["workbench_viewport_aa"] = bpy.context.scene.display.viewport_aa

        # cycles
        ##############
        #  if "CYCLES" == bpy.context.scene.render.engine:
        userRenderSettings["cycles_samples"] = bpy.context.scene.cycles.samples
        userRenderSettings["cycles_preview_samples"] = bpy.context.scene.cycles.preview_samples

        return userRenderSettings

    def _restoreUserRenderSettings(userRenderSettings):
        bpy.context.space_data.overlay.show_overlays = userRenderSettings["show_overlays"]
        bpy.context.scene.render.resolution_x = userRenderSettings["resolution_x"]
        bpy.context.scene.render.resolution_y = userRenderSettings["resolution_y"]
        bpy.context.scene.render.engine = userRenderSettings["render_engine"]

        # eevee
        ##############
        #   if "BLENDER_EEVEE" == bpy.context.scene.render.engine:
        bpy.context.scene.eevee.taa_render_samples = userRenderSettings["eevee_taa_render_samples"]
        bpy.context.scene.eevee.taa_samples = userRenderSettings["eevee_taa_samples"]

        # workbench
        ##############
        # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
        bpy.context.scene.display.render_aa = userRenderSettings["workbench_render_aa"]
        bpy.context.scene.display.viewport_aa = userRenderSettings["workbench_viewport_aa"]

        # cycles
        ##############
        #        if "CYCLES" == bpy.context.scene.render.engine:
        bpy.context.scene.cycles.samples = userRenderSettings["cycles_samples"]
        bpy.context.scene.cycles.preview_samples = userRenderSettings["cycles_preview_samples"]

        return

    userRenderSettings = _storeUserRenderSettings()

    props.renderContext.applyRenderQualitySettings()

    for i, shot in enumerate(shotList):
        # context.window_manager.UAS_shot_manager_progressbar = (i + 1) / len(shotList) * 100.0
        # bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=2)

        if True:  # shot.enabled:

            newTempRenderPath = rootPath + takeName + "\\" + shot.getName_PathCompliant() + "\\"

            # compositedMediaPath = shot.getOutputFileName(fullPath=True, rootFilePath=rootPath)     # if we use that the shot .mp4 is rendered in the shot dir
            # here we render in the take dir
            compositedMediaPath = f"{rootPath}{takeName}\\{shot.getOutputFileName(fullPath=False)}.{videoFileFormat}"
            newMediaFiles.append(compositedMediaPath)

            if not fileListOnly:
                print("\n----------------------------------------------------")
                print("\n  Shot rendered: ", shot.name)
                print("newTempRenderPath: ", newTempRenderPath)

                # set scene as current
                bpy.context.window.scene = scene
                #     props.setCurrentShotByIndex(i)
                #     props.setSelectedShotByIndex(i)

                scene.frame_start = shot.start - handles
                scene.frame_end = shot.end + handles
                scene.camera = shot.camera
                print("Scene.name:", scene.name)
                print("Scene.camera:", scene.camera)
                utils.setCurrentCameraToViewport()
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
                            scene.render.filepath = shot.getOutputFileName(
                                frameIndex=scene.frame_current, fullPath=True, rootFilePath=rootPath
                            )
                            print("      ------------------------------------------")
                            print(
                                f"      \nFrame: {currentFrame}    ( {f + 1} / {numFramesInShot} )    -     Shot: {shot.name}"
                            )

                            print("scene.render.filepath: ", scene.render.filepath)
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
                            shot.getOutputFileName(frameIndex=-1, fullPath=True, rootFilePath=rootPath) + "_"
                        )
                        print("scene.render.filepath: ", scene.render.filepath)
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
                        RRS_StampInfo, props, takeName, shot, rootPath, newTempRenderPath, handles, verbose=False
                    )

                #######################
                # print info
                #######################

                if not fileListOnly:
                    currentShotRenderTime = time.monotonic()
                    print(
                        f"      \nShot render time (images only): {(currentShotRenderTime - previousShotRenderTime):0.2f} sec."
                    )
                    print("----------------------------------------")
                    previousShotRenderTime = currentShotRenderTime

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
                vse_render = context.window_manager.UAS_vse_render
                vse_render.inputOverMediaPath = (scene.render.filepath)[0:-8] + "####" + ".png"
                #    print("inputOverMediaPath: ", vse_render.inputOverMediaPath)
                vse_render.inputOverResolution = (1280, 720)
                vse_render.inputBGMediaPath = newTempRenderPath + "_tmp_StampInfo.####.png"
                vse_render.inputBGResolution = (1280, 960)
                vse_render.inputAudioMediaPath = audioFilePath

                vse_render.compositeVideoInVSE(
                    projectFps,
                    1,
                    shot.end - shot.start + 2 * handles + 1,
                    compositedMediaPath,
                    shot.getName_PathCompliant(),
                )

                # bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=True)
                # bpy.ops.render.render('INVOKE_DEFAULT', animation = True)
                # bpy.ops.render.opengl ( animation = True )

                # delete unsused rendered frames
                files_in_directory = os.listdir(newTempRenderPath)
                filtered_files = [file for file in files_in_directory if file.endswith(".png") or file.endswith(".wav")]

                deleteTempFiles = True
                if deleteTempFiles:
                    for file in filtered_files:
                        path_to_file = os.path.join(newTempRenderPath, file)
                        os.remove(path_to_file)
                    try:
                        os.rmdir(newTempRenderPath)
                    except Exception:
                        print("Cannot delete Dir: ", newTempRenderPath)

                # print(f"shot.getEditStart: {shot.getEditStart()}, handles: {handles}")

                if generateSequenceVideo:
                    # audio clip
                    vse_render.createNewClip(
                        sequenceScene,
                        compositedMediaPath,
                        sequenceScene.frame_start,
                        shot.getEditStart() - handles,
                        offsetStart=handles,
                        offsetEnd=handles,
                        importVideo=False,
                        importAudio=True,
                    )

                    # video clip
                    vse_render.createNewClip(
                        sequenceScene,
                        compositedMediaPath,
                        sequenceScene.frame_start,
                        shot.getEditStart() - handles,
                        offsetStart=handles,
                        offsetEnd=handles,
                        importVideo=True,
                        importAudio=False,
                    )

    if not fileListOnly:
        # render full sequence
        # Note that here we are back to the sequence scene, not anymore in the shot scene

        #######################
        # render sequence video
        #######################

        if generateSequenceVideo:
            bpy.context.window.scene = sequenceScene
            bpy.ops.render.opengl(animation=True, sequencer=True)

            # cleaning current file from temp scenes
            if not config.uasDebug:
                # current scene is sequenceScene
                bpy.ops.scene.delete()

        currentTakeRenderTime = time.monotonic()
        print(f"      \nTake render time: {(currentTakeRenderTime - previousTakeRenderTime):0.2f} sec.")
        print("----------------------------------------")
        previousTakeRenderTime = currentTakeRenderTime

    newMediaFiles.append(sequenceOutputFullPath)
    failedFiles = []

    filesDict = {"rendered_files": newMediaFiles, "failed_files": failedFiles}

    _restoreUserRenderSettings(userRenderSettings)

    return filesDict


def launchRenderWithVSEComposite(
    renderMode,
    takeIndex=-1,
    filePath="",
    useStampInfo=True,
    fileListOnly=False,
    generateSequenceVideo=True,
    specificShotList=None,
    handles=0,
):
    """ Generate the media for the specified take
        Return a dictionary with a list of all the created files and a list of failed ones
        filesDict = {"rendered_files": newMediaFiles, "failed_files": failedFiles}
    """
    context = bpy.context
    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props
    videoFileFormat = "mp4"

    fileListOnly = False
    import time

    startRenderintTime = time.monotonic()

    print(f"Start Time: {startRenderintTime}")

    _logger.info(f" *** launchRenderWithVSEComposite")
    _logger.info(f"    render_shot_prefix: {props.renderShotPrefix()}")

    take = props.getCurrentTake() if -1 == takeIndex else props.getTakeByIndex(takeIndex)
    takeName = take.getName_PathCompliant()
    shotList = take.getShotList(ignoreDisabled=True) if specificShotList is None else specificShotList

    projectFps = scene.render.fps
    sequenceFileName = props.renderShotPrefix() + takeName
    print("  sequenceFileName 1: ", sequenceFileName)

    if props.use_project_settings:
        props.restoreProjectSettings()
        scene.render.image_settings.file_format = "PNG"
        projectFps = scene.render.fps
        sequenceFileName = props.renderShotPrefix()

    print("  sequenceFileName 2: ", sequenceFileName)
    newMediaFiles = []

    rootPath = filePath if "" != filePath else os.path.dirname(bpy.data.filepath)
    # use absolute path
    rootPath = bpy.path.abspath(rootPath)

    if not rootPath.endswith("\\"):
        rootPath += "\\"

    sequenceOutputFullPath = f"{rootPath}{takeName}\\{sequenceFileName}.{videoFileFormat}"
    print("  sequenceOutputFullPath: ", sequenceOutputFullPath)

    preset_useStampInfo = False
    RRS_StampInfo = None

    sequenceScene = None

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

        # sequenceScene = None
        # if generateSequenceVideo:
        #     # sequence composite scene
        #     sequenceScene = bpy.data.scenes.new(name="VSE_SequenceRenderScene")
        #     if not sequenceScene.sequence_editor:
        #         sequenceScene.sequence_editor_create()
        #     sequenceScene.render.fps = projectFps
        #     sequenceScene.render.resolution_x = 1280
        #     sequenceScene.render.resolution_y = 960
        #     sequenceScene.frame_start = 0
        #     sequenceScene.frame_end = props.getEditDuration() - 1
        #     sequenceScene.render.image_settings.file_format = "FFMPEG"
        #     sequenceScene.render.ffmpeg.format = "MPEG4"
        #     sequenceScene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
        #     sequenceScene.render.ffmpeg.gopsize = 5  # keyframe interval
        #     sequenceScene.render.ffmpeg.audio_codec = "AC3"
        #     sequenceScene.render.filepath = sequenceOutputFullPath

        context.window_manager.UAS_shot_manager_shots_play_mode = False
        context.window_manager.UAS_shot_manager_display_timeline = False

    previousTakeRenderTime = time.monotonic()
    currentTakeRenderTime = previousTakeRenderTime

    previousShotRenderTime = time.monotonic()
    currentShotRenderTime = previousShotRenderTime

    bpy.context.scene.use_preview_range = False

    renderFrameByFrame = (
        "PLAYBLAST_LOOP" == props.renderContext.renderComputationMode
        or "ENGINE_LOOP" == props.renderContext.renderComputationMode
    )
    renderWithOpengl = (
        "PLAYBLAST_LOOP" == props.renderContext.renderComputationMode
        or "PLAYBLAST_ANIM" == props.renderContext.renderComputationMode
    )

    if (
        "PLAYBLAST_LOOP" == props.renderContext.renderComputationMode
        or "PLAYBLAST_ANIM" == props.renderContext.renderComputationMode
    ):
        if not "CUSTOM" == props.renderContext.renderEngineOpengl:
            bpy.context.scene.render.engine = props.renderContext.renderEngineOpengl
    else:
        if not "CUSTOM" == props.renderContext.renderEngine:
            bpy.context.scene.render.engine = props.renderContext.renderEngine

    userRenderSettings = {}

    def _storeUserRenderSettings():
        userRenderSettings["show_overlays"] = bpy.context.space_data.overlay.show_overlays
        userRenderSettings["resolution_x"] = bpy.context.scene.render.resolution_x
        userRenderSettings["resolution_y"] = bpy.context.scene.render.resolution_y
        userRenderSettings["render_engine"] = bpy.context.scene.render.engine

        # eevee
        ##############
        # if "BLENDER_EEVEE" == bpy.context.scene.render.engine:
        userRenderSettings["eevee_taa_render_samples"] = bpy.context.scene.eevee.taa_render_samples
        userRenderSettings["eevee_taa_samples"] = bpy.context.scene.eevee.taa_samples

        # workbench
        ##############
        # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
        userRenderSettings["workbench_render_aa"] = bpy.context.scene.display.render_aa
        userRenderSettings["workbench_viewport_aa"] = bpy.context.scene.display.viewport_aa

        # cycles
        ##############
        #  if "CYCLES" == bpy.context.scene.render.engine:
        userRenderSettings["cycles_samples"] = bpy.context.scene.cycles.samples
        userRenderSettings["cycles_preview_samples"] = bpy.context.scene.cycles.preview_samples

        return userRenderSettings

    def _restoreUserRenderSettings(userRenderSettings):
        bpy.context.space_data.overlay.show_overlays = userRenderSettings["show_overlays"]
        bpy.context.scene.render.resolution_x = userRenderSettings["resolution_x"]
        bpy.context.scene.render.resolution_y = userRenderSettings["resolution_y"]
        bpy.context.scene.render.engine = userRenderSettings["render_engine"]

        # eevee
        ##############
        #   if "BLENDER_EEVEE" == bpy.context.scene.render.engine:
        bpy.context.scene.eevee.taa_render_samples = userRenderSettings["eevee_taa_render_samples"]
        bpy.context.scene.eevee.taa_samples = userRenderSettings["eevee_taa_samples"]

        # workbench
        ##############
        # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
        bpy.context.scene.display.render_aa = userRenderSettings["workbench_render_aa"]
        bpy.context.scene.display.viewport_aa = userRenderSettings["workbench_viewport_aa"]

        # cycles
        ##############
        #        if "CYCLES" == bpy.context.scene.render.engine:
        bpy.context.scene.cycles.samples = userRenderSettings["cycles_samples"]
        bpy.context.scene.cycles.preview_samples = userRenderSettings["cycles_preview_samples"]

        return

    userRenderSettings = _storeUserRenderSettings()

    props.renderContext.applyRenderQualitySettings()

    for i, shot in enumerate(shotList):
        # context.window_manager.UAS_shot_manager_progressbar = (i + 1) / len(shotList) * 100.0
        # bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=2)

        if True:  # shot.enabled:

            newTempRenderPath = rootPath + takeName + "\\" + shot.getName_PathCompliant() + "\\"

            # compositedMediaPath = shot.getOutputFileName(fullPath=True, rootFilePath=rootPath)     # if we use that the shot .mp4 is rendered in the shot dir
            # here we render in the take dir
            compositedMediaPath = f"{rootPath}{takeName}\\{shot.getOutputFileName(fullPath=False)}.{videoFileFormat}"
            newMediaFiles.append(compositedMediaPath)

            if not fileListOnly:
                print("\n----------------------------------------------------")
                print("\n  Shot rendered: ", shot.name)
                print("newTempRenderPath: ", newTempRenderPath)

                # set scene as current
                bpy.context.window.scene = scene
                #     props.setCurrentShotByIndex(i)
                #     props.setSelectedShotByIndex(i)

                scene.frame_start = shot.start - handles
                scene.frame_end = shot.end + handles
                scene.camera = shot.camera
                print("Scene.name:", scene.name)
                print("Scene.camera:", scene.camera)
                utils.setCurrentCameraToViewport()
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
                            scene.render.filepath = shot.getOutputFileName(
                                frameIndex=scene.frame_current, fullPath=True, rootFilePath=rootPath
                            )
                            print("      ------------------------------------------")
                            print(
                                f"      \nFrame: {currentFrame}    ( {f + 1} / {numFramesInShot} )    -     Shot: {shot.name}"
                            )

                            print("scene.render.filepath: ", scene.render.filepath)
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
                            shot.getOutputFileName(frameIndex=-1, fullPath=True, rootFilePath=rootPath) + "_"
                        )
                        print("scene.render.filepath: ", scene.render.filepath)
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
                        RRS_StampInfo, props, takeName, shot, rootPath, newTempRenderPath, handles, verbose=False
                    )

                #######################
                # print info
                #######################

                if not fileListOnly:
                    currentShotRenderTime = time.monotonic()
                    print(
                        f"      \nShot render time (images only): {(currentShotRenderTime - previousShotRenderTime):0.2f} sec."
                    )
                    print("----------------------------------------")
                    previousShotRenderTime = currentShotRenderTime

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
                vse_render = context.window_manager.UAS_vse_render
                vse_render.inputOverMediaPath = (scene.render.filepath)[0:-8] + "####" + ".png"
                #    print("inputOverMediaPath: ", vse_render.inputOverMediaPath)
                vse_render.inputOverResolution = (1280, 720)
                vse_render.inputBGMediaPath = newTempRenderPath + "_tmp_StampInfo.####.png"
                vse_render.inputBGResolution = (1280, 960)
                vse_render.inputAudioMediaPath = audioFilePath

                vse_render.compositeVideoInVSE(
                    projectFps,
                    1,
                    shot.end - shot.start + 2 * handles + 1,
                    compositedMediaPath,
                    shot.getName_PathCompliant(),
                )

                # bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=True)
                # bpy.ops.render.render('INVOKE_DEFAULT', animation = True)
                # bpy.ops.render.opengl ( animation = True )

                # delete unsused rendered frames
                files_in_directory = os.listdir(newTempRenderPath)
                filtered_files = [file for file in files_in_directory if file.endswith(".png") or file.endswith(".wav")]

                deleteTempFiles = True
                if deleteTempFiles:
                    for file in filtered_files:
                        path_to_file = os.path.join(newTempRenderPath, file)
                        os.remove(path_to_file)
                    try:
                        os.rmdir(newTempRenderPath)
                    except Exception:
                        print("Cannot delete Dir: ", newTempRenderPath)

                # print(f"shot.getEditStart: {shot.getEditStart()}, handles: {handles}")

                # if generateSequenceVideo:
                #     # audio clip
                #     vse_render.createNewClip(
                #         sequenceScene,
                #         compositedMediaPath,
                #         sequenceScene.frame_start,
                #         shot.getEditStart() - handles,
                #         offsetStart=handles,
                #         offsetEnd=handles,
                #         importVideo=False,
                #         importAudio=True,
                #     )

                #     # video clip
                #     vse_render.createNewClip(
                #         sequenceScene,
                #         compositedMediaPath,
                #         sequenceScene.frame_start,
                #         shot.getEditStart() - handles,
                #         offsetStart=handles,
                #         offsetEnd=handles,
                #         importVideo=True,
                #         importAudio=False,
                #     )

    if not fileListOnly:
        # render full sequence
        # Note that here we are back to the sequence scene, not anymore in the shot scene

        #######################
        # render sequence video
        #######################

        # if generateSequenceVideo:
        #     bpy.context.window.scene = sequenceScene
        #     bpy.ops.render.opengl(animation=True, sequencer=True)

        #     # cleaning current file from temp scenes
        #     if not config.uasDebug:
        #         # current scene is sequenceScene
        #         bpy.ops.scene.delete()

        print(f"newMediaFiles: {newMediaFiles}")
        vse_render.buildSequenceVideo(newMediaFiles, sequenceOutputFullPath, handles, projectFps)

        currentTakeRenderTime = time.monotonic()
        print(f"      \nTake render time: {(currentTakeRenderTime - previousTakeRenderTime):0.2f} sec.")
        print("----------------------------------------")
        previousTakeRenderTime = currentTakeRenderTime

    newMediaFiles.append(sequenceOutputFullPath)
    failedFiles = []

    filesDict = {"rendered_files": newMediaFiles, "failed_files": failedFiles}

    _restoreUserRenderSettings(userRenderSettings)

    return filesDict



def renderStampedInfoForFrame(scene, shot):
    pass


def renderStampedInfoForShot(
    stampInfoSettings, shotManagerProps, takeName, shot, rootPath, newTempRenderPath, handles, verbose=False
):
    props = shotManagerProps
    scene = props.parentScene

    stampInfoSettings.takeName = takeName

    stampInfoSettings.notesUsed = shot.hasNotes()
    stampInfoSettings.notesLine01 = shot.note01
    stampInfoSettings.notesLine02 = shot.note02
    stampInfoSettings.notesLine03 = shot.note03

    stampInfoSettings.shotHandles = handles

    # wkip faux!!!!!!!!!
    stampInfoSettings.edit3DTotalNumber = props.getEditDuration()

    scene.camera = shot.camera
    scene.frame_start = shot.start - handles
    scene.frame_end = shot.end + handles
    numFramesInShot = scene.frame_end - scene.frame_start + 1

    if props.use_project_settings:
        scene.render.resolution_x = props.project_resolution_framed_x
        scene.render.resolution_y = props.project_resolution_framed_y

    for f, currentFrame in enumerate(range(scene.frame_start, scene.frame_end + 1)):

        # to do
        renderStampedInfoForFrame(scene, currentFrame)

        # scene.frame_current = currentFrame
        scene.frame_set(currentFrame)

        scene.render.filepath = shot.getOutputFileName(
            frameIndex=scene.frame_current, fullPath=True, rootFilePath=rootPath
        )

        if verbose:
            print("      ------------------------------------------")
            print(
                f"      \nStamp Info Frame: {currentFrame}    ( {f + 1} / {numFramesInShot} )    -     Shot: {shot.name}"
            )

        stampInfoSettings.shotName = f"{props.renderShotPrefix()}_{shot.name}"
        stampInfoSettings.cameraName = shot.camera.name
        stampInfoSettings.edit3DFrame = props.getEditTime(shot, currentFrame)
        stampInfoSettings.renderRootPath = newTempRenderPath
        stampInfoSettings.renderTmpImageWithStampedInfo(scene, currentFrame)


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
    elif "ALL" == renderMode:
        preset = props.renderSettingsAll
        print("   ALL, preset: ", preset.name)
    else:
        preset = props.renderSettingsOtio
        print("   EDL, preset: ", preset.name)

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
            print("Render Still")
            shot = props.getCurrentShot()

            if preset_useStampInfo:
                setRRS_StampInfoSettings(scene)

                # set current cam
                # if shot.camera is not None:
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

            if props.use_project_settings:
                scene.render.image_settings.file_format = props.project_images_output_format

            # bpy.ops.render.opengl ( animation = True )
            scene.render.filepath = shot.getOutputFileName(
                frameIndex=scene.frame_current, fullPath=True, rootFilePath=rootPath
            )

            bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=preset.writeToDisk)
        #                bpy.ops.render.view_show()
        #                bpy.ops.render.render(animation=False, use_viewport=True, write_still = preset.writeToDisk)

        elif "ANIMATION" == preset.renderMode:
            _logger.debug("Render Animation")

            shot = props.getCurrentShot()

            renderedFilesDict = launchRenderWithVSEComposite(
                "PROJECT",
                takeIndex=-1,
                filePath=props.renderRootPath,
                fileListOnly=False,
                generateSequenceVideo=False,
                specificShotList=[shot],
                handles=props.handles if preset.renderWithHandles else 0,
            )
            # if props.renderSettingsAnim.renderWithHandles:
            #     scene.frame_start = shot.start - props.handles
            #     scene.frame_end = shot.end + props.handles
            # else:
            #     scene.frame_start = shot.start
            #     scene.frame_end = shot.end

            # print("shot.start: ", shot.start)
            # print("scene.frame_start: ", scene.frame_start)

            # if preset_useStampInfo:
            #     stampInfoSettings.stampInfoUsed = False
            #     stampInfoSettings.activateStampInfo = False
            #     setRRS_StampInfoSettings(scene)
            #     stampInfoSettings.activateStampInfo = True
            #     stampInfoSettings.stampInfoUsed = True

            #     stampInfoSettings.shotName = shot.name
            #     stampInfoSettings.takeName = take_name

            # # wkip
            # if props.use_project_settings:
            #     scene.render.image_settings.file_format = "FFMPEG"
            #     scene.render.ffmpeg.format = "MPEG4"

            #     scene.render.filepath = shot.getOutputFileName(fullPath=True, rootFilePath=rootPath)
            #     print("scene.render.filepath: ", scene.render.filepath)

            # bpy.ops.render.render("INVOKE_DEFAULT", animation=True)

        elif "ALL" == preset.renderMode:
            print(f"Render All:" + str(props.renderSettingsAll.renderAllTakes))
            print(f"Render All, preset.renderAllTakes: {preset.renderAllTakes}")

            takesToRender = [-1]
            if preset.renderAllTakes:
                print("Render All takes")
                takesToRender = [i for i in range(0, len(props.takes))]

            for takeInd in takesToRender:
                renderedFilesDict = launchRenderWithVSEComposite(
                    "PROJECT",
                    takeIndex=takeInd,
                    filePath=props.renderRootPath,
                    fileListOnly=False,
                    generateSequenceVideo=preset.generateEditVideo,
                    handles=props.handles,  # if preset.renderWithHandles else 0
                )

                if preset.renderOtioFile:
                    from shotmanager.otio.exports import exportOtio

                    bpy.context.window.scene = scene
                    renderedOtioFile = exportOtio(
                        scene, takeIndex=takeInd, filePath=props.renderRootPath, fileListOnly=False
                    )
                    # renderedFilesDict["edl_files"] = [renderedOtioFile]

            # #   wkip to remove
            # shot = props.getCurrentShot()
            # if preset_useStampInfo:
            #     stampInfoSettings.stampInfoUsed = False
            #     stampInfoSettings.activateStampInfo = False
            #     setRRS_StampInfoSettings(scene)
            #     stampInfoSettings.activateStampInfo = True
            #     stampInfoSettings.stampInfoUsed = True

            # shots = props.get_shots()

            # if props.use_project_settings:
            #     scene.render.image_settings.file_format = "FFMPEG"
            #     scene.render.ffmpeg.format = "MPEG4"

            # for i, shot in enumerate(shots):
            #     if shot.enabled:
            #         print("\n  Shot rendered: ", shot.name)
            #         #     props.setCurrentShotByIndex(i)
            #         #     props.setSelectedShotByIndex(i)

            #         scene.camera = shot.camera

            #         if preset_useStampInfo:
            #             stampInfoSettings.shotName = shot.name
            #             stampInfoSettings.takeName = take_name
            #             print("stampInfoSettings.takeName: ", stampInfoSettings.takeName)

            #         # area.spaces[0].region_3d.view_perspective = 'CAMERA'
            #         scene.frame_current = shot.start
            #         scene.frame_start = shot.start - props.handles
            #         scene.frame_end = shot.end + props.handles
            #         scene.render.filepath = shot.getOutputFileName(fullPath=True, rootFilePath=rootPath)
            #         print("scene.render.filepath: ", scene.render.filepath)

            #         # bpy.ops.render.render(animation=True)
            #         bpy.ops.render.render("INVOKE_DEFAULT", animation=True)

            # bpy.ops.render.opengl ( animation = True )

        else:
            pass

        # xwkip to remove
        if preset_useStampInfo:
            # scene.UAS_StampInfo_Settings.stampInfoUsed = False
            #  props.useStampInfoDuringRendering = False
            pass
