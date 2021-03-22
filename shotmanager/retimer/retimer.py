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

import bpy


class FCurve:
    def __init__(self, fcurve):
        self.fcurve = fcurve

    def get_key_coordinates(self, index):
        return self.fcurve.keyframe_points[index].co

    def set_key_coordinates(self, index, coordinates):
        self.fcurve.keyframe_points[index].co = coordinates

    def handles(self, index):
        return self.fcurve.keyframe_points[index].handle_left, self.fcurve.keyframe_points[index].handle_right

    # Seems to be passed by reference...
    # def set_handles ( self, index, value ):
    #    self.fcurve.keyframe_points[ index ].handle_left, self.fcurve.keyframe_points[ index ].handle_right = value

    def insert_frame(self, coordinates):
        kf = self.fcurve.keyframe_points.insert(coordinates[0], coordinates[1])

    def remove_frames(self, start, end):
        to_remove = list()

        for k in self.fcurve.keyframe_points:
            if start < k.co[0] < end:
                to_remove.append(k)

        for k in reversed(to_remove):
            self.fcurve.keyframe_points.remove(k)

    def __len__(self):
        return len(self.fcurve.keyframe_points)


class GPFCurve(FCurve):
    def get_key_coordinates(self, index):
        return self.fcurve.frames[index].frame_number, 0

    def set_key_coordinates(self, index, coordinates):
        self.fcurve.frames[index].frame_number = coordinates[0]

    def handles(self, index):
        return [0, 0], [0, 0]

    def set_handles(self, index, value):
        pass

    def insert_frame(self, coordinates):
        pass

    def remove_frames(self, start, end):
        to_remove = list()

        for k in self.fcurve.frames:
            if start <= k.frame_number <= end:
                to_remove.append(k)

        for k in reversed(to_remove):
            self.fcurve.frames.remove(k)

    def __len__(self):
        return len(self.fcurve.frames)


def _stretch_frames(fcurve: FCurve, start_frame, end_frame, factor, pivot_value, clamp):
    def compute_offset(frame, pivot, factor):
        pivot_space_frame = frame - pivot
        return round(pivot_space_frame * factor - pivot_space_frame)

    # First pass.
    if clamp:
        remove_pre_start = list()
        remove_post_end = list()
        for i in range(len(fcurve)):
            coordinates = fcurve.get_key_coordinates(i)
            dist_from_pivot = coordinates[0] - pivot_value
            if start_frame >= round(pivot_value + dist_from_pivot * factor):
                remove_pre_start.append(coordinates[0])
            elif round(pivot_value + dist_from_pivot * factor) >= end_frame:
                remove_post_end.append(coordinates[0])

        if remove_pre_start:
            _remove_frames(fcurve, min(remove_pre_start), max(remove_pre_start), False)

        if remove_post_end:
            _remove_frames(fcurve, min(remove_post_end), max(remove_post_end), False)
    else:
        if factor > 1:
            _offset_frames(fcurve, end_frame + 1, compute_offset(end_frame, pivot_value, factor))

    for i in range(len(fcurve)):
        coordinates = fcurve.get_key_coordinates(i)
        if start_frame <= coordinates[0] <= end_frame:
            handles = fcurve.handles(i)
            offset = compute_offset(coordinates[0], pivot_value, factor)
            fcurve.set_key_coordinates(i, (coordinates[0] + offset, coordinates[1]))
            handles[0][0] += compute_offset(handles[0][0], pivot_value, factor)
            handles[1][0] += compute_offset(handles[1][0], pivot_value, factor)

    if factor < 1.0:
        _offset_frames(fcurve, end_frame, compute_offset(end_frame, pivot_value, factor))


def _remove_frames(fcurve: FCurve, start_frame, end_frame, remove_gap):
    fcurve.remove_frames(start_frame - 1, end_frame)
    if remove_gap:
        _offset_frames(fcurve, end_frame, start_frame - end_frame)
        pass


def _offset_frames(fcurve: FCurve, reference_frame, offset):
    for i in range(len(fcurve)):
        key_time, value = fcurve.get_key_coordinates(i)
        if key_time >= reference_frame:
            fcurve.set_key_coordinates(i, (key_time + offset, value))
            left_handle, right_handle = fcurve.handles(i)
            left_handle[0] += offset
            right_handle[0] += offset


def retime_frames(fcurve: FCurve, mode, start_frame=0, end_frame=0, remove_gap=True, factor=1.0, pivot=""):

    if mode == "INSERT":
        _offset_frames(fcurve, start_frame, end_frame - start_frame)
    elif mode == "FREEZE":
        for i in range(len(fcurve)):
            key_time, value = fcurve.get_key_coordinates(i)
            new_keys = list()
            if key_time == start_frame:
                new_keys.append((key_time, value))
                new_keys.append((key_time + end_frame - start_frame, value))

            if key_time >= start_frame:
                fcurve.set_key_coordinates(i, (key_time + end_frame - start_frame, value))

                left_handle, right_handle = fcurve.get_handles(i)
                left_handle[0] += end_frame - start_frame
                right_handle[0] += end_frame - start_frame
                fcurve.set_handles(i, (left_handle, right_handle))

            for v in new_keys:
                fcurve.insert_frame(v)

    elif mode == "DELETE" or mode == "CLEAR_ANIM":
        _remove_frames(fcurve, start_frame, end_frame, remove_gap)

    elif mode == "RESCALE":
        _stretch_frames(fcurve, start_frame, end_frame, factor, pivot, False)


