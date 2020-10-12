import os
from pathlib import Path
from urllib.parse import unquote_plus, urlparse
import re

from random import uniform
from math import radians

import bpy
import opentimelineio

from ..utils import utils

from . import otio_wrapper as ow

import logging

_logger = logging.getLogger(__name__)


def importTrack(track, trackInd, track_type, timeRange=None, offsetFrameNumber=0, alternative_media_folder=""):

    range_start = -9999999
    range_end = 9999999
    fps = 25
    if timeRange is not None:
        range_start = timeRange[0]
        range_end = timeRange[1]

    for i, clip in enumerate(track.each_clip()):
        clip_start = ow.get_clip_frame_final_start(clip, fps)
        clip_end = ow.get_timeline_clip_end_inclusive(clip)

        media_path = Path(ow.get_clip_media_path(clip))
        clipInfo = f"\n-----------------------------"
        clipInfo += f"\n  - Clip name: {clip.name}, Clip ind: {i}, media: {media_path}\n"

        #   print(f"       Import Otio media_path: {media_path}")

        isInRange = utils.segment_is_in_range(clip_start, clip_end, range_start, range_end, partly_inside=True)

        mediaExt = Path(media_path).suffix
        if not isInRange:  # or mediaExt == ".wav":
            excludInfo = "    ** Media exluded: "
            # if mediaExt == ".wav":
            #     excludInfo += ".wav,"
            if not isInRange:
                excludInfo += " not in range"
        # print(f"{clipInfo}")
        # print(f"{excludInfo}")

        else:
            # print("       Clip is in range")
            print(f"{clipInfo}")
            # offsetFrameNumber = 2
            _logger.debug(f"media_path: {media_path}")
            print(f"       Import at frame: offsetFrameNumber: {offsetFrameNumber}")
            if not media_path.exists():
                print(f"    *** Media not found: {media_path}")
                # Lets find it inside next to the xml
                # media_path = Path(otioFile).parent.joinpath(media_path.name)
                media_path = Path(alternative_media_folder).joinpath(media_path.name)
                _logger.debug(f'** media not found, so using alternative_media_folder: "{alternative_media_folder}"')
                _logger.debug(f"   and new media_path: {media_path}")

            if not media_path.exists():
                print(f"    *** Media not found: {media_path}")
            else:
                media_path = str(media_path)

                # start = ow.get_clip_frame_final_start(clip) + offsetFrameNumber
                start = opentimelineio.opentime.to_frames(clip.range_in_parent().start_time)
                end = ow.get_timeline_clip_end_inclusive(clip) + offsetFrameNumber
                availableRange = clip.available_range()
                # _logger.debug(f"  clip.available_range(): {clip.available_range()}")
                # _logger.debug(f"  clip.available_range().duration: {clip.available_range().duration}")
                # _logger.debug(
                #     f"  clip.available_range().rescaled_to(25): {(clip.available_range().end_time_inclusive()).rescaled_to(25)}"
                # )
                # _logger.debug(
                #     f"  clip.available_range().value_rescaled_to(25): {clip.available_range().end_time_exclusive().value_rescaled_to(25)}"
                # )

                offsetEnd = (
                    start
                    + clip.available_range().end_time_exclusive().value_rescaled_to(25)
                    - opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_exclusive())
                    - opentimelineio.opentime.to_frames(clip.source_range.start_time)
                )

                frameStart = ow.get_clip_frame_start(clip, fps)
                frameEnd = ow.get_clip_frame_end(clip, fps)
                frameFinalStart = ow.get_clip_frame_final_start(clip, fps)
                frameFinalEnd = ow.get_clip_frame_final_end(clip, fps)
                frameOffsetStart = ow.get_clip_frame_offset_start(clip, fps)
                frameOffsetEnd = ow.get_clip_frame_offset_end(clip, fps)
                frameDuration = ow.get_clip_frame_duration(clip, fps)
                frameFinalDuration = ow.get_clip_frame_final_duration(clip, fps)

                frameStart += offsetFrameNumber
                frameEnd += offsetFrameNumber
                frameFinalStart += offsetFrameNumber
                frameFinalEnd += offsetFrameNumber

                _logger.debug(
                    f"Abs clip values: clip frameStart: {frameStart}, frameFinalStart:{frameFinalStart}, frameFinalEnd:{frameFinalEnd}, frameEnd: {frameEnd}"
                )
                _logger.debug(
                    f"Rel clip values: clip frameOffsetStart: {frameOffsetStart}, frameOffsetEnd:{frameOffsetEnd}"
                )
                _logger.debug(
                    f"Duration clip values: clip frameDuration: {frameDuration}, frameFinalDuration:{frameFinalDuration}"
                )

                vse_render = bpy.context.window_manager.UAS_vse_render
                newClipInVSE = vse_render.createNewClip(
                    bpy.context.scene,
                    media_path,
                    trackInd,
                    frameStart,
                    offsetStart=frameOffsetStart,
                    offsetEnd=frameOffsetEnd,
                    importVideo=track_type == "VIDEO",
                    importAudio=track_type == "AUDIO",
                    clipName=clip.name,
                )

                vse_render.printClipInfo(newClipInVSE, printTimeInfo=True)
                # _logger.debug(f"newClipInVSE: {newClipInVSE.name}")

                # frameStart = newClipInVSE.frame_start
                # frameEnd = -1  # newClipInVSE.frame_end
                # frameFinalStart = newClipInVSE.frame_final_start
                # frameFinalEnd = newClipInVSE.frame_final_end
                # frameOffsetStart = newClipInVSE.frame_offset_start
                # frameOffsetEnd = newClipInVSE.frame_offset_end
                # frameDuration = newClipInVSE.frame_duration
                # frameFinalDuration = newClipInVSE.frame_final_duration

                # frameStart += offsetFrameNumber
                # frameEnd += offsetFrameNumber
                # frameFinalStart += offsetFrameNumber
                # frameFinalEnd += offsetFrameNumber

                # _logger.debug(
                #     f"Abs clip values: clip frameStart: {frameStart}, frameFinalStart:{frameFinalStart}, frameFinalEnd:{frameFinalEnd}, frameEnd: {frameEnd}"
                # )
                # _logger.debug(
                #     f"Rel clip values: clip frameOffsetStart: {frameOffsetStart}, frameOffsetEnd:{frameOffsetEnd}"
                # )
                # _logger.debug(
                #     f"Duration clip values: clip frameDuration: {frameDuration}, frameFinalDuration:{frameFinalDuration}"
                # )

                # fix to prevent the fact that the sound is sometimes longer than expected by 1 frame
                if newClipInVSE.frame_final_duration > ow.get_clip_frame_final_duration(clip, fps):
                    print(
                        f"newClipInVSE.frame_final_duration: {newClipInVSE.frame_final_duration}, ow.get_clip_frame_final_duration(clip, fps): {ow.get_clip_frame_final_duration(clip, fps)}"
                    )
                    # newClipInVSE.frame_offset_end = -1 * (
                    #     newClipInVSE.frame_final_duration - ow.get_clip_frame_final_duration(clip, fps)
                    # )
                    newClipInVSE.frame_final_duration = ow.get_clip_frame_final_duration(clip, fps)

                # bpy.context.window_manager.UAS_vse_render.createNewClip(
                #     bpy.context.scene,
                #     media_path,
                #     trackInd,
                #     start - otio_clipLocalCutStart,
                #     offsetStart=otio_clipLocalCutStart,
                #     offsetEnd=offsetEnd,
                #     # offsetEnd=end - otio_clipLocalCutStart + trimmedClipDuration,
                #     # trimmedClipDuration=trimmedClipDuration,
                #     importVideo=track_type == "VIDEO",
                #     importAudio=track_type == "AUDIO",
                # )

    pass


