import os
from pathlib import Path
from urllib.parse import unquote_plus, urlparse
import re

from random import uniform
from math import radians

import bpy
import opentimelineio

from shotmanager import config
from shotmanager.utils import utils
from shotmanager.utils import utils_vse

from . import otio_wrapper as ow

import logging

_logger = logging.getLogger(__name__)


def importTrack(track, trackInd, track_type, timeRange=None, offsetFrameNumber=0, alternative_media_folder=""):
    verbose = False
    #   verbose = "VIDEO" == track_type

    trackInfo = f"\n\n------------------------------------------------------------"
    trackInfo += f"\n------------------------------------------------------------"
    trackInfo += f"\n  - Track {trackInd}: {track.name}, {track_type}"

    range_start = -9999999
    range_end = 9999999
    fps = 25
    if timeRange is not None:
        range_start = timeRange[0]
        range_end = timeRange[1]
        trackInfo += f" - import from {range_start} to {range_end} (included)"
    if verbose:
        print(f"{trackInfo}")

    for i, clip in enumerate(track.each_clip()):
        # if 5 < i:
        #    break
        clip_start = ow.get_clip_frame_final_start(clip, fps)
        clip_end = ow.get_timeline_clip_end_inclusive(clip)

        clipInfo = f"\n\n- *** ----------------------------"
        clipInfo += f"\n  - Clip name: {clip.name}, Clip ind: {i}"

        isInRange = utils.segment_is_in_range(clip_start, clip_end, range_start, range_end, partly_inside=True)

        # excluse media out of range
        if not isInRange:
            excludInfo = " not in range"
            # print(f"{excludInfo}")
            continue

        media_path = Path(ow.get_clip_media_path(clip))

        # possibly excluse some media types
        # mediaExt = Path(media_path).suffix
        # if mediaExt == ".wav":
        #     excludInfo = "    ** Media exluded: "
        #     continue

        clipInfo += f", media: {media_path}"
        # clipInfo += f"\n  -   metadata:{clip.metadata['fcp_xml']}\n"
        clipInfo += f"\n  -   metadata:{clip.metadata}\n"
        if verbose:
            print(f"{clipInfo}")
            print(f"clip_start: {clip_start}, clip_end: {clip_end}, range_start: {range_start}, range_end: {range_end}")
            # _logger.debug(f"{clipInfo}")

            # print(f"{clip}")
            #   print(f"       Import Otio media_path: {media_path}")

            # print(f"{clipInfo}")
            # print(f"{clip}")

            # print("       Clip is in range")
            #    print(f"{clipInfo}")
            # offsetFrameNumber = 2
            #    _logger.debug(f"media_path: {media_path}")
            print(f"       Import at frame: offsetFrameNumber: {offsetFrameNumber}")
        if not media_path.exists():
            print(f"    *** Media not found: {media_path}")
            # Lets find it inside next to the xml
            # media_path = Path(otioFile).parent.joinpath(media_path.name)
            media_path = Path(alternative_media_folder).joinpath(media_path.name)
            _logger.debug(f'** media not found, so using alternative_media_folder: "{alternative_media_folder}"')
            _logger.debug(f"   and new media_path: {media_path}")

        if not media_path.exists():
            print(f"    *** Media still not found: {media_path}")
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

            if newClipInVSE is not None:

                clipEnabled = True
                if verbose:
                    print(f" -*- clip metadata: {clip.metadata}")

                if "fcp_xml" in clip.metadata:
                    # print(" -*- fcp_xml is ok")
                    # print(f"metadata; clip.metadata['fcp_xml']['enabled']: {clip.metadata['fcp_xml']['enabled']}")
                    if "enabled" in clip.metadata["fcp_xml"]:
                        clipEnabled = not ("FALSE" == clip.metadata["fcp_xml"]["enabled"])
                newClipInVSE.mute = not clipEnabled

                if track_type == "AUDIO":
                    if "fcp_xml" in clip.metadata:
                        if "filter" in clip.metadata["fcp_xml"]:
                            if "effect" in clip.metadata["fcp_xml"]["filter"]:
                                if "parameter" in clip.metadata["fcp_xml"]["filter"]["effect"]:
                                    if "parameter" in clip.metadata["fcp_xml"]["filter"]["effect"]:
                                        if "value" in clip.metadata["fcp_xml"]["filter"]["effect"]["parameter"]:
                                            volumeVal = float(
                                                clip.metadata["fcp_xml"]["filter"]["effect"]["parameter"]["value"]
                                            )
                                            if verbose:
                                                print(f" volume value: {volumeVal}")
                                            newClipInVSE.volume = volumeVal

                    audio_volume_keyframes = []
                    if clip.metadata is not None:
                        effect = clip.metadata.get("fcp_xml", {}).get("filter", {}).get("effect")
                        if effect is not None and effect["effectcategory"] == "audiolevels":
                            keyframe_data = effect.get("parameter", {}).get("keyframe")
                            if keyframe_data is not None:
                                if isinstance(keyframe_data, opentimelineio._otio.AnyVector):
                                    for keyframe in keyframe_data:
                                        frame = opentimelineio.opentime.to_frames(
                                            opentimelineio.opentime.RationalTime(float(keyframe["when"]))
                                        )
                                        audio_volume_keyframes.append((frame, float(keyframe["value"])))
                                else:
                                    frame = opentimelineio.opentime.to_frames(
                                        opentimelineio.opentime.RationalTime(float(keyframe_data["when"]))
                                    )
                                    audio_volume_keyframes.append((frame, float(keyframe_data["value"])))

                    for f, v in audio_volume_keyframes:
                        newClipInVSE.volume = v
                        newClipInVSE.keyframe_insert("volume", frame=f)

            if verbose:
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
                if verbose:
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
    montageOtio,
    ref_sequence_name,
    clipList,
    timeRange=None,
    offsetTime=True,
    importAtFrame=0,
    reformatShotNames=False,
    createCameras=True,
    useMediaAsCameraBG=False,
    mediaHaveHandles=False,
    mediaHandlesDuration=0,
    useMediaSoundtrackForCameraBG=False,
    importVideoInVSE=False,
    importAudioInVSE=True,
    videoTracksList=None,
    audioTracksList=None,
    animaticFile=None,
):
    """
        timeRange: use a 2 elments array
        When offsetTime is True and a range is used then the start of the extracted edit range will be
        placed at the frame specified by importAtFrame
        timeRange end is inclusive!
    """

    # filePath="", fileName=""):

    offsetFrameNumber = 0
    if offsetTime:
        if timeRange is None:
            offsetFrameNumber = importAtFrame
        else:
            offsetFrameNumber = importAtFrame - timeRange[0]

    print(f"Import Otio File: {montageOtio.otioFile}, num clips: {len(clipList)}")
    if timeRange is not None:
        print(f"   from {timeRange[0]} to {timeRange[1]} (included)")

    # print("clipList:", clipList)

    # wkip temp - to remove! Shots are added to another take!
    props = scene.UAS_shot_manager_props
    if len(props.getCurrentTake().getShotList()) != 0:
        bpy.ops.uas_shot_manager.take_add(name=Path(montageOtio.otioFile).stem)

    handlesDuration = 0
    if mediaHaveHandles:
        handlesDuration = mediaHandlesDuration

    # try:
    if True:
        timeline = montageOtio.timeline
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
                    montageOtio.timeline,
                    vse,
                    timeRange=timeRange,
                    offsetFrameNumber=offsetFrameNumber,
                    track_type=trackType,
                    videoTracksList=videoTracksList,
                    audioTracksList=audioTracksList,
                    alternative_media_folder=Path(montageOtio.otioFile).parent,
                )

                # restore workspace
                # bpy.context.window.workspace = bpy.data.workspaces["Layout"]
                bpy.context.window.workspace = currentWorkspace

            if animaticFile is not None:
                importAnimatic(montageOtio, ref_sequence_name, animaticFile, offsetFrameNumber)

            # restore context
            # wkip ajouter time range original
            props.setCurrentShotByIndex(0)
            props.setSelectedShotByIndex(0)

        # except opentimelineio.exceptions.NoKnownAdapterForExtensionError:
        #     from ..utils.utils import ShowMessageBox

        # ShowMessageBox("File not recognized", f"{otioFile} could not be understood by Opentimelineio", "ERROR")


