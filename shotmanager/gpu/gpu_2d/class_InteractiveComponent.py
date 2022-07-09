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

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class InteractiveComponent:
    """Kind of abstract class or template to predefine the functions for interactions"""

    def __init__(
        self,
        targetArea,
    ):
        self.targetArea = targetArea

        self.isHighlighted = False
        self.isSelected = False

    def get_region_at_xy(self, context, x, y, area_type="VIEW_3D"):
        """Return the region and the area containing this region
        Does not support quadview right now
        Args:
            x:
            y:
        """
        for area in context.screen.areas:
            if area.type != area_type:
                continue
            # is_quadview = len ( area.spaces.active.region_quadviews ) == 0
            i = -1
            for region in area.regions:
                if region.type == "WINDOW":
                    i += 1
                    if region.x <= x < region.width + region.x and region.y <= y < region.height + region.y:

                        return region, area

        return None, None

    # to be overriden by inheriting classes
    def isInBBox(self, ptX, ptY):
        """Return True if the specified location is in the bbox of this InteractiveComponent instance
        ptX and ptY are in screen coordinate system
        """
        # ptX_inRegion =
        return False

    # to override in classes inheriting from this class:
    def handle_event_custom(self, context, event, region):
        event_handled = False
        # if event.type == "G":
        mouseIsInBBox = self.isInBBox(event.mouse_x - region.x, event.mouse_y - region.y)

        # highlight ##############
        if mouseIsInBBox:
            if not self.isHighlighted:
                self.isHighlighted = True
                # _logger.debug_ext("component2D handle_events set highlighte true", col="PURPLE", tag="EVENT")
                config.gRedrawShotStack = True
        else:
            if self.isHighlighted:
                self.isHighlighted = False
                config.gRedrawShotStack = True

        # # selection ##############
        # if event.type == "LEFTMOUSE":
        #     if event.value == "PRESS":
        #         if mouseIsInBBox:
        #             if not self.isSelected:
        #                 self.isSelected = True
        #                 #_logger.debug_ext("component2D handle_events set selected true", col="PURPLE", tag="EVENT")
        #                 config.gRedrawShotStack = True

        #     if event.value == "RELEASE":

        return event_handled

    def handle_event(self, context, event):
        """handle event for InteractiveSpace operator"""
        _logger.debug_ext(" component2D handle_events", col="PURPLE", tag="EVENT")

        event_handled = False
        region, area = self.get_region_at_xy(context, event.mouse_x, event.mouse_y, "DOPESHEET_EDITOR")

        # get only events in the target area
        # wkip: mouse release out of the region have to be taken into account

        # events doing the action
        if not event_handled:
            if self.targetArea is not None and area == self.targetArea:
                if region:
                    # if ignoreWidget(bpy.context):
                    #     return False
                    # else:

                    # children
                    # for widget in self.widgets:
                    #     if widget.handle_event(context, event, region):
                    #         event_handled = True
                    #         break

                    # self
                    event_handled = self.handle_event_custom(context, event, region)

        return event_handled
