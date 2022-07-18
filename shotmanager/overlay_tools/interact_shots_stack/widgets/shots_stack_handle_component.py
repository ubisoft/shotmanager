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

from shotmanager.utils.utils_python import clamp
from shotmanager.utils.utils import color_to_sRGB, lighten_color, set_color_alpha, alpha_to_linear

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class ShotHandleComponent(Component2D):
    """Handle for shot clip component"""

    def __init__(self, targetArea, posY=2, width=32, alignment="BOTTOM_LEFT", parent=None, shot=None, isStart=True):
        Component2D.__init__(
            self,
            targetArea,
            posXIsInRegionCS=True,
            posX=0,
            posYIsInRegionCS=True,
            posY=posY,
            widthIsInRegionCS=True,
            width=width,
            heightIsInRegionCS=True,
            height=1,
            alignment=alignment,
            alignmentToRegion="BOTTOM_LEFT",
            parent=parent,
        )

        # shot ###################
        self.shot = shot
        self.zOrder = -1.0

        self.isStart = isStart

        self.color = self.shot.color

        # green or orange
        self.color_highlight = (0.2, 0.7, 0.2, 1) if self.isStart else (0.7, 0.3, 0.0, 1)
        self.color_highlight_durationLocked = (0.14, 0.28, 0.99, 1)
        self.color_selected = (0.6, 0.9, 0.9, 0.9)
        self.color_selected_highlight = (0.6, 0.9, 0.9, 0.9)

    #################################################################
    # functions ########
    #################################################################

    # override QuadObject
    def _getFillShader(self):
        self.color = self.parent.color

        widColor = self.color
        opacity = self.opacity

        if self.isManipulated:
            widColor = self.color_highlight_durationLocked if self.shot.durationLocked else self.color_highlight
            opacity = clamp(1.6 * opacity, 0, 1)

        elif self.isSelected:
            #  widColor = lighten_color(widColor, 0.2)
            # widColor = self.color
            opacity = min(0.75, clamp(1.5 * opacity, 0, 1))
            if self.isHighlighted:
                widColor = lighten_color(widColor, 0.1)
                opacity = clamp(1.1 * opacity, 0, 1)

        elif self.isHighlighted:
            # widColor = lighten_color(widColor, 0.1)
            widColor = self.color_highlight_durationLocked if self.shot.durationLocked else self.color_highlight
            opacity = clamp(1.2 * opacity, 0, 1)

        color = set_color_alpha(widColor, alpha_to_linear(widColor[3] * opacity))

        UNIFORM_SHADER_2D.bind()
        UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB(color))
        shader = UNIFORM_SHADER_2D

        return shader

    # override Component2D
    def draw(self, shader=None, region=None, draw_types="TRIS", cap_lines=False, preDrawOnly=False):

        # NOTE: Don't use getLaneHeight() here because it will create artefacts dues to conversion
        # from float to int according to the lane on which is the item
        # handleHeight = getLaneHeight()        # NO!
        handleHeight = self.parent.getHeightInRegion(clamped=False)
        self.height = handleHeight
        # self.width = int(handleHeight * 0.5)

        self.posX = 0 if self.isStart else self.parent.getWidthInRegion(clamped=False)

        # children such as the text2D are drawn in Component2D
        Component2D.draw(self, None, region, draw_types, cap_lines, preDrawOnly=preDrawOnly)

    #################################################################

    # event actions ##############

    #################################################################

    # override of InteractiveComponent
    def _on_highlighted_changed(self, context, isHighlighted):
        """isHighlighted has the same value than self.isHighlighted, which is set right before this
        function is called
        """
        if isHighlighted:
            # _logger.debug_ext("component2D handle_events set highlighte true", col="PURPLE", tag="EVENT"
            config.gRedrawShotStack = True
        else:
            config.gRedrawShotStack = True

    # override of InteractiveComponent
    def _on_manipulated_mouse_moved(self, context, mouse_delta_frames=0):
        """wkip note: delta_frames is in frames but may need to be in pixels in some cases"""
        # !! we have to be sure we work on the selected shot !!!
        if self.isStart:
            self.shot.start += mouse_delta_frames
            # bpy.ops.uas_shot_manager.set_shot_start(newStart=self.start + mouse_delta_frames)
        else:
            self.shot.end += mouse_delta_frames
