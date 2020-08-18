from collections import defaultdict
from statistics import mean

import gpu
import bgl, blf
import bpy
from gpu_extras.batch import batch_for_shader
import bpy_extras.view3d_utils as view3d_utils
import mathutils

from .ogl_ui import Square

font_info = {"font_id": 0, "handler": None}


class UAS_ShotManager_DrawCameras_UI(bpy.types.Operator):
    bl_idname = "uas_shot_manager.draw_cameras_ui"
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
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_camera_ui, (context,), "WINDOW", "POST_PIXEL"
        )
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)

    def unregister_handlers(self, context):
        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")

        self.draw_handle = None
        self.draw_event = None

    def modal(self, context, event):
        if not context.scene.UAS_shot_manager_props.display_shotname_in_3dviewport:
            # if not context.window_manager.UAS_shot_manager_display_timeline:
            self.unregister_handlers(context)
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def cancel(self, context):
        self.unregister_handlers(context)

    def draw_camera_ui(self, context):
        self.draw_shots_names(context)

    def draw_shots_names(self, context):
        scn = context.scene
        props = context.scene.UAS_shot_manager_props
        shots = props.getShotsList()
        current_shot = props.getCurrentShot()
        square_size = 4.0
        hud_offset = 19

        shot_names_by_camera = defaultdict(list)
        for shot in shots:
            if shot.enabled:
                shot_names_by_camera[shot.camera.name].append(shot)

        #
        # Filter out shots in order to restrict the number of shots to be displayed as a list
        #
        shot_trim_info = dict()
        shot_trim_length = 2  # Limit the display of x shot before and after the current_shot

        for cam, shots in shot_names_by_camera.items():
            shot_trim_info[cam] = [False, False]

            current_shot_index = 0
            if current_shot in shots:
                current_shot_index = shots.index(current_shot)

            before_range = max(current_shot_index - shot_trim_length, 0)
            after_range = min(current_shot_index + shot_trim_length + 1, len(shots))
            shot_names_by_camera[cam] = shots[before_range:after_range]

            if before_range > 0:
                shot_trim_info[cam][0] = True
            if after_range < len(shots):
                shot_trim_info[cam][1] = True

        font_size = 10

        # For all camera which have a shot draw on the ui a list of shots associated with it.
        blf.size(0, font_size, 72)
        for obj in scn.objects:
            if obj.type == "CAMERA" and obj.name in shot_names_by_camera:
                pos_2d = view3d_utils.location_3d_to_region_2d(
                    context.region, context.space_data.region_3d, mathutils.Vector(obj.location)
                )
                if pos_2d is not None:
                    blf.color(0, 0.9, 0.9, 0.9, 0.9)
                    # Move underneath object name
                    x_offset = hud_offset
                    y_offset = int(obj.show_name) * -12

                    # Draw ... if we don't display previous shots.
                    if shot_trim_info[obj.name][0]:
                        blf.position(0, pos_2d[0] + x_offset, pos_2d[1] + y_offset, 0)
                        blf.draw(0, "...")
                        y_offset -= font_size  # Seems to do the trick for this value

                    # Draw the shot names.
                    for s in shot_names_by_camera[obj.name]:
                        blf.position(0, pos_2d[0] + x_offset, pos_2d[1] + y_offset, 0)
                        if current_shot == s:
                            blf.color(0, 0.4, 0.9, 0.1, 1)
                        else:
                            blf.color(0, 0.9, 0.9, 0.9, 0.9)
                        blf.draw(0, s.name)

                        gamma = 1.0 / 2.2
                        linColor = (pow(s.color[0], gamma), pow(s.color[1], gamma), pow(s.color[2], gamma), s.color[3])
                        Square(
                            pos_2d[0] + x_offset - 7, pos_2d[1] + y_offset + 3, square_size, square_size, linColor
                        ).draw()
                        y_offset -= font_size  # Seems to do the trick for this value

                    # Draw ... if we don't display next shots.
                    if shot_trim_info[obj.name][1]:
                        blf.position(0, pos_2d[0] + x_offset, pos_2d[1] + y_offset, 0)
                        blf.draw(0, "...")


_classes = (UAS_ShotManager_DrawCameras_UI,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
