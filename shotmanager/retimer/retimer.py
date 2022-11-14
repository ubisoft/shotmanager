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
Retimer functions
"""

import bpy

from shotmanager.utils.utils_markers import sortMarkers

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

# FCurve
################################################


class FCurve:
    def __init__(self, fcurve):
        self.fcurve = fcurve

    def get_key(self, index):
        return self.fcurve.keyframe_points[index]

    def get_key_coordinates(self, index):
        return self.fcurve.keyframe_points[index].co

    def set_key_coordinates(self, index, coordinates):
        self.fcurve.keyframe_points[index].co = coordinates

    def get_key_index_at_frame(self, frame):
        """Return the index of the key at the specified frame, -1 if no key found"""
        for i in range(len(self.fcurve.keyframe_points)):
            if frame == self.fcurve.keyframe_points[i].co[0]:
                return i
        return -1

    def handles(self, index):
        return self.fcurve.keyframe_points[index].handle_left, self.fcurve.keyframe_points[index].handle_right

    # Seems to be passed by reference...
    # def set_handles ( self, index, value ):
    #    self.fcurve.keyframe_points[ index ].handle_left, self.fcurve.keyframe_points[ index ].handle_right = value

    def insert_frame(self, coordinates, roundToNearestFrame=True):
        frame_val = round(coordinates[0]) if roundToNearestFrame else coordinates[0]
        self.fcurve.keyframe_points.insert(frame_val, coordinates[1])

    def remove_frames(self, start_incl, end_incl, remove_gap=False, roundToNearestFrame=True):
        to_remove = list()

        for k in self.fcurve.keyframe_points:
            #    print(f" FCurve.remove_frames  start_incl:{start_incl}, k.co[0]: {k.co[0]}, end_incl: {end_incl}")
            if start_incl <= k.co[0] <= end_incl:
                to_remove.append(k)

        # wkip to delete
        # if remove_gap and False:
        #     # the handle values of the start and end must be stored before deletion otherwise they are modified
        #     start_incl_key_index = self.get_key_index_at_frame(start_incl - 1)
        #     print(f" rr start_incl_key_index {start_incl_key_index}")
        #     start_incl_key_right_handle_right = None
        #     if -1 != start_incl_key_index:
        #         start_incl_key_right_handle_right = self.fcurve.keyframe_points[start_incl_key_index].handle_right
        #         print(
        #             f" rr02 start_incl_key_right_handle_right {start_incl_key_right_handle_right}, type: {self.fcurve.keyframe_points[start_incl_key_index].handle_right_type}"
        #         )
        # end_incl_key = self.get_key_index_at_frame(start_incl)

        for k in reversed(to_remove):
            self.fcurve.keyframe_points.remove(k)

        # wkip to delete
        # if remove_gap and False:
        #     print("Fixing 00")
        #     # restore handles
        #     if -1 != start_incl_key_index and start_incl_key_right_handle_right is not None:
        #         print("Fixing")
        #         self.fcurve.keyframe_points[start_incl_key_index].handle_right[0] = start_incl_key_right_handle_right[0]
        #         print(f" rr03 start_incl_key_right_handle_right {start_incl_key_right_handle_right}")
        #         start_incl_key_right_handle_right02 = self.fcurve.keyframe_points[start_incl_key_index].handle_right
        #         print(f" rr04 start_incl_key_right_handle_right02 {start_incl_key_right_handle_right02}")

        if remove_gap:
            _offset_fCurve_frames(self, end_incl, start_incl - end_incl - 1, roundToNearestFrame)

    def __len__(self):
        return len(self.fcurve.keyframe_points)


# def _offset_fCurve_frames(fcurve: FCurve, start_incl, offset):
#     for i in range(len(fcurve)):
#         key_time, value = fcurve.get_key_coordinates(i)
#         if start_incl <= key_time:
#             fcurve.set_key_coordinates(i, (key_time + offset, value))
#             left_handle, right_handle = fcurve.handles(i)
#             left_handle[0] += offset
#             right_handle[0] += offset

# GPFCurve
################################################

# not used!!!
# class GPFCurve(FCurve):
#     def get_key_coordinates(self, index):
#         return self.fcurve.frames[index].frame_number, 0

#     def set_key_coordinates(self, index, coordinates):
#         self.fcurve.frames[index].frame_number = coordinates[0]

#     def handles(self, index):
#         return [0, 0], [0, 0]

#     def set_handles(self, index, value):
#         pass

#     def insert_frame(self, coordinates):
#         pass

#     def remove_frames(self, start, end):
#         to_remove = list()

#         for k in self.fcurve.frames:
#             if start <= k.frame_number <= end:
#                 to_remove.append(k)

#         for k in reversed(to_remove):
#             self.fcurve.frames.remove(k)

#     def __len__(self):
#         return len(self.fcurve.frames)


# Functions
################################################


def computeNewFrameValue(frame_value, mode, start_incl=0, end_incl=0, pivot=0, factor=1.0, roundToNearestFrame=True):
    """Return the value of the time (in frames) after the retiming
    Return None if the new time value is not available (deleted time for example)
    It supports floating time frames.
    Args:
        roundToNearestFrame:  round the frame time value
    """

    new_frame_value = frame_value
    # offset is also the duration_incl
    offset = end_incl - start_incl + 1

    if mode == "INSERT":
        if start_incl <= frame_value:
            return frame_value + offset

    elif mode == "DELETE" or mode == "CLEAR_ANIM":
        if start_incl <= frame_value:
            if frame_value <= end_incl:
                # or return new_frame_value = start_incl, as in _compute_retimed_frame???
                new_frame_value = None
            else:
                #   offset = end_incl - start_incl + 1
                new_frame_value = frame_value - offset

    elif mode == "RESCALE":
        new_frame_value = rescale_frame(frame_value, start_incl, end_incl, pivot, factor, roundToNearestFrame=False)

        # if start_incl <= frame_value:
        #     if frame_value <= end_incl:
        #         return None
        #     else:
        #         offset = (end_incl - start_incl - 1) * factor - end_incl + start_incl - 1
        #         # _logger.debug_ext(f" In computeNewFrameValue() Rescale mode: offset: {offset}")
        #         return frame_value + offset

    elif mode == "FREEZE":
        pass
    elif mode == "CLEAR_ANIM":
        pass

    if roundToNearestFrame:
        new_frame_value = round(new_frame_value)
    return new_frame_value


def compute_offset(frame_value, pivot, factor, roundToNearestFrame=True):
    """Compute the offset value to add to frame_value to scale it from the pivot and by the given factor.
    If frame_value > pivot then the computed offset is negative.
    Return the offset"""
    duration_to_pivot = pivot - frame_value
    new_duration_to_pivot = duration_to_pivot * factor
    offset = duration_to_pivot - new_duration_to_pivot
    offset = round(offset) if roundToNearestFrame else offset
    return offset


def apply_offset(frame_value, pivot, factor, roundToNearestFrame=True):
    """Compute the new value of frame_value when scaled from the pivot and by the given factor"""
    duration_to_pivot = frame_value - pivot
    offset = duration_to_pivot * factor
    new_frame_value = frame_value + offset
    new_frame_value = round(new_frame_value) if roundToNearestFrame else new_frame_value
    return new_frame_value


def rescale_frame(frame_value, start_incl, end_incl, pivot, factor, roundToNearestFrame=True):
    """Compute the new value of frame_value when scaled from the pivot and by the given factor
    in the specified range
    Note: this works only for frames, not floating points
    """
    new_frame_value = frame_value
    duration_to_pivot = frame_value - pivot
    # round(duration_to_pivot * factor) + pivot

    if start_incl <= frame_value:
        if end_incl < frame_value:
            duration_to_pivot = end_incl + 1 - pivot
            new_frame_value = round(duration_to_pivot * factor) + pivot + frame_value - end_incl - 1
        else:
            duration_to_pivot = frame_value - pivot
            new_frame_value = round(duration_to_pivot * factor) + pivot

    return new_frame_value


# TODO wkip generic function to finish
# Adding an option to offset - or to keep fix - the values out of the range
# Adding an optional range min and range max

# def rescale_value(value: float, start_range: float, end_range: float, origin: float, factor: float, round_result=False):
#     """Compute the new value of frame_value when scaled from the origin and by the given factor
#     in the specified range
#     *** works with any floating value, not just frame. Required for key handle values
#     """
#     new_value = value
#     distance_to_origin = value - origin
#     round(duration_to_pivot * factor) + origin

