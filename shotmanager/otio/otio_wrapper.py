import logging

import opentimelineio

from pathlib import Path
from urllib.parse import unquote_plus, urlparse
import re

from ..utils import utils

_logger = logging.getLogger(__name__)


def parseOtioFile(otioFile):

    timeline = opentimelineio.adapters.read_from_file(otioFile)

    #### test get_media_list
    ############
    media_list = get_media_list(timeline, track_type="VIDEO")

    import os

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
                seq_list.append(itemSplited[1])

    for item in seq_list:
        print(item)
    return

    #### test get_media_occurence
    ############
    seq = "Seq0145"
    seq = "05 "
    # occ = get_media_occurence(timeline, seq, "ALL")
    get_media_occurence(timeline, seq, track_type="ALL", last_occurence=True)
    return

    ############

    # file name
    print("Otio file: ", otioFile)

    # framerate
    time = timeline.duration()
    rate = int(time.rate)
    print("\n    Framerate: ", rate)

    #############
    # # video tracks
    #############

    # number
    numVideoTracks = len(timeline.video_tracks())
    print("\n    Video Tracks: ", numVideoTracks)

    # list with index and name
    for trackInd, editTrack in enumerate(timeline.video_tracks()):
        print(f"     - {trackInd}: {editTrack.name}")

    print("\n\n*******************")
    for i in range(0, numVideoTracks):
        parseTrack(timeline, "VIDEO", i)

    #############
    # audio tracks
    #############

    # number
    numAudioTracks = len(timeline.audio_tracks())
    print("\n    Audio Tracks: ", numAudioTracks)

    # list with index and name
    for trackInd, editTrack in enumerate(timeline.audio_tracks()):
        print(f"     - {trackInd}: {editTrack.name}")

    print("\n\n*******************")
    for i in range(0, numVideoTracks):
        parseTrack(timeline, "VIDEO", i)


def parseTrack(timeline, track_type, track_index):
    """ Display the track information
        track_type can be "VIDEO" or "AUDIO"
    """
    # timeline = opentimelineio.adapters.read_from_file(otioFile)

    def _parseTrack(track):

        # print(f"    : {track.name}")
        tab = "   "
        tab2 = "      "

        ind = -1
        for i, clip in enumerate(track.each_clip()):
            ind += 1

            # i not working
            print(f"\n{tab}Clip: {ind}, {clip.name}")

            print(f"{tab2}clip.media_reference.target_url: {clip.media_reference.target_url}")
            media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
            print(f"{tab2}media_path: {media_path}")
            if not media_path.exists():
                # Lets find it inside next to the xml
                media_path = Path(otioFile).parent.joinpath(media_path.name)
                print(f"{tab2}   ** media not found, so Path(self.otioFile).parent: {Path(otioFile).parent}")
                print(f"{tab2}      and new media_path: {media_path}")

            if media_path.exists():
                media_path = str(media_path)
            else:
                print("   Media not found")

    #####
    #####

    if "VIDEO" == track_type:
        tracks = timeline.video_tracks()
        if track_index <= len(tracks):
            track_name = "<no name>" if "" == tracks[track_index].name else tracks[track_index].name
            print(f"\n\n*** Video Track: {track_index}, {track_name}:")
            _parseTrack(tracks[track_index])

    elif "AUDIO" == track_type:
        tracks = timeline.audio_tracks()
        if track_index <= len(tracks):
            track_name = "<no name>" if "" == tracks[track_index].name else tracks[track_index].name
            print(f"\n\n*** Audio Track: {track_index}, {track_name}:")
            _parseTrack(tracks[track_index])


