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
from bpy.props import PointerProperty, FloatProperty

# from shotmanager.properties.shot import UAS_ShotManager_Shot

from shotmanager.utils import utils_greasepencil, utils


class GreasePencilProperties(PropertyGroup):
    """ Contains the grease pencil related to the shot
    """

    # parentShot: PointerProperty(type=UAS_ShotManager_Shot)
    parentCamera: PointerProperty(
        name="Camera", description="Camera parent of the grease pencil object", type=bpy.types.Object
    )

    def initialize(self, parentShot):
        """Set the parent camera of the Grease Pencil Properties
        """
        print(f"\nInitializing new Grease Pencil Properties for shot {parentShot.name}...")

        self.parentCamera = parentShot.camera

    def _update_gpDistance(self, context):
        # print("gpDistance")
        utils_greasepencil.fitGreasePencilToFrustum(self.parentCamera, self.gpDistance)

    gpDistance: FloatProperty(
        name="Distance",
        description="Distance between the storyboard frame and the parent camera",
        subtype="DISTANCE",
        soft_min=0.02,
        min=0.001,
        soft_max=10.0,
        # max=1.0,
        step=0.1,
        update=_update_gpDistance,
        default=0.5,
        options=set(),
    )

    def _update_gpCanvasOpacity(self, context):
        # print("gpCanvasOpacity")
        gp_child = utils_greasepencil.get_greasepencil_child(self.parentCamera)
        canvasLayer = utils_greasepencil.get_grease_pencil_layer(
            gp_child, gpencil_layer_name="GP_Canvas", create_layer=False
        )
        if canvasLayer is not None:
            canvasLayer.opacity = utils.to_sRGB(self.gpCanvasOpacity)

    gpCanvasOpacity: FloatProperty(
        name="Canvas Opacity",
        description="Opacity of the Canvas layer",
        min=0.0,
        max=1.0,
        step=0.01,
        update=_update_gpCanvasOpacity,
        default=1.0,
        options=set(),
    )

    def updateGreasePencilToFrustum(self):
        utils_greasepencil.fitGreasePencilToFrustum(self.parentCamera, self.gpDistance)

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


_classes = (GreasePencilProperties,)


def register():
    pass
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
