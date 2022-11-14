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
Shot Manager API - Interface with Otio
"""

from shotmanager.utils.utils_os import module_can_be_imported

from shotmanager.properties.props import UAS_ShotManager_Props

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def export_otio(
    shot_manager: UAS_ShotManager_Props,
    file_path: str = "",
    file_name: str = "",
    add_take_name_to_path: bool = False,
    take_index: int = -1,
    fps: float = -1,
):
    """Create an OpenTimelineIO XML file for the specified take
    Return the file path of the created file
    If file_name is left to default then the rendered file will be a .xml
    """
    if module_can_be_imported("shotmanager.otio"):
        from shotmanager.otio import exports

        parent_scene = shot_manager.getParentScene()
        res = exports.exportShotManagerEditToOtio(
            parent_scene,
            filePath=file_path,
            fileName=file_name,
            addTakeNameToPath=add_take_name_to_path,
            takeIndex=take_index,
            fps=fps,
        )
    else:
        _logger.error("Otio module not available (no OpenTimelineIO)")
        res = None
    return res
