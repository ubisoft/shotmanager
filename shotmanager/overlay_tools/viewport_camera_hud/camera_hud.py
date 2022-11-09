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
Camera HUD
"""

import bpy

from .camera_hud_bgl import draw_shots_names, draw_all_shots_names, drawShotName, view3d_camera_border, drawCameraPlane

from shotmanager.config import config


class UAS_ShotManager_DrawCameras_UI(bpy.types.Operator):
    bl_idname = "uas_shot_manager.draw_camera_hud_in_viewports"
    bl_label = "ShotManager_DrawCameras_UI"
    bl_description = "ShotManager_DrawCameras_UI."
    bl_options = {"REGISTER", "INTERNAL"}

    def __init__(self):
        self.draw_handle = None
        self.draw_event = None

    def invoke(self, context, event):
        self.register_handlers(context)

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def register_handlers(self, context):
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw, (context,), "WINDOW", "POST_PIXEL")
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)

    def unregister_handlers(self, context):
        context.window_manager.event_timer_remove(self.draw_event)
        self.draw_event = None
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")
        self.draw_handle = None

    def modal(self, context, event):
        if not context.scene.UAS_shot_manager_props.camera_hud_display_in_viewports:
            # if not context.window_manager.UAS_shot_manager_display_overlay_tools:
            self.unregister_handlers(context)
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def cancel(self, context):
        self.unregister_handlers(context)

    def draw(self, context):
        if not hasattr(context.scene, "UAS_shot_manager_props"):
            print("Error in UAS_ShotManager_DrawHudinViewport draw: no UAS_shot_manager_props defined")
            return

        if bpy.context.space_data.overlay.show_overlays:
            draw_shots_names(context)
        #     drawCameraPlane(context, camera=context.scene.camera)
        # drawCameraPlane(context)
        # try:
        #     if bpy.context.space_data.overlay.show_overlays:
        #         draw_shots_names(context)
        # except Exception as e:
        #     print(f"Paf in draw camera hud in viewport: {e}")
        #     pass


class UAS_ShotManager_DrawHudOnCamPov(bpy.types.Operator):
    bl_idname = "uas_shot_manager.draw_camera_hud_in_pov"
    bl_label = "Shot Manager Draw HUD on Camera POV."
    bl_description = "Draw the shot manager camera hud when the current point of view is a camera"
    bl_options = {"REGISTER", "INTERNAL"}

    def __init__(self):
        self.draw_handle = None
        self.draw_event = None

    def invoke(self, context, event):
        self.register_handlers(context)

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def register_handlers(self, context):
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw, (context,), "WINDOW", "POST_PIXEL")
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)

    def unregister_handlers(self, context):
        context.window_manager.event_timer_remove(self.draw_event)
        self.draw_event = None
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")
        self.draw_handle = None

    def modal(self, context, event):
        if not context.scene.UAS_shot_manager_props.camera_hud_display_in_pov:
            # if not context.window_manager.UAS_shot_manager_display_overlay_tools:
            self.unregister_handlers(context)
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def cancel(self, context):
        self.unregister_handlers(context)

    def draw(self, context):
        if not hasattr(context.scene, "UAS_shot_manager_props"):
            print("Error in UAS_ShotManager_DrawHudOnCamPov draw: no UAS_shot_manager_props defined")
            return

        props = config.getAddonProps(context.scene)
        current_shot = props.getCurrentShot()
        cam = context.scene.camera
        if (
            current_shot is None
            or context.space_data.region_3d.view_perspective != "CAMERA"
            or context.scene.camera is None
            or "CAMERA" != context.scene.camera.type
            or cam is None
            or cam.name not in context.scene.objects
        ):
            return

        line_separation = 3
        u_r_corner, d_r_corner, d_l_corner, u_l_corner = view3d_camera_border(context)
        line_position = u_l_corner
        line_position.x += 3

        draw_all_shots_names(context, cam, line_position.x, line_position.y + 5, vertical=False)
        pass


_classes = (
    UAS_ShotManager_DrawCameras_UI,
    UAS_ShotManager_DrawHudOnCamPov,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    # print(f" *** Unregister Cam HUD *** ")
    # try:
    #     bpy.ops.uas_shot_manager.draw_camera_hud_in_viewports.unregister_handlers(context)
    # except exeption as e:
    #     print(f" *** paf in Unregister Cam HUD *** ")

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
