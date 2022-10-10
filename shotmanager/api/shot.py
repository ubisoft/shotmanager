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
Shot Manager API - Interface with shot class
"""

import bpy
from shotmanager.properties.shot import UAS_ShotManager_Shot


def get_shot_manager_owner(shot_instance: UAS_ShotManager_Shot):
    """Return the shot manager properties instance the shot is belonging to."""
    return shot_instance.shotManager()


def get_name(shot_instance: UAS_ShotManager_Shot) -> str:
    return shot_instance.name


def set_name(shot_instance: UAS_ShotManager_Shot, name: str):
    """Set a unique name to the shot"""
    shot_instance.name = name


def get_name_path_compliant(shot_instance: UAS_ShotManager_Shot) -> str:
    return shot_instance.getName_PathCompliant()


def get_start(shot_instance: UAS_ShotManager_Shot) -> float:
    return shot_instance.start


def set_start(shot_instance: UAS_ShotManager_Shot, value: float):
    shot_instance.start = value


def get_end(shot_instance: UAS_ShotManager_Shot) -> float:
    return shot_instance.end


def set_end(shot_instance: UAS_ShotManager_Shot, value: float):
    shot_instance.end = value


def get_duration(shot_instance: UAS_ShotManager_Shot) -> float:
    """Returns the shot duration in frames
    in Blender - and in Shot Manager - the last frame of the shot is included in the rendered images
    """
    return shot_instance.getDuration()


def get_color(shot_instance: UAS_ShotManager_Shot):
    return shot_instance.get_color()


def set_color(shot_instance: UAS_ShotManager_Shot, value: float):
    shot_instance.set_color(value)


def get_enable_state(shot_instance: UAS_ShotManager_Shot) -> bool:
    return shot_instance.enabled


def set_enable_state(shot_instance: UAS_ShotManager_Shot, value: float):
    shot_instance.enabled = value


def is_camera_valid(shot_instance: UAS_ShotManager_Shot) -> bool:
    """Sometimes a pointed camera can seem to work but the camera object doesn't exist anymore in the scene.
    Return True if the camera is really there, False otherwise
    Note: This doesn't change the camera attribute of the shot
    """
    return shot_instance.isCameraValid()


def get_camera(shot_instance: UAS_ShotManager_Shot) -> bpy.types.Camera:
    return shot_instance.camera


def set_camera(shot_instance: UAS_ShotManager_Shot, camera: bpy.types.Camera):
    shot_instance.camera = camera


def get_edit_start(shot_instance: UAS_ShotManager_Shot, scene: bpy.types.Scene) -> float:
    return shot_instance.getEditStart(scene)


def get_edit_end(shot_instance: UAS_ShotManager_Shot, scene: bpy.types.Scene) -> float:
    return shot_instance.getEditEnd(scene)
