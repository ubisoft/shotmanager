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


import os

import bpy
import gpu
import blf

from shotmanager.gpu.gpu_2d.class_QuadObject import QuadObject
from shotmanager.gpu.gpu_2d.class_Text2D import Text2D

# from shotmanager.gpu.gpu_2d.class_Component2D import Component2D


# from shotmanager.gpu.gpu_2d.gpu_2d import loadImageAsTexture

from shotmanager.utils import utils
from shotmanager.utils.utils_python import clamp
from shotmanager.utils.utils import color_to_sRGB, lighten_color, set_color_alpha, alpha_to_linear, color_to_linear


from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class InfoComponent(QuadObject):
    """Info component"""

    def __init__(self, shotsStack=None):
        QuadObject.__init__(
            self,
            posXIsInRegionCS=True,
            posX=10,
            posYIsInRegionCS=True,
            posY=18,
            widthIsInRegionCS=True,
            width=252,
            heightIsInRegionCS=True,
            height=35,
            alignment="BOTTOM_LEFT",
            alignmentToRegion="BOTTOM_LEFT",
        )

        self.shotsStackWidget = shotsStack

        self.useDebugComponents = True

        self.text = ""
        self.modifierKeyPressed = False
        self.ctrlAction = False
        self.altAction = False
        self.shiftAction = False
        self.show = True

        self.fontSize = 11

    def init(self, context):
        self.color = (0.4, 0.4, 0.4, 0.5)
        self.textTitleColor = (0.9, 0.9, 0.9, 0.94)
        self.textColor = (0.7, 0.7, 0.7, 0.9)
        self.keyModifierPressedColor = (0.9, 0.9, 0.0, 0.9)

        self.textLineTitle = Text2D(
            text="",
            fontSize=self.fontSize,
            parent=self,
        )
        self.textLineTitle.color = self.textTitleColor

        self.textLine01 = Text2D(
            text="",
            fontSize=self.fontSize,
            parent=self,
        )

        self.textLine02 = Text2D(
            text="",
            fontSize=self.fontSize,
            parent=self,
        )

        if self.useDebugComponents:
            self.debugInfosQuad = QuadObject(
                posXIsInRegionCS=True,
                posX=280,
                posYIsInRegionCS=True,
                posY=18,
                widthIsInRegionCS=True,
                width=260,
                heightIsInRegionCS=True,
                height=20,
                alignment="BOTTOM_LEFT",
                alignmentToRegion="BOTTOM_RIGHT",
            )
            self.debugInfosQuad.color = (0.6, 0.4, 0.4, 0.5)

            self.debugTextLine01 = Text2D(
                text="Debug infos",
                posX=5,
                posY=5,
                fontSize=self.fontSize,
                parent=self.debugInfosQuad,
            )

    #################################################################

    # def setText(self, text):
    #     if text != self.text:
    #         self.text = text
    #         self.updateDisplayedInfo()
    #         config.gRedrawShotStack = True

    # def setModifierKeyState(self, modifierKeyPressed):
    #     if modifierKeyPressed != self.modifierKeyPressed:
    #         self.modifierKeyPressed = modifierKeyPressed
    #         self.updateDisplayedInfo()
    #         config.gRedrawShotStack = True

    def updateFromEvent(self, event):
        # newCtrlAction = event.ctrl and not event.alt and not event.shift
        newAltAction = not event.ctrl and event.alt and not event.shift
        newShiftAction = not event.ctrl and not event.alt and event.shift

        if newAltAction != self.altAction or newShiftAction != self.shiftAction:
            self.altAction = newAltAction
            self.shiftAction = newShiftAction
            # self.updateDisplayedInfo()
            config.gRedrawShotStack = True

    def updateDisplayedInfo(self):
        props = config.getAddonProps(bpy.context.scene)
        selectedShot = props.getSelectedShot()
        manipulatedCompoType = type(self.shotsStackWidget.manipulatedComponent).__name__

        if selectedShot:
            self.show = True
            self.textLine01.color = self.textColor
            self.textLine02.color = self.textColor

            if "PREVIZ" == selectedShot.shotType:
                self.height = 50
                self.textLineTitle.text = "Camera Shot"
                self.textLine01.text = "+ Shift on Handles: Scale camera keys"
                self.textLine02.text = "+ Shift on clip: Move camera keys"

                if self.shiftAction:
                    if "ShotHandleComponent" == manipulatedCompoType:
                        self.textLine01.color = self.keyModifierPressedColor
                        self.textLine01.text = "Shift pressed: Scaling camera keys"
                    elif "ShotClipComponent" == manipulatedCompoType:
                        self.textLine02.color = self.keyModifierPressedColor
                        self.textLine02.text = "Shift pressed: Moving camera keys"
                    else:
                        self.textLine01.color = self.keyModifierPressedColor
                        self.textLine02.color = self.keyModifierPressedColor
            else:
                self.height = 50
                self.textLineTitle.text = "Storyboard Shot"
                self.textLine01.text = "+ Shift on Handles: Scale storyboard frame keys"
                self.textLine02.text = "+ Alt: Sleep shot range only"

                if self.shiftAction:
                    self.textLine01.color = self.keyModifierPressedColor
                    if "ShotHandleComponent" == manipulatedCompoType:
                        self.textLine01.text = "Shift pressed: Scaling storyboard frame keys"

                if self.altAction:
                    self.textLine02.color = self.keyModifierPressedColor
                    if "ShotClipComponent" == manipulatedCompoType:
                        self.textLine02.text = "Alt pressed: Sleeping shot range only"

        else:
            # self.textLineTitle.text = "-"
            self.show = False

    #################################################################

    # drawing ##########

    #################################################################

    # override QuadObject
    def draw(self, shader=None, region=None, draw_types="TRIS", cap_lines=False, preDrawOnly=False):
        prefs = config.getAddonPrefs()
        if not prefs.shtStack_display_info_widget:
            return

        leftOffset = 6

        self.updateDisplayedInfo()
        vOffset = self.height - self.textLine01.fontSize - 2

        self.textLineTitle.posX = leftOffset
        self.textLineTitle.posY = vOffset

        vOffset -= 15
        self.textLine01.posX = leftOffset
        self.textLine01.posY = vOffset

        vOffset -= 15
        self.textLine02.posX = leftOffset
        self.textLine02.posY = vOffset

        # self.draw_infos(region)

        # def draw_infos(self, region):
        #     blf.color(0, 0.9, 0.9, 0.9, 0.9)
        #     blf.size(0, 12, 72)
        #     offset_y = 80

        #     txtStr = f"Mouse pos: Screen: x: "

        #     blf.position(0, 60, offset_y, 0)
        #     blf.draw(0, txtStr)

        if self.useDebugComponents:
            self.debugTextLine01.text = f"Manip Compo: {type(self.shotsStackWidget.manipulatedComponent).__name__}"

            self.debugInfosQuad.draw(None, region)

        if self.show:
            # children such as the text2D are drawn in QuadObject
            QuadObject.draw(self, None, region)