def retime_shot(shot, mode, start_frame=0, end_frame=0, remove_gap=True, factor=1.0, pivot=0):

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
        # if start_frame <= shot.start and shot.end <= end_frame:
        #     shot.start = start_frame
        #     shot.end = end_frame

        # # shot is before, nothing happens
        # elif shot.start < start_frame and shot.end < start_frame:
        #     pass

        # # shot is after, we offset
        # elif end_frame <= shot.start and shot.end <= end_frame:
        #     offset = end_frame - start_frame
        #     shot.start -= offset
        #     shot.end -= offset

        # else:

        print(" DELETE: start_frame, end: ", start_frame, end_frame)
        offset = end_frame - start_frame

        if shot.durationLocked:
            if shot.start <= start_frame:
                if shot.end <= start_frame:
                    pass
                elif shot.end <= end_frame:
                    shot.durationLocked = False
                    shot.end = start_frame  # goes to a non deleted part
                    shot.durationLocked = True
                else:
                    shot.durationLocked = False
                    shot.end -= offset
                    shot.durationLocked = True

            elif start_frame < shot.start and shot.start < end_frame:
                if shot.end <= end_frame:
                    shot.durationLocked = False
                    shot.start = start_frame
                    shot.end = start_frame
                    shot.durationLocked = True
                    shot.enabled = False
                else:
                    shot.durationLocked = False
                    shot.start = start_frame
                    shot.end -= offset
                    shot.durationLocked = True

            else:
                shot.start -= offset

        else:
            if shot.start <= start_frame:
                if shot.end <= start_frame:
                    pass
                elif shot.end <= end_frame:
                    shot.end = start_frame  # goes to a non deleted part
                else:
                    shot.end -= offset

            elif start_frame < shot.start and shot.start < end_frame:
                shot.start = start_frame

                if shot.end <= end_frame:
                    shot.end = start_frame
                    shot.enabled = False
                else:
                    shot.end -= offset

            else:
                shot.start -= offset
                shot.end -= offset

    elif mode == "RESCALE":
        offset = (end_frame - start_frame) * (factor - 1)

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
                    shot.end = (shot.end - pivot) * factor + pivot
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


# start parameter is replaced here by duration
def retimeScene(
    scene,
    mode: str,
    objects,
    start: float,
    duration: float,
    join_gap=True,
    factor=1.0,
    pivot=0,
    apply_on_objects=True,
    apply_on_shape_keys=True,
    apply_on_grease_pencils=True,
    apply_on_shots=True,
    apply_on_vse=True,
):
    retimer(
        scene,
        mode,
        objects,
        start,
        start + duration,
        join_gap=join_gap,
        factor=factor,
        pivot=pivot,
        apply_on_objects=apply_on_objects,
        apply_on_shape_keys=apply_on_shape_keys,
        apply_on_grease_pencils=apply_on_grease_pencils,
        apply_on_shots=apply_on_shots,
        apply_on_vse=apply_on_vse,
    )


def retimer(
    scene,
    mode: str,
    objects,
    start: int,
    end: int,
    join_gap=True,
    factor=1.0,
    pivot=0,
    apply_on_objects=True,
    apply_on_shape_keys=True,
    apply_on_grease_pencils=True,
    apply_on_shots=True,
    apply_on_vse=True,
):

    print("Retiming scene: , factor: ", mode, factor)
    retime_args = (mode, start, end, join_gap, factor, pivot)
    print("retime_args: ", retime_args)

    actions_done = set()  # Actions can be linked so we must make sure to only retime them once.
    for obj in objects:
        # Standard object keyframes.
        if apply_on_objects:
            if obj.animation_data is not None:
                action = obj.animation_data.action
                if action is None or action in actions_done:
                    continue

                for fcurve in action.fcurves:
                    retime_frames(FCurve(fcurve), *retime_args)

                actions_done.add(action)

        # Shape keys
        if apply_on_shape_keys:
            if (
                obj.type == "MESH"
                and obj.data.shape_keys is not None
                and obj.data.shape_keys.animation_data is not None
            ):
                action = obj.data.shape_keys.animation_data.action
                if action is None or action in actions_done:
                    continue

                for fcurve in action.fcurves:
                    retime_frames(FCurve(fcurve), *retime_args)

                actions_done.add(action)

        # Grease pencil
        if apply_on_grease_pencils:
            if obj.type == "GPENCIL":
                for layer in obj.data.layers:
                    retime_frames(GPFCurve(layer), *retime_args)

    # VSE
    if apply_on_vse:
        retime_vse(scene, mode, start, end)

    # Shots
    if apply_on_shots:
        props = scene.UAS_shot_manager_props
        shotList = props.getShotsList(ignoreDisabled=False)

        if "INSERT" == mode:
            retime_args = (mode, start - 1, end - 1, join_gap, factor, pivot)
        elif "DELETE" == mode:
            retime_args = (mode, start - 1, end - 1, join_gap, factor, pivot)
        #  retime_args = (mode, start, end, join_gap, factor, pivot)
        elif "RESCALE" == mode:
            retime_args = (mode, start - 1, end - 1, join_gap, factor, pivot)
            pass

        for shot in shotList:
            retime_shot(shot, *retime_args)
