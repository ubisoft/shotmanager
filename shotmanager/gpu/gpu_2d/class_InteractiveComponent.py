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


import time

import bpy
import gpu


from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class InteractiveComponent:
    """Kind of abstract class or template to predefine the functions for interactions

    - Event action callbacks:
      - Some attributes of InteractiveComponent have callbacks that are triggered when the attribute is changed. This is
        the case for isHighlighted, isSelected, isManipulated.
    """

    def __init__(
        self,
        targetArea,
    ):
        self.targetArea = targetArea

        # wkip good idea?
        self.context = bpy.context

        # attributes with event action ##########
        #########################################
        self._isHighlighted = False
        self._isSelected = False
        self._isManipulated = False

        # used in the draw functions to adopt the color associated to the isManipulated state
        self.isManipulatedByAnotherComponent = False

        # event control ##########
        #########################################
        # in seconds
        self.doubleClickDuration = 0.3

        self.prev_click = 0

        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.frame_under_mouse = -1

        self.mouseFrame = 0
        self.previousMouseFrame = 0

    @property
    def isHighlighted(self):
        return self._isHighlighted

    @isHighlighted.setter
    def isHighlighted(self, value):
        self._isHighlighted = value
        self._on_highlighted_changed(self.context, None, value)

    @property
    def isSelected(self):
        return self._isSelected

    @isSelected.setter
    def isSelected(self, value):
        self._isSelected = value
        self._on_selected_changed(self.context, None, value)

    @property
    def isManipulated(self):
        return self._isManipulated

    @isManipulated.setter
    def isManipulated(self, value):
        self._isManipulated = value
        self._on_manipulated_changed(self.context, None, value)

    #################################################################
    # functions ########
    #################################################################

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

        NOTE: bBox is defined by [xMin, YMin, xMax, yMax], in pixels in region CS (so bottom left, compatible with mouse position)
        In the bounding boxes, the max values, corresponding to pixel coordinates, are NOT included in the component
        Consequently the width of the rectangle, in pixels belonging to it, is given by xMax - xMin (and NOT xMax - xMin + 1 !)
        """
        # ptX_inRegion =
        return False

    #################################################################

    # events ###########

    #################################################################

    # to override by inheriting classes
    def _event_highlight(self, context, event, region):
        mouseIsInBBox = False

        # for debug, used to interupt for breakpoint:
        # if event.type == "G":
        #     print("Debug G key")

        mouseIsInBBox = self.isInBBox(event.mouse_x - region.x, event.mouse_y - region.y)

        # highlight ##############
        if event.type in ["MOUSEMOVE", "INBETWEEN_MOUSEMOVE"]:
            if mouseIsInBBox:
                if not self.isHighlighted:
                    self.isHighlighted = True
                    # _logger.debug_ext("component2D handle_events set highlighte true", col="PURPLE", tag="EVENT")
                # self._on_highlighted_changed(context, event, self.isHighlighted)
            else:
                if self.isHighlighted:
                    self.isHighlighted = False
                # self._on_highlighted_changed(context, event, self.isHighlighted)

    # # to override by inheriting classes
    # def _handle_event_custom(self, context, event, region):
    #     event_handled = False
    #     mouseIsInBBox = False

    #     mouseIsInBBox = self.isInBBox(event.mouse_x - region.x, event.mouse_y - region.y)

    #     # for debug, used to interupt for breakpoint:
    #     if mouseIsInBBox:
    #         if event.type == "G":
    #             print("Debug G key")

    #     # # highlight ##############
    #     # if event.type in ["MOUSEMOVE", "INBETWEEN_MOUSEMOVE"]:
    #     #     if mouseIsInBBox:
    #     #         if not self.isHighlighted:
    #     #             self.isHighlighted = True
    #     #             # _logger.debug_ext("component2D handle_events set highlighte true", col="PURPLE", tag="EVENT")
    #     #             config.gRedrawShotStack = True
    #     #     else:
    #     #         if self.isHighlighted:
    #     #             self.isHighlighted = False
    #     #             config.gRedrawShotStack = True

    #     # # selection ##############
    #     # if event.type == "LEFTMOUSE":
    #     #     if event.value == "PRESS":
    #     #         if mouseIsInBBox:
    #     #             if not self.isSelected:
    #     #                 self.isSelected = True
    #     #                 #_logger.debug_ext("component2D handle_events set selected true", col="PURPLE", tag="EVENT")
    #     #                 config.gRedrawShotStack = True

    #     #     if event.value == "RELEASE":

    #     return event_handled

    def handle_event(self, context, event):
        """handle event for InteractiveComponent operator"""
        # _logger.debug_ext(" component2D handle_events", col="PURPLE", tag="EVENT")

        event_handled = False
        region, area = self.get_region_at_xy(context, event.mouse_x, event.mouse_y, "DOPESHEET_EDITOR")

        # get only events in the target area
        # wkip: mouse release out of the region have to be taken into account

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

    # override of InteractiveComponent
    # override by inheriting classes if needed
    def _handle_event_custom(self, context, event, region):
        props = config.getAddonProps(context.scene)

        event_handled = False
        mouseIsInBBox = False

        mouseIsInBBox = self.isInBBox(event.mouse_x - region.x, event.mouse_y - region.y)

        # for debug, used to interupt for breakpoint:
        if mouseIsInBBox:
            if event.type == "H":
                print("Debug H key")

        if "PRESS" == event.value and event.type in ("RIGHTMOUSE", "ESC", "WINDOW_DEACTIVATE"):
            self.cancelAction(context)
            # event_handled = True

        # selection ##############
        if event.type == "LEFTMOUSE":
            if event.value == "PRESS":
                if mouseIsInBBox:
                    # selection ####################
                    if not self.isSelected:
                        self.isSelected = True
                    # _logger.debug_ext("component2D handle_events set selected true", col="PURPLE", tag="EVENT")
                    # self._on_selected_changed(context, event, self.isSelected)

                    # manipulation #################
                    self.isManipulated = True
                    # _logger.debug_ext("Start Clip manip", col="YELLOW", tag="EVENT")
                    # self._on_manipulated_changed(context, self.isManipulated)
                    self.mouseFrame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                    self.previousMouseFrame = self.mouseFrame

                    # double click #################
                    counter = time.perf_counter()
                    #   print(f"pref clic: {self.prev_click}")
                    if counter - self.prev_click < self.doubleClickDuration:
                        # props.setCurrentShotByIndex(uiShot.shot_index, changeTime=False)

                        self._on_doublecliked(context, event, region)

                    self.prev_click = counter

                    #  config.gRedrawShotStack = True
                    event_handled = True

            elif event.value == "RELEASE":
                #  bpy.ops.ed.undo_push(message=f"Change Shot...")
                if self.isManipulated:
                    self.cancelAction(context)
                    event_handled = True

        if event.type in ["MOUSEMOVE", "INBETWEEN_MOUSEMOVE"]:
            if self.isManipulated:

                # NOTE: wkipwkipwkip to fix: use more generic code (= no frames for mouse)
                mouse_frame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                prev_mouse_frame = int(region.view2d.region_to_view(self.prev_mouse_x, 0)[0])
                if mouse_frame != self.mouseFrame or prev_mouse_frame != self.previousMouseFrame:
                    self._on_manipulated_mouse_moved(context, event, mouse_delta_frames=mouse_frame - prev_mouse_frame)
                    self.mouseFrame = mouse_frame
                    self.previousMouseFrame = prev_mouse_frame

                # _logger.debug_ext(
                #     f"   mouse frame: {mouse_frame}, prev_mouse_frame: {prev_mouse_frame}",
                #     col="BLUE",
                #     tag="SHOTSTACK_EVENT",
                # )

                if self.isManipulated:
                    self.frame_under_mouse = mouse_frame
                event_handled = True

        self.prev_mouse_x = event.mouse_x - region.x
        self.prev_mouse_y = event.mouse_y - region.y

        return event_handled

    ######################################################################

    # event actions ##############
    # functions to override in classes inheriting from this class

    ######################################################################

    # to override by inheriting classes
    def validateAction(self, context):
        #  _logger.debug_ext("Validating interactive component action", col="GREEN", tag="SHOTSTACK_EVENT")
        self.isManipulated = False

    #  self._on_manipulated_changed(context, self.isManipulated)

    # to override by inheriting classes
    def cancelAction(self, context):
        # TODO restore the initial state
        #  _logger.debug_ext("Canceling interactive component action", col="ORANGE", tag="SHOTSTACK_EVENT")
        self.isManipulated = False

    #  self._on_manipulated_changed(context, self.isManipulated)

    # to override by inheriting classes
    def _on_highlighted_changed(self, context, event, isHighlighted):
        """isHighlighted has the same value than self.isHighlighted, which is set right before this
        function is called
        """
        if isHighlighted:
            # _logger.debug_ext("interactive handle_events set highlighte true", col="PURPLE", tag="EVENT"
            pass
        else:
            pass

    # to override by inheriting classes
    def _on_selected_changed(self, context, event, isSelected):
        """isSelected has the same value than self.isSelected, which is set right before this
        function is called
        """
        if isSelected:
            # _logger.debug_ext("component2D handle_events set selected true", col="PURPLE", tag="EVENT"
            pass
        else:
            pass

    # to override by inheriting classes
    def _on_manipulated_changed(self, context, event, isManipulated):
        """isManipulated has the same value than self.isManipulated, which is set right before this
        function is called
        """
        if isManipulated:
            # _logger.debug_ext("component2D handle_events set manipulated true", col="PURPLE", tag="EVENT"
            pass
        else:
            pass

    # to override by inheriting classes
    def _on_manipulated_mouse_moved(self, context, event, mouse_delta_frames=0):
        """wkip note: mouse_delta_frames is in frames but may need to be in pixels in some cases"""
        if mouse_delta_frames:
            # _logger.debug_ext("component2D handle_events set manipulated true", col="PURPLE", tag="EVENT"
            pass
        else:
            pass

    # to override by inheriting classes
    def _on_doublecliked(self, context, event, region):
        pass
