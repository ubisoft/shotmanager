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
Shot Manager grease pencil operators
"""

import bpy

from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    BoolProperty,
)

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_FrameUsagePreset(PropertyGroup):
    """
    Example:
        id:             id: Can be anything (nothing hardcoded in SM) but most common are:
                        "CANVAS", "BG_LINES", "BG_FILLS", "MG_LINES", "MG_FILLS", "FG_LINES", "FG_FILLS", "PERSP", "ROUGH"
        label:          Background Fills
        used:           True
        layerName:      BG Fills
        materialName:   <depends>


    """

    id: StringProperty(default="ID")
    used: BoolProperty(name="Used", default=False)
    label: StringProperty(name="Label", default="")

    def _get_layerName(self):
        val = self.get("layerName", True)
        return val

    def _set_layerName(self, value):
        self["layerName"] = value
        _logger.debug_ext(f"\n _set_layerName: {value} - {self['layerName']}", col="RED", tag="GREASE_PENCIL")

    layerName: StringProperty(name="Layer Name", get=_get_layerName, set=_set_layerName, default="")

    materialName: StringProperty(name="Material Name", default="")


_classes = (UAS_ShotManager_FrameUsagePreset,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