#     if start_range < value:
#         if end_range < value:
#             distance_to_origin = end_range + 1 - origin
#             new_value = round(distance_to_origin * factor) + origin + value - end_range - 1
#         else:
#             distance_to_origin = value - origin
#             new_value = round(distance_to_origin * factor) + origin

#     new_value = if round_result else
#     return new_value

##########################################################################
# fcurve
##########################################################################


def _offset_fCurve_key(key, offset):
    key_time, value = key.co
    new_key_time = key_time + offset
    key.handle_left[0] += offset
    key.handle_right[0] += offset
    key.co = (new_key_time, value)


def _set_time_fCurve_key(key, new_key_time):
    key_time, value = key.co
    offset = new_key_time - key_time
    key.handle_left[0] += offset
    key.handle_right[0] += offset
    key.co = (new_key_time, value)


def _offset_fCurve_frames(fcurve: FCurve, start_incl, offset, roundToNearestFrame):
    for i in range(len(fcurve)):
        key = fcurve.get_key(i)
        key_time = key.co[0]
        # key_time, value = fcurve.get_key_coordinates(i)
        if start_incl <= key_time:
            # key_time = key_time + offset
            # if roundToNearestFrame:
            #     key_time = round(key_time)
            # fcurve.set_key_coordinates(i, (key_time, value))
            # left_handle, right_handle = fcurve.handles(i)
            # left_handle[0] += offset
            # right_handle[0] += offset

            new_key_time = key_time + offset
            if roundToNearestFrame:
                new_key_time = round(new_key_time)

            _set_time_fCurve_key(key, new_key_time)
            # offset_with_rounded_added_offset = new_key_time - key_time
            # left_handle, right_handle = fcurve.handles(i)
            # left_handle[0] += offset_with_rounded_added_offset
            # right_handle[0] += offset_with_rounded_added_offset
            # fcurve.set_key_coordinates(i, (new_key_time, value))