def importAnimatic(montageOtio, sequenceName, animaticFile, offsetFrameNumber=0):
    if not Path(animaticFile).exists():
        return

    vse_render = bpy.context.window_manager.UAS_vse_render
    # newClipInVSE = vse_render.createNewClip(
    #     bpy.context.scene,
    #     animaticFile,
    #     31,
    #     25,
    #     # offsetStart=frameOffsetStart,
    #     # offsetEnd=frameOffsetEnd,
    #     importVideo=True,
    #     importAudio=True,
    #     clipName="Animatic",
    # )

    # sequence
    # seq = montageOtio.get_sequence_by_name(sequenceName)
    # if seq is not None:

    #     offsetFrameNumber = 25
    #     newClipInVSE = vse_render.createNewClipFromRange(
    #         bpy.context.scene,
    #         animaticFile,
    #         31,
    #         frame_start=offsetFrameNumber - 1 * seq.get_frame_start(),
    #         frame_final_start=1 * offsetFrameNumber,
    #         frame_final_end=seq.get_frame_duration() + offsetFrameNumber,
    #         importVideo=True,
    #         importAudio=True,
    #         clipName="Animatic",
    #     )
    #     if newClipInVSE is not None:
    #         pass
    # pass

    seq = montageOtio.get_sequence_by_name(sequenceName)
    if seq is not None:
        shots = seq.getEditShots()

        offsetFrameNumber = 0
        for sh in shots:
            print(f"{sh.get_name()}: sh.get_frame_final_start(): {sh.get_frame_final_start()}")

            #####
            # Code has to be repeated otherwise not working... :/
            #####
            newClipInVSE = vse_render.createNewClipFromRange(
                bpy.context.scene,
                animaticFile,
                31,
                frame_start=0,  # - 1 * sh.get_frame_start(),
                frame_final_start=1 * offsetFrameNumber + sh.get_frame_final_start(),
                frame_final_end=sh.get_frame_final_end() + offsetFrameNumber,
                importVideo=True,
                importAudio=False,
                clipName="Animatic",
            )
            print(f"newClipInVSE video .frame_start: {newClipInVSE.frame_start}")

            newClipInVSE = vse_render.createNewClipFromRange(
                bpy.context.scene,
                animaticFile,
                32,
                frame_start=0,  # - 1 * sh.get_frame_start(),
                frame_final_start=1 * offsetFrameNumber + sh.get_frame_final_start(),
                frame_final_end=sh.get_frame_final_end() + offsetFrameNumber,
                importVideo=False,
                importAudio=True,
                clipName="Animatic",
            )

            print(f"newClipInVSE audio.frame_start: {newClipInVSE.frame_start}")


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
    mediaInEDLHaveHandles=False,
    mediaInEDLHandlesDuration=0,
    clearVSE=True,
    clearCameraBG=True,
    changeShotsTiming=True,
    createMissingShots=True,
    createCameras=True,
    useMediaAsCameraBG=False,
    useMediaSoundtrackForCameraBG=False,
    videoShotsFolder=None,
    mediaHaveHandles=False,
    mediaHandlesDuration=0,
    takeIndex=-1,
    importVideoInVSE=False,
    importAudioInVSE=False,
    videoTracksList=None,
    audioTracksList=None,
    animaticFile=None,
):
    """
        Conform / update current montage to match specified montage
        If ref_sequence_name is specified then only this sequence is compared
    """

    # scene = bpy.context.scene
    props = scene.UAS_shot_manager_props

    takeInd = (
        props.getCurrentTakeIndex()
        if -1 == takeIndex
        else (takeIndex if 0 <= takeIndex and takeIndex < len(props.getTakes()) else -1)
    )
    if -1 == takeInd:
        return

    take = props.getTakeByIndex(takeInd)
    shotList = props.get_shots(takeIndex=takeInd)

    if not mediaInEDLHaveHandles:
        mediaInEDLHandlesDuration = 0
    if not mediaHaveHandles:
        mediaHandlesDuration = 0

    def printInfoLine(col00, col01, col02=None, modifsSelf=None, jumpLine=True):
        if col02 is not None:
            formatedTextLine = f"{col00: >6}  {col01: <40}    - {col02: <30}"
        else:
            if len(modifsSelf):
                formatedTextLine = "\n" if jumpLine else ""
                formatedTextLine += f"{col00: >6}  {col01: <40}     {modifsSelf[0]: <30}"
                for i in range(1, len(modifsSelf)):
                    col00 = ""
                    col01 = ""
                    formatedTextLine += f"\n{col00: >6}  {col01: <40}        - {modifsSelf[i]: <30}"

        # print(formatedTextLine)
        return "\n" + formatedTextLine

    def _writeToLogFile(infoText):
        textFilePath = str(Path(bpy.data.filepath).parent) + "\\" + "ConfoLog.txt"
        print(f" -- output file: {textFilePath}")
        with open(textFilePath, "w") as text_file:

            from datetime import datetime

            now = datetime.now()

            confoDisplayInfo = f"\nConformation of {bpy.data.filepath}"
            confoDisplayInfo += f"\n---------------------------------------------------------------------\n\n"
            confoDisplayInfo += f"{'   - Date: ': <20}{now.strftime('%b-%d-%Y')}  -  {now.strftime('%H:%M:%S')}\n"

            confoDisplayInfo += f"{'   - File: ': <20}{bpy.data.filepath}\n"
            confoDisplayInfo += f"{'   - Scene: ': <20}{scene.name}\n"
            if config.uasDebug:
                confoDisplayInfo += f"{'   - Debug Mode: ': <20}{config.uasDebug}\n"

            print(f"{confoDisplayInfo}", file=text_file)

            print(f"{infoText}", file=text_file)
        return textFilePath

    textSelf = ""
    textRef = ""

    print(f"\n\n {utils.bcolors.HEADER}Conform montage to {ref_montage.get_name()}:{utils.bcolors.ENDC}\n")

    infoStr = f"\n\n------ ------ ------ ------ ------ ------ ------ ------ ------ "
    infoStr += f"\n\nConform montage to {ref_montage.get_name()}:\n"
    # print(infoStr)

    # infoStr += (
    #     f"\nNote: All the end values are EXCLUSIVE (= not the last used frame of the range but the one after)"
    # )
    # infoStr += f"\n        Ref: {ref_montage.get_name(): >30}       -  {props.get_name() : >30}"
    textRef = ref_montage.get_name()
    textSelf = props.get_name()
    # printInfoLine("", textRef, textSelf)
    infoStr += f"\n  {textRef + ':' :<44} {textSelf + ':' :<30}"

    # selfSeq = props.get_sequence_by_name(ref_sequence_name)
    selfSeq = (props.get_sequences())[0]  # wkip limité à 1 take pour l'instant
    textSelf = f"  Current Sequence: {selfSeq.get_name()}"

    refSeq = ref_montage.get_sequence_by_name(ref_sequence_name)
    if "" != ref_sequence_name:
        if refSeq is not None:
            textRef = f"  Ref Sequence: {refSeq.get_name()}"

    infoStr += f"\n  {textRef + ':' :<44} {textSelf + ':' :<30}"

    if refSeq is None:
        infoStr += "\n Ref Sequence is None, aborting conformation..."
        print(infoStr)
        return _writeToLogFile(infoStr)

    ###################
    # update take infos
    ###################
    # wkip dir hardcoded :S
    print(f"\n *** animatif file: {animaticFile}")
    if animaticFile is not None:
        take.globalEditDirectory = str(Path(animaticFile).parent)
        take.globalEditVideo = animaticFile
    take.startInGlobalEdit = refSeq.getEditShots()[0].get_frame_final_start()

    ###################
    # clear VSE
    ###################
    vse_render = bpy.context.window_manager.UAS_vse_render
    if clearVSE:
        vse_render.clearAllChannels(scene)
    utils_vse.showSecondsInVSE(False)

    ###################
    # conform order and enable state
    ###################

    # comparedShotsList = selfSeq.getEditShots(ignoreDisabled=False)  # .copy()  # .getEditShots()

    # newEditShots = list()
    numShotsInRefEdit = len(refSeq.getEditShots())
    expectedIndInSelfEdit = 0
    previousShotSelf = None
    shotIndForBGCam = 0
    for indInRefEdit, shot in enumerate(refSeq.getEditShots()):
        shotRef = shot
        textRef = shotRef.get_name()
        shotRefName = Path(shotRef.get_name()).stem
        shotRefType = shotRef.get_type()

        shotSelfModifs = []

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
                # print(
                #     f"here 01: seqSelfName: {seqSelfName}, shotRefName: {shotRefName}, {shotRefName.find(seqSelfName)}"
                # )
                # if the current ref shot name starts with the current sequence name then it is a valid shot for this sequence
                if 0 == shotRefName.find(seqSelfName):
                    shotRefNameWithoutPrefix = shotRefName[len(seqSelfName) :]

                    frame_start_3D = 25 if previousShotSelf is None else previousShotSelf.end + 1
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
                    if shotSelf.camera is not None:
                        shotSelf.camera.color = [0, 0, 1, 1]

                    noteStr = "New shot added from "
                    if "RRSpecial_ACT01_AQ_201103_TECH" == ref_montage.get_name():
                        noteStr += "Act01_Edit_Previz.xml (Oct. 4th, 2020)"
                    else:
                        noteStr += ref_montage.get_name()
                    shotSelf.note01 = noteStr

                    shotSelf = props.moveShotToIndex(shotSelf, expectedIndInSelfEdit)
                    expectedIndInSelfEdit += 1

                    modifStr = f"{shotSelf.get_name()}:  "
                    modifStr += " *** New shot ***"

                    textSelf = modifStr
                    textSelf += " / new shot"
                    shotSelfModifs.append(modifStr)

                else:
                    modifStr = f"- (No shot created, ref shot belongs to another sequence)"
                    textSelf = modifStr
                    shotSelfModifs.append(modifStr)

            else:
                modifStr = f"-"
                textSelf = modifStr
                shotSelfModifs.append(modifStr)

        else:
            modifStr = f"{shotSelf.get_name()}  "
            textSelf = modifStr
            shotSelfModifs.append(modifStr)

            # set shot position in take edit
            shotInd = props.getShotIndex(shotSelf)
            if expectedIndInSelfEdit != shotInd:
                shotSelf = props.moveShotToIndex(shotSelf, expectedIndInSelfEdit)

            # newEditShots.append(shotSelf)
            if not shotSelf.enabled:
                modifStr = "enabled"
                shotSelfModifs.append(modifStr)
                textSelf += f" / {modifStr}"
            # print(f" ++ shot name before enabled: {shotSelf.name}, enabled: {shotSelf.enabled}")
            shotSelf.enabled = True

            if changeShotsTiming:
                # we check if the start handle is used in the edit. When the clip is a Stack we cannot know if there is a clip start frame in the handle
                if "Clip" == shotRefType:
                    offsetStart = shotRef.get_frame_offset_start()
                    if offsetStart != mediaInEDLHandlesDuration:
                        deltaStart = offsetStart - mediaInEDLHandlesDuration
                        modifStr = f"offset start modified ({offsetStart} instead of {mediaInEDLHandlesDuration} fr.) (delta:{deltaStart})"
                        shotSelfModifs.append(modifStr)
                        textSelf += f" / {modifStr}"
                        shotSelf.start += deltaStart

                previousDuration = shotSelf.get_frame_final_duration()
                newDuration = shotRef.get_frame_final_duration()
                if previousDuration != newDuration:
                    shotSelf.setDuration(newDuration, bypassLock=True)
                    modifStr = f"duration changed (was {previousDuration} fr.)"
                    shotSelfModifs.append(modifStr)
                    textSelf += f" / {modifStr}"

                shotSelf.durationLocked = True

            expectedIndInSelfEdit += 1

            # make camera unique
            if useMediaAsCameraBG:
                if shotSelf.camera is not None and 1 < props.getNumSharedCamera(shotSelf.camera):
                    camName = shotSelf.camera.name
                    shotSelf.makeCameraUnique()
                    modifStr = (
                        f"camera {camName} was shared with another shot, duplicated to become {shotSelf.camera.name}"
                    )
                    shotSelfModifs.append(modifStr)
                    textSelf += f" / {modifStr}"

        ###################
        # clear camera BG and add new ones from edit
        ###################
        # if clearCameraBG:
        if shotSelf is not None:
            if shotSelf.camera is not None:
                # print(f"--- Adding BG to: {shotSelf.get_name()}")
                # utils.remove_background_video_from_cam(shotSelf.camera.data)
                shotSelf.removeBGImages()

                if useMediaAsCameraBG:
                    media_path = Path(videoShotsFolder + "/" + shotRef.get_name())
                    if "" == media_path.suffix:
                        media_path = Path(str(media_path) + ".mp4")

                    modifStr = f"New cam BG: {media_path.name}"
                    textSelf += f" / {modifStr}"

                    if not media_path.exists():
                        print(f"** BG video shot not found: {media_path}")
                        modifStr += f" (!!! Not Found in {media_path.parent})"
                        textSelf += f" (!!! Not Found in {media_path.parent})"
                    else:
                        # if True:
                        # start frame of the background video is not set here since it will be linked to the shot start frame
                        utils.add_background_video_to_cam(
                            shotSelf.camera.data, str(media_path), 0, alpha=props.shotsGlobalSettings.backgroundAlpha
                        )

                        # modifStr += f" (BG Added, new BG: {shotSelf.camera.data.background_images[0].clip.name})"
                        # print(f"shotSelf.camera.data BG:{shotSelf.camera.data.background_images[0].clip.name}")

                        shotSelf.bgImages_linkToShotStart = True
                        if mediaHaveHandles:
                            shotSelf.bgImages_offset = -1 * mediaHandlesDuration

                    shotSelfModifs.append(modifStr)

                    ###################
                    # use sound for cam BG
                    ###################
                    if useMediaSoundtrackForCameraBG:

                        # store current workspace cause it may not be the Layout one
                        # currentWorkspace = bpy.context.window.workspace

                        # # creation VSE si existe pas
                        # vse = utils.getSceneVSE(scene.name, createVseTab=True)
                        # bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]

                        # for indInRefEdit, shot in enumerate(refSeq.getEditShots()):
                        #     shotRef = shot
                        #     textRef = shotRef.get_name()
                        #     shotRefName = Path(shotRef.get_name()).stem

                        #     media_path = Path(videoShotsFolder + "/" + shotRef.get_name())
                        #     if "" == media_path.suffix:
                        #         media_path = Path(str(media_path) + ".mp4")

                        # if not media_path.exists():
                        #     print(f"** Edit video shot not found for VSE: {media_path}")
                        # else:

                        #####################
                        # trackInd = 4 + shotIndForBGCam
                        # newClipInVSE = vse_render.createNewClip(
                        #     scene,
                        #     str(media_path),
                        #     trackInd,
                        #     # shotRef.get_frame_final_start(),  # shotSelf.start + offsetFrameNumber
                        #     shotSelf.start,
                        #     importVideo=False,
                        #     importAudio=True,
                        #     clipName=shotRefName,
                        # )
                        # if newClipInVSE is not None:
                        #     shotSelf.bgImages_sound_trackIndex = newClipInVSE.channel

                        trackInd = 4 + shotIndForBGCam
                        props.addBGSoundToShot(str(media_path), shotSelf)

                        # refresh properties and their update function
                        shotSelf.bgImages_linkToShotStart = shotSelf.bgImages_linkToShotStart
                        shotSelf.bgImages_offset = shotSelf.bgImages_offset

                        shotIndForBGCam += 1
                        pass

        infoStr += printInfoLine(
            str(indInRefEdit),
            f"{textRef}  ({shotRefType} - {shotRef.get_frame_final_duration()} fr.)",
            modifsSelf=shotSelfModifs,
        )

        if shotSelf is not None:
            previousShotSelf = shotSelf

    ###################
    # fit time range
    ###################
    scene.use_preview_range = False
    if len(take.shots):
        scene.frame_start = take.shots[0].start

    if previousShotSelf is not None:
        scene.frame_end = previousShotSelf.end

    ###################
    # list other shots and disabled them
    ###################
    infoStr += f"\n\n   Shots not used in current sequence (and then disabled):"
    infoStr += f"\n   -------------------------------------------------------\n"

    ind = 0
    for i in range(expectedIndInSelfEdit, len(shotList)):
        shotSelfModifs = []

        # if shotList[i] not in newEditShots:
        if not shotList[i].name.endswith("_removed"):
            shotList[i].name += "__removed"
        textSelf = shotList[i].get_name()

        # following code removed because a camera can be shared by several shots
        # if shotList[i].camera is not None:
        #     shotList[i].camera.color = [1, 0, 0, 1]

        noteStr = "Shot removed from "
        if "RRSpecial_ACT01_AQ_201103_TECH" == ref_montage.get_name():
            noteStr += "Act01_Edit_Previz.xml (Oct. 4th, 2020)"
        else:
            noteStr += ref_montage.get_name()
        shotList[i].note01 = noteStr

        if shotList[i].enabled:
            shotList[i].enabled = False
            textSelf += " / disabled"

        shotSelfModifs.append(textSelf)

        # infoStr += printInfoLine(str(ind + numShotsInRefEdit), "-", modifsSelf=shotSelfModifs)
        infoStr += printInfoLine("", "-", modifsSelf=shotSelfModifs, jumpLine=False)
        ind += 1

        ###################
        # clear camera BG
        ###################
        # if clearCameraBG:
        #     if shotList[i].camera is not None:
        #         utils.remove_background_video_from_cam(shotList[i].camera.data)

    if 0 == ind:
        infoStr += printInfoLine("", "-", "-")

    ###################
    # sort disabled shots
    ###################
    props.sortShotsVersions()

    ###################
    # import sound tracks in VSE
    ###################

    shotList = props.getShotsList(ignoreDisabled=True, takeIndex=takeInd)
    if len(shotList):
        if importVideoInVSE or importAudioInVSE:
            # store current workspace cause it may not be the Layout one
            currentWorkspace = bpy.context.window.workspace

            # creation VSE si existe pas
            vse = utils.getSceneVSE(scene.name, createVseTab=True)
            bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]

            # for area in screen.areas:
            #     if area.type == "SEQUENCE_EDITOR":
            #         for space_data in area.spaces:
            #             if space_data.type == "SEQUENCE_EDITOR":
            #                 space_data.show_seconds = True
            #                 break

            trackType = "ALL"
            if importVideoInVSE and not importAudioInVSE:
                trackType = "VIDEO"
            elif not importVideoInVSE and importAudioInVSE:
                trackType = "AUDIO"

            # timeRange end is inclusive, meaning that clips overlaping this value will be imported
            timeRange = [refSeq.get_frame_start(), refSeq.get_frame_end() - 1]
            # get the start time of the first shot

            importAtFrame = shotList[0].start
            offsetFrameNumber = importAtFrame - timeRange[0]

            # trackType = "ALL"
            # if importVideoInVSE and not importAudioInVSE:
            #     trackType = "VIDEO"
            # elif not importVideoInVSE and importAudioInVSE:
            #     trackType = "AUDIO"

            # we import the sound only, because videos coming from the EDL are not the shots from the edit!
            trackType = "AUDIO"

            importToVSE(
                ref_montage.timeline,
                vse,
                timeRange=timeRange,
                offsetFrameNumber=offsetFrameNumber,
                track_type=trackType,
                videoTracksList=videoTracksList,
                audioTracksList=audioTracksList,
                alternative_media_folder=Path(ref_montage.otioFile).parent,
            )

            # add videos from the edit
            vse_render = bpy.context.window_manager.UAS_vse_render

            for indInRefEdit, shot in enumerate(refSeq.getEditShots()):
                shotRef = shot
                textRef = shotRef.get_name()
                shotRefName = Path(shotRef.get_name()).stem

                media_path = Path(videoShotsFolder + "/" + shotRef.get_name())
                if "" == media_path.suffix:
                    media_path = Path(str(media_path) + ".mp4")

                if not media_path.exists():
                    print(f"** Edit video shot not found for VSE: {media_path}")
                else:
                    newClipInVSE = vse_render.createNewClip(
                        scene,
                        str(media_path),
                        18,
                        shotRef.get_frame_final_start() + offsetFrameNumber,
                        importVideo=True,
                        importAudio=False,
                        clipName=shotRefName,
                    )

                    if newClipInVSE is not None:
                        res_x = 1280
                        res_y = 960
                        clip_x = 1280
                        clip_y = 720
                        vse_render.cropClipToCanvas(
                            res_x, res_y, newClipInVSE, clip_x, clip_y, mode="FIT_WIDTH",
                        )
                        # newClipInVSE.use_crop = True
                        # newClipInVSE.crop.min_x = 1 * int((1280 - 1280) / 2)
                        # newClipInVSE.crop.max_x = newClipInVSE.crop.min_x
                        # newClipInVSE.crop.min_y = 1 * int((960 - 720) / 2)
                        # newClipInVSE.crop.max_y = newClipInVSE.crop.min_y

                        # overClip.blend_type = "OVER_DROP"

            # restore workspace
            # bpy.context.window.workspace = bpy.data.workspaces["Layout"]
            bpy.context.window.workspace = currentWorkspace

    # if animaticFile is not None:
    #     importAnimatic(ref_montage, sequenceName, animaticFile, offsetFrameNumber)

    # props.setCurrentShotByIndex(0)
    # props.setSelectedShotByIndex(0)

    infoStr += "\n"
    print(infoStr)

    return _writeToLogFile(infoStr)


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

