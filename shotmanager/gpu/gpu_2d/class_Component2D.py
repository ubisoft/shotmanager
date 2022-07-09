# GPLv3 License
#
# Copyright (C) 2020 Ubisoft
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
Useful entities for 2D gpu drawings
"""

import gpu

from .class_InteractiveComponent import InteractiveComponent
from .class_QuadObject import QuadObject

from shotmanager.utils.utils import color_to_sRGB, set_color_alpha, alpha_to_linear

# from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class Component2D(InteractiveComponent, QuadObject):
    """Interactive graphic 2D component"""

    def __init__(
        self,
        targetArea,
        posXIsInRegionCS=True,
        posX=30,
        posYIsInRegionCS=True,
        posY=50,
        widthIsInRegionCS=True,
        width=40,
        heightIsInRegionCS=True,
        height=20,
        alignment="BOTTOM_LEFT",
        alignmentToRegion="BOTTOM_LEFT",
        parent=None,
    ):
        InteractiveComponent.__init__(
            self,
            targetArea,
        )
        QuadObject.__init__(
            self,
            posXIsInRegionCS,
            posX,
            posYIsInRegionCS,
            posY,
            widthIsInRegionCS,
            width,
            heightIsInRegionCS,
            height,
            alignment,
            alignmentToRegion,
            parent=parent,
        )

        self.color = (0.2, 0.6, 0.0, 0.9)
        self.color_highlight = (0.6, 0.9, 0.6, 0.9)
        self.color_selected = (0.6, 0.9, 0.9, 0.9)
        self.color_selected_highlight = (0.6, 0.9, 0.9, 0.9)

    # override InteractiveComponent
    # def handle_event_custom(self, context, event):
    #     event_handled = False
    #     if self.isInBBox(event.mouse_x, event.mouse_y):
    #         self.isHighlighted = True
    #     else:
    #         self.isHighlighted = False

    #     return event_handled

    # override InteractiveComponent
    def isInBBox(self, ptX, ptY):
        """Return True if the specified location is in the bbox of this InteractiveComponent instance
        ptX and ptY are in pixels, in region coordinate system
        """
        if not self.isFullyClamped:
            # if self._bBox[0] <= ptX <= self._bBox[2] and self._bBox[1] <= ptY <= self._bBox[3]:
            if (
                self._clamped_bBox[0] <= ptX <= self._clamped_bBox[2]
                and self._clamped_bBox[1] <= ptY <= self._clamped_bBox[3]
            ):
                return True
        return False

    # override Mesh2D
    def draw(self, shader=None, region=None, draw_types="TRIS", cap_lines=False):

        if self.isSelected:
            if self.isHighlighted:
                widColor = self.color_selected_highlight
            else:
                widColor = self.color_selected
        else:
            if self.isHighlighted:
                widColor = self.color_highlight
            else:
                widColor = self.color

        # match (self.isHighlighted, self.isSelected):
        #     case (False, False):
        #         widColor = self.color
        #     case (True, False):
        #         widColor = self.color_highlight
        #     case (True, False):
        #         widColor = self.color_selected
        #     case (True, True):
        #         widColor = self.color_selected_highlight

        if shader is None:
            UNIFORM_SHADER_2D.bind()
            color = set_color_alpha(widColor, alpha_to_linear(widColor[3] * self.opacity))
            UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB(color))
            shader = UNIFORM_SHADER_2D

        QuadObject.draw(self, shader, region, draw_types, cap_lines)

        for child in self._children:
            child.draw(None, region)