def _rescale_fCurve_frames(
    *,
    fcurve: FCurve,
    start_incl,
    end_incl,
    factor,
    pivot,
    clamp=False,
    roundToNearestFrame=True,
    keysBeforeRangeMode="DO_NOTHING",
    keysAfterRangeMode="DO_NOTHING",
):
    """
    Args:
        keysBeforeRangeMode: Action to do on keys located before the specified time range. Can be "DO_NOTHING", "OFFSET", "RESCALE"
        keysAfterRangeMode: Action to do on keys located after the specified time range. Can be "DO_NOTHING", "OFFSET", "RESCALE"
    """
    # First pass.
    if clamp:
        remove_pre_start = list()
        remove_post_end = list()
        for i in range(len(fcurve)):
            coordinates = fcurve.get_key_coordinates(i)
            dist_from_pivot = coordinates[0] - pivot
            if start_incl >= round(pivot + dist_from_pivot * factor):
                remove_pre_start.append(coordinates[0])
            elif round(pivot + dist_from_pivot * factor) >= end_incl:
                remove_post_end.append(coordinates[0])

        if remove_pre_start:
            fcurve.remove_frames(min(remove_pre_start), max(remove_pre_start), False)

        if remove_post_end:
            fcurve.remove_frames(min(remove_post_end), max(remove_post_end), False)

    # else:
    #     if factor > 1:
    #         _offset_fCurve_frames(
    #             fcurve,
    #             end_incl + 1,
    #             compute_offset(end_incl + 1, pivot, factor, roundToNearestFrame=False)
    #             - (end_incl - start_incl + 1),
    #             roundToNearestFrame,
    #         )
    #         # print(f" rescale offset 01: {compute_offset(end_incl + 1, pivot, factor)}")

    # TODO: wkip delete existing or ducplicated keys when factor < 1.0

    # bpy.ops.action.clean(threshold=0.001, channels=False)
    for i in range(len(fcurve)):
        key = fcurve.get_key(i)
        key_time, key_value = key.co
        # key_time, key_value = fcurve.get_key_coordinates(i)
        changeMode = "RESCALE"
        if key_time < start_incl:
            changeMode = keysBeforeRangeMode
        elif end_incl < key_time:
            changeMode = keysAfterRangeMode

        if "RESCALE" == changeMode:
            offset = compute_offset(key_time, pivot, factor, roundToNearestFrame=False)  # - start_incl + 1
            new_key_time = key_time + offset
            if roundToNearestFrame:
                new_key_time = round(new_key_time)
            fcurve.set_key_coordinates(i, (new_key_time, key_value))

            # handle coordinates are absolute, not changing when the key position changes
            # we want to apply the scaling on the x axis of the handles that corresponds to the
            # final move of the key (so including the rounding, if applicated)
            # To do so we then compute back the corresponding scale factor

            # offset_with_rounded_added_offset = new_key_time - key_time

            left_handle, right_handle = fcurve.handles(i)
            if key_time != pivot:
                factor_for_rounded_offset = (new_key_time - pivot) / (key_time - pivot)

                left_handle[0] += compute_offset(
                    left_handle[0], pivot, factor_for_rounded_offset, roundToNearestFrame=False
                )
                right_handle[0] += compute_offset(
                    right_handle[0], pivot, factor_for_rounded_offset, roundToNearestFrame=False
                )

            # since the handle is on the pivot it is not affected by the scaling... but at least
            # one of its handles is (if the pivot is one of the boundaries of the range), if not
            # both, if the pivot is inbetween
            else:
                if start_incl < left_handle[0]:
                    left_handle[0] += compute_offset(left_handle[0], pivot, factor, roundToNearestFrame=False)
                if right_handle[0] < end_incl:
                    right_handle[0] += compute_offset(right_handle[0], pivot, factor, roundToNearestFrame=False)

        elif "OFFSET" == changeMode:
            if key_time < start_incl:
                offset = compute_offset(start_incl, pivot, factor, roundToNearestFrame=False)
            elif end_incl < key_time:
                offset = compute_offset(end_incl, pivot, factor, roundToNearestFrame=False)

            new_key_time = key_time + offset
            if roundToNearestFrame:
                new_key_time = round(new_key_time)

            _set_time_fCurve_key(key, new_key_time)
            # fcurve.set_key_coordinates(i, (new_key_time, key_value))

            # offset_with_rounded_added_offset = new_key_time - key_time
            # left_handle, right_handle = fcurve.handles(i)
            # left_handle[0] += offset_with_rounded_added_offset
            # right_handle[0] += offset_with_rounded_added_offset

    # if factor < 1.0:
    #     _offset_fCurve_frames(
    #         fcurve,
    #         end_incl + 1,
    #         compute_offset(end_incl + 1, pivot, factor) - (end_incl - start_incl + 1),
    #         roundToNearestFrame,
    #     )


def _snap_fCurve_frames(
    *,
    fcurve: FCurve,
    start_incl,
    end_incl,
    keysBeforeRangeMode="DO_NOTHING",
    keysAfterRangeMode="DO_NOTHING",
):
    """
    Args:
        keysBeforeRangeMode: Action to do on keys located before the specified time range. Can be DO_NOTHING, SNAP
        keysAfterRangeMode: Action to do on keys located after the specified time range. Can be DO_NOTHING, SNAP
    """
    # TODO: wkip delete ducplicated keys !!!

    # bpy.ops.action.clean(threshold=0.001, channels=False)
    for i in range(len(fcurve)):
        key = fcurve.get_key(i)
        key_time, key_value = key.co
        # key_time, key_value = fcurve.get_key_coordinates(i)
        changeMode = "SNAP"
        if key_time < start_incl:
            changeMode = keysBeforeRangeMode
        elif end_incl < key_time:
            changeMode = keysAfterRangeMode

        if "SNAP" == changeMode:
            # fcurve.set_key_coordinates(i, (round(key_time), key_value))
            _set_time_fCurve_key(key, round(key_time))


def retime_fCurve_frames(
    fcurve: FCurve,
    mode,
    start_incl=0,
    end_incl=0,
    remove_gap=True,
    factor=1.0,
    pivot=0,
    roundToNearestFrame=True,
    keysBeforeRangeMode="DO_NOTHING",
    keysAfterRangeMode="DO_NOTHING",
):
    """
    Args:
        retimeMode: Can be GLOBAL_OFFSET, INSERT_BEFORE, INSERT_AFTER, DELETE_RANGE, RESCALE, CLEAR_ANIM, SNAP, FREEZE
        start_incl (int): The included start frame
        duration_incl (int): The range of retime frames (new or deleted)
        keysBeforeRangeMode: Action to do on keys located before the specified time range. Can be DO_NOTHING, OFFSET, RESCALE, SNAP
        keysAfterRangeMode: Action to do on keys located after the specified time range. Can be DO_NOTHING, OFFSET, RESCALE, SNAP
    """

    if mode == "INSERT":
        _offset_fCurve_frames(fcurve, start_incl, end_incl - start_incl + 1, roundToNearestFrame)

    elif mode == "DELETE" or mode == "CLEAR_ANIM":
        fcurve.remove_frames(start_incl, end_incl, remove_gap)

    elif mode == "RESCALE":
        _rescale_fCurve_frames(
            fcurve=fcurve,
            start_incl=start_incl,
            end_incl=end_incl,
            factor=factor,
            pivot=pivot,
            clamp=False,
            roundToNearestFrame=roundToNearestFrame,
            keysBeforeRangeMode=keysBeforeRangeMode,
            keysAfterRangeMode=keysAfterRangeMode,
        )

    elif mode == "SNAP":
        _snap_fCurve_frames(
            fcurve=fcurve,
            start_incl=start_incl,
            end_incl=end_incl,
            keysBeforeRangeMode=keysBeforeRangeMode,
            keysAfterRangeMode=keysAfterRangeMode,
        )

    elif mode == "FREEZE":
        for i in range(len(fcurve)):
            key_time, value = fcurve.get_key_coordinates(i)
            new_keys = list()
            if key_time == start_incl:
                new_keys.append((key_time, value))
                new_keys.append((key_time + end_incl - start_incl, value))

            if key_time >= start_incl:
                fcurve.set_key_coordinates(i, (key_time + end_incl - start_incl, value))

                left_handle, right_handle = fcurve.get_handles(i)
                left_handle[0] += end_incl - start_incl
                right_handle[0] += end_incl - start_incl
                fcurve.set_handles(i, (left_handle, right_handle))

            for v in new_keys:
                fcurve.insert_frame(v, roundToNearestFrame)


