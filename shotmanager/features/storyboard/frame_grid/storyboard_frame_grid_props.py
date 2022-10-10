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
Grid definition to order storyboard frames in the 3D space
"""

from math import radians

import bpy
from bpy.types import PropertyGroup
from bpy.props import FloatProperty, FloatVectorProperty, IntProperty, EnumProperty


class UAS_ShotManager_FrameGrid(PropertyGroup):
    """3D grid to place the storyboard frames in space"""

    origin: FloatVectorProperty(
        name="Origin",
        description="Top left corner of the grid",
        size=3,
        default=(10, 0, 10),
        options=set(),
    )

    offset_x: FloatProperty(
        name="Offset on X",
        description="",
        min=0.5,
        step=0.1,
        default=2.7,
        options=set(),
    )
    offset_y: FloatProperty(
        name="Offset on Y",
        description="",
        min=0.5,
        step=0.1,
        default=1.7,
        options=set(),
    )
    offset_z: FloatProperty(
        name="Offset on Z",
        description="",
        min=0.5,
        step=0.1,
        default=2.0,
        options=set(),
    )

    numShotsPerRow: IntProperty(
        name="Number of Shots per Row",
        description="",
        min=1,
        soft_max=10,
        default=5,
        options=set(),
    )
    # numShots_y: IntProperty(default=1)
    # numShots_z: IntProperty(default=1)

    orientTowardAxis: EnumProperty(
        name="Orient Toward Axis",
        description="Orient the Storyboard Shots in the direction of the specifed axis",
        items=(
            ("X_POSITIVE", "X", ""),
            ("X_NEGATIVE", "-X", ""),
            ("Y_POSITIVE", "Y", ""),
            ("Y_NEGATIVE", "-Y", ""),
        ),
        default="Y_POSITIVE",
        options=set(),
    )

    def updateStoryboardGrid(self, frameList):
        """Set the camera of the storyboard frames on the 3D grid
        Only cameras related to storyboard frames, and not shots, are affected"""

        import math

        grid = self
        numShots = len(frameList)
        numRows = math.ceil(numShots / grid.numShotsPerRow)

        for rowInd in range(0, numRows):
            for colInd in range(0, grid.numShotsPerRow):
                shotColInd = rowInd * grid.numShotsPerRow + colInd
                if shotColInd < len(frameList):
                    shot = frameList[shotColInd]
                    if shot.isCameraValid():
                        shot.camera.location[0] = grid.origin[0] + grid.offset_x * colInd
                        shot.camera.location[2] = grid.origin[2] + grid.offset_y * (-1.0 * rowInd)
                        shot.camera.location[1] = grid.origin[1]  # + grid.offset_z * ((i - 1) % grid.numShotsPerRow)

                        # the whole grid has to be re-oriented for this to work...
                        # match grid.orientTowardAxis:
                        #     case "X_POSITIVE":
                        #         shot.camera.rotation_euler = (radians(90), 0.0, radians(-90))
                        #     case "X_NEGATIVE":
                        #         shot.camera.rotation_euler = (radians(90), 0.0, radians(90))
                        #     case "Y_POSITIVE":
                        #         shot.camera.rotation_euler = (radians(90), 0.0, 0.0)
                        #     case "Y_NEGATIVE":
                        #         shot.camera.rotation_euler = (radians(90), 0.0, radians(-180))

                        if "X_POSITIVE" == grid.orientTowardAxis:
                            shot.camera.rotation_euler = (radians(90), 0.0, radians(-90))
                        elif "X_NEGATIVE" == grid.orientTowardAxis:
                            shot.camera.rotation_euler = (radians(90), 0.0, radians(90))
                        elif "Y_POSITIVE" == grid.orientTowardAxis:
                            shot.camera.rotation_euler = (radians(90), 0.0, 0.0)
                        elif "Y_NEGATIVE" == grid.orientTowardAxis:
                            shot.camera.rotation_euler = (radians(90), 0.0, radians(-180))


_classes = (UAS_ShotManager_FrameGrid,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
