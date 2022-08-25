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

    def insert_frame(self, coordinates):
        kf = self.fcurve.keyframe_points.insert(coordinates[0], coordinates[1])

    def remove_frames(self, start_incl, end_incl, remove_gap=False):
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
            _offset_frames(self, end_incl, start_incl - end_incl - 1)

    def __len__(self):
        return len(self.fcurve.keyframe_points)


# def _offset_frames(fcurve: FCurve, start_incl, offset):
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


def compute_offset(frame_value, pivot, factor):
    """Compute the new value of frame_value when scaled from the pivot and by the given factor"""
    duration_to_pivot = frame_value - pivot
    return round(duration_to_pivot * factor)  # + pivot


def rescale_frame(frame_value, start_incl, end_incl, pivot, factor):
    """Compute the new value of frame_value when scaled from the pivot and by the given factor
    in the specified range
    Note: this works only for frames, not floating points
    """
    new_frame_value = frame_value
    duration_to_pivot = frame_value - pivot
    round(duration_to_pivot * factor) + pivot

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


def _stretch_frames(fcurve: FCurve, start_incl, end_incl, factor, pivot_value, clamp):
    # First pass.
    if clamp:
        remove_pre_start = list()
        remove_post_end = list()
        for i in range(len(fcurve)):
            coordinates = fcurve.get_key_coordinates(i)
            dist_from_pivot = coordinates[0] - pivot_value
            if start_incl >= round(pivot_value + dist_from_pivot * factor):
                remove_pre_start.append(coordinates[0])
            elif round(pivot_value + dist_from_pivot * factor) >= end_incl:
                remove_post_end.append(coordinates[0])

        if remove_pre_start:
            fcurve.remove_frames(min(remove_pre_start), max(remove_pre_start), False)

        if remove_post_end:
            fcurve.remove_frames(min(remove_post_end), max(remove_post_end), False)
    else:
        if factor > 1:
            _offset_frames(
                fcurve, end_incl + 1, compute_offset(end_incl + 1, pivot_value, factor) - (end_incl - start_incl + 1)
            )
            # print(f" rescale offset 01: {compute_offset(end_incl + 1, pivot_value, factor)}")

    # wkip delete existing keys when factor < 1.0
    # bpy.ops.action.clean(threshold=0.001, channels=False)
    for i in range(len(fcurve)):
        coordinates = fcurve.get_key_coordinates(i)
        if start_incl <= coordinates[0] <= end_incl:
            handles = fcurve.handles(i)
            offset = compute_offset(coordinates[0], pivot_value, factor)  # - start_incl + 1
            # fcurve.set_key_coordinates(i, (coordinates[0] + offset, coordinates[1]))
            fcurve.set_key_coordinates(i, (pivot_value + offset, coordinates[1]))
            handles[0][0] = pivot_value + compute_offset(handles[0][0], pivot_value, factor)
            handles[1][0] = pivot_value + compute_offset(handles[1][0], pivot_value, factor)

    if factor < 1.0:
        _offset_frames(
            fcurve, end_incl + 1, compute_offset(end_incl + 1, pivot_value, factor) - (end_incl - start_incl + 1)
        )


def _offset_frames(fcurve: FCurve, start_incl, offset):
    for i in range(len(fcurve)):
        key_time, value = fcurve.get_key_coordinates(i)
        if start_incl <= key_time:
            fcurve.set_key_coordinates(i, (key_time + offset, value))
            left_handle, right_handle = fcurve.handles(i)
            left_handle[0] += offset
            right_handle[0] += offset


def _offset_GPframes(layer, start_incl, offset):
    """Move the layer frames that are AT THE SAME TIME or later than the reference frame"""
    # print(f"layer:{layer.info}")
    for f in layer.frames:
        if start_incl <= f.frame_number:
            f.frame_number += offset


