import os
import json

import bpy

from ..config import config
from ..scripts.rrs.RRS_StampInfo import setRRS_StampInfoSettings


def launchRenderWithVSEComposite(renderMode, takeIndex=-1, filePath="", useStampInfo=True, fileListOnly=False):
    """ Generate the media for the specified take
        Return a dictionary with a list of all the created files and a list of failed ones
        filesDict = {"rendered_files": newMediaFiles, "failed_files": failedFiles}
    """
    context = bpy.context
    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props

    print(" *** launchRenderWithVSEComposite")
    print("    render_shot_prefix:", props.renderShotPrefix())

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
    sequenceScene.frame_start = 0
    sequenceScene.frame_end = props.getEditDuration() - 1
    sequenceScene.render.image_settings.file_format = "FFMPEG"
    sequenceScene.render.ffmpeg.format = "MPEG4"
    sequenceScene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
    sequenceScene.render.ffmpeg.gopsize = 5  # keyframe interval
    sequenceScene.render.ffmpeg.audio_codec = "AC3"
    sequenceScene.render.filepath = f"{rootPath}{take.getName_PathCompliant()}\\{props.renderShotPrefix()}.mp4"

    context.window_manager.UAS_shot_manager_shots_play_mode = False
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
        # context.window_manager.UAS_shot_manager_progressbar = (i + 1) / len(shotList) * 100.0
        # bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=2)

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

                RRS_StampInfo.notesUsed = shot.hasNotes()
                RRS_StampInfo.notesLine01 = shot.note01
                RRS_StampInfo.notesLine02 = shot.note02
                RRS_StampInfo.notesLine03 = shot.note03

                #    print("RRS_StampInfo.takeName: ", RRS_StampInfo.takeName)
            #        RRS_StampInfo.shotName = f"{props.renderShotPrefix()}_{shot.name}"
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
                    RRS_StampInfo.shotName = f"{props.renderShotPrefix()}_{shot.name}"
                    RRS_StampInfo.cameraName = shot.camera.name
                    scene.render.resolution_x = 1280
                    scene.render.resolution_y = 960
                    RRS_StampInfo.edit3DFrame = props.getEditTime(shot, currentFrame)

                    print("RRS_StampInfo.takeName: ", RRS_StampInfo.takeName)
                    print("RRS_StampInfo.renderRootPath: ", RRS_StampInfo.renderRootPath)
                    RRS_StampInfo.renderRootPath = newTempRenderPath

                    if not fileListOnly:
                        RRS_StampInfo.renderTmpImageWithStampedInfo(scene, currentFrame)

                # area.spaces[0].region_3d.view_perspective = 'CAMERA'

                scene.render.resolution_x = 1280
                scene.render.resolution_y = 720

                if not fileListOnly:
                    bpy.ops.render.render(animation=False, write_still=True)

            # render sound
            if not fileListOnly:
                audioFilePath = newTempRenderPath + f"{props.renderShotPrefix()}_{shot.name}" + ".wav"
                print("audioFilePath: ", audioFilePath)
                # bpy.ops.sound.mixdown(filepath=audioFilePath, relative_path=True, container='WAV', codec='PCM')
                bpy.ops.sound.mixdown(filepath=audioFilePath, relative_path=False, container="WAV", codec="PCM")

            # compositedMediaPath = shot.getOutputFileName(fullPath=True, rootFilePath=rootPath)     # if we use that the shot .mp4 is rendered in the shot dir
            # here we render in the take dir
            compositedMediaPath = f"{rootPath}{take.getName_PathCompliant()}\\{shot.getOutputFileName(fullPath=False)}"

            # use vse_render to store all the elements to composite
            if not fileListOnly:
                vse_render = context.window_manager.UAS_vse_render
                vse_render.inputOverMediaPath = (scene.render.filepath)[0:-8] + "####" + ".png"
                print("inputOverMediaPath: ", vse_render.inputOverMediaPath)
                vse_render.inputOverResolution = (1280, 720)
                vse_render.inputBGMediaPath = newTempRenderPath + "_tmp_StampInfo.####.png"
                vse_render.inputBGResolution = (1280, 960)
                vse_render.inputAudioMediaPath = audioFilePath

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
            if not fileListOnly:
                files_in_directory = os.listdir(newTempRenderPath)
                filtered_files = [file for file in files_in_directory if file.endswith(".png") or file.endswith(".wav")]

                for file in filtered_files:
                    path_to_file = os.path.join(newTempRenderPath, file)
                    os.remove(path_to_file)
                try:
                    os.rmdir(newTempRenderPath)
                except Exception:
                    print("Cannot delete Dir: ", newTempRenderPath)

            print(f"shot.getEditStart: {shot.getEditStart()}, props.handles: {props.handles}")

            if not fileListOnly:
                vse_render.createNewClip(
                    sequenceScene,
                    compositedMediaPath,
                    sequenceScene.frame_start,
                    shot.getEditStart() - props.handles,
                    offsetStart=props.handles,
                    offsetEnd=props.handles,
                )

    # render full sequence
    # Note that here we are back to the sequence scene, not anymore in the shot scene
    bpy.context.window.scene = sequenceScene

    if not fileListOnly:
        bpy.ops.render.opengl(animation=True, sequencer=True)

    newMediaFiles.append(sequenceScene.render.filepath)
    failedFiles = []

    filesDict = {"rendered_files": newMediaFiles, "failed_files": failedFiles}

    # cleaning current file from temp scenes
    if not config.uasDebug:
        # current scene is sequenceScene
        bpy.ops.scene.delete()

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