def importToVSE(
    timeline,
    vse,
    timeRange=None,
    offsetFrameNumber=0,
    track_type="ALL",
    videoTracksList=None,
    audioTracksList=None,
    alternative_media_folder="",
):
    """
        track_type can be "ALL", "VIDEO" or "AUDIO"
    """
    # print(f"\nimportToVSE: track_type: {track_type}")

    # alternative_media_folder = Path(otioFile).parent

    # bpy.context.scene.frame_start = -999999
    # bpy.context.scene.frame_end = 999999

    # video
    if "ALL" == track_type or "VIDEO" == track_type:
        for trackInd, editTrack in enumerate(timeline.video_tracks()):
            if videoTracksList is None or (trackInd + 1) in videoTracksList:
                importTrack(
                    editTrack,
                    trackInd + 1,
                    "VIDEO",
                    timeRange=timeRange,
                    offsetFrameNumber=offsetFrameNumber,
                    alternative_media_folder=alternative_media_folder,
                )

    # audio
    if "ALL" == track_type or "AUDIO" == track_type:
        for trackInd, editTrack in enumerate(timeline.audio_tracks()):
            if audioTracksList is None or (trackInd + 1) in audioTracksList:
                importTrack(
                    editTrack,
                    trackInd + 1,
                    "AUDIO",
                    timeRange=timeRange,
                    offsetFrameNumber=offsetFrameNumber,
                    alternative_media_folder=alternative_media_folder,
                )


