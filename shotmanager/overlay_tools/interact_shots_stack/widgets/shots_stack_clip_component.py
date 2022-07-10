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

import gpu

from shotmanager.gpu.gpu_2d.class_Component2D import Component2D
from shotmanager.gpu.gpu_2d.class_Text2D import Text2D

from shotmanager.utils.utils_python import clamp
from shotmanager.utils.utils_editors_dopesheet import getLaneHeight
from shotmanager.utils.utils import color_to_sRGB, lighten_color, set_color_alpha, alpha_to_linear

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class ShotClipComponent(Component2D):
    """Interactive shot component"""

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

        self.isCurrent = False
        self.shot = shot

        self.color = (0.5, 0.6, 0.6, 0.9)
        self.color_highlight = (0.6, 0.9, 0.6, 0.9)
        self.color_selected = (0.6, 0.9, 0.9, 0.9)
        self.color_selected_highlight = (0.6, 0.9, 0.9, 0.9)

        self.color_currentShot_border = (0.92, 0.55, 0.18, 0.99)
        self.color_currentShot_border_mix = (0.94, 0.3, 0.1, 0.99)
        self.color_selectedShot_border = (0.8, 0.8, 0.8, 0.99)

        self.color_disabled = (0.0, 0.0, 0.0, 1)

        self.color_text = (0.0, 0.0, 0.0, 1)
        self.color_text_disabled = (0.4, 0.4, 0.4, 1)

        self._name_color_light = (0.9, 0.9, 0.9, 1)
        self._name_color_dark = (0.07, 0.07, 0.07, 1)
        self._name_color_disabled = (0.8, 0.8, 0.8, 1)

        self.textComponent = Text2D(
            posXIsInRegionCS=True, posYIsInRegionCS=True, posY=0, alignment="MID_LEFT", parent=self
        )
        self.textComponent.hasShadow = False

    # override QuadObject
    def _getFillShader(self, shader):
        widColor = self.color
        opacity = self.opacity

        if self.isSelected:
            #  widColor = lighten_color(widColor, 0.2)
            widColor = self.color
            opacity = min(0.75, clamp(1.5 * opacity, 0, 1))
            if self.isHighlighted:
                widColor = lighten_color(widColor, 0.1)
                opacity = clamp(1.1 * opacity, 0, 1)

        elif self.isHighlighted:
            widColor = lighten_color(widColor, 0.1)
            opacity = clamp(1.4 * opacity, 0, 1)

        color = set_color_alpha(widColor, alpha_to_linear(widColor[3] * opacity))

        UNIFORM_SHADER_2D.bind()
        UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB(color))
        shader = UNIFORM_SHADER_2D

        return shader

    def _getLineShader(self, shader):
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

        # text ############
        self.textComponent.text = self.shot.name
        # vertically center the text + add a small offset to compensate the lower part of the font
        self.textComponent.posY = int(getLaneHeight() * (0.06 + 0.5))
        self.textComponent.fontSize = int(getLaneHeight() * 0.6)
        if self.isSelected:
            self.textComponent.bold = True
            self.textComponent.color = self.color_text
        else:
            self.textComponent.bold = False
            level = 0.1 if self.isHighlighted else 0.75
            self.textComponent.color = lighten_color(self.color_text, level)

        # automatic offset of the text when the start of the shot disappears on the left side
        self.textComponent.inheritPosFromParent = True
        self.textComponent.posX = 10
        self.textComponent.offsetText_leftSide = True

        # children such as the text2D are drawn in Component2D
        Component2D.draw(self, None, region, draw_types, cap_lines)
