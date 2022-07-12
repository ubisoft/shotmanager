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


import time
import os

import bpy
import gpu

from shotmanager.gpu.gpu_2d.class_Component2D import Component2D
from shotmanager.gpu.gpu_2d.class_Text2D import Text2D
from shotmanager.gpu.gpu_2d.class_QuadObject import QuadObject

from .shots_stack_handle_component import ShotHandleComponent

# from shotmanager.gpu.gpu_2d.gpu_2d import loadImageAsTexture

from shotmanager.utils import utils
from shotmanager.utils.utils_python import clamp
from shotmanager.utils.utils_editors_dopesheet import getLaneHeight
from shotmanager.utils.utils import color_to_sRGB, lighten_color, set_color_alpha, alpha_to_linear, color_to_linear

# from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class ShotClipComponent(Component2D):
    """Shot clip component"""

    def __init__(self, targetArea, posY=2, shot=None):
        Component2D.__init__(
            self,
            targetArea,
            posXIsInRegionCS=False,
            posX=10,
            posYIsInRegionCS=False,
            posY=posY,
            widthIsInRegionCS=False,
            width=10,
            heightIsInRegionCS=False,
            height=1,
            alignment="BOTTOM_LEFT",
            alignmentToRegion="TOP_LEFT",
        )

        # preferences ############
        self.pref_handleWidth = int(getLaneHeight() * 0.5)
        self.pref_distanceFromParentOrigin = self.pref_handleWidth * 1.5
        self.pref_distanceFromRegionLeft = self.pref_handleWidth * 0.9
        self.pref_avoidClamp_spacePreservedOnRight = self.pref_distanceFromParentOrigin
        self.pref_currentShotImage_width = 20

        # shot ###################
        self.shot = shot
        self.isCurrent = False

        self.color = (0.5, 0.6, 0.6, 0.9)
        self.color_highlight = (0.6, 0.9, 0.6, 0.9)
        self.color_selected = (0.6, 0.9, 0.9, 0.9)
        self.color_selected_highlight = (0.6, 0.9, 0.9, 0.9)

        self.color_currentShot_border = (0.92, 0.55, 0.18, 0.99)
        self.color_currentShot_border_mix = (0.94, 0.3, 0.1, 0.99)
        self.color_selectedShot_border = (0.8, 0.8, 0.8, 0.99)

        self.color_manipulated = color_to_linear((0.6, 0.7, 0.95, 0.9))

        self.color_disabled = (0.0, 0.0, 0.0, 1)

        self._name_color_light = (0.9, 0.9, 0.9, 1)
        self._name_color_dark = (0.07, 0.07, 0.07, 1)
        self._name_color_disabled = (0.8, 0.8, 0.8, 1)

        # text component #########
        self.textComponent = Text2D(
            posXIsInRegionCS=True, posYIsInRegionCS=True, posY=0, alignment="MID_LEFT", parent=self
        )
        self.textComponent.hasShadow = True
        self.textComponent.avoidClamp_leftSide = True
        self.textComponent.avoidClamp_spacePreservedOnRight = self.pref_avoidClamp_spacePreservedOnRight

        self.color_text = (0.1, 0.1, 0.1, 1)
        self.color_text_selected = (0.0, 0.0, 0.0, 1)
        self.color_text_disabled = (0.4, 0.4, 0.4, 1)

        # image component ########
        imgPath = os.path.join(os.path.dirname(__file__), "../../../icons/")
        self.imageCam = utils.getDataImageFromPath(imgPath, "ShotManager_ShotsStack_Orange.png")
        self.imageCamSelected = utils.getDataImageFromPath(imgPath, "ShotManager_ShotsStack_Orange.png")

        self.currentShotImage = QuadObject(
            posXIsInRegionCS=True,
            posX=self.pref_distanceFromParentOrigin - 0.1 * self.pref_currentShotImage_width,
            posYIsInRegionCS=True,
            posY=0,
            widthIsInRegionCS=True,
            width=self.pref_currentShotImage_width,
            heightIsInRegionCS=True,
            height=self.pref_currentShotImage_width,
            alignment="MID_LEFT",
            #  alignmentToRegion="TOP_LEFT",
            parent=self,
        )
        # self.currentShotImage.color = (0.0, 0.4, 0.0, 0.5)
        self.currentShotImage.hasFill = False
        self.currentShotImage.hasTexture = True
        self.currentShotImage.avoidClamp_leftSide = True
        self.currentShotImage.avoidClamp_leftSideOffset = (
            self.pref_distanceFromRegionLeft - 0.1 * self.pref_currentShotImage_width
        )
        self.currentShotImage.avoidClamp_spacePreservedOnRight = self.pref_avoidClamp_spacePreservedOnRight

        # start handle component ######
        self.handleStart = ShotHandleComponent(
            targetArea,
            posY=0,
            width=self.pref_handleWidth,
            alignment="BOTTOM_LEFT",
            parent=self,
            shot=self.shot,
            isStart=True,
        )

        # end handle component ########
        self.handleEnd = ShotHandleComponent(
            targetArea,
            posY=0,
            width=self.pref_handleWidth,
            alignment="BOTTOM_RIGHT",
            parent=self,
            shot=self.shot,
            isStart=False,
        )

    #################################################################
    # functions ########
    #################################################################

    # override QuadObject
    def _getFillShader(self):
        widColor = self.color
        opacity = self.opacity

        if self.isManipulated:
            widColor = self.color_manipulated
            opacity = clamp(1.6 * opacity, 0, 1)

        elif self.isSelected:
            #  widColor = lighten_color(widColor, 0.2)
            # widColor = self.color
            opacity = min(0.75, clamp(1.5 * opacity, 0, 1))
            if self.isHighlighted:
                widColor = lighten_color(widColor, 0.1)
                opacity = clamp(1.1 * opacity, 0, 1)

        elif self.isHighlighted:
            widColor = lighten_color(widColor, 0.1)
            opacity = clamp(1.2 * opacity, 0, 1)

        color = set_color_alpha(widColor, alpha_to_linear(widColor[3] * opacity))

        UNIFORM_SHADER_2D.bind()
        UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB(color))
        shader = UNIFORM_SHADER_2D

        return shader

    # override QuadObject
    def _getLineShader(self):
        widColor = self.color
        opacity = min(0.7, clamp(1.4 * self.opacity, 0, 1))
        # opacity = 1

        # if self.isCurrent:
        #     widColor = self.color_currentShot_border
        #     if self.isSelected:
        #         widColor = self.color_currentShot_border_mix
        if self.isSelected:
            widColor = self.color_selectedShot_border
            opacity = 0.99
        # widColor = lighten_color(widColor, 0.1)

        color = set_color_alpha(widColor, alpha_to_linear(widColor[3] * opacity))

        UNIFORM_SHADER_2D.bind()
        UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB(color))
        shader = UNIFORM_SHADER_2D

        return shader

    # override Component2D
    def draw(self, shader=None, region=None, draw_types="TRIS", cap_lines=False):

        # wkip put all that in the FillShader fct?
        if self.shot.enabled:
            self.color = self.shot.color
            self.textComponent.color = self.color_text
        else:
            self.color = self.color_disabled
            self.textComponent.color = self.color_text_disabled

        # update clip from shot ########
        self.posX = self.shot.start
        self.width = self.shot.getDuration()
        if self.isCurrent:
            self.hasLine = True
            self.lineThickness = 1
            if self.isSelected:
                self.lineThickness = 3
        elif self.isSelected:
            self.hasLine = True
            self.lineThickness = 2
        else:
            self.hasLine = False

        # text ########################
        self.textComponent.text = self.shot.name
        # vertically center the text + add a small offset to compensate the lower part of the font
        # self.textComponent.posY = int(getLaneHeight() * (0.06 + 0.5))
        self.textComponent.posY = int(getLaneHeight() * (0.00 + 0.5))
        self.textComponent.fontSize = 13
        # self.textComponent.fontSize = int(getLaneHeight() * 0.6)
        if self.isSelected:
            self.textComponent.bold = True
            self.textComponent.color = self.color_text_selected
        else:
            self.textComponent.bold = False
            # level = 0.95 if self.isHighlighted else 0.8
            # self.textComponent.color = lighten_color(self.color_text, level)
            self.textComponent.color = self.color_text

        # automatic offset of the text when the start of the shot disappears on the left side
        self.textComponent.posX = self.pref_distanceFromParentOrigin
        self.textComponent.avoidClamp_leftSideOffset = self.pref_distanceFromRegionLeft

        # current shot image ##########
        imgHeight = int(getLaneHeight() * 0.85)
        self.currentShotImage.height = imgHeight
        self.currentShotImage.width = imgHeight

        if self.isCurrent:
            offsetFromImage = 5
            self.currentShotImage.isVisible = True
            self.currentShotImage.posY = int(getLaneHeight() * (0.06 + 0.5))
            self.textComponent.posX = (
                self.currentShotImage.getWidthInRegion() + self.pref_distanceFromParentOrigin + offsetFromImage
            )
            self.textComponent.avoidClamp_leftSideOffset = (
                self.pref_distanceFromRegionLeft + self.currentShotImage.getWidthInRegion() + offsetFromImage
            )
            if self.isSelected:
                self.currentShotImage.image = self.imageCam
            else:
                self.currentShotImage.image = self.imageCamSelected
        else:
            self.currentShotImage.isVisible = False

        # hide components when clip is too small
        clipWidth = self.getWidthInRegion(clamped=False)

        if clipWidth <= 2 * self.pref_handleWidth + 8:
            self.handleStart.isVisible = False
            self.handleEnd.isVisible = False
        else:
            self.handleStart.isVisible = True
            self.handleEnd.isVisible = True

        clipInnerWidth = clipWidth - 2 * self.pref_distanceFromParentOrigin

        if self.isCurrent:
            # ideal solution but for some reason text is not restored correctly:
            if clipInnerWidth < self.textComponent.getWidthInRegion(
                clamped=False
            ) + self.currentShotImage.getWidthInRegion(clamped=False):
                self.textComponent.isVisible = False
            else:
                self.textComponent.isVisible = True

            if clipInnerWidth < self.currentShotImage.getWidthInRegion(clamped=False):
                self.currentShotImage.isVisible = False
            else:
                self.currentShotImage.isVisible = True

        else:
            # ideal solution but for some reason text is not restored correctly:
            if clipInnerWidth < self.textComponent.getWidthInRegion(clamped=False):
                self.textComponent.isVisible = False
            else:
                self.textComponent.isVisible = True

        # fixed solution (not working either...):
        # if self.textComponent.isVisible:
        #     if clipInnerWidth < self.textComponent.getWidthInRegion(clamped=False):
        #         self.textComponent.isVisible = False
        # else:
        #     self.textComponent.isVisible = True
        #     if clipInnerWidth + self.pref_distanceFromParentOrigin < self.textComponent.getWidthInRegion(clamped=False):
        #         self.textComponent.isVisible = False

        # handles #####################
        # -

        # children such as the text2D are drawn in Component2D
        Component2D.draw(self, None, region, draw_types, cap_lines)

    ######################################################################

    # events ################

    ######################################################################

    def handle_mouse_interaction(self, handle, mouse_disp):
        """
        handle: if handle == -1:    left clip handle (start)
                if handle == 0:     clip (start and end)
                if handle == 1:     right clip handle (end)
        """
        # from shotmanager.properties.shot import UAS_ShotManager_Shot

        #  bpy.ops.ed.undo_push(message=f"Set Shot Start...")

        shot = self.shot
        # !! we have to be sure we work on the selected shot !!!
        if handle == 1:
            shot.end += mouse_disp
        elif handle == -1:
            shot.start += mouse_disp
            # bpy.ops.uas_shot_manager.set_shot_start(newStart=self.start + mouse_disp)
        else:
            # Very important, don't use properties for changing both start and ends. Depending of the amount of displacement duration can change.
            if shot.durationLocked:
                if mouse_disp > 0:
                    shot.end += mouse_disp
                # shot.start += mouse_disp
                else:
                    shot.start += mouse_disp
                # shot.end += mouse_disp
            else:
                if mouse_disp > 0:
                    shot.end += mouse_disp
                    shot.start += mouse_disp
                else:
                    shot.start += mouse_disp
                    shot.end += mouse_disp

    def validateAction(self):
        _logger.debug_ext("Validating Shot Clip action", col="GREEN", tag="SHOTSTACK_EVENT")
        self.isManipulated = False

    def cancelAction(self):
        # TODO restore the initial
        _logger.debug_ext("Canceling Shot Clip action", col="ORANGE", tag="SHOTSTACK_EVENT")
        self.isManipulated = False

    # override of InteractiveComponent
    def _handle_event_custom(self, context, event, region):
        props = context.scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences

        event_handled = False
        mouseIsInBBox = False

        mouseIsInBBox = self.isInBBox(event.mouse_x - region.x, event.mouse_y - region.y)

        # for debug, used to interupt for breakpoint:
        if mouseIsInBBox:
            if event.type == "H":
                print("Debug H key")

        if "PRESS" == event.value and event.type in ("RIGHTMOUSE", "ESC", "WINDOW_DEACTIVATE"):
            self.cancelAction()
            # event_handled = True

        # selection ##############
        if event.type == "LEFTMOUSE":
            if event.value == "PRESS":
                if mouseIsInBBox:
                    # selection ####################
                    if not self.isSelected:
                        self.isSelected = True
                    # _logger.debug_ext("component2D handle_events set selected true", col="PURPLE", tag="EVENT")
                    prefs.shot_selected_from_shots_stack__flag = True
                    props.setSelectedShot(self.shot)
                    prefs.shot_selected_from_shots_stack__flag = False

                    # manipulation #################
                    self.isManipulated = True
                    _logger.debug_ext(f"Start Clip manip", col="YELLOW", tag="EVENT")
                    self.mouseFrame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                    self.previousMouseFrame = self.mouseFrame

                    # double click #################
                    counter = time.perf_counter()
                    #   print(f"pref clic: {self.prev_click}")
                    if counter - self.prev_click < 0.3:  # Double click.
                        # props.setCurrentShotByIndex(uiShot.shot_index, changeTime=False)
                        mouse_frame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                        context.scene.frame_current = mouse_frame
                        bpy.ops.uas_shot_manager.set_current_shot(
                            index=props.getShotIndex(self.shot),
                            calledFromShotStack=True,
                            event_ctrl=event.ctrl,
                            event_alt=event.alt,
                            event_shift=event.shift,
                        )

                    self.prev_click = counter

                    #  config.gRedrawShotStack = True
                    event_handled = True

            elif event.value == "RELEASE":
                #  bpy.ops.ed.undo_push(message=f"Change Shot...")
                # self.manipulated_clip = None
                # self.manipulated_clip_handle = None
                # print("Titi")
                if self.isManipulated:
                    self.cancelAction()
                    event_handled = True

        if event.type in ["MOUSEMOVE", "INBETWEEN_MOUSEMOVE"]:
            if self.isManipulated:

                mouse_frame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                prev_mouse_frame = int(region.view2d.region_to_view(self.prev_mouse_x, 0)[0])
                if mouse_frame != self.mouseFrame or prev_mouse_frame != self.previousMouseFrame:
                    self.handle_mouse_interaction(0, mouse_frame - prev_mouse_frame)
                    self.mouseFrame = mouse_frame
                    self.previousMouseFrame = prev_mouse_frame

                # _logger.debug_ext(
                #     f"   mouse frame: {mouse_frame}, prev_mouse_frame: {prev_mouse_frame}",
                #     col="BLUE",
                #     tag="SHOTSTACK_EVENT",
                # )

                # self.manipulated_clip.update()

                # if self.manipulated_clip_handle != 0:
                #     self.frame_under_mouse = mouse_frame
                if self.isManipulated:
                    self.frame_under_mouse = mouse_frame
                event_handled = True

        self.prev_mouse_x = event.mouse_x - region.x
        self.prev_mouse_y = event.mouse_y - region.y

        return event_handled