def getSequenceListFromOtio(otioFile):

    timeline = opentimelineio.adapters.read_from_file(otioFile)
    return getSequenceListFromOtioTimeline(timeline)


def getSequenceNameFromMediaName(fileName):
    print("\n\n **** Deprecated : imports.py getSequenceNameFromMediaName !!!")
    seqName = ""

    seq_pattern = "Seq"
    media_name_splited = fileName.split("_")
    if 2 <= len(media_name_splited):
        seqName = media_name_splited[1]

    return seqName

    # get file names only
    file_list = list()
    for item in media_list:
        filename = os.path.split(item)[1]
        file_list.append(os.path.splitext(filename)[0])
        # print(item)

    # get sequences
    seq_list = list()
    seq_pattern = "_seq"
    for item in file_list:
        if seq_pattern in item.lower():
            itemSplited = item.split("_")
            if 2 <= len(itemSplited):
                if itemSplited[1] not in seq_list:
                    seq_list.append(itemSplited[1])

    # for item in seq_list:
    #     print(item)

    return seq_list


def getSequenceListFromOtioTimeline(timeline):

    print("\n\n **** Deprecated : imports.py getSequenceListFromOtioTimeline !!!")
    if timeline is None:
        _logger.error("getSequenceListFromOtioTimeline: Timeline is None!")
        return

    media_list = ow.get_media_list(timeline, track_type="VIDEO")

    # get file names only
    file_list = list()
    for item in media_list:
        filename = os.path.split(item)[1]
        file_list.append(os.path.splitext(filename)[0])
        # print(item)

    # get sequences
    seq_list = list()
    seq_pattern = "_seq"
    for item in file_list:
        if seq_pattern in item.lower():
            itemSplited = item.split("_")
            if 2 <= len(itemSplited):
                if itemSplited[1] not in seq_list:
                    seq_list.append(itemSplited[1])

    # for item in seq_list:
    #     print(item)

    return seq_list


def createShotsFromOtio(
    scene,
    otioFile,
    importAtFrame=0,
    reformatShotNames=False,
    createCameras=True,
    useMediaAsCameraBG=False,
    mediaHaveHandles=False,
    mediaHandlesDuration=0,
    importAudioInVSE=True,
):
    # filePath="", fileName=""):

    print("Import Otio File createShotsFromOtio: ", otioFile)
    from random import uniform
    from math import radians

    props = scene.UAS_shot_manager_props
    if len(props.getCurrentTake().getShotList()) != 0:
        bpy.ops.uas_shot_manager.take_add(name=Path(otioFile).stem)

    handlesDuration = 0
    if mediaHaveHandles:
        handlesDuration = mediaHandlesDuration

    try:
        timeline = opentimelineio.adapters.read_from_file(otioFile)
        if len(timeline.video_tracks()):
            track = timeline.video_tracks()[0]  # Assume the first one contains the shots.

            cam = None
            if not createCameras:  # Create Default Camera
                cam_ob = utils.create_new_camera("Camera", location=[0, 0, 0])
                cam = cam_ob.data

            shot_re = re.compile(r"sh_?(\d+)", re.IGNORECASE)
            for i, clip in enumerate(track.each_clip()):
                clipName = clip.name
                if createCameras:
                    if reformatShotNames:
                        match = shot_re.search(clipName)
                        if match:
                            clipName = scene.UAS_shot_manager_props.new_shot_prefix + match.group(1)

                    cam_ob = utils.create_new_camera("Cam_" + clipName, location=[0.0, i, 0.0])
                    cam = cam_ob.data
                    cam_ob.color = [uniform(0, 1), uniform(0, 1), uniform(0, 1), 1]
                    cam_ob.rotation_euler = (radians(90), 0.0, radians(90))

                    # add media as camera background
                    if useMediaAsCameraBG:
                        print("Import Otio clip.media_reference.target_url: ", clip.media_reference.target_url)
                        media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
                        print("Import Otio media_path: ", media_path)
                        if not media_path.exists():
                            # Lets find it inside next to the xml
                            media_path = Path(otioFile).parent.joinpath(media_path.name)
                            print("** not found, so Path(self.otioFile).parent: ", Path(otioFile).parent)
                            print("   and new media_path: ", media_path)

                        # start frame of the background video is not set here since it will be linked to the shot start frame
                        utils.add_background_video_to_cam(
                            cam, str(media_path), 0, alpha=props.shotsGlobalSettings.backgroundAlpha
                        )

                shot = props.addShot(
                    name=clipName,
                    start=opentimelineio.opentime.to_frames(clip.range_in_parent().start_time) + importAtFrame,
                    end=opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame,
                    camera=cam_ob,
                    color=cam_ob.color,
                )
                # bpy.ops.uas_shot_manager.shot_add(
                #     name=clipName,
                #     start=opentimelineio.opentime.to_frames(clip.range_in_parent().start_time) + importAtFrame,
                #     end=opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame,
                #     cameraName=cam.name,
                #     color=(cam_ob.color[0], cam_ob.color[1], cam_ob.color[2]),
                # )
                shot.bgImages_linkToShotStart = True
                shot.bgImages_offset = -1 * handlesDuration

                # wkip maybe to remove
                scene.frame_start = importAtFrame
                scene.frame_end = (
                    opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame
                )

            if importAudioInVSE:
                # creation VSE si existe pas
                vse = utils.getSceneVSE(scene.name)
                # bpy.context.space_data.show_seconds = False
                bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]
                importOtioToVSE(otioFile, vse, importAtFrame=importAtFrame, importVideoTracks=False)

    except opentimelineio.exceptions.NoKnownAdapterForExtensionError:
        from ..utils.utils import ShowMessageBox

        ShowMessageBox("File not recognized", f"{otioFile} could not be understood by Opentimelineio", "ERROR")


