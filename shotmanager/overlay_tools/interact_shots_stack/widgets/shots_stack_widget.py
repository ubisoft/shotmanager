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

import time

import bpy
import blf

import bgl
import gpu
from mathutils import Vector

from .shot_clip_widget import BL_UI_ShotClip
from ..shots_stack_bgl import build_rectangle_mesh, get_lane_origin_y

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class BL_UI_ShotStack:
    def __init__(self, target_area=None):
        self.context = None
        self.target_area = target_area

        self.ui_shots = list()

        self.manipulated_clip = None
        self.manipulated_clip_handle = None

        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.frame_under_mouse = -1

        self.mouseFrame = -1
        self.previousMouseFrame = -1

        self.previousDrawWasInAClip = False

        self.debug_mesh = None

    def init(self, context):
        self.context = context

        # debug
        # height = 20
        # lane = 3
        # startframe = 120
        # numFrames = 15
        # origin = Vector([startframe, get_lane_origin_y(lane)])
        # self.debug_mesh = build_rectangle_mesh(origin, numFrames, height)

    def draw_shots(self):
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
                            lane = ln
                            pass
                shots_from_lane[lane].append(shot)

                s = _getUIShotFromShotIndex(shotTupple[0])
                if s is None:
                    s = BL_UI_ShotClip(self.context, shotTupple[0])
                s.update(lane)
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
                s.update(lane)
                self.ui_shots.append(s)
                s.draw()

    def getRegionFrameRange(self, inViewUnits=True):
        """Return the region bottom left and top right of the target dopesheet area,
        with the x in frames and the y in something"""

        context = self.context

        c = context.copy()
        for i, area in enumerate(context.screen.areas):
            if area != self.target_area:
                continue
            region = area.regions[-1]
            # print("SCREEN:", context.screen.name, "[", i, "]")
            c["space_data"] = area.spaces.active
            c["area"] = area
            c["region"] = region

            # region size
            h = region.height  # screen
            w = region.width  #
            bl = region.view2d.region_to_view(0, 0)
            tr = region.view2d.region_to_view(w, h)
            # print(f"region bottom left: {(bl[0]):03.2f} fr, {(bl[1]):03.2f}")
            # print(f"region top right: {(tr[0]):03.2f} fr, {(tr[1]):03.2f}")

            range = Vector(tr) - Vector(bl)

            # return (Vector(bl), Vector(tr))
            if inViewUnits:
                return (bl[0], bl[1], tr[0], tr[1])
            else:
                return (0.0, 0.0, w, h)

        return None

    def drawClipHandle_Debug(self):
        

    def draw(self):
        if self.target_area is not None and self.context.area != self.target_area:
            return

        # Debug - red rectangle ####################
        drawDebugRect = True
        if drawDebugRect:
            print("ogl draw shot stack")

            # get_lane_origin_y
            # get_lane_height():

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

            self.debug_mesh.draw(UNIFORM_SHADER_2D, self.context.region)

            # draw text
            blf.color(0, 0.9, 0.9, 0.9, 0.9)

            # blf.size(0, round(self.font_size * get_prefs_ui_scale()), 72)
            blf.size(0, 12, 72)
            # textPos_y = self.origin.y + 6 * get_prefs_ui_scale()
            # textPos_y = self.origin.y + get_lane_height() * 0.2 * get_prefs_ui_scale()
            # blf.position(0, *context.region.view2d.view_to_region(self.origin.x + 1.4, textPos_y), 0)

            offset_y = 20
            # in view units
            areaBoxSize = self.getRegionFrameRange(inViewUnits=True)
            widthStr = f"Width range: {(areaBoxSize[0]):03.2f} fr, {(areaBoxSize[2]):03.2f} fr, width: {(areaBoxSize[2] - areaBoxSize[0]):03.2f} fr"
            heightStr = f"Height range: {(areaBoxSize[1]):03.2f} , {(areaBoxSize[3]):03.2f} , height: {(areaBoxSize[3] - areaBoxSize[1]):03.2f} fr"

            blf.position(0, 60, offset_y, 0)
            blf.draw(0, widthStr)
            blf.position(0, 60, offset_y * 2, 0)
            blf.draw(0, heightStr)

            # in screen units
            # This defines the dopesheet content region size in pixels (without the left panel listing the channels)
            # Bottom left is the origin, so at [0, 0]
            areaBoxSize = self.getRegionFrameRange(inViewUnits=False)
            widthStr = f"Width range: {(areaBoxSize[0]):03.2f} px, {(areaBoxSize[2]):03.2f} px"
            heightStr = f"Height range: {(areaBoxSize[1]):03.2f} px, {(areaBoxSize[3]):03.2f} px"

            blf.position(0, 60, offset_y * 3, 0)
            blf.draw(0, widthStr)
            blf.position(0, 60, offset_y * 4, 0)
            blf.draw(0, heightStr)

            # return

        #  print("draw shot stack")
        self.draw_shots()

    def validateAction(self):
        _logger.debug_ext(f"Validating Shot Stack action", col="GREEN", tag="SHOTSTACK_EVENT")
        if self.manipulated_clip:
            self.manipulated_clip.highlight = False
            self.manipulated_clip = None
            self.manipulated_clip_handle = None

    def cancelAction(self):
        # TODO restore the initial
        _logger.debug_ext(f"Canceling Shot Stack action", col="ORANGE", tag="SHOTSTACK_EVENT")
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

        match (event.type, event.value):
            # case ("RIGHTMOUSE", "PRESS") | ("ESC", "PRESS") | ("WINDOW_DEACTIVATE", "PRESS"):
            #     self.cancelAction()
            #     event_handled = True

            case _:

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
                                    context.scene.frame_current = mouse_frame
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
                                # print("Titi")
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
                                # print("tata")
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
                                    _logger.debug_ext(f"   LEave clip", col="BLUE", tag="SHOTSTACK_EVENT")
                                    config.gRedrawShotStack = True
                                # self.previousDrawWasInAClip = False
                                self.previousDrawWasInAClip = currentDrawIsInAClip

                        #  uiShot.mouseover = False

        self.prev_mouse_x = event.mouse_x - region.x
        self.prev_mouse_y = event.mouse_y - region.y

        return event_handled
