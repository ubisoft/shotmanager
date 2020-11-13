import os
from pathlib import Path
import json
import time

import bpy

from shotmanager.otio.exports import exportOtio
from shotmanager.config import config
from shotmanager.scripts.rrs.RRS_StampInfo import setRRS_StampInfoSettings

from shotmanager.utils import utils
from shotmanager.utils import utils_store_context as utilsStore


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
    generateShotVideos=True,
    specificShotList=None,
    specificFrame=None,
    render_handles=True,
    renderSound=True,
    renderAlsoDisabled=False,
    area=None,
    override_all_viewports=False,
):
    """ Generate the media for the specified take
        Return a dictionary with a list of all the created files and a list of failed ones
        filesDict = {"rendered_files": newMediaFiles, "failed_files": failedFiles}
        specificFrame: When specified, only this frame is rendered. Handles are ignored and the resulting media in an image, not a video
    """

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

    renderFrameByFrame = (
        "PLAYBLAST_LOOP" == props.renderContext.renderComputationMode
        or "ENGINE_LOOP" == props.renderContext.renderComputationMode
    )
    renderWithOpengl = (
        "PLAYBLAST_LOOP" == props.renderContext.renderComputationMode
        or "PLAYBLAST_ANIM" == props.renderContext.renderComputationMode
    )

    if "PLAYBLAST" == renderMode:
        renderFrameByFrame = False  # wkip crash a la génération du son si mode framebyframe...
        renderWithOpengl = True

    #######################
    # store current scene settings
    #######################
    userRenderSettings = {}
    userRenderSettings = utilsStore.storeUserRenderSettings(context, userRenderSettings)

    #######################
    # set specific render context
    #######################

    projectFps = scene.render.fps
    sequenceFileName = props.renderShotPrefix() + takeName
    scene.use_preview_range = False
    renderResolution = [scene.render.resolution_x, scene.render.resolution_y]
    renderResolutionFramed = [scene.render.resolution_x, scene.render.resolution_y]

    # override local variables with project settings
    if props.use_project_settings:
        props.applyProjectSettings()
        scene.render.image_settings.file_format = props.project_images_output_format
        projectFps = scene.render.fps
        sequenceFileName = props.renderShotPrefix()
        renderResolution = [props.project_resolution_x, props.project_resolution_y]
        renderResolutionFramed = [props.project_resolution_framed_x, props.project_resolution_framed_y]

    if "PLAYBLAST" == renderMode:
        scene.render.resolution_percentage = props.renderSettingsPlayblast.resolutionPercentage
        renderResolution[0] = int(renderResolution[0] * props.renderSettingsPlayblast.resolutionPercentage / 100)
        renderResolution[1] = int(renderResolution[1] * props.renderSettingsPlayblast.resolutionPercentage / 100)

        if preset_useStampInfo:
            # wkip
            renderResolutionFramed[0] = int(1280 * props.renderSettingsPlayblast.resolutionPercentage / 100)
            renderResolutionFramed[1] = int(960 * props.renderSettingsPlayblast.resolutionPercentage / 100)
        else:
            renderResolutionFramed[0] = int(
                renderResolutionFramed[0] * props.renderSettingsPlayblast.resolutionPercentage / 100
            )
            renderResolutionFramed[1] = int(
                renderResolutionFramed[1] * props.renderSettingsPlayblast.resolutionPercentage / 100
            )

    # set output format settings
    #######################

    ################
    # video settings
    ################

    # scene.render.image_settings.file_format = "FFMPEG"
    # scene.render.ffmpeg.format = "MPEG4"
    # scene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
    # scene.render.ffmpeg.gopsize = 5  # keyframe interval
    # scene.render.ffmpeg.audio_codec = "AAC"
    scene.render.use_file_extension = True

    # set render quality
    #######################

    if not "PLAYBLAST" == renderMode:
        if renderWithOpengl:
            spaces = list()
            if override_all_viewports:
                for area in context.screen.areas:
                    if area.type == "VIEW_3D":
                        for space_data in area.spaces:
                            if space_data.type == "VIEW_3D":
                                spaces.append(space_data)
            else:
                spaces.append(context.space_data)

            for space_data in spaces:
                if not "CUSTOM" == props.renderContext.renderEngineOpengl:
                    scene.render.engine = props.renderContext.renderEngineOpengl
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
            scene.render.use_compositing = False
            scene.render.use_sequencer = False

            if not "CUSTOM" == props.renderContext.renderEngine:
                scene.render.engine = props.renderContext.renderEngine

    if "PLAYBLAST" == renderMode:
        props.renderContext.applyRenderQualitySettings(context, renderQuality="VERY_LOW")
        if not preset_useStampInfo:
            props.renderContext.applyBurnInfos(context)
    else:
        props.renderContext.applyRenderQualitySettings(context)

    scene.view_settings.view_transform = "Standard"

    #######################
    # render each shots
    #######################

    renderedShotSequencesArr = []

    previousTakeRenderTime = time.monotonic()
    currentTakeRenderTime = previousTakeRenderTime

    startRenderTime = time.monotonic()
    allRenderTimes = dict()

    startFrameIn3D = -1
    startFrameInEdit = -1
    for i, shot in enumerate(shotList):

        if 0 == i:
            startFrameIn3D = shot.start
            startFrameInEdit = shot.getEditStart()
            textInfo = f"  *** Playblast Start Time: 3D: {startFrameIn3D}, Edit: {startFrameInEdit}"
            print(f"TextInfo: {textInfo}")

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
            startShotRenderTime = time.monotonic()
            infoStr = f"\n----------------------------------------------------"
            infoStr += f"\n\n  Rendering Shot: {shot.getName_PathCompliant(withPrefix=True)} - {shot.getDuration()} fr."
            infoStr += f"\n  ---------------"
            infoStr += f"\n\nRenderer: "

            if "PLAYBLAST" == renderMode:
                infoStr += f"PLAYBLAST: "
                if renderWithOpengl:
                    infoStr += f"OpenGl - "
                else:
                    infoStr += f"Engine - "
                if renderFrameByFrame:
                    infoStr += f"Frame by Frame Mode"
                else:
                    infoStr += f"Loop Mode"
            else:
                if renderWithOpengl:
                    infoStr += f"{props.renderContext.renderEngineOpengl} - "
                else:
                    infoStr += f"{props.renderContext.renderEngine} - "
                infoStr += f"{props.renderContext.renderComputationMode}"

            print(infoStr)

            # print("\n     newTempRenderPath: ", newTempRenderPath)
            # print("     compositedMediaPath: ", compositedMediaPath)

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
                    utils.setCurrentCameraToViewport2(area)
            else:
                utils.setCurrentCameraToViewport2(viewportArea)
            # props.setCurrentShot(shot)
            numFramesInShot = scene.frame_end - scene.frame_start + 1
            previousFrameRenderTime = time.monotonic()
            currentFrameRenderTime = previousFrameRenderTime

            #######################
            # render image only
            #######################

            renderShotContent = True
            if renderShotContent and not fileListOnly:

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

                        print("      \n")
                        textInfo = f"Frame: {currentFrame}  ( {f + 1} / {numFramesInShot} )"
                        textInfo02 = f"Shot: {shot.name}"
                        print("      ------------------------------------------")
                        print("      \n" + textInfo + "  -  " + textInfo02)

                        if "PLAYBLAST" == renderMode and not preset_useStampInfo:
                            bpy.context.scene.render.use_stamp_frame = False
                            scene.render.use_stamp_note = True
                            scene.render.stamp_note_text += textInfo02 + "\\n" + textInfo

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

                    if "PLAYBLAST" == renderMode and not preset_useStampInfo:
                        textInfo02 = f"Shot: {shot.name}"
                        textInfo02 += f"  *** Playblast Start Time: 3D: {startFrameIn3D}, Edit: {startFrameInEdit}"
                        print(f"TextInfo02: {textInfo02}")
                        scene.render.use_stamp_note = True
                        scene.render.stamp_note_text = textInfo02

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

            # print render time
            #######################

            deltaTime = time.monotonic() - startShotRenderTime
            print(f"      \nShot render time (images only): {deltaTime:0.2f} sec.")
            allRenderTimes[shot.name + "_" + "images"] = deltaTime

            #######################
            # render sound
            #######################

            audioFilePath = None
            if specificFrame is None and renderSound:
                # render sound
                audioFilePath = (
                    newTempRenderPath + f"{props.renderShotPrefix()}_{shot.getName_PathCompliant()}" + ".wav"
                )
                print(f"\n Sound for shot {shot.name}:  {audioFilePath}")

                if Path(audioFilePath).exists():
                    print(f" *** Sound file still exists... Should have been deleted ***")
                    try:
                        os.remove(audioFilePath)
                        if Path(audioFilePath).exists():
                            print(f"\n*** File locked (by system?): {audioFilePath}")
                    except Exception as e:
                        _logger.exception(f"\n*** File locked (by system?): {audioFilePath}")
                        print(f"\n*** Exception : File locked (by system?): {audioFilePath}")
                        audioFilePath = (
                            str(Path(audioFilePath).parent)
                            + "/"
                            + str(Path(audioFilePath).stem)
                            + "1"
                            # + "."
                            + str(Path(audioFilePath).suffix)
                        )

                #     import os.path
                # os.path.exists(file_path)

                # crash ici lorsqu'on est en rendu frame per frame

                # wkip pour que ca marche, mettre les render settings en mode video ??
                # scene.render.filepath = "//"
                # scene.frame_start = 0
                # scene.frame_end = 50
                # bpy.ops.render.opengl(animation=True, write_still=False)
                # https://blenderartists.org/t/scripterror-mixdown-operstor/548056/4
                bpy.ops.sound.mixdown(filepath=str(audioFilePath), relative_path=False, container="WAV", codec="PCM")
                # bpy.ops.sound.mixdown(filepath=audioFilePath, relative_path=False, container="MP3", codec="MP3")

            overImgSeq = newTempRenderPath + shot.getOutputMediaPath(providePath=False, genericFrame=True)
            overImgSeq_resolution = renderResolution

            bgImgSeq = None
            bgImgSeq_resolution = overImgSeq_resolution
            if preset_useStampInfo:
                frameIndStr = "####" if specificFrame is None else f"{specificFrame:04}"
                _logger.debug(f"\n - specificFrame: {specificFrame}")
                bgImgSeq = newTempRenderPath + "_tmp_StampInfo." + frameIndStr + ".png"
                bgImgSeq_resolution = renderResolutionFramed

            if generateShotVideos:

                #######################
                # Generate shot video
                #######################

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
                vse_render.clearMedia()
                if specificFrame is None:
                    vse_render.inputOverMediaPath = overImgSeq
                else:
                    vse_render.inputOverMediaPath = newTempRenderPath + shot.getOutputMediaPath(
                        providePath=False, specificFrame=specificFrame
                    )

                _logger.debug(f"\n - OverMediaPath: {vse_render.inputOverMediaPath}")
                vse_render.inputOverResolution = overImgSeq_resolution

                if preset_useStampInfo:
                    frameIndStr = "####" if specificFrame is None else f"{specificFrame:04}"
                    _logger.debug(f"\n - specificFrame: {specificFrame}")
                    vse_render.inputBGMediaPath = bgImgSeq
                    _logger.debug(f"\n - BGMediaPath: {vse_render.inputBGMediaPath}")
                    vse_render.inputBGResolution = bgImgSeq_resolution

                if specificFrame is None and renderSound:
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

            else:
                #######################
                # Collect rendered image sequences
                #######################
                videoAndSound = dict()

                videoAndSound["image_sequence"] = overImgSeq
                videoAndSound["image_sequence_resolution"] = overImgSeq_resolution

                videoAndSound["bg_resolution"] = bgImgSeq_resolution
                if preset_useStampInfo:
                    videoAndSound["bg"] = bgImgSeq
                videoAndSound["sound"] = audioFilePath

                renderedShotSequencesArr.append(videoAndSound)

            #  print(f"** renderedShotSequencesArr: {renderedShotSequencesArr}")

            # print render time
            #######################

            deltaTime = time.monotonic() - startShotRenderTime
            print(f"      \nShot render time (incl. video): {deltaTime:0.2f} sec.")
            allRenderTimes[shot.name + "_" + "full"] = deltaTime

            print("----------------------------------------")

    #######################
    # render sequence video
    #######################

    deltaTime = time.monotonic() - startRenderTime
    print(f"      \nAll shots render time: {deltaTime:0.2f} sec.")
    allRenderTimes["AllShots"] = deltaTime

    startSequenceRenderTime = time.monotonic()
    sequenceOutputFullPath = ""
    if generateSequenceVideo and specificFrame is None:

        if generateShotVideos:
            #######################
            # render sequence video based on shot videos
            #######################

            sequenceOutputFullPath = f"{rootPath}{takeName}\\{sequenceFileName}.{props.getOutputFileFormat()}"
            print(f"  Rendered sequence from shot videos: {sequenceOutputFullPath}")

            if not fileListOnly:
                # print(f"sequenceFiles: {sequenceFiles}")
                vse_render.buildSequenceVideo(sequenceFiles, sequenceOutputFullPath, handles, projectFps)

                # currentTakeRenderTime = time.monotonic()
                # print(f"      \nTake render time: {(currentTakeRenderTime - previousTakeRenderTime):0.2f} sec.")
                # print("----------------------------------------")
                # previousTakeRenderTime = currentTakeRenderTime
                pass

            newMediaFiles.append(sequenceOutputFullPath)

        else:
            #######################
            # render sequence video based on shot image sequences
            #######################
            # wkip tmp
            sequenceOutputFullPath = f"{rootPath}\\_playblast_.{props.getOutputFileFormat()}"
            # sequenceOutputFullPath = (
            #     f"{rootPath}{takeName}\\_playblast_{sequenceFileName}.{props.getOutputFileFormat()}"
            # )
            print(f"  Rendered sequence from shot sequences: {sequenceOutputFullPath}")

            if len(renderedShotSequencesArr):
                vse_render.buildSequenceVideoFromImgSequences(
                    renderedShotSequencesArr, sequenceOutputFullPath, handles, projectFps
                )

            deleteTempFiles = not config.uasDebug_keepVSEContent
            if deleteTempFiles:
                for i in range(len(renderedShotSequencesArr)):
                    _deleteTempFiles(str(Path(renderedShotSequencesArr[i]["image_sequence"]).parent))

        deltaTime = time.monotonic() - startSequenceRenderTime
        print(f"      \nSequence video render time: {deltaTime:0.2f} sec.")
        allRenderTimes["SequenceVideo"] = deltaTime

    failedFiles = []

    filesDict = {
        "rendered_files": newMediaFiles,
        "failed_files": failedFiles,
        "sequence_video_file": sequenceOutputFullPath,
    }

    deltaTime = time.monotonic() - startRenderTime
    print(f"      \nFull Sequence render time: {deltaTime:0.2f} sec.")
    allRenderTimes["SequenceAndShots"] = deltaTime

    printAllRenderTimes = True  # config.uasDebug
    if printAllRenderTimes:
        print("\nRender times:")
        for key, value in allRenderTimes.items():
            print(f"{key:>20}: {value:0.2f} sec.")
        print("\n")

    #######################
    # restore current scene settings
    #######################
    utilsStore.restoreUserRenderSettings(context, userRenderSettings)

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

    if not render_handles:
        handles = 0

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