def createShotsFromOtioTimelineClass(
    scene,
    otioTimelineClass,
    sequenceName,
    clipList,
    timeRange=None,
    offsetTime=True,
    importAtFrame=0,
    reformatShotNames=False,
    createCameras=True,
    useMediaAsCameraBG=False,
    mediaHaveHandles=False,
    mediaHandlesDuration=0,
    importVideoInVSE=False,
    importAudioInVSE=True,
    videoTracksList=None,
    audioTracksList=None,
):
    """
        timeRange: use a 2 elments array
        When offsetTime is True and a range is used then the start of the extracted edit range will be
        placed at the frame specified by importAtFrame
    """

    # filePath="", fileName=""):

    offsetFrameNumber = 0
    if offsetTime:
        if timeRange is None:
            offsetFrameNumber = importAtFrame
        else:
            offsetFrameNumber = importAtFrame - timeRange[0]

    print(f"Import Otio File: {otioTimelineClass.otioFile}, num clips: {len(clipList)}")
    if timeRange is not None:
        print(f"   from {timeRange[0]} to {timeRange[1]}")

    # print("clipList:", clipList)

    # wkip temp - to remove! Shots are added to another take!
    props = scene.UAS_shot_manager_props
    if len(props.getCurrentTake().getShotList()) != 0:
        bpy.ops.uas_shot_manager.take_add(name=Path(otioTimelineClass.otioFile).stem)

    handlesDuration = 0
    if mediaHaveHandles:
        handlesDuration = mediaHandlesDuration

    # try:
    if True:
        timeline = otioTimelineClass.timeline
        fps = 25
        if len(timeline.video_tracks()):
            # track = timeline.video_tracks()[0]  # Assume the first one contains the shots.

            cam = None
            if not createCameras:  # Create Default Camera
                cam_ob = utils.create_new_camera("Camera", location=[0, 0, 0])
                cam = cam_ob.data

            shot_re = re.compile(r"sh_?(\d+)", re.IGNORECASE)
            # for i, clip in enumerate(track.each_clip()):
            for i, clip in enumerate(clipList):
                clipName = clip.clip.name
                if createCameras:
                    if reformatShotNames:
                        match = shot_re.search(clipName)
                        if match:
                            clipName = scene.UAS_shot_manager_props.new_shot_prefix + match.group(1)

                    cam_ob = utils.create_new_camera("Cam_" + clipName, location=[0.0, i, 0.0])
                    cam = cam_ob.data
                    cam_ob.color = [uniform(0, 1), uniform(0, 1), uniform(0, 1), 1]
                    cam_ob.rotation_euler = (radians(90), 0.0, radians(90))

                    # add media as camera background
                    if useMediaAsCameraBG:
                        media_path = ow.get_clip_media_path(clip.clip)
                        # print("Import Otio media_path 1: ", media_path)
                        media_path = Path(media_path)
                        # print("Import Otio media_path 2: ", media_path)
                        if not media_path.exists():
                            # Lets find it inside next to the xml
                            media_path = Path(otioFile).parent.joinpath(media_path.name)
                            print("** not found, so Path(self.otioFile).parent: ", Path(otioFile).parent)
                            print("   and new media_path: ", media_path)

                        # start frame of the background video is not set here since it will be linked to the shot start frame
                        utils.add_background_video_to_cam(
                            cam, str(media_path), 0, alpha=props.shotsGlobalSettings.backgroundAlpha
                        )

                shot = props.addShot(
                    name=clipName,
                    start=ow.get_clip_frame_final_start(clip.clip, fps) + offsetFrameNumber,
                    end=ow.get_timeline_clip_end_inclusive(clip.clip) + offsetFrameNumber,
                    camera=cam_ob,
                    color=cam_ob.color,
                )
                shot.durationLocked = True

                shot.bgImages_linkToShotStart = True
                shot.bgImages_offset = -1 * handlesDuration

                # wkip maybe to remove
                scene.frame_start = offsetFrameNumber
                scene.frame_end = (
                    opentimelineio.opentime.to_frames(clip.clip.range_in_parent().end_time_inclusive())
                    + offsetFrameNumber
                )

            if importVideoInVSE or importAudioInVSE:
                # store current workspace cause it may not be the Layout one
                currentWorkspace = bpy.context.window.workspace

                # creation VSE si existe pas
                vse = utils.getSceneVSE(scene.name, createVseTab=True)
                bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]
                # bpy.context.space_data.show_seconds = False

                trackType = "ALL"
                if importVideoInVSE and not importAudioInVSE:
                    trackType = "VIDEO"
                elif not importVideoInVSE and importAudioInVSE:
                    trackType = "AUDIO"

                importToVSE(
                    otioTimelineClass.timeline,
                    vse,
                    timeRange=timeRange,
                    offsetFrameNumber=offsetFrameNumber,
                    track_type=trackType,
                    videoTracksList=videoTracksList,
                    audioTracksList=audioTracksList,
                    alternative_media_folder=Path(otioTimelineClass.otioFile).parent,
                )

                # restore workspace
                # bpy.context.window.workspace = bpy.data.workspaces["Layout"]
                bpy.context.window.workspace = currentWorkspace

            # restore context
            # wkip ajouter time range original
            props.setCurrentShotByIndex(0)
            props.setSelectedShotByIndex(0)

        # except opentimelineio.exceptions.NoKnownAdapterForExtensionError:
        #     from ..utils.utils import ShowMessageBox

        # ShowMessageBox("File not recognized", f"{otioFile} could not be understood by Opentimelineio", "ERROR")


