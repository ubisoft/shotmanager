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
Grease pencil shot class
"""

import bpy
from bpy.types import PropertyGroup
from bpy.props import FloatProperty

from shotmanager.utils import utils
from shotmanager.utils import utils_greasepencil


class GreasePencilStoryboard(PropertyGroup):
    """ Contains the grease pencil related to the shot
    """

    # def _update_distance():
    #     fitCanvasToFrustum(gpStroke, camera)

    distance: FloatProperty(
        name="Distance",
        description="Distance",
        soft_min=0.0,
        min=0.0,
        soft_max=1.0,
        max=1.0,
        step=0.1,
        # update=_update_distance,
        default=0.9,
    )

    # def __init__(self, parent, shot):
    #     self._distance = 0

    # @property
    # def distance(self):
    #     return self._distance

    # @distance.setter
    # def distance(self, value):
    #     self._distance = value

    # def get_grease_pencil(self):
    #     return utils_greasepencil


_classes = (GreasePencilStoryboard,)


def register():
    pass
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