def launchRender(context, renderMode, rootPath, area=None):
    # def launchRender(context, renderMode, rootPath, useStampInfo=True, area = None ):
    """
        rootPath: directory to render the files
    """
    context = bpy.context
    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props
    renderDisplayInfo = ""

    renderDisplayInfo += "\n\n*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***\n"
    renderDisplayInfo += "\n                                 *** UAS Shot Manager V " + props.version()[0] + " - "

    preset = None
    if "STILL" == renderMode:
        preset = props.renderSettingsStill
        renderDisplayInfo += f"  Rendering with {preset.name}"
    elif "ANIMATION" == renderMode:
        preset = props.renderSettingsAnim
        renderDisplayInfo += f"  Rendering with {preset.name}"
    elif "ALL" == renderMode:
        preset = props.renderSettingsAll
        renderDisplayInfo += f"  Rendering with {preset.name}"
    elif "OTIO" == renderMode:
        preset = props.renderSettingsOtio
        renderDisplayInfo += f"  Rendering with {preset.name}"
    elif "PLAYBLAST" == renderMode:
        preset = props.renderSettingsPlayblast
        renderDisplayInfo += f"  Rendering with {preset.name}"
    else:
        _logger.error(f"No valid render preset found")

    stampInfoSettings = None
    preset_useStampInfo = False
    useStampInfo = preset.useStampInfo

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

    renderDisplayInfo += "  ***"
    renderDisplayInfo += "\n\n*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***\n\n"

    from datetime import datetime

    now = datetime.now()
    renderDisplayInfo += f"{'   - Date: ': <20}{now.strftime('%b-%d-%Y')}  -  {now.strftime('%H:%M:%S')}\n"

    renderDisplayInfo += f"{'   - File: ': <20}{bpy.data.filepath}\n"
    renderDisplayInfo += f"{'   - Scene: ': <20}{scene.name}\n"
    renderDisplayInfo += f"{'   - RootPath: ': <20}{rootPath}\n"
    if config.uasDebug:
        renderDisplayInfo += f"{'   - Debug Mode: ': <20}{config.uasDebug}\n"

    renderDisplayInfo += f"\n"
    print(renderDisplayInfo)

    if True:
        # prepare render settings
        # camera
        # range
        # takes

        take = props.getCurrentTake()
        if take is None:
            print("Shot Manager Rendering: No current take found - Rendering aborted")
            return False

        context.window_manager.UAS_shot_manager_shots_play_mode = False
        context.window_manager.UAS_shot_manager_display_timeline = False

        # if props.use_project_settings:
        #     props.applyProjectSettings()

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
                useStampInfo=preset.useStampInfo,
                generateSequenceVideo=False,
                specificShotList=[shot],
                specificFrame=scene.frame_current,
                area=area,
            )
            print(json.dumps(renderedFilesDict, indent=4))

        elif "ANIMATION" == preset.renderMode:
            _logger.debug("Render Animation")

            bpy.ops.wm.save_mainfile()

            shot = props.getCurrentShot()

            renderedFilesDict = launchRenderWithVSEComposite(
                context,
                "PROJECT",
                filePath=props.renderRootPath,
                useStampInfo=preset.useStampInfo,
                generateSequenceVideo=False,
                specificShotList=[shot],
                render_handles=preset.renderHandles if preset.bypass_rendering_project_settings else True,
                area=area,
            )
            print(json.dumps(renderedFilesDict, indent=4))

        elif "ALL" == preset.renderMode:
            _logger.debug(f"Render All:" + str(props.renderSettingsAll.renderAllTakes))
            _logger.debug(f"Render All, preset.renderAllTakes: {preset.renderAllTakes}")

            bpy.ops.wm.save_mainfile()

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
                    useStampInfo=preset.useStampInfo,
                    rerenderExistingShotVideos=preset.rerenderExistingShotVideos,
                    generateSequenceVideo=preset.generateEditVideo,
                    renderAlsoDisabled=preset.renderAlsoDisabled,
                    area=area,
                )

                if preset.renderOtioFile:
                    bpy.context.window.scene = scene
                    renderedOtioFile = exportOtio(
                        scene,
                        takeIndex=takeInd,
                        filePath=props.renderRootPath,
                        fileListOnly=False,
                        montageCharacteristics=props.get_montage_characteristics(),
                    )
                    # renderedFilesDict["edl_files"] = [renderedOtioFile]
            print(json.dumps(renderedFilesDict, indent=4))

        elif "PLAYBLAST" == preset.renderMode:
            _logger.debug(f"Render Playblast")

            bpy.ops.wm.save_mainfile()

            renderedFilesDict = launchRenderWithVSEComposite(
                context,
                "PLAYBLAST",
                takeIndex=-1,
                filePath=props.renderRootPath,
                fileListOnly=False,
                useStampInfo=preset.useStampInfo,
                rerenderExistingShotVideos=True,
                generateShotVideos=False,
                generateSequenceVideo=True,
                renderAlsoDisabled=False,
                render_handles=False,
                renderSound=preset.renderSound,
                area=area,
            )

            # open rendered media in a player
            if len(renderedFilesDict["sequence_video_file"]):
                utils.openMedia(renderedFilesDict["sequence_video_file"], inExternalPlayer=True)

        else:
            print("\n *** preset.renderMode is invalid, cannot render anything... ***\n")
            pass

        print("Render done\n")