##########################################################################
# grease pencil
##########################################################################
def _offset_GPframes(layer, start_incl, offset):
    """Move the layer frames that are AT THE SAME TIME or later than the reference frame"""
    # print(f"layer:{layer.info}")
    for f in layer.frames:
        if start_incl <= f.frame_number:
            f.frame_number += offset


def _rescale_GPframes(
    *,
    layer,
    start_incl,
    end_incl,
    factor,
    pivot,
    roundToNearestFrame=True,
    keysBeforeRangeMode="DO_NOTHING",
    keysAfterRangeMode="DO_NOTHING",
):

    for f in layer.frames:
        # NOTE: whereas key_time in fcurve is a float, here frameNumber is an int !!!
        frame_number_float = f.frame_number
        changeMode = "RESCALE"
        if frame_number_float < start_incl:
            changeMode = keysBeforeRangeMode
        elif end_incl < frame_number_float:
            changeMode = keysAfterRangeMode

        if "RESCALE" == changeMode:
            offset = compute_offset(frame_number_float, pivot, factor, roundToNearestFrame=False)  # - start_incl + 1
            new_frame_number_float = frame_number_float + offset

            # rounding has to be done anyway since GP frames are integer
            # if roundToNearestFrame:
            new_frame_number_float = round(new_frame_number_float)
            f.frame_number = new_frame_number_float

        elif "OFFSET" == changeMode:
            if frame_number_float < start_incl:
                offset = compute_offset(start_incl, pivot, factor, roundToNearestFrame=False)
            elif end_incl < frame_number_float:
                offset = compute_offset(end_incl, pivot, factor, roundToNearestFrame=False)

            new_frame_number_float = frame_number_float + offset

            # rounding has to be done anyway since GP frames are integer
            # if roundToNearestFrame:
            new_frame_number_float = round(new_frame_number_float)
            f.frame_number = new_frame_number_float


def retime_GPframes(
    layer,
    mode,
    start_incl=0,
    end_incl=0,
    remove_gap=True,
    factor=1.0,
    pivot=0,
    roundToNearestFrame=True,
    keysBeforeRangeMode="DO_NOTHING",
    keysAfterRangeMode="DO_NOTHING",
):
    """Retime "frames" (= each drawing of a Grease Pencil object)"""
    offset = end_incl - start_incl + 1

    if mode == "INSERT":
        _offset_GPframes(layer, start_incl, offset)

    elif mode == "DELETE" or mode == "CLEAR_ANIM":
        # delete frames
        if 0 < len(layer.frames):
            f_ind = 0
            while f_ind < len(layer.frames):
                if start_incl <= layer.frames[f_ind].frame_number <= end_incl:
                    # we suppose frames are sorted according to increasing time
                    layer.frames.remove(layer.frames[f_ind])
                # print(f" *** deleting frame {f_ind}, end_incl= {end_incl}")
                else:
                    f_ind += 1

        # remove empty gap
        if mode == "DELETE":
            _offset_GPframes(layer, end_incl, -offset)
            pass
            # if 0 < len(layer.frames):
            #     for f in layer.frames:
            #         if end_incl < f.frame_number:
            #             f.frame_number -= end_incl - start_incl

    elif mode == "RESCALE":
        _rescale_GPframes(
            layer=layer,
            start_incl=start_incl,
            end_incl=end_incl,
            factor=factor,
            pivot=pivot,
            roundToNearestFrame=roundToNearestFrame,
            keysBeforeRangeMode=keysBeforeRangeMode,
            keysAfterRangeMode=keysAfterRangeMode,
        )

        # # push out of range frames later in time
        # if factor > 1.0:
        #     # wkip sur du +1 on end frame????
        #     _offset_GPframes(
        #         layer, end_incl + 1, compute_offset(end_incl + 1, pivot, factor) - (end_incl - start_incl + 1)
        #     )

        # # scale range
        # for f in layer.frames:
        #     if start_incl <= f.frame_number <= end_incl:
        #         offset = compute_offset(f.frame_number, pivot, factor)
        #         f.frame_number = offset + pivot

        # # pull out of range frames sooner in time
        # if factor < 1.0:
        #     _offset_GPframes(
        #         layer, end_incl + 1, compute_offset(end_incl + 1, pivot, factor) - (end_incl - start_incl + 1)
        #     )

    return ()