def get_media_occurence(timeline, media_name, track_type="ALL", last_occurence=False):
    """ Return the first (or last if last_occurence is True) occurence of the clip with a name containing
        media_name found in the timeline
        track_type can be "ALL", "VIDEO" or "AUDIO"
    """
    found_clip = None
    tab = "   "

    def _get_media_first_occurence(tracks):
        first_c = None
        ind = -1
        for track in tracks:
            for i, clip in enumerate(track.each_clip()):
                ind += 1

                clip_name_l = clip.name.lower()
                if media_name_l in clip_name_l:
                    if first_c is None or get_timeline_clip_start(clip) < get_timeline_clip_start(first_c):
                        first_c = clip
                        print(f"\n{tab}Clip: {ind}, {clip.name}")
                        break

        return first_c

    def _get_media_last_occurence(tracks):
        last_c = None
        ind = -1
        for track in tracks:
            for i, clip in enumerate(track.each_clip()):
                ind += 1

                clip_name_l = clip.name.lower()
                if media_name_l in clip_name_l:
                    if last_c is None or get_timeline_clip_end_inclusive(clip) > get_timeline_clip_end_inclusive(
                        last_c
                    ):
                        last_c = clip
                        print(f"\n{tab}Clip: {ind}, {clip.name}")
                        break

        return last_c

    media_name_l = media_name.lower()

    if "ALL" == track_type or "VIDEO" == track_type:
        tracks = timeline.video_tracks()
        if last_occurence:
            found_clip = _get_media_last_occurence(tracks)
        else:
            found_clip = _get_media_first_occurence(tracks)

    if "ALL" == track_type or "AUDIO" == track_type:
        tracks = timeline.audio_tracks()
        found_audio_clip = None
        if last_occurence:
            found_audio_clip = _get_media_last_occurence(tracks)
        else:
            found_audio_clip = _get_media_first_occurence(tracks)

        if found_clip is None:
            found_clip = found_audio_clip
        elif found_audio_clip is None:
            pass
        else:
            first_clip_start = get_timeline_clip_start(found_clip)
            first_audio_clip_start = get_timeline_clip_start(found_audio_clip)
            if first_audio_clip_start < first_clip_start:
                found_clip = found_audio_clip

    # print result
    print("\n Track Type: ", track_type)

    if found_clip is None:
        print("   No clip found")
    else:
        start = get_timeline_clip_start(found_clip)
        end = get_timeline_clip_end_exclusive(found_clip)
        print(f"   Found clip: {found_clip.name}, start: {start}, end: {end}")

    return found_clip


def get_timeline_clip_start(clip):
    return opentimelineio.opentime.to_frames(clip.range_in_parent().start_time)


def get_timeline_clip_end_inclusive(clip):
    return opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive())


def get_timeline_clip_end_exclusive(clip):
    return opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_exclusive())


def get_media_list(timeline, track_type="ALL"):
    """ Return the list of the media found in the timeline
        track_type can be "ALL", "VIDEO" or "AUDIO"
    """

    media_list = list()

    # if "ALL" == track_type or "VIDEO" == track_type:

    def _get_media_list(tracks):
        m_list = list()

        for track in tracks:
            for clip in track:
                if isinstance(clip, opentimelineio.schema.Clip):
                    # print(clip.media_reference)
                    media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
                    # print(f"{media_path}")
                    if media_path not in m_list:
                        m_list.append(media_path)

                    # print(f"{tab2}clip.media_reference.target_url: {clip.media_reference.target_url}")
                    # media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
                    # print(f"{tab2}media_path: {media_path}")
        return m_list

    tracks = timeline.tracks
    if "VIDEO" == track_type:
        tracks = timeline.video_tracks()
    elif "AUDIO" == track_type:
        tracks = timeline.audio_tracks()

    media_list = _get_media_list(tracks)

    # for item in media_list:
    #     print(item)

    return media_list


def get_clips_in_range(timeline, track_type="ALL", mode="STRICTLY"):
    """ Return the clips in the specified range
        track_type can be "ALL", "VIDEO" or "AUDIO"
        mode: "STRICTLY", "OVERLAPPING"
        *** Warning: track owner is not kept at the moment ***
    """

    if "ALL" == track_type or "VIDEO" == track_type:
        pass
    elif "ALL" == track_type or "AUDIO" == track_type:
        pass

    return

