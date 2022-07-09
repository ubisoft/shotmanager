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
UI in BGL for the Interactive Shots Stack overlay tool
"""


import bpy
import bgl
import blf
import gpu

from shotmanager.utils.utils import color_to_sRGB, color_is_dark, lighten_color, set_color_alpha
from shotmanager.gpu.gpu_2d.gpu_2d import Component2D


class ShotClipComponent(Component2D):
    """Interactive shot component"""

    def __init__(self, targetArea, posX=30, posY=2, width=40, name="Shot Clip", color=(0.9, 0.0, 0.0, 1.0)):
        Component2D.__init__(
            self,
            targetArea,
            posXIsInRegionCS=False,
            posX=posX,
            posYIsInRegionCS=False,
            posY=posY,
            widthIsInRegionCS=False,
            width=width,
            heightIsInRegionCS=False,
            height=1,
            alignment="BOTTOM_LEFT",
            alignmentToRegion="TOP_LEFT",
        )

        self.name = name
        self.color = color
        self.color_highlight = (0.6, 0.9, 0.6, 0.9)
        self.color_selected = (0.6, 0.9, 0.9, 0.9)
        self.color_selected_highlight = (0.6, 0.9, 0.9, 0.9)
