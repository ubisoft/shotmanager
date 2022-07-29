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

from collections import defaultdict

import os
import time
from mathutils import Vector

import bpy
import bgl
import gpu

from shotmanager.overlay_tools.interact_shots_stack.widgets.shots_stack_clip_component import ShotClipComponent

from .shot_clip_widget import BL_UI_ShotClip
from ..shots_stack_bgl import get_lane_origin_y

from shotmanager.utils import utils_editors_dopesheet
from shotmanager.utils.utils import color_to_linear

from shotmanager.gpu.gpu_2d.class_Mesh2D import Mesh2D, build_rectangle_mesh
from shotmanager.gpu.gpu_2d.class_QuadObject import QuadObject
from shotmanager.gpu.gpu_2d.class_Component2D import Component2D
from shotmanager.gpu.gpu_2d.class_Text2D import Text2D

from shotmanager.overlay_tools.workspace_info import workspace_info

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class BL_UI_ShotStack:
    def __init__(self, target_area=None):
        prefs = bpy.context.preferences.addons["shotmanager"].preferences

        self.useDebugComponents = False
        self.use_shots_old_way = False

        self.context = None
        self.target_area = target_area

        self.ui_shots = list()
        self.shotComponents = []

        self.manipulated_clip = None
        self.manipulated_clip_handle = None

        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.frame_under_mouse = -1

        self.mouseFrame = -1
        self.previousMouseFrame = -1

        self.previousDrawWasInAClip = False

        self.debug_mesh = None
        self.debug_quadObject = None
        self.debug_quadObject_Ruler = None
        self.debug_quadObject_test = None

        self.color_currentShot_border = color_to_linear((0.92, 0.55, 0.18, 0.99))
        # self.color_currentShot_border = (1, 0, 0, 1)
        self.color_currentShot_border_mix = (0.94, 0.3, 0.1, 0.99)

        # prefs settings ###################
        self.opacity = prefs.shtStack_opacity
        self.color_text = (0.0, 0.0, 0.0, 1)

    def init(self, context):
        self.context = context

        self.rebuildShotComponents()

        self.currentShotBorder = QuadObject(
            posXIsInRegionCS=False,
            posYIsInRegionCS=False,
            widthIsInRegionCS=False,
            heightIsInRegionCS=False,
            alignment="BOTTOM_LEFT",
            alignmentToRegion="TOP_LEFT",
        )
        self.currentShotBorder.hasFill = False
        self.currentShotBorder.hasLine = True
        self.currentShotBorder.colorLine = self.color_currentShot_border_mix
        self.currentShotBorder.lineThickness = 2
        self.currentShotBorder.isVisible = False
        # self.currentShotBorder.lineOffsetPerEdge = [0, -1, -1, 0]

        # wip not super clean
        config.gRedrawShotStack = True
        config.gRedrawShotStack_preDrawOnly = True

        if self.useDebugComponents:
            ###############################################
            # debug
            ###############################################
            # height = 20
            # lane = 3
            # startframe = 120
            # numFrames = 15
            # origin = Vector([startframe, get_lane_origin_y(lane)])
            # self.debug_mesh = build_rectangle_mesh(origin, numFrames, height)

            # this quad is supposed to cover the time ruler all the time to check the top clipping zone
            # BOTTOM_LEFT TOP_LEFT
            self.debug_quadObject_Ruler = QuadObject(
                posXIsInRegionCS=True,
                posX=0,
                posYIsInRegionCS=True,
                posY=0,
                widthIsInRegionCS=True,
                width=1900,
                heightIsInRegionCS=True,
                height=utils_editors_dopesheet.getRulerHeight(),
                alignment="TOP_LEFT",
                alignmentToRegion="TOP_LEFT",
                displayOverRuler=True,
            )
            self.debug_quadObject_Ruler.color = (0.4, 0.0, 0.0, 0.5)

            self.debug_quadObject_test = QuadObject(
                posXIsInRegionCS=False,
                posX=20,
                posYIsInRegionCS=False,
                posY=1,
                widthIsInRegionCS=False,
                width=40,
                heightIsInRegionCS=False,
                height=10,
                alignment="TOP_LEFT",
                alignmentToRegion="TOP_LEFT",
            )
            self.debug_quadObject_test.color = (0.0, 0.4, 0.0, 0.5)
            imgFile = os.path.join(os.path.dirname(__file__), "../../../icons/ShotMan_EnabledCurrentCam.png")
            self.debug_quadObject_test.setImageFromFile(imgFile)
            self.debug_quadObject_test.hasTexture = True

            self.debug_quadObject = QuadObject(
                posXIsInRegionCS=True,
                posX=60,
                posYIsInRegionCS=True,
                posY=90,
                widthIsInRegionCS=False,
                width=25,
                heightIsInRegionCS=True,
                height=70,
                alignment="TOP_LEFT",
                alignmentToRegion="BOTTOM_RIGHT",
            )

            self.debug_component2D = Component2D(
                self.target_area,
                posXIsInRegionCS=False,
                posX=15,
                posYIsInRegionCS=False,
                posY=3,
                widthIsInRegionCS=False,
                width=20,
                heightIsInRegionCS=False,
                height=2,
                alignment="BOTTOM_LEFT",
                alignmentToRegion="BOTTOM_LEFT",
            )
            self.debug_component2D.color = (0.7, 0.5, 0.6, 0.6)
            self.debug_component2D.hasLine = True
            self.debug_component2D.colorLine = (0.7, 0.8, 0.8, 0.9)
            self.debug_component2D.lineThickness = 3

            self.debug_Text2D = Text2D(
                posXIsInRegionCS=False,
                posX=25,
                posYIsInRegionCS=False,
                posY=6,
                alignment="BOTTOM_LEFT",
                alignmentToRegion="BOTTOM_LEFT",
                text="MyText",
                fontSize=20,
            )

    def rebuildShotComponents(self, forceRebuild=False):
        props = self.context.scene.UAS_shot_manager_props
        shots = props.get_shots()
        # lenShots = len(shots)

        if not len(shots):
            self.shotComponents = []
            return

        rebuildList = forceRebuild or len(self.shotComponents) != len(shots)

        # check if the components list matches the shots list
        if not rebuildList:
            shotCompoInd = 0
            for _i, shot in enumerate(shots):
                if self.shotComponents[shotCompoInd].shot != shot:
                    rebuildList = True
                    break
                shotCompoInd += 1

        # rebuild the list with ALL the shots
        if rebuildList:
            self.shotComponents = []

            lane = 1
            for _i, shot in enumerate(shots):
                shotCompo = ShotClipComponent(self.target_area, posY=lane, shot=shot)
                shotCompo.opacity = self.opacity
                shotCompo.color_text = self.color_text

                self.shotComponents.append(shotCompo)
                lane += 1

    def drawCurrentShotDecoration(self, shotCompoCurrent, preDrawOnly=False):
        """Draw the quad lines for the current shot"""
        if shotCompoCurrent:
            self.currentShotBorder.posX = shotCompoCurrent.posX
            self.currentShotBorder.posY = shotCompoCurrent.posY
            self.currentShotBorder.width = shotCompoCurrent.width
            self.currentShotBorder.height = shotCompoCurrent.height
            self.currentShotBorder.isVisible = True
            self.currentShotBorder.draw(None, self.context.region, preDrawOnly=preDrawOnly)
        else:
            self.currentShotBorder.isVisible = False

    def drawShots(self, preDrawOnly=False):
        props = self.context.scene.UAS_shot_manager_props
        self.rebuildShotComponents()

        currentShotInd = props.getCurrentShotIndex()
        selectedShotInd = props.getSelectedShotIndex()

        debug_maxShots = 5000  # 6

        lane = 1
        shotCompoCurrent = None
        for i, shotCompo in enumerate(self.shotComponents):
            shotCompo.isCurrent = i == currentShotInd

            # NOTE: we use _isSelected instead of the property isSelected in order
            # to avoid the call of the callback function _on_selected_changed, otherwise
            # the event loops and keep redrawing all the time
            shotCompo._isSelected = i == selectedShotInd

            if debug_maxShots < i:
                shotCompo.isVisible = False
                continue
            if not shotCompo.shot.enabled and not props.interactShotsStack_displayDisabledShots:
                shotCompo.isVisible = False
                continue

            if i == currentShotInd:
                shotCompoCurrent = shotCompo
            shotCompo.isVisible = True
            shotCompo.posY = lane

            shotCompo.draw(None, self.context.region, preDrawOnly=preDrawOnly)
            lane += 1

        # draw quad for current shot over the result
        self.drawCurrentShotDecoration(shotCompoCurrent, preDrawOnly=preDrawOnly)

    def drawShots_compactMode(self, preDrawOnly=False):
        # return
        props = self.context.scene.UAS_shot_manager_props
        self.rebuildShotComponents()

        currentShot = props.getCurrentShot()
        selectedShot = props.getSelectedShot()

        shotComponentsSorted = sorted(self.shotComponents, key=lambda shotCompo: shotCompo.shot.start)

        shots_from_lane = defaultdict(list)

        for i, shotCompo in enumerate(shotComponentsSorted):
            if not props.interactShotsStack_displayDisabledShots and not shotCompo.shot.enabled:
                shotCompo.isVisible = False
                continue
            lane = 1
            if i > 0:
                for ln, shots_in_lane in shots_from_lane.items():
                    for s in shots_in_lane:
                        if s.start <= shotCompo.shot.start <= s.end:
                            break
                    else:
                        lane = ln
                        break
                else:
                    if len(shots_from_lane):
                        lane = max(shots_from_lane) + 1  # No free lane, make a new one.
                    else:
                        #   lane = ln
                        pass
            shots_from_lane[lane].append(shotCompo.shot)

            shotCompo.isCurrent = shotCompo.shot == currentShot

            # NOTE: we use _isSelected instead of the property isSelected in order
            # to avoid the call of the callback function _on_selected_changed, otherwise
            # the event loops and keep redrawing all the time
            shotCompo._isSelected = shotCompo.shot == selectedShot

            shotCompo.isVisible = True
            shotCompo.posY = lane
            shotCompo.draw(None, self.context.region, preDrawOnly=preDrawOnly)

    def draw_shots_old_way(self):
        props = self.context.scene.UAS_shot_manager_props
        shots = props.get_shots()
        ui_shots_previous = []

        def _getUIShotFromShotIndex(shot_index):
            """Return the instance of BL_UI_ShotClip in ui_shots_previous that uses the
            specified shot index or None if not found"""
            for s in ui_shots_previous:
                if shot_index == s.shot_index:
                    return s
            return None

        # create an array of tupples (ind, shot) to keep the association between the shot and its position
        shotTupples = []
        for i, shot in enumerate(shots):
            shotTupples.append((i, shot))

        ui_shots_previous = self.ui_shots.copy()
        self.ui_shots.clear()
        # print(f"num items in: self.ui_shots: {len(self.ui_shots)}, ui_shots_previous: {len(ui_shots_previous)}")

        if props.interactShotsStack_displayInCompactMode:
            shotTupplesSorted = sorted(
                shotTupples,
                key=lambda shotTupple: shotTupple[1].start,
            )
            #  print(f"Tupples sorted: {shotTupplesSorted}")
            shots_from_lane = defaultdict(list)

            for ind, shotTupple in enumerate(shotTupplesSorted):
                shot = shotTupple[1]
                if not props.interactShotsStack_displayDisabledShots and not shot.enabled:
                    continue
                lane = 0
                if ind > 0:
                    for ln, shots_in_lane in shots_from_lane.items():
                        for s in shots_in_lane:
                            if s.start <= shot.start <= s.end:
                                break
                        else:
                            lane = ln
                            break
                    else:
                        if len(shots_from_lane):
                            lane = max(shots_from_lane) + 1  # No free lane, make a new one.
                        else:
                            #  lane = ln
                            pass
                shots_from_lane[lane].append(shot)

                s = _getUIShotFromShotIndex(shotTupple[0])
                if s is None:
                    s = BL_UI_ShotClip(self.context, shotTupple[0])
                s.update(lane + 10)
                self.ui_shots.append(s)
                s.draw()
        else:
            shots = props.get_shots()
            lane = -1
            for i, shot in enumerate(shots):
                if not props.interactShotsStack_displayDisabledShots and not shot.enabled:
                    continue
                lane += 1

                s = _getUIShotFromShotIndex(i)
                if s is None:
                    s = BL_UI_ShotClip(self.context, i)
                # debug:
                s.update(lane + 10)
                # s.update(lane)

                self.ui_shots.append(s)
                s.draw()

    def draw(self, preDrawOnly=False):
        if self.target_area is not None and self.context.area != self.target_area:
            return

        props = self.context.scene.UAS_shot_manager_props

        # Debug - red rectangle ####################
        if self.useDebugComponents:
            height = 20
            lane = 5
            startframe = 160
            numFrames = 15
            origin = Vector([startframe, get_lane_origin_y(lane)])
            self.debug_mesh = build_rectangle_mesh(origin, numFrames, height)

            bgl.glEnable(bgl.GL_BLEND)
            UNIFORM_SHADER_2D.bind()
            color = (0.9, 0.0, 0.0, 0.9)
            UNIFORM_SHADER_2D.uniform_float("color", color)

            # self.debug_mesh.draw(UNIFORM_SHADER_2D, self.context.region)

            # Quad object
            ###############################

            # self.debug_quadObject_Ruler.draw(None, self.context.region)
            self.debug_quadObject_test.draw(None, self.context.region)
            # self.debug_quadObject.draw(None, self.context.region)
            self.debug_component2D.draw(None, self.context.region)
            self.debug_Text2D.draw(None, self.context.region)

            # draw text
            ###############################

            workspace_info.draw_callback__dopesheet_size(self, self.context, self.target_area)
            workspace_info.draw_callback__dopesheet_mouse_pos(self, self.context, self.target_area)
            workspace_info.draw_callback__dopesheet_lane_numbers(self, self.context, self.target_area)

            # return

        #  print("draw shot stack")
        if props.interactShotsStack_displayInCompactMode:
            self.drawShots_compactMode(preDrawOnly=preDrawOnly)
        else:
            self.drawShots(preDrawOnly=preDrawOnly)

        if self.use_shots_old_way:
            self.draw_shots_old_way()

    def validateAction(self):
        _logger.debug_ext("Validating Shot Stack action", col="GREEN", tag="SHOTSTACK_EVENT")
        if self.manipulated_clip:
            self.manipulated_clip.highlight = False
            self.manipulated_clip = None
            self.manipulated_clip_handle = None

    def cancelAction(self):
        # TODO restore the initial
        _logger.debug_ext("Canceling Shot Stack action 22", col="ORANGE", tag="SHOTSTACK_EVENT")
        if self.manipulated_clip:
            self.manipulated_clip.highlight = False
            self.manipulated_clip = None
            self.manipulated_clip_handle = None

    def handle_event(self, context, event, region):
        """Return True if the event is handled for BL_UI_ShotStack"""
        prefs = bpy.context.preferences.addons["shotmanager"].preferences

        # _logger.debug_ext("*** handle event for BL_UI_ShotStack", col="GREEN", tag="SHOTSTACK_EVENT")
        if not context.window_manager.UAS_shot_manager_toggle_shots_stack_interaction:
            return False

        event_handled = False
        # if event.type not in ["MOUSEMOVE", "INBETWEEN_MOUSEMOVE", "TIMER"]:
        #     _logger.debug_ext(f"  *** event in BL_UI_ShotStack: {event.type}", col="GREEN", tag="SHOTSTACK_EVENT")

        context = self.context
        props = context.scene.UAS_shot_manager_props

        mouse_x, mouse_y = region.view2d.region_to_view(event.mouse_x - region.x, event.mouse_y - region.y)

        currentDrawIsInAClip = False

        if event.type not in ["TIMER"]:
            _logger.debug_ext(f"event: type: {event.type}, value: {event.value}", col="GREEN", tag="SHOTSTACK_EVENT")

        for shotCompo in self.shotComponents:
            if not shotCompo.isVisible:
                continue
            event_handled = shotCompo.handle_event(context, event)
            if event_handled:
                break

        if self.use_shots_old_way:
            #  if True and not event_handled:
            if "PRESS" == event.value and event.type in ("RIGHTMOUSE", "ESC", "WINDOW_DEACTIVATE"):
                self.cancelAction()
                event_handled = True
            else:
                for uiShot in self.ui_shots:
                    # if uiShot.handle_event(context, event, region):
                    #     event_handled = True
                    #     break
                    manipulated_clip_handle = uiShot.get_clip_handle(mouse_x, mouse_y)
                    uiShot.mouseover = False

                    if manipulated_clip_handle is not None:

                        # mouse over #################
                        # NOTE: mouseover works but is not used (= desactivated in draw function) because it has to be associated
                        # with a redraw when no events are handle, which is hardware greedy (moreover reactive components are not
                        # in the philosophy of Blender)

                        # self.previousDrawWasInAClip = True
                        currentDrawIsInAClip = True
                        uiShot.mouseover = True
                        # event_handled = True
                        # config.gRedrawShotStack = True

                        if event.type == "LEFTMOUSE":
                            if event.value == "PRESS":
                                prefs.shot_selected_from_shots_stack__flag = True
                                props.setSelectedShotByIndex(uiShot.shot_index)
                                prefs.shot_selected_from_shots_stack__flag = False

                                # active clip ##################
                                self.manipulated_clip = uiShot
                                self.manipulated_clip_handle = manipulated_clip_handle
                                self.mouseFrame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                                self.previousMouseFrame = self.mouseFrame

                                # double click #################
                                counter = time.perf_counter()
                                print(f"pref clic: {uiShot.prev_click}")
                                if counter - uiShot.prev_click < 0.3:  # Double click.
                                    # props.setCurrentShotByIndex(uiShot.shot_index, changeTime=False)
                                    mouse_frame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                                    #   context.scene.frame_current = mouse_frame
                                    bpy.ops.uas_shot_manager.set_current_shot(
                                        index=uiShot.shot_index,
                                        calledFromShotStack=True,
                                        event_ctrl=event.ctrl,
                                        event_alt=event.alt,
                                        event_shift=event.shift,
                                    )

                                uiShot.prev_click = counter
                                event_handled = True

                            elif event.value == "RELEASE":
                                #  bpy.ops.ed.undo_push(message=f"Change Shot...")
                                # self.manipulated_clip = None
                                # self.manipulated_clip_handle = None
                                print("Tutu Release")
                                self.cancelAction()
                            # event_handled = False

                        elif event.type in ["MOUSEMOVE", "INBETWEEN_MOUSEMOVE"]:
                            #   _logger.debug_ext(f"In MouseMouve 01", col="RED", tag="SHOTSTACK_EVENT")
                            pass
                        #  uiShot.highlight = True

                        # #_mouseMove()
                        # if event.value == "PRESS":
                        #     #  _logger.debug_ext(f"   key pressed", col="BLUE", tag="SHOTSTACK_EVENT")
                        #     if self.manipulated_clip:
                        #         mouse_frame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                        #         prev_mouse_frame = int(region.view2d.region_to_view(self.prev_mouse_x, 0)[0])
                        #         self.manipulated_clip.handle_mouse_interaction(
                        #             self.manipulated_clip_handle, mouse_frame - prev_mouse_frame
                        #         )
                        #         # self.manipulated_clip.update()
                        #         if self.manipulated_clip_handle != 0:
                        #             self.frame_under_mouse = mouse_frame
                        #         event_handled = True
                        # elif event.value == "RELEASE":
                        #     #  _logger.debug_ext(f"   key released", col="BLUE", tag="SHOTSTACK_EVENT")
                        #     if self.manipulated_clip:
                        #         self.manipulated_clip.highlight = False
                        #         self.manipulated_clip = None
                        #         self.frame_under_mouse = None
                        #         event_handled = True

                    else:
                        # events out of the shot clips
                        if event.type == "LEFTMOUSE":
                            if event.value == "RELEASE":
                                #  bpy.ops.ed.undo_push(message=f"Change Shot...")
                                # uiShot.highlight = False
                                # self.manipulated_clip = None
                                # self.manipulated_clip_handle = None

                                # note that this is called probably too many times due to
                                # the fact that the event can occur on another component
                                # This can probably be cleaned
                                _logger.debug_ext("tata Release")
                                self.cancelAction()
                                event_handled = True

                        # if self.previousDrawWasInAClip:
                        #     config.gRedrawShotStack = True
                        #     if not event_handled:
                        #         self.previousDrawWasInAClip = False

                    if event.type in ["MOUSEMOVE", "INBETWEEN_MOUSEMOVE"]:
                        #  _logger.debug_ext(f"  In MouseMouve 02", col="PURPLE", tag="SHOTSTACK_EVENT")

                        #    uiShot.highlight = True
                        # _mouseMove()

                        if True or event.value == "PRESS":

                            #   _logger.debug_ext(f"     move key pressed", col="BLUE", tag="SHOTSTACK_EVENT")
                            if self.manipulated_clip:
                                # _logger.debug_ext(
                                #     f"         move key pressed on manipulated clip", col="BLUE", tag="SHOTSTACK_EVENT"
                                # )
                                self.manipulated_clip.highlight = True

                                mouse_frame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                                prev_mouse_frame = int(region.view2d.region_to_view(self.prev_mouse_x, 0)[0])
                                if mouse_frame != self.mouseFrame or prev_mouse_frame != self.previousMouseFrame:
                                    self.manipulated_clip.handle_mouse_interaction(
                                        self.manipulated_clip_handle, mouse_frame - prev_mouse_frame
                                    )
                                    self.mouseFrame = mouse_frame
                                    self.previousMouseFrame = prev_mouse_frame

                                # _logger.debug_ext(
                                #     f"   mouse frame: {mouse_frame}, prev_mouse_frame: {prev_mouse_frame}",
                                #     col="BLUE",
                                #     tag="SHOTSTACK_EVENT",
                                # )

                                # self.manipulated_clip.update()
                                if self.manipulated_clip_handle != 0:
                                    self.frame_under_mouse = mouse_frame
                                event_handled = True
                            # elif event.value == "RELEASE":
                            #     #  _logger.debug_ext(f"   key released", col="BLUE", tag="SHOTSTACK_EVENT")
                            #     if self.manipulated_clip:
                            #         self.manipulated_clip.highlight = False
                            #         self.manipulated_clip = None
                            #         self.frame_under_mouse = None
                            #         event_handled = True

                            else:
                                uiShot.highlight = False

                                # do a draw when the mouse leave a clip
                                if self.previousDrawWasInAClip and not currentDrawIsInAClip:
                                    _logger.debug_ext("   LEave clip", col="BLUE", tag="SHOTSTACK_EVENT")
                                    config.gRedrawShotStack = True
                                # self.previousDrawWasInAClip = False
                                self.previousDrawWasInAClip = currentDrawIsInAClip

                        #  uiShot.mouseover = False

        # debug
        if not event_handled:
            if self.useDebugComponents:
                event_handled = self.debug_component2D.handle_event(context, event)

        self.prev_mouse_x = event.mouse_x - region.x
        self.prev_mouse_y = event.mouse_y - region.y

        return event_handled