# used only in functions here
def _addNewShot(
    props, shotName, start, end, createCameras, useMediaAsCameraBG=False, media_path=None, handlesDuration=0
):

    clipName = shotName
    if createCameras:
        # if reformatShotNames:
        #     match = shot_re.search(clipName)
        #     if match:
        #         clipName = scene.UAS_shot_manager_props.new_shot_prefix + match.group(1)

        cam_ob = utils.create_new_camera("Cam_" + clipName, location=[0.0, 0.0, 0.0])
        cam = cam_ob.data
        cam_ob.color = [uniform(0, 1), uniform(0, 1), uniform(0, 1), 1]
        cam_ob.rotation_euler = (radians(90), 0.0, radians(90))

        # add media as camera background
        if useMediaAsCameraBG:
            print("Import Otio clip.media_reference.target_url: ", clip.media_reference.target_url)
            # media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
            # print("Import Otio media_path: ", media_path)
            # if not media_path.exists():
            #     # Lets find it inside next to the xml
            #     media_path = Path(otioFile).parent.joinpath(media_path.name)
            #     print("** not found, so Path(self.otioFile).parent: ", Path(otioFile).parent)
            #     print("   and new media_path: ", media_path)

            # start frame of the background video is not set here since it will be linked to the shot start frame
            utils.add_background_video_to_cam(cam, str(media_path), 0, alpha=props.shotsGlobalSettings.backgroundAlpha)

    shot = props.addShot(name=clipName, start=start, end=end, durationLocked=True, camera=cam_ob, color=cam_ob.color,)
    shot.bgImages_linkToShotStart = True
    shot.bgImages_offset = -1 * handlesDuration

    return shot


