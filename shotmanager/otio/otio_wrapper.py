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
To do: module description here.
"""

import opentimelineio

from pathlib import Path
from urllib.parse import unquote_plus, urlparse
import re

import math

from ..utils import utils

import logging

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


def get_timeline_from_file(otioFile):
    return opentimelineio.adapters.read_from_file(otioFile)


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
            media_path = Path(get_clip_media_path(clip))
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
                    if first_c is None or get_clip_frame_final_start(clip) < get_clip_frame_final_start(first_c):
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
            first_clip_start = get_clip_frame_final_start(found_clip)
            first_audio_clip_start = get_clip_frame_final_start(found_audio_clip)
            if first_audio_clip_start < first_clip_start:
                found_clip = found_audio_clip

    # print result
    print("\n Track Type: ", track_type)

    if found_clip is None:
        print("   No clip found")
    else:
        start = get_clip_frame_final_start(found_clip)
        end = get_timeline_clip_end_exclusive(found_clip)
        print(f"   Found clip: {found_clip.name}, start: {start}, end: {end}")

    return found_clip


def get_clip_media_path(clip):
    """Return the media used by the clip, or None if the clip is not a media user (if it is a stack or nested edit for example)
    """
    # media_path = clip.media_reference.target_url
    # media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
    media_path = None
    if isinstance(clip, opentimelineio.schema.Clip):
        print(f"clip.media_reference: {clip.media_reference}")
        media_path = utils.file_path_from_url(clip.media_reference.target_url)
    return media_path


def get_clip_empty_duration(clip, fps):
    """For some strange reason some media (.wav) have a long empty time before their content. This has
    to be removed when used as sequence
    """
    return int(round(clip.available_range().start_time.value_rescaled_to(fps)))


def get_clip_frame_start(clip, fps):
    # relatif to media, usually 0:
    # frame = opentimelineio.opentime.to_frames(clip.available_range().start_time)

    clipEmptyDuration = get_clip_empty_duration(clip, fps)

    # absolute in track, clip frame final start:
    frame_final_start = opentimelineio.opentime.to_frames(clip.range_in_parent().start_time)

    # relative to start, clip frame offset start:
    frame_offset_start = int(round(clip.source_range.start_time.value))

    return frame_final_start - frame_offset_start + clipEmptyDuration


def get_clip_frame_end(clip, fps):
    """
        Exclusive
        Doesn't exist in blender
    """
    # absolute in track, clip frame final start:
    frame_start = get_clip_frame_start(clip, fps)

    duration = get_clip_frame_duration(clip, fps)

    # duration =

    return frame_start + duration


def get_clip_frame_final_start(clip, fps):
    return opentimelineio.opentime.to_frames(clip.range_in_parent().start_time)


def get_clip_frame_final_end(clip, fps):
    """
        Exclusive
    """
    # absolute in track, clip frame final start:
    frame_final_start = opentimelineio.opentime.to_frames(clip.range_in_parent().start_time)

    final_duration = int(math.ceil(opentimelineio.opentime.to_frames(clip.range_in_parent().duration)))

    return frame_final_start + final_duration


def get_clip_frame_offset_start(clip, fps):
    #  print("wkip get_clip_frame_offset_start: mettre un framerate au lieu de 25!!!")
    return int(math.ceil(clip.source_range.start_time.value)) - int(
        math.ceil(clip.available_range().start_time.value_rescaled_to(fps))
    )


def get_clip_frame_offset_end(clip, fps):
    frame_end = get_clip_frame_end(clip, fps)
    frame_final_end = get_clip_frame_final_end(clip, fps)
    return frame_end - frame_final_end


def get_clip_frame_duration(clip, fps):
    # get_clip_frame_end(clip) - get_clip_frame_start(clip)
    # print("get_clip_duration: clip.available_range():", clip.available_range())
    # computedDuration = clip.available_range().duration.value_rescaled_to(25)
    # print("get_clip_duration: computedDuration:", computedDuration)
    computedDuration = int(math.ceil((clip.available_range().duration.value_rescaled_to(fps))))
    # print("get_clip_duration: computedDuration:", computedDuration)

    # endExclusive = opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_exclusive())
    # print("get_clip_duration: endExclusive:", endExclusive)

    # endExclusive - get_clip_frame_start(clip)  # pb manque une frame!!
    # print("clip.duration_from_start_end_time():", clip.duration_from_start_end_time())
    return computedDuration


def get_clip_frame_final_duration(clip, fps):
    return int(math.ceil(opentimelineio.opentime.to_frames(clip.range_in_parent().duration)))


def get_timeline_clip_end_inclusive(clip):
    return opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive())


def get_timeline_clip_end_exclusive(clip):
    return opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_exclusive())


# ----------------------------------


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
                    media_path = get_clip_media_path(clip)
                    # print(f"{media_path}")
                    if media_path not in m_list:
                        m_list.append(media_path)
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
        mode: "STRICTLY": start and end of clip are inside the range or equal to its boundaries
        mode: "OVERLAPPING": start, end or frames inbetweens are in the range
        *** Warning: track owner is not kept at the moment ***
    """

    if "ALL" == track_type or "VIDEO" == track_type:
        pass
    elif "ALL" == track_type or "AUDIO" == track_type:
        pass

    return

