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

from shotmanager.otio import exports


def export_otio(shot_manager, file_path="", file_name="", add_take_name_to_path=False, take_index=-1, fps=-1):
    """ Create an OpenTimelineIO XML file for the specified take
        Return the file path of the created file
        If file_name is left to default then the rendered file will be a .xml
    """
    parent_scene = shot_manager.getParentScene()
    res = exports.exportShotManagerEditToOtio(
        parent_scene,
        filePath=file_path,
        fileName=file_name,
        addTakeNameToPath=add_take_name_to_path,
        takeIndex=take_index,
        fps=fps,
    )
    return res


# wkip to do: add import otio