##########################################################################
# shot range
##########################################################################
# wkip warining here start_frame is EXCLUSIF - To change!!
# end frame is inclusive
def retime_shot(shot, mode, start_incl=0, end_incl=0, remove_gap=True, factor=1.0, pivot=0):

    start_frame = start_incl - 1
    end_frame = end_incl  # + 1
    if mode == "INSERT":
        offset = end_frame - start_frame

        if shot.durationLocked:
            if start_frame < shot.start:
                shot.start += offset
            elif start_frame < shot.end:
                shot.durationLocked = False
                shot.end += offset
                shot.durationLocked = True
        else:
            # important to offset end first!!
            if start_frame < shot.end:
                shot.end += offset
            if start_frame < shot.start:
                shot.start += offset

    elif mode == "FREEZE":
        pass

    elif mode == "DELETE":

        # # the removal lets a 1 frame space, not an overlap of start by end!!
        # # if start and end are in the range then we create a 1 frame shot
        # if start_incl - 1 <= shot.start and shot.end <= end_frame:
        #     shot.start = start_incl - 1
        #     shot.end = end_frame

        # # shot is before, nothing happens
        # elif shot.start < start_incl - 1 and shot.end < start_incl - 1:
        #     pass

        # # shot is after, we offset
        # elif end_frame <= shot.start and shot.end <= end_frame:
        #     offset = end_frame - start_incl - 1
        #     shot.start -= offset
        #     shot.end -= offset

        # else:

        # offset = end_frame - start_incl - 1
        offset = end_incl - start_incl + 1
        #  print(f" In retime_shot() Delete mode: offset: {offset}")

        if shot.durationLocked:
            if shot.start <= start_incl - 1:
                if shot.end <= start_incl - 1:
                    pass
                elif shot.end <= end_frame:
                    shot.durationLocked = False
                    shot.end = start_incl - 1  # goes to a non deleted part
                    shot.durationLocked = True
                else:
                    shot.durationLocked = False
                    shot.end -= offset
                    shot.durationLocked = True

            elif start_incl - 1 < shot.start and shot.start < end_frame:
                if shot.end <= end_frame:
                    shot.durationLocked = False
                    shot.start = start_incl - 1
                    shot.end = start_incl - 1
                    shot.durationLocked = True
                    shot.enabled = False
                else:
                    shot.durationLocked = False
                    shot.start = start_incl - 1
                    shot.end -= offset
                    shot.durationLocked = True

            else:
                shot.start -= offset

        else:
            if shot.start <= start_incl - 1:
                if shot.end <= start_incl - 1:
                    pass
                elif shot.end <= end_frame:
                    shot.end = start_incl - 1  # goes to a non deleted part
                else:
                    shot.end -= offset

            elif start_incl - 1 < shot.start and shot.start < end_frame:
                shot.start = start_incl - 1

                if shot.end <= end_frame:
                    shot.end = start_incl - 1
                    shot.enabled = False
                else:
                    shot.end -= offset

            else:
                shot.start -= offset
                shot.end -= offset

    elif mode == "RESCALE":
        offset = (end_frame - start_frame) * factor - end_frame + start_frame
        _logger.debug_ext(f" In retime_shot() Rescale mode: offset: {offset}")

        if shot.durationLocked:
            if offset > 0:
                # important to offset END first!!
                # shot.end = rescale_frame(shot.end + 1, start_incl, end_incl, pivot, factor) - 1
                # shot.start = rescale_frame(shot.start, start_incl, end_incl, pivot, factor)
                if end_frame < shot.end:
                    if end_frame < shot.start:
                        # shot.start += offset
                        shot.start = rescale_frame(shot.start, start_incl, end_incl, pivot, factor)
                    elif start_frame < shot.start and shot.start <= end_frame:
                        shot.durationLocked = False
                        # shot.end += offset
                        shot.end = rescale_frame(shot.end + 1, start_incl, end_incl, pivot, factor) - 1
                        # shot.start = (shot.start - pivot) * factor + pivot
                        shot.start = rescale_frame(shot.start, start_incl, end_incl, pivot, factor)
                        shot.durationLocked = True
                    else:
                        shot.durationLocked = False
                        # shot.end += offset
                        shot.end = rescale_frame(shot.end + 1, start_incl, end_incl, pivot, factor) - 1
                        shot.durationLocked = True

                elif start_frame < shot.end and shot.end <= end_frame:
                    if start_frame < shot.start and shot.start <= end_frame:
                        shot.durationLocked = False
                        # shot.end = (shot.end - pivot) * factor + pivot
                        shot.end = rescale_frame(shot.end + 1, start_incl, end_incl, pivot, factor) - 1
                        # shot.start = (shot.start - pivot) * factor + pivot
                        shot.start = rescale_frame(shot.start, start_incl, end_incl, pivot, factor)
                        shot.durationLocked = True
                    else:
                        shot.durationLocked = False
                        # shot.end = (shot.end - pivot) * factor + pivot
                        shot.end = rescale_frame(shot.end + 1, start_incl, end_incl, pivot, factor) - 1
                        shot.durationLocked = True

            else:
                # important to offset START first!!
                if end_frame < shot.start:
                    # shot.start += offset
                    shot.start = rescale_frame(shot.start, start_incl, end_incl, pivot, factor)
                elif start_frame < shot.start and shot.start <= end_frame:
                    if end_frame < shot.end:
                        shot.durationLocked = False
                        # shot.start = (
                        #     (shot.start - pivot) * factor + pivot + 0.005
                        # )  # approximation to make sure the rounded value is done to the upper value
                        shot.start = rescale_frame(shot.start, start_incl, end_incl, pivot, factor)
                        # shot.end += offset
                        shot.end = rescale_frame(shot.end + 1, start_incl, end_incl, pivot, factor) - 1
                        shot.durationLocked = True
                    else:
                        shot.durationLocked = False
                        # shot.start = (
                        #     (shot.start - pivot) * factor + pivot + 0.005
                        # )  # approximation to make sure the rounded value is done to the upper value
                        shot.start = rescale_frame(shot.start, start_incl, end_incl, pivot, factor)
                        # shot.end = (
                        #     (shot.end - pivot) * factor + pivot + 0.005
                        # )  # approximation to make sure the rounded value is done to the upper value
                        shot.end = rescale_frame(shot.end + 1, start_incl, end_incl, pivot, factor) - 1
                        shot.durationLocked = True

                else:
                    if end_frame < shot.end:
                        shot.durationLocked = False
                        # shot.end += offset
                        shot.end = rescale_frame(shot.end + 1, start_incl, end_incl, pivot, factor) - 1
                        shot.durationLocked = True
                    elif start_frame < shot.end and shot.end <= end_frame:
                        shot.durationLocked = False
                        # shot.end = (
                        #     (shot.end - pivot) * factor + pivot + 0.005
                        # )  # approximation to make sure the rounded value is done to the upper value
                        shot.end = rescale_frame(shot.end + 1, start_incl, end_incl, pivot, factor) - 1
                        shot.durationLocked = True

        else:
            if offset > 0:
                # important to offset END first!!
                print(
                    f" In retime_shot() Rescale mode: offset > 0: {offset}, shot: {shot.name}, s:{shot.start}, e:{shot.end}"
                )
                shot.end = rescale_frame(shot.end + 1, start_incl, end_incl, pivot, factor) - 1
                shot.start = rescale_frame(shot.start, start_incl, end_incl, pivot, factor)
                print(
                    f" In retime_shot() Rescale mode: offset > 0: {offset}, shot: {shot.name}, ns:{shot.start}, ne:{shot.end}\n"
                )

            else:
                shot.start = rescale_frame(shot.start, start_incl, end_incl, pivot, factor)
                shot.end = rescale_frame(shot.end + 1, start_incl, end_incl, pivot, factor) - 1
                # # important to offset START first!!
                # if end_frame < shot.start:
                #     shot.start += offset
                # elif start_frame < shot.start and shot.start <= end_frame:
                #     shot.start = (
                #         (shot.start - pivot) * factor + pivot + 0.005
                #     )  # approximation to make sure the rounded value is done to the upper value

                # if end_frame < shot.end:
                #     shot.end += offset
                # elif start_frame < shot.end and shot.end <= end_frame:
                #     shot.end = (
                #         (shot.end - pivot) * factor + pivot + 0.005
                #     )  # approximation to make sure the rounded value is done to the upper value

    elif mode == "RESCALE_OLD":
        # offset = (end_frame - start_frame) * (factor - 1)
        offset = (end_frame - start_frame) * factor - end_frame + start_frame

        print(f" In retime_shot() Rescale mode: offset: {offset}")

        if shot.durationLocked:
            if offset > 0:
                # important to offset END first!!
                if end_frame < shot.end:
                    if end_frame < shot.start:
                        shot.start += offset
                    elif start_frame < shot.start and shot.start <= end_frame:
                        shot.durationLocked = False
                        shot.end += offset
                        shot.start = (shot.start - pivot) * factor + pivot
                        shot.durationLocked = True
                    else:
                        shot.durationLocked = False
                        shot.end += offset
                        shot.durationLocked = True

                elif start_frame < shot.end and shot.end <= end_frame:
                    if start_frame < shot.start and shot.start <= end_frame:
                        shot.durationLocked = False
                        shot.end = (shot.end - pivot) * factor + pivot
                        shot.start = (shot.start - pivot) * factor + pivot
                        shot.durationLocked = True
                    else:
                        shot.durationLocked = False
                        shot.end = (shot.end - pivot) * factor + pivot
                        shot.durationLocked = True

                else:
                    pass

            else:
                # important to offset START first!!
                if end_frame < shot.start:
                    shot.start += offset
                elif start_frame < shot.start and shot.start <= end_frame:
                    if end_frame < shot.end:
                        shot.durationLocked = False
                        shot.start = (
                            (shot.start - pivot) * factor + pivot + 0.005
                        )  # approximation to make sure the rounded value is done to the upper value
                        shot.end += offset
                        shot.durationLocked = True
                    else:
                        shot.durationLocked = False
                        shot.start = (
                            (shot.start - pivot) * factor + pivot + 0.005
                        )  # approximation to make sure the rounded value is done to the upper value
                        shot.end = (
                            (shot.end - pivot) * factor + pivot + 0.005
                        )  # approximation to make sure the rounded value is done to the upper value
                        shot.durationLocked = True

                else:
                    if end_frame < shot.end:
                        shot.durationLocked = False
                        shot.end += offset
                        shot.durationLocked = True
                    elif start_frame < shot.end and shot.end <= end_frame:
                        shot.durationLocked = False
                        shot.end = (
                            (shot.end - pivot) * factor + pivot + 0.005
                        )  # approximation to make sure the rounded value is done to the upper value
                        shot.durationLocked = True
                    else:
                        pass

        else:
            if offset > 0:
                # important to offset END first!!
                if end_frame < shot.end:
                    shot.end += offset
                elif start_frame < shot.end and shot.end <= end_frame:
                    shot.end = (shot.end + 1 - pivot) * factor + pivot - 1
                else:
                    pass

                if end_frame < shot.start:
                    shot.start += offset
                elif start_frame < shot.start and shot.start <= end_frame:
                    shot.start = (shot.start - pivot) * factor + pivot
                else:
                    pass

            else:
                # important to offset START first!!
                if end_frame < shot.start:
                    shot.start += offset
                elif start_frame < shot.start and shot.start <= end_frame:
                    shot.start = (
                        (shot.start - pivot) * factor + pivot + 0.005
                    )  # approximation to make sure the rounded value is done to the upper value
                else:
                    pass

                if end_frame < shot.end:
                    shot.end += offset
                elif start_frame < shot.end and shot.end <= end_frame:
                    shot.end = (
                        (shot.end - pivot) * factor + pivot + 0.005
                    )  # approximation to make sure the rounded value is done to the upper value
                else:
                    pass

    elif mode == "CLEAR_ANIM":
        pass


