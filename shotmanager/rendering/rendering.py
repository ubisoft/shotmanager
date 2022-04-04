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
Rendering code for takes and shots
"""

import os
from pathlib import Path
from stat import S_IMODE, S_IWRITE

import json
import time

import bpy

from shotmanager.config import config
from shotmanager.rendering.rendering_stampinfo import setStampInfoSettings, renderStampedInfoForShot

from shotmanager.utils import utils
from shotmanager.utils import utils_store_context as utilsStore
from shotmanager.utils.utils_os import module_can_be_imported


from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def launchRenderWithVSEComposite(
    context,
    renderPreset=None,
    takeIndex=-1,
    filePath="",
    useStampInfo=True,
    stampInfoCustomSettingsDict=None,
    rerenderExistingShotVideos=True,
    generateSequenceVideo=True,
    generateShotVideos=True,
    specificShotList=None,
    specificFrame=None,
    render_handles=True,
    renderSound=True,
    renderAlsoDisabled=False,
    area=None,
    override_all_viewports=False,
    fileListOnly=False,
):
    """Generate the media for the specified takes
    Return a dictionary with a list of all the created files and a list of failed ones.
    Previous rendered files are deleted before the new rendering occurs. It this cleaning fails the rendering gets aborted.
    Use fileListOnly to get only the list of the media that will be created during the rendering process.

    Args:
        filesDict (dict)= {"rendered_files": newMediaFiles, "failed_files": failedFiles}
        specificFrame (int): When specified, only this frame is rendered. Handles are ignored and the resulting media in an image, not a video
        fileListOnly (bool):    When set to True, no rendering nor change in the scene are done, the function just
                                returns the list of the files to generate
    """

    def _deleteTempFiles(dirPath):
        # delete unsused rendered frames
        if config.devDebug:
            print(f"Cleaning shot temp dir: {dirPath}")

        if os.path.exists(dirPath):
            files_in_directory = os.listdir(dirPath)
            filtered_files = [file for file in files_in_directory if file.endswith(".png") or file.endswith(".wav")]

            for file in filtered_files:
                path_to_file = os.path.join(dirPath, file)
                try:
                    os.remove(path_to_file)
                except Exception:
                    _logger.exception(f"\n*** File locked (by system?): {path_to_file}")
                    print(f"\n*** File locked (by system?): {path_to_file}")
            try:
                os.rmdir(dirPath)
            except Exception:
                print("Cannot delete Dir: ", dirPath)

        if config.devDebug:
            print("Cleaning temp scenes")

        scenesToDelete = [
            s
            for s in bpy.data.scenes
            if (s.name.startswith("Tmp_VSE_RenderScene") or s.name.startswith("VSE_SequenceRenderScene"))
        ]
        for s in scenesToDelete:
            bpy.data.scenes.remove(s, do_unlink=True)

    # context = bpy.context
    scene = context.scene
    props = scene.UAS_shot_manager_props
    vse_render = context.window_manager.UAS_vse_render
    prefs = context.preferences.addons["shotmanager"].preferences

    currentShot = props.getCurrentShot()

    displayRenderTimes = True

    renderMode = "PROJECT" if renderPreset is None else renderPreset.renderMode
    renderInfo = dict()

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

    take = props.getCurrentTake() if -1 == takeIndex else props.getTakeByIndex(takeIndex)
    takeName = take.getName_PathCompliant()
    shotListTmp = (
        take.getShotList(ignoreDisabled=not renderAlsoDisabled) if specificShotList is None else specificShotList
    )

    # remove shots ending with "_removed" and not enabled
    shotList = list()
    for shot in shotListTmp:
        if not shot.get_name().endswith("_removed") or shot.enabled:
            shotList.append(shot)

    newMediaFiles = []
    sequenceFiles = []  # only enabled shots

    rootPath = filePath if "" != filePath else os.path.dirname(bpy.data.filepath)
    # use absolute path
    rootPath = bpy.path.abspath(rootPath)

    if not rootPath.endswith("\\"):
        rootPath += "\\"

    preset_useStampInfo = False
    stampInfoSettings = None

    if not fileListOnly:
        if getattr(scene, "UAS_StampInfo_Settings", None) is not None:
            stampInfoSettings = scene.UAS_StampInfo_Settings

            preset_useStampInfo = useStampInfo
            if not useStampInfo:
                stampInfoSettings.stampInfoUsed = False
            else:
                stampInfoSettings.renderRootPathUsed = True
                stampInfoSettings.renderRootPath = rootPath

                stampInfoSettings.stampInfoUsed = props.useStampInfoDuringRendering
                if stampInfoSettings.stampInfoUsed:
                    setStampInfoSettings(scene)

        context.window_manager.UAS_shot_manager_shots_play_mode = False
        context.window_manager.UAS_shot_manager_display_overlay_tools = False

    renderFrameByFrame = "LOOP" == props.renderContext.renderFrameIterationMode
    renderWithOpengl = "OPENGL" == props.renderContext.renderHardwareMode

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

    # projectFps = scene.render.fps
    projectFps = utils.getSceneEffectiveFps(scene)

    # sequence name will get a different value is project settings are used
    sequenceFileName = props.getSequenceName("FULL", addSeparator=True)

    scene.use_preview_range = False
    renderResolution = [scene.render.resolution_x, scene.render.resolution_y]
    renderResolutionFramed = [scene.render.resolution_x, scene.render.resolution_y]
    renderResolutionFramed = [scene.render.resolution_x, scene.render.resolution_y]
    if preset_useStampInfo:
        renderResolutionFramedFull = stampInfoSettings.getRenderResolutionForStampInfo(scene)
        renderResolutionFramed[0] = int(renderResolutionFramedFull[0] * renderPreset.resolutionPercentage / 100)
        renderResolutionFramed[1] = int(renderResolutionFramedFull[1] * renderPreset.resolutionPercentage / 100)

    # override local variables with project settings
    if props.use_project_settings:
        props.applyProjectSettings()
        scene.render.image_settings.file_format = props.project_images_output_format
        projectFps = props.project_fps
        renderResolution = [props.project_resolution_x, props.project_resolution_y]
        renderResolutionFramed = [props.project_resolution_framed_x, props.project_resolution_framed_y]

    if "PLAYBLAST" == renderMode:
        scene.render.resolution_percentage = int(renderPreset.resolutionPercentage)
        renderResolution[0] = int(renderResolution[0] * renderPreset.resolutionPercentage / 100)
        renderResolution[1] = int(renderResolution[1] * renderPreset.resolutionPercentage / 100)

        # renderResolution = props.getRenderResolutionForFinalOutput(resPercentage=renderPreset.resolutionPercentage)

        # wkipwkipwkip use that instead of the block below:
        # renderResolutionFramed = props.getRenderResolutionForFinalOutput(
        #     resPercentage=renderPreset.resolutionPercentage, useStampInfo=preset_useStampInfo
        # )

        # if preset_useStampInfo:
        #     renderResolutionFramedFull = stampInfoSettings.getRenderResolutionForStampInfo(scene)
        #     renderResolutionFramed[0] = int(renderResolutionFramedFull[0] * renderPreset.resolutionPercentage / 100)
        #     renderResolutionFramed[1] = int(renderResolutionFramedFull[1] * renderPreset.resolutionPercentage / 100)
        # else:
        #     renderResolutionFramed[0] = int(renderResolutionFramed[0] * renderPreset.resolutionPercentage / 100)
        #     renderResolutionFramed[1] = int(renderResolutionFramed[1] * renderPreset.resolutionPercentage / 100)

        if preset_useStampInfo:
            # getRenderResolutionForStampInfo already integrates the percentage_res value (*** found in the current scene ! ***)
            renderResolutionFramed = stampInfoSettings.getRenderResolutionForStampInfo(scene)
            # renderResolutionFramed[0] = int(renderResolutionFramedFull[0] * renderPreset.resolutionPercentage / 100)
            # renderResolutionFramed[1] = int(renderResolutionFramedFull[1] * renderPreset.resolutionPercentage / 100)
        else:
            renderResolutionFramed[0] = int(renderResolutionFramed[0] * renderPreset.resolutionPercentage / 100)
            renderResolutionFramed[1] = int(renderResolutionFramed[1] * renderPreset.resolutionPercentage / 100)

        # print(
        #     f"\ntoto renderResolutionFramed: {renderResolutionFramed}, resPercent: {renderPreset.resolutionPercentage}\n"
        # )

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
            # scene.render.use_compositing = False
            scene.render.use_sequencer = False

            if not "CUSTOM" == props.renderContext.renderEngine:
                scene.render.engine = props.renderContext.renderEngine

    if "PLAYBLAST" == renderMode:
        props.renderContext.applyRenderQualitySettingsOpengl(context, renderQuality="VERY_LOW")
        if not preset_useStampInfo:
            props.renderContext.applyBurnInfos(context)
    else:
        if renderWithOpengl:
            props.renderContext.applyRenderQualitySettingsOpengl(context)
        else:
            props.renderContext.applyRenderQualitySettings(context)

    # change color tone mode to prevent washout bug (usually with "filmic" mode)
    scene.view_settings.view_transform = "Standard"

    #######################
    # render each shots
    #######################

    renderedShotSequencesArr = []

    # previousTakeRenderTime = time.monotonic()
    # currentTakeRenderTime = previousTakeRenderTime

    startRenderTime = time.monotonic()
    allRenderTimes = dict()

    startFrameIn3D = -1
    startFrameInEdit = -1
    startShot = None

    for i, shot in enumerate(shotList):
        if 0 == i:
            startFrameIn3D = shot.start
            startFrameInEdit = shot.getEditStart(referenceLevel="GLOBAL_EDIT")
            startShot = shot
            textInfo = f"  *** Playblast Start Time: 3D: {startFrameIn3D}, Edit: {startFrameInEdit}"
            print(f"{textInfo}")

        # context.window_manager.UAS_shot_manager_progressbar = (i + 1) / len(shotList) * 100.0
        # bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=2)

        # newTempRenderPath = shot.getOutputMediaPath(rootPath=rootPath, insertTempFolder=True, provideName=False)
        newTempRenderPath = shot.getOutputMediaPath("SH_INTERM_IMAGE_SEQ", rootPath=rootPath, provideName=False)

        compositedMediaPath = shot.getOutputMediaPath(
            "SH_VIDEO", rootPath=rootPath, insertSeqPrefix=True, specificFrame=specificFrame
        )

        newMediaFiles.append(compositedMediaPath)
        if shot.enabled:
            sequenceFiles.append(compositedMediaPath)

        if not rerenderExistingShotVideos:
            if Path(compositedMediaPath).exists():
                print(f" - File {Path(compositedMediaPath).name} already computed")
                continue

        if not fileListOnly:
            startShotRenderTime = time.monotonic()
            infoStr = "\n----------------------------------------------------"
            infoStr += f"\n\n  Rendering Shot: {shot.getName_PathCompliant(withPrefix=True)} - {shot.getDuration()} fr."
            infoStr += "\n  ---------------"
            infoStr += "\n\nRenderer: "

            if "PLAYBLAST" == renderMode:
                infoStr += "PLAYBLAST: "
                if renderWithOpengl:
                    infoStr += "OpenGl - "
                else:
                    infoStr += "Engine - "
                if renderFrameByFrame:
                    infoStr += "Frame by Frame Mode"
                else:
                    infoStr += "Loop Mode"
            else:
                if renderWithOpengl:
                    infoStr += f"{props.renderContext.renderEngineOpengl} - "
                else:
                    infoStr += f"{props.renderContext.renderEngine} - "
                infoStr += f"{props.renderContext.renderHardwareMode} - {props.renderContext.renderFrameIterationMode}"

            print(infoStr)

            _deleteTempFiles(newTempRenderPath)

            # wkip if bg sounds used
            #  props.enableBGSoundForShot()

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

            if override_all_viewports:
                for area in context.screen.areas:
                    utils.setCurrentCameraToViewport2(context, area)
            else:
                utils.setCurrentCameraToViewport2(context, viewportArea)
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

                        # scene.render.filepath = shot.getOutputMediaPath(
                        #     rootPath=rootPath, insertTempFolder=True, specificFrame=scene.frame_current
                        # )
                        scene.render.filepath = shot.getOutputMediaPath(
                            "SH_INTERM_IMAGE_SEQ", rootPath=rootPath, specificFrame=scene.frame_current
                        )

                        print("      \n")
                        textInfo = f"Frame: {currentFrame}  ( {f + 1} / {numFramesInShot} )"
                        textInfo02 = f"Shot: {shot.name}"
                        print("      ------------------------------------------")
                        print("      \n" + textInfo + "  -  " + textInfo02)

                        if "PLAYBLAST" == renderMode and renderPreset.stampRenderInfo and not preset_useStampInfo:
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
                    scene.render.filepath = shot.getOutputMediaPath(
                        "SH_INTERM_IMAGE_SEQ",
                        rootPath=rootPath,
                        provideExtension=False,
                        genericFrame=True,
                    )

                    #   _logger.debug("ici PAS loop")

                    if "PLAYBLAST" == renderMode and not preset_useStampInfo:
                        textInfo02 = f"Shot: {shot.name}"
                        textInfo02 += f"  *** Playblast Start Time: 3D: {startFrameIn3D}, Edit: {startFrameInEdit}"
                        _logger.debug(f"TextInfo02: {textInfo02}")
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

            renderedImgSeq_resolution = renderResolution

            #######################
            # render stamped info
            #######################
            infoImgSeq = None
            infoImgSeq_resolution = renderedImgSeq_resolution
            if preset_useStampInfo:
                # returns "#####" if specificFrame is None, a formated frame otherwise
                # frameIndStr = props.getFramePadding(frame=specificFrame)
                # _logger.debug(f"\n - specificFrame: {specificFrame}")
                #    infoImgSeq = newTempRenderPath + "_tmp_StampInfo." + frameIndStr + ".png"
                # infoImgSeq = newTempRenderPath + shot.getOutputMediaPath(
                #     providePath=False, insertStampInfoPrefix=True, genericFrame=True
                # )
                infoImgSeq = newTempRenderPath + shot.getOutputMediaPath(
                    "SH_INTERM_STAMPINFO_SEQ", providePath=False, genericFrame=True
                )
                infoImgSeq_resolution = renderResolutionFramed
                #   print(f"\ntoto infoImgSeq_resolution: {infoImgSeq_resolution}\n")
                # infoImgSeq_resolution = stampInfoSettings.getRenderResolutionForStampInfo(scene)

                renderStampedInfoForShot(
                    stampInfoSettings,
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
            _logger.info_ext(
                f"Shot render time (images only): {deltaTime:0.2f} sec.", tag="RENDERTIME", display=displayRenderTimes
            )

            allRenderTimes[shot.name + "_" + "images"] = deltaTime

            #######################
            # render sound
            #######################

            audioFilePath = None
            if specificFrame is None and renderSound:
                # render sound
                # audioFilePath = (
                #     newTempRenderPath + f"{props.getRenderShotPrefix()}_{shot.getName_PathCompliant()}" + ".wav"
                # )
                audioFilePath = (
                    newTempRenderPath
                    # + shot.getOutputMediaPath(providePath=False, insertSeqPrefix=True, provideExtension=False)
                    + shot.getOutputMediaPath(
                        "SH_AUDIO", providePath=False, insertSeqPrefix=True, provideExtension=False
                    )
                    + ".wav"
                )
                _logger.debug(f"\n Sound for shot {shot.name}:  {audioFilePath}")

                if Path(audioFilePath).exists():
                    print(" *** Sound file still exists... Should have been deleted ***")
                    try:
                        os.remove(audioFilePath)
                        if Path(audioFilePath).exists():
                            print(f"\n*** File locked (by system?): {audioFilePath}")
                    except Exception:
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
                bpy.ops.sound.mixdown(filepath=audioFilePath, relative_path=False, container="WAV", codec="PCM")
                # bpy.ops.sound.mixdown(filepath=audioFilePath, relative_path=False, container="MP3", codec="MP3")

            # renderedImgSeq = newTempRenderPath + shot.getOutputMediaPath(providePath=False, genericFrame=True)
            renderedImgSeq = newTempRenderPath + shot.getOutputMediaPath(
                "SH_IMAGE_SEQ", providePath=False, genericFrame=True
            )

            if generateShotVideos:

                #######################
                # Generate shot video
                #######################

                # use vse_render to store all the elements to composite

                vse_render.clearMedia()
                if specificFrame is None:
                    vse_render.inputBGMediaPath = renderedImgSeq
                else:
                    # vse_render.inputBGMediaPath = newTempRenderPath + shot.getOutputMediaPath(
                    #     providePath=False, specificFrame=specificFrame
                    # )
                    vse_render.inputBGMediaPath = newTempRenderPath + shot.getOutputMediaPath(
                        "SH_IMAGE_SEQ", providePath=False, specificFrame=specificFrame
                    )

                _logger.debug(f"\n - BGMediaPath: {vse_render.inputBGMediaPath}")
                vse_render.inputBGResolution = renderedImgSeq_resolution
                vse_render.outputResolution = vse_render.inputBGResolution

                if preset_useStampInfo:
                    _logger.debug(f"\n - specificFrame: {specificFrame}")
                    vse_render.inputOverMediaPath = infoImgSeq
                    _logger.debug(f"\n - OverMediaPath: {vse_render.inputOverMediaPath}")
                    vse_render.inputOverResolution = infoImgSeq_resolution
                    vse_render.outputResolution = vse_render.inputOverResolution

                if specificFrame is None and renderSound:
                    vse_render.inputAudioMediaPath = audioFilePath

                padding = (
                    props.project_img_name_digits_padding
                    if props.use_project_settings
                    else prefs.img_name_digits_padding
                )

                # Warning: this defines the start index of the first image (usually 0 or 1)
                # This is different from props.editStartFrame which is the offset of the scene take relatively to a main edit
                #   compositedMedia_PathOnly = shot.getOutputMediaPath(rootPath=rootPath, provideName=False)
                compositedImgSeqPath = shot.getOutputMediaPath("SH_IMAGE_SEQ", rootPath=rootPath, genericFrame=True)
                compositedMedia_NameOnly = shot.getName_PathCompliant()
                print("--    newTempRenderPath: ", newTempRenderPath)
                print("--    compositedMediaPath: ", compositedMediaPath)
                print("--    compositedImgSeqPath: ", compositedImgSeqPath)

                if specificFrame is None:
                    video_frame_start = (
                        props.project_output_first_frame if props.use_project_settings else prefs.output_first_frame
                    )
                    video_frame_end = shot.end - shot.start + video_frame_start
                    if renderHandles:
                        video_frame_end += 2 * handles

                    vse_render.compositeVideoInVSE(
                        projectFps,
                        video_frame_start,
                        video_frame_end,
                        compositedMediaPath,
                        compositedMedia_NameOnly,
                        compositedImgSeqPath=compositedImgSeqPath,
                        output_file_prefix=props.getRenderShotPrefix(),
                        postfixSceneName=shot.getName_PathCompliant(),
                        output_resolution=infoImgSeq_resolution,
                        output_media_mode=renderPreset.outputMediaMode,
                        importAtFrame=video_frame_start,
                        frame_padding=padding,
                    )
                else:
                    vse_render.compositeVideoInVSE(
                        projectFps,
                        specificFrame,
                        specificFrame,
                        compositedMediaPath,
                        compositedMedia_NameOnly,
                        output_file_prefix=props.getRenderShotPrefix(),
                        postfixSceneName=shot.getName_PathCompliant(),
                        output_resolution=infoImgSeq_resolution,
                        output_media_mode=renderPreset.outputMediaMode,
                        importAtFrame=0,
                        frame_padding=padding,
                    )

                # bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=True)
                # bpy.ops.render.render('INVOKE_DEFAULT', animation = True)
                # bpy.ops.render.opengl ( animation = True )

                deleteTempFiles = not config.devDebug_keepVSEContent and not renderPreset.keepIntermediateFiles
                if deleteTempFiles:
                    _deleteTempFiles(newTempRenderPath)

            else:
                #######################
                # Collect rendered image sequences
                #######################
                videoAndSound = dict()

                videoAndSound["bg"] = renderedImgSeq
                videoAndSound["bg_resolution"] = renderedImgSeq_resolution

                print(f"*** setting output_resolution: {infoImgSeq_resolution}")
                videoAndSound["output_resolution"] = infoImgSeq_resolution

                videoAndSound["fg_sequence_resolution"] = infoImgSeq_resolution
                if preset_useStampInfo:
                    videoAndSound["fg_sequence"] = infoImgSeq
                videoAndSound["sound"] = audioFilePath

                renderedShotSequencesArr.append(videoAndSound)

            print("\n** renderedShotSequencesArr:")
            for item in renderedShotSequencesArr:
                print(f"\n    {item}")

            # print render time
            #######################

            deltaTime = time.monotonic() - startShotRenderTime
            _logger.info_ext(
                f"Shot render time (incl. video): {deltaTime:0.2f} sec.", tag="RENDERTIME", display=displayRenderTimes
            )

            allRenderTimes[shot.name + "_" + "full"] = deltaTime

            print("----------------------------------------")

    #######################
    # render sequence video
    #######################

    deltaTime = time.monotonic() - startRenderTime
    _logger.info_ext(f"All shots render time: {deltaTime:0.2f} sec.", tag="RENDERTIME", display=displayRenderTimes)
    allRenderTimes["AllShots"] = deltaTime

    startSequenceRenderTime = time.monotonic()
    sequenceOutputFullPath = ""
    if generateSequenceVideo and specificFrame is None:

        if generateShotVideos:
            #######################
            # render sequence video based on shot videos
            #######################

            print(" --- In generateShotVideos")
            sequenceOutputFullPath = f"{rootPath}{takeName}\\{sequenceFileName}"
            # if props.use_project_settings:
            #     sequenceOutputFullPath += props.project_naming_separator_char
            # else:
            #     sequenceOutputFullPath += "_"
            sequenceOutputFullPath += f"{takeName}"
            sequenceOutputFullPath += f".{props.getOutputFileFormat()}"
            print(f"  Rendered sequence from shot videos: {sequenceOutputFullPath}")

            if not fileListOnly:
                # print(f"sequenceFiles: {sequenceFiles}")
                vse_render.buildSequenceVideoFromMedia(
                    sequenceOutputFullPath, handles, projectFps, mediaFiles=sequenceFiles
                )

                # currentTakeRenderTime = time.monotonic()
                # print(f"      \nTake render time: {(currentTakeRenderTime - previousTakeRenderTime):0.2f} sec.")
                # print("----------------------------------------")
                # previousTakeRenderTime = currentTakeRenderTime
                pass

            newMediaFiles.append(sequenceOutputFullPath)

        else:
            print(" --- In else that generateShotVideos")
            #######################
            # render sequence video based on shot image sequences
            #######################
            # wkipwkipwkip tmp

            # if "PLAYBLAST" == renderMode
            #    sequenceOutputFullPath = f"{rootPath}\\_playblast_.{props.getOutputFileFormat()}"
            sequenceOutputFullPath = props.getOutputMediaPath("TK_PLAYBLAST", take, rootPath=props.renderRootPath)

            # sequenceOutputFullPath = (
            #     f"{rootPath}{takeName}\\_playblast_{sequenceFileName}.{props.getOutputFileFormat()}"
            # )
            print(f"  Rendered sequence from shot sequences: {sequenceOutputFullPath}")

            if len(renderedShotSequencesArr):
                vse_render.buildSequenceVideoFromMedia(
                    sequenceOutputFullPath, handles, projectFps, mediaDictArr=renderedShotSequencesArr
                )

            deleteTempFiles = not config.devDebug_keepVSEContent and not renderPreset.keepIntermediateFiles
            if deleteTempFiles:
                # _deleteTempFiles(newTempRenderPath)
                for i in range(len(renderedShotSequencesArr)):
                    _deleteTempFiles(str(Path(renderedShotSequencesArr[i]["bg"]).parent))

        renderInfo["scene"] = scene.name
        renderInfo["outputFullPath"] = sequenceOutputFullPath
        renderInfo["resolution_x"] = scene.render.resolution_x
        renderInfo["resolution_y"] = scene.render.resolution_y

        renderInfo["render_percentage"] = (
            renderPreset.resolutionPercentage if "PLAYBLAST" == renderMode else scene.render.resolution_percentage
        )
        renderInfo["renderSound"] = renderSound

        deltaTime = time.monotonic() - startSequenceRenderTime
        _logger.info_ext(f"Sequence video render time: {deltaTime:0.2f} sec.", tag="RENDERTIME")
        allRenderTimes["SequenceVideo"] = deltaTime

    # playblastInfos = {"startFrameIn3D": startFrameIn3D, "startFrameInEdit": startFrameInEdit}
    renderInfo["startFrameIn3D"] = startFrameIn3D
    renderInfo["startFrameInEdit"] = startFrameInEdit
    renderInfo["startShotName"] = props.getRenderShotPrefix() + "_" + startShot.get_name()
    # startFrameIn3D = -1
    # startFrameInEdit = -1

    failedFiles = []
    filesDict = {
        "rendered_files": newMediaFiles,
        "failed_files": failedFiles,
        "sequence_video_file": sequenceOutputFullPath,
    }

    if "PLAYBLAST" == renderMode:
        filesDict["playblastInfos"] = renderInfo

    deltaTime = time.monotonic() - startRenderTime
    _logger.info_ext(f"Full Sequence render time: {deltaTime:0.2f} sec.", tag="RENDERTIME")
    allRenderTimes["SequenceAndShots"] = deltaTime

    if displayRenderTimes:
        _logger.info_ext("Render times:", tag="RENDERTIME")
        for key, value in allRenderTimes.items():
            _logger.info_ext(f"{key:>20}: {value:0.2f} sec.", tag="RENDERTIME")

        _logger.info_ext("\n", tag="RENDERTIME")

    #######################
    # restore current scene settings
    #######################
    utilsStore.restoreUserRenderSettings(context, userRenderSettings)

    props.setCurrentShot(currentShot, changeTime=False)

    return filesDict


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
    renderDisplayInfo += "\n                                 *** Shot Manager V " + props.version()[0] + " - "

    def _generateEditFiles():
        """renderedFilesDict is also updated"""
        if not module_can_be_imported("shotmanager.otio"):
            _logger.error("Otio module not available - Edit file export failed")
            return

        from shotmanager.otio.exports import exportTakeEditToOtio

        renderedFilesDict["edit_files"] = []

        if "VIDEO" in preset.outputMediaMode or not config.devDebug:
            output_filepath = f"{props.getOutputMediaPath('TK_EDIT_VIDEO', take, rootPath=props.renderRootPath, insertSeqPrefix=True, provideExtension=False)}.{props.renderSettingsOtio.otioFileType.lower()}"
            renderedOtioFile = exportTakeEditToOtio(
                scene,
                take,
                props.renderRootPath,
                output_filepath=output_filepath,
                fileListOnly=False,
                output_media_mode="VIDEO",
            )
            renderedFilesDict["edit_files"].append(output_filepath)

        if config.devDebug and "IMAGE_SEQ" in preset.outputMediaMode:
            output_filepath = f"{props.getOutputMediaPath('TK_EDIT_IMAGE_SEQ', take, rootPath=props.renderRootPath, insertSeqPrefix=True, provideExtension=False)}.{props.renderSettingsOtio.otioFileType.lower()}"
            renderedOtioFile = exportTakeEditToOtio(
                scene,
                take,
                props.renderRootPath,
                output_filepath=output_filepath,
                fileListOnly=False,
                output_media_mode="IMAGE_SEQ",
            )
            renderedFilesDict["edit_files"].append(output_filepath)

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
        _logger.error("No valid render preset found")

    stampInfoSettings = None
    useStampInfo = preset.useStampInfo
    if "PLAYBLAST" == renderMode:
        useStampInfo = useStampInfo and preset.stampRenderInfo

    fileIsReadOnly = False
    currentFilePath = bpy.path.abspath(bpy.data.filepath)
    if "" == currentFilePath:
        fileIsReadOnly = True
    else:
        stat = Path(currentFilePath).stat()
        # print(f"Blender file Stats: {stat.st_mode}")
        fileIsReadOnly = S_IMODE(stat.st_mode) & S_IWRITE == 0

    if props.use_project_settings and props.isStampInfoAvailable() and useStampInfo:
        stampInfoSettings = scene.UAS_StampInfo_Settings
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
    renderDisplayInfo += f"{'   - Stamp Info: ': <20}{useStampInfo}\n"
    if config.devDebug:
        renderDisplayInfo += f"{'   - Debug Mode: ': <20}{config.devDebug}\n"

    renderDisplayInfo += "\n"
    print(renderDisplayInfo)

    take = props.getCurrentTake()
    if take is None:
        print("Shot Manager Rendering: No current take found - Rendering aborted")
        return False

    context.window_manager.UAS_shot_manager_shots_play_mode = False
    context.window_manager.UAS_shot_manager_display_overlay_tools = False

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

        # get the list of files to write, delete them is they exists, stop everything if the delete cannot be done
        #            shotFileName = shot.

        renderedFilesDict = launchRenderWithVSEComposite(
            context,
            preset,
            filePath=props.renderRootPath,
            useStampInfo=preset.useStampInfo,
            generateSequenceVideo=False,
            specificShotList=[shot],
            specificFrame=scene.frame_current,
            area=area,
        )

    elif "ANIMATION" == preset.renderMode:
        _logger.debug("Render Animation")
        if not fileIsReadOnly:
            bpy.ops.wm.save_mainfile()
        shot = props.getCurrentShot()

        renderedFilesDict = launchRenderWithVSEComposite(
            context,
            preset,
            filePath=props.renderRootPath,
            useStampInfo=preset.useStampInfo,
            generateSequenceVideo=False,
            specificShotList=[shot],
            render_handles=preset.renderHandles if preset.bypass_rendering_project_settings else True,
            area=area,
        )

    elif "ALL" == preset.renderMode:
        _logger.debug(f"Render All: {str(props.renderSettingsAll.renderAllTakes)}")
        _logger.debug(f"Render All, preset.renderAllTakes: {preset.renderAllTakes}")
        if not fileIsReadOnly:
            bpy.ops.wm.save_mainfile()

        takesToRender = None
        if preset.renderAllTakes:
            print("Render All takes")
            takesToRender = [i for i in range(0, len(props.takes))]
        elif len(props.takes):
            currentTakeInd = props.getCurrentTakeIndex()
            if -1 != currentTakeInd:
                takesToRender = [currentTakeInd]

        for takeInd in takesToRender:
            renderedFilesDict = launchRenderWithVSEComposite(
                context,
                preset,
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

                take = props.takes[takeInd]
                if "VIDEO" in props.renderSettingsAll.outputMediaMode:
                    _generateEditFiles()

                # renderedOtioFile = exportShotManagerEditToOtio(
                #     scene,
                #     takeIndex=takeInd,
                #     filePath=props.renderRootPath,
                #     fileName=f"{props.getCurrentTake().getName_PathCompliant(withPrefix=True)}.{props.renderSettingsOtio.otioFileType.lower()}",
                #     fileListOnly=False,
                #     #  montageCharacteristics=props.get_montage_characteristics(),
                # )

                # renderedFilesDict["edl_files"] = [renderedOtioFile]

    elif "OTIO" == renderMode:
        take = props.getCurrentTake()
        renderedFilesDict = dict()
        _generateEditFiles()

    elif "PLAYBLAST" == preset.renderMode:
        _logger.debug("Render Playblast")
        if not fileIsReadOnly:
            bpy.ops.wm.save_mainfile()

        if context.space_data.overlay.show_overlays and preset.disableCameraBG:
            bpy.ops.uas_shots_settings.use_background(useBackground=False)

        renderedFilesDict = launchRenderWithVSEComposite(
            context,
            preset,
            takeIndex=-1,
            filePath=props.renderRootPath,
            fileListOnly=False,
            useStampInfo=preset.stampRenderInfo and preset.useStampInfo,
            rerenderExistingShotVideos=True,
            generateShotVideos=False,
            generateSequenceVideo=True,
            renderAlsoDisabled=False,
            render_handles=False,
            renderSound=preset.renderSound,
            area=area,
        )

        # open rendered media in a player
        if preset.openPlayblastInPlayer:
            if len(renderedFilesDict["sequence_video_file"]):
                utils.openMedia(renderedFilesDict["sequence_video_file"], inExternalPlayer=True)

        # open rendered media in vse
        # wkip removed until uas_videotracks works
        if False and preset.updatePlayblastInVSM:
            from shotmanager.scripts.rrs.rrs_playblast import rrs_playblast_to_vsm

            rrs_playblast_to_vsm(playblastInfo=renderedFilesDict["playblastInfos"])

    else:
        print("\n *** preset.renderMode is invalid, cannot render anything... ***\n")

    if renderedFilesDict is not None:
        # TODO: improve rendering log display
        print(json.dumps(renderedFilesDict, indent=4))

    print("Shot Manager rendering done\n")
