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
import bpy

from shotmanager.gpu.gpu_2d.class_Component2D import Component2D

from shotmanager.utils.utils_python import clamp
from shotmanager.utils.utils import color_to_sRGB, lighten_color, set_color_alpha, alpha_to_linear
from shotmanager.retimer.retimer import retimeScene

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class ShotHandleComponent(Component2D):
    """Handle for shot clip component"""

    def __init__(
        self,
        targetArea,
        posY=2,
        width=32,
        alignment="BOTTOM_LEFT",
        parent=None,
        shot=None,
        isStart=True,
        shotsStack=None,
    ):
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

        self.shotsStackWidget = shotsStack

        # shot ###################
        self.shot = shot
        self.zOrder = -1.0

        self.isStart = isStart
        self.color = self.shot.color

        # manipulation
        # filled when isManipulated changes
        self.manipulatedChildren = None
        self.manipulationBeginingFrame = None
        self.scalingShot = False

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

        # elif self.isSelected:
        #     #  widColor = lighten_color(widColor, 0.2)
        #     # widColor = self.color
        #     opacity = min(0.75, clamp(1.5 * opacity, 0, 1))
        #     if self.isHighlighted:
        #         widColor = lighten_color(widColor, 0.1)
        #         opacity = clamp(1.1 * opacity, 0, 1)

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
    def _on_highlighted_changed(self, context, event, isHighlighted):
        """isHighlighted has the same value than self.isHighlighted, which is set right before this
        function is called
        """
        if isHighlighted:
            # _logger.debug_ext("component2D handle_events set highlighte true", col="PURPLE", tag="EVENT"
            config.gRedrawShotStack = True
        else:
            config.gRedrawShotStack = True

    # override of InteractiveComponent
    def _on_selected_changed(self, context, event, isSelected):
        """isSelected has the same value than self.isSelected, which is set right before this
        function is called
        """
        # the notion of selection is not used for shot clip handles
        if isSelected:
            self.isSelected = False

    # override of InteractiveComponent
    def _on_manipulated_changed(self, context, event, isManipulated):
        """isManipulated has the same value than self.isManipulated, which is set right before this
        function is called
        """
        # we use this to set the color of the clip as for when manipulated

        if isManipulated:
            self.manipulatedChildren = None
            self.scalingShot = False
            self.shotsStackWidget.manipulatedComponent = self
            self.parent.isManipulatedByAnotherComponent = True
            self.manipulationBeginingFrame = context.scene.frame_current

            if self.shot.isStoryboardType():
                self.manipulatedChildren = self.shot.getStoryboardChildren()
                bpy.ops.ed.undo_push(message="Pre-Modify Storyboard Shot Clip Handle in the Interactive Shots Stack")
            else:
                if self.shot.isCameraValid():
                    self.manipulatedChildren = self.shot.getStoryboardChildren()
                    if self.manipulatedChildren is None:
                        self.manipulatedChildren = list()
                    self.manipulatedChildren.append(self.shot.camera)
                    bpy.ops.ed.undo_push(message="Pre-Modify Camera Shot Clip Handle in the Interactive Shots Stack")
        else:
            # snap keys to frames
            if self.scalingShot:
                retimerApplyToSettings = context.window_manager.UAS_shot_manager_shots_stack_retimerApplyTo

                if self.shot.isStoryboardType():
                    retimerApplyToSettings.initialize("STB_SHOT_CLIP")
                else:
                    retimerApplyToSettings.initialize("PVZ_SHOT_CLIP")

                start_incl = self.shot.start
                duration_incl = self.shot.end - start_incl + 1

                retimeScene(
                    context=context,
                    retimeMode="SNAP",
                    retimerApplyToSettings=retimerApplyToSettings,
                    objects=self.manipulatedChildren,
                    # start_incl=-10000,
                    # duration_incl=900000,
                    start_incl=start_incl,
                    duration_incl=duration_incl,
                    keysBeforeRangeMode="SNAP",
                    keysAfterRangeMode="SNAP",
                )

            self.manipulatedChildren = None
            self.manipulationBeginingFrame = None
            self.shotsStackWidget.manipulatedComponent = None
            self.parent.isManipulatedByAnotherComponent = False
            self.scalingShot = False
        #   bpy.ops.ed.undo_push(message="Modified Shot Clip Handle in the Interactive Shots Stack")

    # override of InteractiveComponent
    def _on_manipulated_mouse_moved(self, context, event, mouse_delta_frames=0):
        """wkip note: delta_frames is in frames but may need to be in pixels in some cases"""
        # !! we have to be sure we work on the selected shot !!!
        prevShotStart = self.shot.start
        prevShotEnd = self.shot.end

        if self.isStart:
            self.shot.start += mouse_delta_frames
            pivot = self.shot.end
            start_incl = prevShotStart
            end_incl = self.shot.end
            duration_incl = end_incl - start_incl + 1
        else:
            self.shot.end += mouse_delta_frames
            pivot = self.shot.start
            start_incl = self.shot.start
            end_incl = prevShotEnd
            duration_incl = end_incl - start_incl + 1

        # bpy.ops.uas_shot_manager.set_shot_start(newStart=self.start + mouse_delta_frames)

        prefs = config.getAddonPrefs()
        if prefs.shtStack_link_stb_clips_to_keys and self.manipulatedChildren is not None:

            retimerApplyToSettings = context.window_manager.UAS_shot_manager_shots_stack_retimerApplyTo

            scaleShotContent = False
            if self.shot.isStoryboardType():
                scaleShotContent = not event.ctrl and not event.alt and event.shift
                retimerApplyToSettings.initialize("STB_SHOT_CLIP")
            else:
                scaleShotContent = not event.ctrl and not event.alt and event.shift
                retimerApplyToSettings.initialize("PVZ_SHOT_CLIP")

            if scaleShotContent:
                # do NOT snap on frames during scaling transformation otherwhise frames will be lost because merged at the same time !
                self.scalingShot = True
                retimerApplyToSettings.snapKeysToFrames = False

                retimeFactor = (self.shot.end - self.shot.start) / (prevShotEnd - prevShotStart)
                retimeScene(
                    context=context,
                    retimeMode="RESCALE",
                    retimerApplyToSettings=retimerApplyToSettings,
                    objects=self.manipulatedChildren,
                    # start_incl=-10000,
                    # duration_incl=900000,
                    start_incl=start_incl,
                    duration_incl=duration_incl,
                    join_gap=True,
                    factor=retimeFactor,
                    pivot=pivot,
                    keysBeforeRangeMode="RESCALE",
                    keysAfterRangeMode="RESCALE",
                )
