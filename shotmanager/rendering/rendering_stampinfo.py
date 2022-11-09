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
Rendering code for stamp info
"""

import bpy

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def setStampInfoSettings(scene, resolution, resolutionFramed):

    if bpy.context.scene.UAS_SM_StampInfo_Settings is not None:

        props = config.getAddonProps(scene)
        stampInfoSettings = scene.UAS_SM_StampInfo_Settings

        stampInfoSettings.stampInfoUsed = props.useStampInfoDuringRendering

        if stampInfoSettings.stampInfoUsed:

            #####################
            # enable or disable stamp info properties
            #####################
            if props.use_project_settings:
                # wkip get stamp info configuration specifed for the project

                ####################################
                # top
                ####################################

                stampInfoSettings.dateUsed = True
                stampInfoSettings.timeUsed = True
                stampInfoSettings.userNameUsed = True

                stampInfoSettings.videoFrameUsed = True
                stampInfoSettings.videoRangeUsed = True
                stampInfoSettings.videoHandlesUsed = True

                stampInfoSettings.animDurationUsed = True

                # defined per shot?
                # stampInfoSettings.notesUsed = shot.hasNotes()
                # stampInfoSettings.cornerNoteUsed = not shot.enabled

                ####################################
                # bottom
                ####################################

                if hasattr(stampInfoSettings, "sequenceUsed"):
                    stampInfoSettings.sequenceUsed = True
                stampInfoSettings.sceneUsed = True
                stampInfoSettings.takeUsed = True
                #  stampInfoSettings.shotName       = shotName
                stampInfoSettings.shotUsed = True
                stampInfoSettings.cameraUsed = True
                stampInfoSettings.cameraLensUsed = True

                stampInfoSettings.edit3DFrameUsed = True
                stampInfoSettings.edit3DTotalNumberUsed = True
                stampInfoSettings.framerateUsed = True

                stampInfoSettings.shotDurationUsed = True

                stampInfoSettings.filenameUsed = True
                stampInfoSettings.filepathUsed = True

                stampInfoSettings.currentFrameUsed = True
                stampInfoSettings.frameRangeUsed = True
                stampInfoSettings.frameHandlesUsed = True
                # stampInfoSettings.shotHandles = props.handles

                ####################################
                # general
                ####################################

                stampInfoSettings.borderUsed = True
                stampInfoSettings.stampPropertyLabel = False
                stampInfoSettings.stampPropertyValue = True

                stampInfoSettings.debug_DrawTextLines = False

            else:
                # use stamp info settings from scene
                pass

            #####################
            # set the value of stamp info global properties (ie not dependent on current time not on scene state),
            # this independently from their display state set above
            #####################

            if props.use_project_settings:
                projProp_Name = props.project_name

                # projProp_resolution_x = props.project_resolution_x
                # projProp_resolution_y = props.project_resolution_y
                # projProp_resolutionFramed = [props.project_resolution_framed_x, props.project_resolution_framed_y]

                # projProp_resolution_x = resolution[0]  # not used
                projProp_resolution_y = resolution[1]
                projProp_resolutionFramed = resolutionFramed

                stampInfoSettings.stampInfoRenderMode = "OUTSIDE"
                stampInfoSettings.stampRenderResYOutside_percentage = (
                    float(projProp_resolutionFramed[1]) / projProp_resolution_y
                ) * 100.0 - 100.0

                stampInfoSettings.stampInfoRenderMode = "OVER"
                # wkipwkipwkip we should use outside mode when framed_y > y
                stampInfoSettings.stampRenderResOver_percentage = (
                    projProp_resolution_y / float(projProp_resolutionFramed[1]) * 100.0
                )

                stampInfoSettings.automaticTextSize = False
                stampInfoSettings.extPaddingNorm = 0.020
                stampInfoSettings.fontScaleHNorm = 0.0168
                stampInfoSettings.interlineHNorm = 0.0072

                ####################################
                # top
                ####################################

                ############
                # logo

                if "" == props.project_logo_path:
                    # no logo used at all because none specified
                    stampInfoSettings.logoUsed = False
                else:
                    stampInfoSettings.logoUsed = True
                    stampInfoSettings.logoMode = "CUSTOM"
                    stampInfoSettings.logoFilepath = f"{props.project_logo_path}"

                stampInfoSettings.logoScaleH = 0.05
                stampInfoSettings.logoPosNormX = 0.018
                stampInfoSettings.logoPosNormY = 0.014

                stampInfoSettings.projectName = projProp_Name
                stampInfoSettings.projectUsed = True

                # stampInfoSettings.edit3DFrame = props.     # set in the render loop
                # stampInfoSettings.edit3DTotalNumber = props.getEditDuration()

                ####################################
                # bottom
                ####################################

            else:
                pass
                # projProp_resolution_x = scene.render.resolution_x
                # projProp_resolution_y = scene.render.resolution_y

            stampInfoSettings.tmp_usePreviousValues = False

            # stampInfoSettings.tmp_previousResolution_x = projProp_resolution_x
            # stampInfoSettings.tmp_previousResolution_y = projProp_resolution_y

            # stampInfoSettings.tmp_stampRenderResYDirToCompo_percentage = (
            #     stampInfoSettings.stampRenderResYDirToCompo_percentage
            # )


def renderStampedInfoForFrame(scene, shot):
    pass


def renderStampedInfoForShot(
    stampInfoSettings,
    shotManagerProps,
    take,
    shot,
    rootPath,
    newTempRenderPath,
    resolution,
    resolutionFramed,
    handles,
    render_handles=True,
    specificFrame=None,
    stampInfoCustomSettingsDict=None,
    verbose=False,
):
    """Launch the rendering or the frames of the shot, with Stamp Info

    In this function Stamp Info properties values are updated according to the current time
    and the state of the scene.
    The display itself of the properties is NOT modified here, it is supposed to be already
    set thanks to a call to setStampInfoSettings

    Args:
        resolution: array [width, height], resolution of the image rendered in Blender
    """
    if not (newTempRenderPath.endswith("/") or newTempRenderPath.endswith("\\")):
        newTempRenderPath += "\\"

    txtIntro = "\nRendering StampInfo image sequence:"
    txtIntro += f"   Shot: {shot.name}, handles: {render_handles} ({handles})"
    txtIntro += f"\n{' - Rendered image resolution: ': <40}{resolution[0]} x {resolution[1]}"
    txtIntro += f"\n{' - Final frame resolution: ': <40}{resolutionFramed[0]} x {resolutionFramed[1]}"
    txtIntro += f"\n{' - Path: ': <20}{newTempRenderPath}"
    txtIntro += "\n---------------\n"
    _logger.print_ext(txtIntro, col="CYAN")
    # scene.render.filepath

    props = shotManagerProps
    scene = props.parentScene
    verbose = verbose or config.devDebug
    takeName = take.getName_PathCompliant()

    #####################
    # TOFIX Custom Stamp Info settings??????????????
    #####################
    if stampInfoCustomSettingsDict is not None:
        print(f"*** customFileFullPath: {stampInfoCustomSettingsDict['customFileFullPath']}")
        if "customFileFullPath" in stampInfoCustomSettingsDict:
            stampInfoSettings.customFileFullPath = stampInfoCustomSettingsDict["customFileFullPath"]

    #####################
    # enable or disable stamp info properties
    #####################
    if props.use_project_settings:
        # wkip get stamp info configuration specifed for the project

        stampInfoSettings.notesUsed = shot.hasNotes()
        stampInfoSettings.cornerNoteUsed = not shot.enabled

        stampInfoSettings.bottomNoteUsed = take.hasNotes()
        if take.hasNotes():
            # TOFIX currently only the first of the 3 take notes is supported here
            stampInfoSettings.bottomNote = take.note01
        else:
            stampInfoSettings.bottomNote = ""

    else:
        # use stamp info settings from scene
        pass

    #####################
    # set properties independently to them being enabled or not
    #####################

    if hasattr(stampInfoSettings, "sequenceName"):
        stampInfoSettings.sequenceName = props.getSequenceName("FULL")

    if props.use_project_settings:
        # wkip get stamp info configuration specifed for the project

        stampInfoSettings.takeName = takeName

        stampInfoSettings.notesLine01 = shot.note01
        stampInfoSettings.notesLine02 = shot.note02
        stampInfoSettings.notesLine03 = shot.note03

        stampInfoSettings.videoFirstFrameIndexUsed = True
        stampInfoSettings.videoFirstFrameIndex = props.project_output_first_frame
        stampInfoSettings.frameDigitsPadding = props.project_img_name_digits_padding

    else:
        # set stamp info property values according to the scene
        stampInfoSettings.takeName = takeName

        stampInfoSettings.notesLine01 = shot.note01
        stampInfoSettings.notesLine02 = shot.note02
        stampInfoSettings.notesLine03 = shot.note03

        # video_frame_start = prefs.output_first_frame

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

    # scene.render.resolution_x = 1280
    # scene.render.resolution_y = 960

    numFramesInShot = scene.frame_end - scene.frame_start + 1

    # if props.use_project_settings:
    #     scene.render.resolution_x = props.project_resolution_framed_x
    #     scene.render.resolution_y = props.project_resolution_framed_y

    # # scene.render.resolution_x = resolution[0]
    # # scene.render.resolution_y = resolution[1]

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

        # TODO
        renderStampedInfoForFrame(scene, currentFrame)

        # scene.frame_current = currentFrame
        scene.frame_set(currentFrame)

        # scene.render.filepath = shot.getOutputMediaPath(
        #     rootPath=rootPath, insertTempFolder=True, specificFrame=scene.frame_current
        # )
        scene.render.filepath = shot.getOutputMediaPath(
            "SH_INTERM_STAMPINFO_SEQ", rootPath=rootPath, specificFrame=scene.frame_current
        )
        #    shotFilename = shot.getName_PathCompliant()

        stampInfoSettings.renderRootPath = newTempRenderPath

        stampInfoSettings.shotName = f"{props.getRenderShotPrefix()}{shot.name}"
        # stampInfoSettings.shotName = f"{shot.name}"

        if stampInfoCustomSettingsDict is not None:
            if True or "asset_tracking_step" in stampInfoCustomSettingsDict:
                stampInfoSettings.bottomNoteUsed = True
                stampInfoSettings.bottomNote = "Step: " + stampInfoCustomSettingsDict["asset_tracking_step"]
            else:
                stampInfoSettings.bottomNoteUsed = False
                stampInfoSettings.bottomNote = ""

        stampInfoSettings.cameraName = shot.camera.name
        stampInfoSettings.edit3DFrame = props.getEditTime(shot, currentFrame, referenceLevel="GLOBAL_EDIT")

        tmpShotFilename = shot.getOutputMediaPath(
            "SH_INTERM_STAMPINFO_SEQ", providePath=False, specificFrame=currentFrame
        )
        if verbose:
            # txt = "      ------------------------------------------"
            txt = f"Stamp Info Frame:  Shot: {shot.name} {currentFrame}   ( {f + 1} / {numFramesInShot} )"
            # txt += f"\n    File path: {scene.render.filepath}"
            # txt += f"\n{'   - File name: ': <20}{tmpShotFilename}"
            txt += f"{'   File: '}{tmpShotFilename}"
            # txt += f"\n    stampInfoSettings.renderRootPath: {stampInfoSettings.renderRootPath}"
            _logger.info_ext(txt)

        stampInfoSettings.renderTmpImageWithStampedInfo(
            scene,
            currentFrame,
            resolution=resolutionFramed,
            innerHeight=resolution[1],
            renderPath=newTempRenderPath,
            renderFilename=tmpShotFilename,
            verbose=False,
        )

    if verbose:
        txt = "\n------------------------------------------\n"
        _logger.info_ext(txt, col="CYAN")

    ##############
    # restore scene state
    ##############

    scene.camera = previousCam
    scene.frame_start = previousFrameStart
    scene.frame_end = previousFrameEnd

    scene.render.resolution_x = previousResX
    scene.render.resolution_y = previousResY