def retime_markers(
    scene, mode, start_incl=0, end_incl=0, remove_gap=True, factor=1.0, pivot=0, roundToNearestFrame=True
):
    # NOTE: there can be several markers per frame!!!

    if mode == "RESCALE":
        offset = (end_incl - start_incl - 1) * factor - end_incl + start_incl - 1
        _logger.debug_ext(f" In retime_markers() Rescale mode: offset: {offset}")

    markers = sortMarkers(scene.timeline_markers)
    if len(markers):
        for m in markers:
            newFrameVal = computeNewFrameValue(
                m.frame, mode, start_incl, end_incl, pivot, factor, roundToNearestFrame=True
            )
            if newFrameVal is None:
                # delete marker
                scene.timeline_markers.remove(m)
            else:
                m.frame = newFrameVal


def retime_vse(scene, mode, start_frame, end_frame, remove_gap=True):
    def insert_time(sed, start_frame, end_frame):
        # This will be a two pass process since we will use operators to cut the clips.
        offset = end_frame - start_frame
        sequences = list()
        for sequence in sed.sequences:
            sequence.select = False
            sequences.append(sequence)

        sequences.sort(key=lambda s: s.frame_start, reverse=True)

        # First pass is about move start frame of the clip if they are behind the start_frame and cutting the clips which contains start_frame.
        for seq in sequences:
            if seq.frame_final_start < start_frame < seq.frame_final_end:
                seq.select = True
                bpy.ops.sequencer.split(frame=start_frame)
                seq.select = False
            elif seq.frame_final_start >= start_frame:
                seq.frame_start += offset

        # Second pass is about offseting clips which just have been cut. They are identified by  seq.frame_start + seq.frame_offset_start == start_frame
        for seq in list(sed.sequences):
            if seq.frame_final_start == start_frame:
                seq.frame_start += offset

    def remove_time(sed, start_frame, end_frame, remove_gap):
        for s in sed.sequences:
            s.select = False

        for s in list(sed.sequences):
            if s.frame_final_start < start_frame < s.frame_final_end:
                s.select = True
            if s.frame_final_start < end_frame < s.frame_final_end:
                s.select = True

        bpy.ops.sequencer.split(frame=start_frame)
        bpy.ops.sequencer.split(frame=end_frame)
        for s in sed.sequences:
            s.select = False

        for s in list(sed.sequences):
            if start_frame <= s.frame_final_start <= end_frame and start_frame <= s.frame_final_end <= end_frame:
                sed.sequences.remove(s)

        if remove_gap:
            insert_time(sed, end_frame, start_frame)

    sed = scene.sequence_editor
    if sed is None:
        return

    if mode == "INSERT":
        insert_time(sed, start_frame, end_frame)

    elif mode == "DELETE":
        remove_time(sed, start_frame, end_frame, remove_gap)