# put this function in imports.py???
def conformToRefMontage(
    scene,
    ref_montage,
    ref_sequence_name="",
    clearVSE=True,
    clearCameraBG=True,
    createMissingShots=True,
    createCameras=True,
    useMediaAsCameraBG=False,
    mediaHaveHandles=False,
    mediaHandlesDuration=0,
    takeIndex=-1,
):
    # scene = bpy.context.scene
    props = scene.UAS_shot_manager_props

    takeInd = (
        props.getCurrentTakeIndex()
        if -1 == takeIndex
        else (takeIndex if 0 <= takeIndex and takeIndex < len(props.getTakes()) else -1)
    )
    if -1 == takeInd:
        return ()

    take = props.getTakeByIndex(takeInd)
    shotList = props.get_shots(takeIndex=takeInd)

    if not mediaHaveHandles:
        mediaHandlesDuration = 0

    """
        Conform / update current montage to match specified montage
        If ref_sequence_name is specified then only this sequence is compared
    """

    def printInfoLine(col00, col01, col02):
        print(f"{col00: >10}   {col01: <37}    - {col02: <30}")

    textSelf = ""
    textRef = ""

    infoStr = f"\n\n ------ ------ ------ ------ ------ ------ ------ ------ ------ "
    infoStr += f"\n\n {utils.bcolors.HEADER}Conform montage to {ref_montage.get_name()}:{utils.bcolors.ENDC}\n"
    print(infoStr)

    # infoStr += (
    #     f"\nNote: All the end values are EXCLUSIVE (= not the last used frame of the range but the one after)"
    # )
    # infoStr += f"\n        Ref: {ref_montage.get_name(): >30}       -  {props.get_name() : >30}"
    textRef = ref_montage.get_name()
    textSelf = props.get_name()
    # printInfoLine("", textRef, textSelf)
    print(f"     {textRef + ':' :<44} {textSelf + ':' :<30}")

    # selfSeq = props.get_sequence_by_name(ref_sequence_name)
    selfSeq = (props.get_sequences())[0]  # wkip limité à 1 take pour l'instant
    textSelf = f"  Current Sequence: {selfSeq.get_name()}"

    refSeq = ref_montage.get_sequence_by_name(ref_sequence_name)
    if "" != ref_sequence_name:
        if refSeq is not None:
            textRef = f"  Ref Sequence: {refSeq.get_name()}"

    print(f"     {textRef + ':' :<44} {textSelf + ':' :<30}")

    if refSeq is None:
        print(" Ref Sequence is None, aborting comparison...")
        return ()

    ###################
    # clear VSE
    ###################
    vse_render = bpy.context.window_manager.UAS_vse_render
    if clearVSE:
        vse_render.clearAllChannels(scene)

    ###################
    # clear camera BG
    ###################
    if clearCameraBG:
        for sh in shotList:
            if sh.camera is not None:
                utils.remove_background_video_from_cam(sh.camera.data)

    ###################
    # conform order and enable state
    ###################

    # comparedShotsList = selfSeq.getEditShots(ignoreDisabled=False)  # .copy()  # .getEditShots()

    # newEditShots = list()
    numShotsInRefEdit = len(refSeq.getEditShots())
    expectedIndInSelfEdit = 0
    for indInRefEdit, shot in enumerate(refSeq.getEditShots()):
        shotRef = shot
        textRef = shotRef.get_name()
        shotRefName = Path(shotRef.get_name()).stem

        shotSelf = None
        for sh in shotList:
            # if sh.get_name() == shotRef.get_name():
            shotName = props.renderShotPrefix() + "_" + sh.get_name()
            # print(f"shotName: {shotName}, shotRefName: {shotRefName}")
            if shotName == shotRefName:
                shotSelf = sh
                break

        if shotSelf is None:
            # wkip pb: we have no idea of the timing for the new shot...

            # media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
            # print("Import Otio media_path: ", media_path)
            # if not media_path.exists():
            #     # Lets find it inside next to the xml
            #     media_path = Path(otioFile).parent.joinpath(media_path.name)
            #     print("** not found, so Path(self.otioFile).parent: ", Path(otioFile).parent)
            #     print("   and new media_path: ", media_path)

            if createMissingShots:
                seqSelfName = props.renderShotPrefix() + "_"
                if 0 == shotRefName.find(seqSelfName):
                    shotRefNameWithoutPrefix = shotRefName[len(seqSelfName) :]

                    frame_start_3D = 25
                    frame_end_3D = frame_start_3D + shotRef.get_frame_final_duration() - 1

                    shotSelf = _addNewShot(
                        props,
                        shotRefNameWithoutPrefix,
                        frame_start_3D,
                        frame_end_3D,
                        createCameras,
                        useMediaAsCameraBG=False,  # useMediaAsCameraBG,
                        media_path="",  # media_path,
                        handlesDuration=mediaHandlesDuration,
                    )
                    shotSelf = props.moveShotToIndex(shotSelf, expectedIndInSelfEdit)
                    expectedIndInSelfEdit += 1

            if shotSelf is None:
                textSelf = "-"
            else:
                textSelf = shotSelf.get_name() + "  "
                textSelf += " / new shot"

        else:
            textSelf = shotSelf.get_name() + "  "

            # set shot position in take edit
            shotInd = props.getShotIndex(shotSelf)
            if expectedIndInSelfEdit != shotInd:
                shotSelf = props.moveShotToIndex(shotSelf, expectedIndInSelfEdit)

            #               newEditShots.append(shotSelf)
            if not shotSelf.enabled:
                textSelf += " / enabled"
            # print(f" ++ shot name before enabled: {shotSelf.name}, enabled: {shotSelf.enabled}")
            shotSelf.enabled = True

            offsetStart = shotRef.get_frame_offset_start()
            if offsetStart != mediaHandlesDuration:
                deltaStart = offsetStart - mediaHandlesDuration
                textSelf += f" / offset start modified ({offsetStart} instead of {mediaHandlesDuration} fr.) (delta:{deltaStart})"
                shotSelf.start += deltaStart

            previousDuration = shotSelf.get_frame_final_duration()
            newDuration = shotRef.get_frame_final_duration()
            if previousDuration != newDuration:
                shotSelf.setDuration(newDuration)
                textSelf += f" / duration changed (was {previousDuration} fr.)"

            shotSelf.durationLocked = True
            expectedIndInSelfEdit += 1

        printInfoLine(str(indInRefEdit), f"{textRef}  ({shotRef.get_frame_final_duration()} fr.)", textSelf)

    ###################
    # list other shots and disabled them
    ###################
    print("\n       Shots not used in current sequence:")
    ind = 0
    for i in range(expectedIndInSelfEdit, len(shotList)):
        # if shotList[i] not in newEditShots:
        textSelf = shotList[i].get_name()
        if shotList[i].enabled:
            shotList[i].enabled = False
            textSelf += " / disabled"

        printInfoLine(str(ind + numShotsInRefEdit), "-", textSelf)
        ind += 1
    if 0 == ind:
        printInfoLine("", "-", "-")

    ###################
    # sort disabled shots
    ###################
    props.sortShotsVersions()

    print("")