def retime_GPframes(layer, mode, start_incl=0, end_incl=0, remove_gap=True, factor=1.0, pivot=0):
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
        # push out of range frames later in time
        if factor > 1.0:
            # wkip sur du +1 on end frame????
            _offset_GPframes(
                layer, end_incl + 1, compute_offset(end_incl + 1, pivot, factor) - (end_incl - start_incl + 1)
            )

        # scale range
        for f in layer.frames:
            if start_incl <= f.frame_number <= end_incl:
                offset = compute_offset(f.frame_number, pivot, factor)
                f.frame_number = offset + pivot

        # pull out of range frames sooner in time
        if factor < 1.0:
            _offset_GPframes(
                layer, end_incl + 1, compute_offset(end_incl + 1, pivot, factor) - (end_incl - start_incl + 1)
            )

    return ()


def retime_frames(fcurve: FCurve, mode, start_incl=0, end_incl=0, remove_gap=True, factor=1.0, pivot=0):

    if mode == "INSERT":
        _offset_frames(fcurve, start_incl, end_incl - start_incl + 1)

    elif mode == "DELETE" or mode == "CLEAR_ANIM":
        fcurve.remove_frames(start_incl, end_incl, remove_gap)

    elif mode == "RESCALE":
        _stretch_frames(fcurve, start_incl, end_incl, factor, pivot, False)

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
                fcurve.insert_frame(v)


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


def computeNewTimeValue(frameVal, mode, start_incl=0, end_incl=0, remove_gap=True, factor=1.0, pivot=0):
    """Return the value of the time (in frames) after the retiming
    Return None if the new time value is not available (deleted time for example)"""

    newFrameVal = frameVal

    if mode == "INSERT":
        offset = end_incl - start_incl + 1
        if start_incl <= frameVal:
            return frameVal + offset

    elif mode == "DELETE" or mode == "CLEAR_ANIM":
        if start_incl <= frameVal:
            if frameVal <= end_incl:
                return None
            else:
                offset = end_incl - start_incl + 1
                return frameVal - offset

    elif mode == "RESCALE":
        newFrameVal = rescale_frame(frameVal, start_incl, end_incl, pivot, factor)
        return newFrameVal
        # if start_incl <= frameVal:
        #     if frameVal <= end_incl:
        #         return None
        #     else:
        #         offset = (end_incl - start_incl - 1) * factor - end_incl + start_incl - 1
        #         # _logger.debug_ext(f" In computeNewTimeValue() Rescale mode: offset: {offset}")
        #         return frameVal + offset

    elif mode == "FREEZE":
        pass

    return newFrameVal