def retimeScene(
    *,
    context,
    retimeMode: str,
    retimerApplyToSettings,
    objects,
    start_incl: float,
    duration_incl: float,
    join_gap=True,
    factor=1.0,
    pivot=0,
    keysBeforeRangeMode="DO_NOTHING",
    keysAfterRangeMode="DO_NOTHING",
):
    """Apply the time change for each type of entities
    Args:
        retimeMode: Can be GLOBAL_OFFSET, INSERT_BEFORE, INSERT_AFTER, DELETE_RANGE, RESCALE, CLEAR_ANIM, SNAP,
        start_incl (int): The included start frame
        duration_incl (int): The range of retime frames (new or deleted)
        keysBeforeRangeMode: Action to do on keys located before the specified time range. Can be DO_NOTHING, OFFSET, RESCALE, SNAP
        keysAfterRangeMode: Action to do on keys located after the specified time range. Can be NOTHING, OFFSET, RESCALE, SNAP
    """
    # prefs = config.getAddonPrefs()
    scene = context.scene

    current_frame = scene.frame_current

    mode = retimeMode
    if "GLOBAL_OFFSET" == retimeMode:
        if 0 < duration_incl:
            mode = "INSERT"
        else:
            mode = "DELETE"
            duration_incl = -1 * duration_incl

    end_incl = start_incl + duration_incl - 1

    # duration_incl: {duration_incl}
    print(f" - retimeScene(): {retimeMode}, str_inc:{start_incl}, ed_inc:{end_incl}, pivot:{pivot}, factor:{factor}")

    #    print("Retiming scene: , factor: ", mode, factor)
    roundToNearestFrame = retimerApplyToSettings.snapKeysToFrames
    retime_args = (mode, start_incl, end_incl, join_gap, factor, pivot)
    #    print("retime_args: ", retime_args)

    # Actions can be linked so we must make sure to only retime them once
    actions_done = set()
    action_tmp = bpy.data.actions.new("Retimer_TmpAction")

    def _retimeFcurve(action, addActionToDone=True):
        if action is not None and action not in actions_done:
            # wkip can we have animated properties that are not actions?
            for fcurve in action.fcurves:
                if not fcurve.lock or retimerApplyToSettings.includeLockAnim:
                    retime_fCurve_frames(
                        FCurve(fcurve), *retime_args, roundToNearestFrame, keysBeforeRangeMode, keysAfterRangeMode
                    )
            # NOTE: wkip keep the test??
            if addActionToDone:
                actions_done.add(action)
            # _logger.debug_ext(f"_retimerFcurve: actions_done len: {len(actions_done)}")

    sceneMaterials = []
    for obj in objects:
        # print(f"Retiming object named: {obj.name}")

        # standard object keyframes
        if retimerApplyToSettings.applyToObjects:
            if obj.type != "GPENCIL":
                if obj.animation_data is not None:
                    _retimeFcurve(obj.animation_data.action)

                # data animation
                if obj.data is not None and obj.data.animation_data is not None:
                    _retimeFcurve(obj.data.animation_data.action)

                # shape keys
                if retimerApplyToSettings.applyToShapeKeys:
                    if (
                        obj.type == "MESH"
                        and obj.data.shape_keys is not None
                        and obj.data.shape_keys.animation_data is not None
                    ):
                        _retimeFcurve(obj.data.shape_keys.animation_data.action)

                # animated materials
                for matSlot in obj.material_slots:
                    if matSlot is not None:
                        mat = matSlot.material
                        if mat is not None and mat not in sceneMaterials:
                            sceneMaterials.append(mat)
                            if mat.animation_data is not None and mat.animation_data.action is not None:
                                _retimeFcurve(mat.animation_data.action)
                            if (
                                mat.node_tree.animation_data is not None
                                and mat.node_tree.animation_data.action is not None
                            ):
                                _retimeFcurve(mat.node_tree.animation_data.action)

        # grease pencil
        if retimerApplyToSettings.applytToGreasePencil:
            #    retime_args = (mode, start_incl, end_incl, join_gap, factor, pivot)

            if obj.type == "GPENCIL":
                action_tmp_added = False

                if obj.animation_data is None:
                    obj.animation_data_create()

                if obj.animation_data is not None:
                    # when a stroke has no transform animation it has no action and because of a bug
                    # the stroke frames are not updated. As a turnaround we force an action and
                    # remove it afterward
                    if obj.animation_data.action is None:
                        obj.animation_data.action = action_tmp
                        action_tmp_added = True

                    _retimeFcurve(obj.animation_data.action, addActionToDone=not action_tmp_added)
                    # action = obj.animation_data.action
                    # if action is not None and action not in actions_done:
                    #     for fcurve in action.fcurves:
                    #         if not fcurve.lock or retimerApplyToSettings.includeLockAnim:
                    #             retime_fCurve_frames(FCurve(fcurve), *retime_args, roundToNearestFrame)
                    #     if not action_tmp_added:
                    #         actions_done.add(action)

                for layer in obj.data.layers:
                    #    print(f"Treating GP object: {obj.name} layer: {layer}")
                    if not layer.lock or retimerApplyToSettings.includeLockAnim:
                        retime_GPframes(
                            layer, *retime_args, roundToNearestFrame, keysBeforeRangeMode, keysAfterRangeMode
                        )

                if action_tmp_added:
                    obj.animation_data.action = None

        # force an update on the actions (cause bug. Other approach would be to save the file and reload it)
        if obj.animation_data is not None:
            if obj.animation_data.action is not None:
                action_backup = obj.animation_data.action
                obj.animation_data.action = None
                obj.animation_data.action = action_backup

    # VSE
    # no operation for CLEAR_ANIM
    if "CLEAR_ANIM" != mode:
        if retimerApplyToSettings.applyToVSE:
            retime_vse(scene, mode, start_incl, end_incl)

    # Shot ranges
    if retimerApplyToSettings.applyToCameraShotRanges:
        props = config.getAddonProps(scene)
        shotList = props.getShotsList(ignoreDisabled=False)

        if "CLEAR_ANIM" != mode:
            for shot in shotList:
                retime_shot(shot, *retime_args)

    # markers
    if retimerApplyToSettings.applyToMarkers:
        retime_markers(scene, *retime_args, roundToNearestFrame)

    # anim range
    # NOTE: end_incl = start_incl + duration_incl - 1  <=>  duration_incl = end_incl - start_incl + 1
    # def _compute_retimed_frame(frame_value, mode, start_incl, end_incl, duration_incl, pivot, factor):
    #     new_frame_value = frame_value

    #     if "INSERT" == mode:
    #         if start_incl <= frame_value:
    #             new_frame_value = frame_value + duration_incl
    #     elif "DELETE" == mode:
    #         if start_incl <= frame_value:
    #             if end_incl < frame_value:
    #                 new_frame_value = frame_value - duration_incl
    #             else:
    #                 new_frame_value = start_incl
    #     elif "RESCALE" == mode:
    #         new_frame_value = rescale_frame(frame_value, start_incl, end_incl, pivot, factor)

    #     # no operation for CLEAR_ANIM

    #     return new_frame_value

    # anim range

    if retimerApplyToSettings.applyToSceneRange and "CLEAR_ANIM" != mode:

        # new_range_start = _compute_retimed_frame(
        #     scene.frame_start, mode, start_incl, end_incl, duration_incl, pivot, factor
        # )
        # new_range_end = _compute_retimed_frame(
        #     scene.frame_end, mode, start_incl, end_incl, duration_incl, pivot, factor
        # )
        # new_range_preview_start = _compute_retimed_frame(
        #     scene.frame_preview_start, mode, start_incl, end_incl, duration_incl, pivot, factor
        # )
        # new_range_preview_end = _compute_retimed_frame(
        #     scene.frame_preview_end, mode, start_incl, end_incl, duration_incl, pivot, factor
        # )
        new_range_start = computeNewFrameValue(
            scene.frame_start, mode, start_incl, end_incl, pivot, factor, roundToNearestFrame=True
        )
        new_range_end = computeNewFrameValue(
            scene.frame_end, mode, start_incl, end_incl, pivot, factor, roundToNearestFrame=True
        )
        new_range_preview_start = computeNewFrameValue(
            scene.frame_preview_start, mode, start_incl, end_incl, pivot, factor, roundToNearestFrame=True
        )
        new_range_preview_end = computeNewFrameValue(
            scene.frame_preview_end, mode, start_incl, end_incl, pivot, factor, roundToNearestFrame=True
        )

        # extension of the animation range end is wanted in these cases
        if "INSERT" == mode:
            if scene.frame_start == start_incl:
                new_range_start = start_incl
            if scene.frame_preview_start == start_incl:
                new_range_preview_start = start_incl

            if scene.frame_end == start_incl:
                new_range_end = end_incl + 1
            if scene.frame_end == start_incl:
                new_range_preview_end = end_incl + 1

        # print(f"\n scene range: new start_incl: {new_range_start}, new end_incl: {new_range_end}")
        scene.frame_start = max(new_range_start, 0)
        scene.frame_end = max(new_range_end, 0)
        scene.frame_preview_start = max(new_range_preview_start, 0)
        scene.frame_preview_end = max(new_range_preview_end, 0)

    # time cursor
    if retimerApplyToSettings.applyToTimeCursor and "CLEAR_ANIM" != mode:
        # new_current_frame = _compute_retimed_frame(
        #     current_frame, mode, start_incl, end_incl, duration_incl, pivot, factor
        # )
        new_current_frame = computeNewFrameValue(
            current_frame, mode, start_incl, end_incl, pivot, factor, roundToNearestFrame=True
        )
        if scene.use_preview_range:
            rangeStart = scene.frame_preview_start
            rangeEnd = scene.frame_preview_end
        else:
            rangeStart = scene.frame_start
            rangeEnd = scene.frame_end
        new_current_frame = max(new_current_frame, rangeStart)
        new_current_frame = min(new_current_frame, rangeEnd)
        scene.frame_set(new_current_frame)

    # NOTE: should be kept but returns an error message in the log:
    # ERROR (bke.lib_id_delete): C:\Users\blender\git\blender-v320\blender.git\source\blender\blenkernel\intern\lib_id_delete.c:344
    # id_delete: Deleting ACRetimer_TmpAction which still has 1 users (including 0 'extra' shallow users)
    # bpy.data.actions.remove(action_tmp)

    return ()