def importOtioToVSE(otioFile, vse, importAtFrame=0, importVideoTracks=True, importAudioTracks=True):
    print("ImportOtioToVSE: **** Deprecated ****")

    # def importTrack(track, trackInd, importAtFrame):
    #     for i, clip in enumerate(track.each_clip()):
    #         clipName = clip.name
    #         print("   Clip name: ", clipName)
    #         print("   Clip ind: ", i)

    #         print("Import Otio clip.media_reference.target_url: ", clip.media_reference.target_url)
    #         media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
    #         print("Import Otio media_path: ", media_path)
    #         print("  Import at frame: ", importAtFrame)
    #         if not media_path.exists():
    #             # Lets find it inside next to the xml
    #             media_path = Path(otioFile).parent.joinpath(media_path.name)
    #             print("** not found, so Path(self.otioFile).parent: ", Path(otioFile).parent)
    #             print("   and new media_path: ", media_path)

    #         if media_path.exists():
    #             media_path = str(media_path)

    #             # local clip infos:

    #             _logger.info(f"Logger info")
    #             _logger.warning(f"logger warning")
    #             _logger.error(f"logger error")

    #             start = opentimelineio.opentime.to_frames(clip.range_in_parent().start_time) + importAtFrame
    #             end = opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame
    #             duration = opentimelineio.opentime.to_frames(clip.available_range().end_time_inclusive())

    #             # local clip infos:
    #             otio_clipSourceRange = clip.source_range
    #             # clip cut in in local clip time ref (= relatively to clip start)
    #             otio_clipLocalCutStart = opentimelineio.opentime.to_frames(clip.source_range.start_time)
    #             # clip cut out in local clip time ref (= relatively to clip start)
    #             otio_clipLocalCutEnd = None  # opentimelineio.opentime.to_frames(clip.source_range.end_time())
    #             otio_clipLocalCutEndInclus = opentimelineio.opentime.to_frames(clip.source_range.end_time_inclusive())
    #             print(
    #                 f"\n   otio_clipSourceRange: {otio_clipSourceRange}, otio_clipLocalCutStart: {otio_clipLocalCutStart}, otio_clipLocalCutEnd: {otio_clipLocalCutEnd}, otio_clipLocalCutEndInclus: {otio_clipLocalCutEndInclus}"
    #             )

    #             otio_clipLocalCutEndInclus = opentimelineio.opentime.to_frames(clip.source_range.end_time_inclusive())
    #             trimmedClipDuration = opentimelineio.opentime.to_frames(clip.duration())
    #             print(
    #                 f"   start: {start}, end: {end}, duration: {duration}, trimmedClipDuration: {trimmedClipDuration}, otio_clipSourceRange: {otio_clipSourceRange}, otio_clipLocalCutEndInclus: {otio_clipLocalCutEndInclus}"
    #             )
    #             print("otio_clipSourceRange[0][0]: ", otio_clipSourceRange.start_time)
    #             print(
    #                 "otio_clipSourceRange[0][0]: ", opentimelineio.opentime.to_frames(otio_clipSourceRange.start_time)
    #             )
    #             # print(f"   range_from_start_end_time: {clip.range_in_parent().range_from_start_end_time()}")
    #             bpy.context.window_manager.UAS_vse_render.createNewClip(
    #                 bpy.context.scene,
    #                 media_path,
    #                 trackInd,
    #                 start - otio_clipLocalCutStart,
    #                 offsetStart=otio_clipLocalCutStart,
    #                 trimmedClipDuration=trimmedClipDuration,
    #             )

    #     pass

    #        try:
    timeline = opentimelineio.adapters.read_from_file(otioFile)
    # if len(timeline.video_tracks()):
    #     track = timeline.video_tracks()[0]  # Assume the first one contains the shots.

    # video
    if importVideoTracks:
        for trackInd, editTrack in enumerate(timeline.video_tracks()):
            print(f"\nDeprec Channel Name: {editTrack.name}, {trackInd}")
        #   importTrack(editTrack, trackInd + 1, importAtFrame)

    # audio
    if importAudioTracks:
        for trackInd, editTrack in enumerate(timeline.audio_tracks()):
            print(f"\nDeprec Channel Name: {editTrack.name}, {trackInd}")
        #  importTrack(editTrack, trackInd + 1, importAtFrame)


