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
Shot Manager API - Interface with take class
"""

import bpy
from shotmanager.properties.take import UAS_ShotManager_Take


def get_name(take_instance: UAS_ShotManager_Take) -> str:
    return take_instance.name


def set_name(take_instance: UAS_ShotManager_Take, name: str):
    """Set a unique name to the take"""
    take_instance.name = name


def get_name_path_compliant(take_instance: UAS_ShotManager_Take) -> str:
    return take_instance.getName_PathCompliant()


def get_shot_list(take_instance: UAS_ShotManager_Take, ignore_disabled: bool = False) -> list:
    """Return a filtered copy of the shots associated to this take"""
    return take_instance.getShotList(ignoreDisabled=ignore_disabled)


def get_num_shots(take_instance: UAS_ShotManager_Take, ignore_disabled: bool = False) -> int:
    """Return the number of shots of the take"""
    return take_instance.getNumShots(ignoreDisabled=ignore_disabled)


def get_shots_using_camera(take_instance: UAS_ShotManager_Take, cam: bpy.types.Camera, ignore_disabled: bool = False):
    """Return the list of all the shots used by the specified camera"""
    return take_instance.getShotsUsingCamera(cam, ignoreDisabled=ignore_disabled)
