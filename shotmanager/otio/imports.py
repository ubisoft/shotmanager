import logging

_logger = logging.getLogger(__name__)

import os
from pathlib import Path
from urllib.parse import unquote_plus, urlparse
import re

import bpy
import opentimelineio


from ..utils import utils

from . import otio_wrapper as ow

from shotmanager.rrs_specific.montage.montage_otio import MontageOtio


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

        clipName = clip.name
        media_path = ow.get_clip_media_path(clip)
        clipInfo = f"\n-----------------------------"
        clipInfo += f"- Clip name: {clipName}, Clip ind: {i}, media: {Path(media_path).name}\n"

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
            print(f"       Import at frame: offsetFrameNumber: {offsetFrameNumber}")
            if not media_path.exists():
                # Lets find it inside next to the xml
                # media_path = Path(otioFile).parent.joinpath(media_path.name)
                media_path = Path(alternative_media_folder).joinpath(media_path.name)
                _logger.debug(f"** not found, so using alternative_media_folder: {alternative_media_folder}")
                _logger.debug(f"   and new media_path: {media_path}")

            if media_path.exists():
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

                bpy.context.window_manager.UAS_vse_render.createNewClip(
                    bpy.context.scene,
                    media_path,
                    trackInd,
                    frameStart,
                    offsetStart=frameOffsetStart,
                    offsetEnd=frameOffsetEnd,
                    importVideo=track_type == "VIDEO",
                    importAudio=track_type == "AUDIO",
                )

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
    print("\nimportToVSE: ")

    # alternative_media_folder = Path(otioFile).parent

    # bpy.context.scene.frame_start = -999999
    # bpy.context.scene.frame_end = 999999

    # video
    if "ALL" == track_type or "VIDEO" == track_type:
        for trackInd, editTrack in enumerate(timeline.video_tracks()):
            if videoTracksList is None or (trackInd + 1) in videoTracksList:
                print(f"\nChannel Name: {editTrack.name}, {trackInd + 1}, video")
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
                print(f"\nChannel Name: {editTrack.name}, {trackInd + 1}, audio")
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


# wkip to rename!!!!
def getSequenceClassListFromOtioTimeline(otioFile, verbose=False):
    print("\n\n **** Deprecated : imports.py getSequenceClassListFromOtioTimeline !!!")
    # wkip to remove!!
    # otioFile = r"Z:\_UAS_Dev\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere.xml"
    # otioFile = r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere.xml"
    # otioFile = r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere_to40.xml"

    # timeline = opentimelineio.adapters.read_from_file(otioFile)
    timeline = ow.get_timeline_from_file(otioFile)

    if timeline is None:
        _logger.error("getSequenceClassListFromOtioTimeline: Timeline is None!")
        return

    otioTimeline = MontageOtio()
    otioTimeline.otioFile = otioFile
    otioTimeline.timeline = timeline
    # otioTimeline.sequenceList = list()
    sequenceList = otioTimeline.sequencesList

    def _getParentSeqIndex(seqList, seqName):
        #    print("\n_getParentSeqIndex: seqName: ", seqName)
        for i, seq in enumerate(seqList):
            if seqName in seq.name.lower():
                #    print(f"    : {seq.name}, i: {i}")
                return i

        return -1

    tracks = timeline.video_tracks()
    for track in tracks:
        for clip in track:
            if isinstance(clip, opentimelineio.schema.Clip):
                # print(clip.media_reference)
                media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
                # print(f"{media_path}")

                # get media name
                filename = os.path.split(media_path)[1]
                media_name = os.path.splitext(filename)[0]
                media_name_lower = media_name.lower()

                # get parent sequence
                seq_pattern = "_seq"
                if seq_pattern in media_name_lower:
                    #    print(f"media_name: {media_name}")

                    media_name_splited = media_name_lower.split("_")
                    if 2 <= len(media_name_splited):
                        parentSeqInd = _getParentSeqIndex(sequenceList, media_name_splited[1])

                        # add new seq if not found
                        newSeq = None
                        if -1 == parentSeqInd:
                            newSeq = otioTimeline.newSequence()
                            newSeq.name = getSequenceNameFromMediaName(media_name)

                        else:
                            newSeq = sequenceList[parentSeqInd]
                        newSeq.newShot(clip)

    # for seq in sequenceList:
    #     # get the start and end of every seq
    #     seq.setStartAndEnd()
    #     if verbose:
    #         seq.printInfo()

    return otioTimeline

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

    print("\n\n **** Deprecated : imports.py getSequenceClassListFromOtioTimeline !!!")
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
    importSoundInVSE=True,
):
    # filePath="", fileName=""):

    print("Import Otio File createShotsFromOtio: ", otioFile)
    from random import uniform
    from math import radians

    props = scene.UAS_shot_manager_props
    if len(props.getCurrentTake().getShotList()) != 0:
        bpy.ops.uas_shot_manager.add_take(name=Path(otioFile).stem)

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
                # bpy.ops.uas_shot_manager.add_shot(
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

            if importSoundInVSE:
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
    importSoundInVSE=True,
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

    from random import uniform
    from math import radians

    props = scene.UAS_shot_manager_props
    if len(props.getCurrentTake().getShotList()) != 0:
        bpy.ops.uas_shot_manager.add_take(name=Path(otioTimelineClass.otioFile).stem)

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

            if importSoundInVSE:
                # store current workspace cause it may not be the Layout one
                currentWorkspace = bpy.context.window.workspace

                # creation VSE si existe pas
                vse = utils.getSceneVSE(scene.name)
                bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]
                # bpy.context.space_data.show_seconds = False

                importToVSE(
                    otioTimelineClass.timeline,
                    vse,
                    timeRange=timeRange,
                    offsetFrameNumber=offsetFrameNumber,
                    track_type="AUDIO",
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