def import_otio(scene, filepath, old_dir, new_dir):
    old_dir = old_dir.replace("\\", "/")
    new_dir = new_dir.replace("\\", "/")
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    seq_editor = scene.sequence_editor

    timeline = opentimelineio.adapters.read_from_file(filepath)
    bad_file_uri_check = re.compile(
        r"^/\S:.*"
    )  # file uri parsing on windows can result in a leading / in front of the drive letter.

    for i, track in enumerate(timeline.tracks):
        track_kind = track.kind

        for clip in track.each_clip():
            media_path = unquote_plus(urlparse(clip.media_reference.target_url).path).replace("\\", "//")

            head, tail = os.path.split(media_path)
            media_path = new_dir + tail
            print("media_path: ", media_path)

            # if bad_file_uri_check.match(media_path):  # Remove leading /
            #     media_path = media_path[1:]
            # media_path = media_path.replace(old_dir, new_dir)

            # print("media_path: ", media_path)
            # media_path = Path(media_path)
            if not Path(media_path).exists():
                print(f"Could not be find {media_path}.")
            #     continue

            # if track_kind == "Video":
            #     c = seq_editor.sequences.new_movie(
            #         clip.name, str(media_path), i, opentimelineio.opentime.to_frames(clip.range_in_parent().start_time)
            #     )
            #     c.frame_final_duration = opentimelineio.opentime.to_frames(clip.duration())

            elif track_kind == "Audio":
                c = seq_editor.sequences.new_sound(
                    clip.name, str(media_path), i, opentimelineio.opentime.to_frames(clip.range_in_parent().start_time)
                )
                c.frame_final_duration = opentimelineio.opentime.to_frames(clip.duration())

