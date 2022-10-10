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


import bpy
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
            targetArea=targetArea,
        )
        QuadObject.__init__(
            self,
            posXIsInRegionCS=posXIsInRegionCS,
            posX=posX,
            posYIsInRegionCS=posYIsInRegionCS,
            posY=posY,
            widthIsInRegionCS=widthIsInRegionCS,
            width=width,
            heightIsInRegionCS=heightIsInRegionCS,
            height=height,
            alignment=alignment,
            alignmentToRegion=alignmentToRegion,
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

        NOTE: bBox is defined by [xMin, YMin, xMax, yMax], in pixels in region CS (so bottom left, compatible with mouse position)
        In the bounding boxes, the max values, corresponding to pixel coordinates, are NOT included in the component
        Consequently the width of the rectangle, in pixels belonging to it, is given by xMax - xMin (and NOT xMax - xMin + 1 !)
        """
        if not self.isFullyClamped:
            # if self._bBox[0] <= ptX <= self._bBox[2] and self._bBox[1] <= ptY <= self._bBox[3]:
            if (
                self._clamped_bBox[0] <= ptX < self._clamped_bBox[2]
                and self._clamped_bBox[1] <= ptY < self._clamped_bBox[3]
            ):
                return True
        return False

    #################################################################

    # drawing ##########

    #################################################################

    # # override Mesh2D
    # def draw(self, shader=None, region=None, draw_types="TRIS", cap_lines=False, preDrawOnly=False):
    #     QuadObject.draw(self, shader, region, draw_types, cap_lines, preDrawOnly=preDrawOnly)

    #################################################################

    # events ###########

    #################################################################

    # override InteractiveComponent to include children
    def handle_event(self, context, event):
        """handle event for Componenent2D operator"""
        # _logger.debug_ext(" component2D handle_events", col="PURPLE", tag="EVENT")

        event_handled = False
        region, area = self.get_region_at_xy(context, event.mouse_x, event.mouse_y, "DOPESHEET_EDITOR")

        # get only events in the target area
        # wkip: mouse release out of the region have to be taken into account

        # children
        # get sorted children and call them. getChildren is inherited from Object2D
        sortedChildren = self.getChildren(sortedByIncreasingZ=True)
        for child in sortedChildren:
            handle_event = getattr(child, "handle_event", None)
            if callable(handle_event):
                event_handled = child.handle_event(context, event)
                if event_handled:
                    break

        if not event_handled:
            self._event_highlight(context, event, region)
            event_handled = self._handle_event_custom(context, event, region)

        # events doing the action
        # if not event_handled:
        #     if self.targetArea is not None and area == self.targetArea:
        #         if region:
        #             # if ignoreWidget(bpy.context):
        #             #     return False
        #             # else:

        #             # children
        #             # for widget in self.widgets:
        #             #     if widget.handle_event(context, event, region):
        #             #         event_handled = True
        #             #         break

        #             # self
        #             self._event_highlight(context, event, region)
        #             event_handled = self._handle_event_custom(context, event, region)

        return event_handled

    ######################################################################

    # event actions ##############

    ######################################################################