def retime_markers(scene, mode, start_incl=0, end_incl=0, remove_gap=True, factor=1.0, pivot=0):
    # NOTE: there can be several markers per frame!!!

    if mode == "RESCALE":
        offset = (end_incl - start_incl - 1) * factor - end_incl + start_incl - 1
        _logger.debug_ext(f" In retime_markers() Rescale mode: offset: {offset}")

    markers = sortMarkers(scene.timeline_markers)
    if len(markers):
        for m in markers:
            newFrameVal = computeNewTimeValue(m.frame, mode, start_incl, end_incl, remove_gap, factor, pivot)
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
    context,
    retimerProps,
    mode: str,
    retimerApplyToSettings,
    objects,
    start_incl: int,
    duration_incl: float,
    join_gap=True,
    factor=1.0,
    pivot=0,
):
    """Apply the time change for each type of entities

    For the following lines keep in mind that:
       - retimerProps.insert_duration is inclusive
       - retimerProps.start_frame is EXCLUSIVE   (in other words it is NOT modified)
       - retimerProps.end_frame is EXCLUSIVE     (in other words is the first frame to be offset)

    But retimeScene() requires INCLUSIVE range of time for the modifications (= all the frames
    created or deleted, not the moved ones).

    Args:
        start_incl (int): The included start frame
        duration_incl (int): The range of retime frames (new or deleted)
    """
    prefs = config.getShotManagerPrefs()
    scene = context.scene
    end_incl = start_incl + duration_incl - 1

    print(
        f" - retimeScene(): {retimerProps.mode}, start_incl: {start_incl}, end_incl: {end_incl}, duration_incl: {duration_incl}"
    )

    #    print("Retiming scene: , factor: ", mode, factor)
    retime_args = (mode, start_incl, end_incl, join_gap, factor, pivot)
    #    print("retime_args: ", retime_args)

    actions_done = set()  # Actions can be linked so we must make sure to only retime them once
    action_tmp = bpy.data.actions.new("Retimer_TmpAction")

    for obj in objects:
        # print(f"Retiming object named: {obj.name}")

        # Standard object keyframes
        if retimerApplyToSettings.applyToObjects:
            if obj.type != "GPENCIL":
                if obj.animation_data is not None:
                    action = obj.animation_data.action
                    if action is not None and action not in actions_done:
                        # wkip can we have animated properties that are not actions?
                        for fcurve in action.fcurves:
                            if not fcurve.lock or retimerApplyToSettings.includeLockAnim:
                                retime_frames(FCurve(fcurve), *retime_args)
                        actions_done.add(action)

        # Shape keys
        if retimerApplyToSettings.applyToShapeKeys:
            if (
                obj.type == "MESH"
                and obj.data.shape_keys is not None
                and obj.data.shape_keys.animation_data is not None
            ):
                action = obj.data.shape_keys.animation_data.action
                if action is not None and action not in actions_done:
                    for fcurve in action.fcurves:
                        if not fcurve.lock or retimerApplyToSettings.includeLockAnim:
                            retime_frames(FCurve(fcurve), *retime_args)
                    actions_done.add(action)

        # Grease pencil
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

                    action = obj.animation_data.action
                    if action is not None and action not in actions_done:
                        for fcurve in action.fcurves:
                            if not fcurve.lock or retimerApplyToSettings.includeLockAnim:
                                retime_frames(FCurve(fcurve), *retime_args)
                        if not action_tmp_added:
                            actions_done.add(action)

                for layer in obj.data.layers:
                    #    print(f"Treating GP object: {obj.name} layer: {layer}")
                    if not layer.lock or retimerApplyToSettings.includeLockAnim:
                        retime_GPframes(layer, *retime_args)

                if action_tmp_added:
                    obj.animation_data.action = None

        # Force an update on the actions (cause bug. Other approach would be to save the file and reload it)
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

    # Shots
    if retimerApplyToSettings.applyToCameraShots:
        props = scene.UAS_shot_manager_props
        shotList = props.getShotsList(ignoreDisabled=False)

        if "CLEAR_ANIM" != mode:
            for shot in shotList:
                retime_shot(shot, *retime_args)

    # markers
    if retimerApplyToSettings.applyToMarkers:
        retime_markers(scene, *retime_args)

    # anim range
    def compute_retimed_frame(frame_value, mode, start_incl, end_incl, duration_incl, pivot, factor):
        new_frame_value = frame_value

        if "INSERT" == mode:
            if start_incl <= frame_value:
                new_frame_value = frame_value + duration_incl
        elif "DELETE" == mode:
            if start_incl <= frame_value:
                if end_incl < frame_value:
                    new_frame_value = frame_value - duration_incl
                else:
                    new_frame_value = start_incl
        elif "RESCALE" == mode:
            new_frame_value = rescale_frame(frame_value, start_incl, end_incl, pivot, factor)

        # no operation for CLEAR_ANIM

        return new_frame_value

    # anim range
    if prefs.applyToSceneRange and "CLEAR_ANIM" != mode:

        new_range_start = compute_retimed_frame(
            scene.frame_start, mode, start_incl, end_incl, duration_incl, pivot, factor
        )
        new_range_end = compute_retimed_frame(scene.frame_end, mode, start_incl, end_incl, duration_incl, pivot, factor)
        new_range_preview_start = compute_retimed_frame(
            scene.frame_preview_start, mode, start_incl, end_incl, duration_incl, pivot, factor
        )
        new_range_preview_end = compute_retimed_frame(
            scene.frame_preview_end, mode, start_incl, end_incl, duration_incl, pivot, factor
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
    if prefs.applyToTimeCursor and "CLEAR_ANIM" != mode:
        new_current_frame = max(
            compute_retimed_frame(scene.frame_current, mode, start_incl, end_incl, duration_incl, pivot, factor), 0
        )
        scene.frame_set(new_current_frame)

    bpy.data.actions.remove(action_tmp)

    return ()


# to do:
# - faire marcher le rescale
#     - verif shots
# - shape keys
# - vse
# - finir fonction generic
