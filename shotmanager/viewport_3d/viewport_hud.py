from collections import defaultdict

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
        #    print(" *** Unregister Display Shot names handler *** ")
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
        try:
            if bpy.context.space_data.overlay.show_overlays:
                self.draw_shots_names(context)
        except Exception as e:
            # print("Paf in draw_camera_ui")
            pass

    def draw_shots_names(self, context):
        scn = context.scene
        props = context.scene.UAS_shot_manager_props

        font_size = 10

        # For all camera which have a shot draw on the ui a list of shots associated with it.
        blf.size(0, font_size, 72)
        for obj in scn.objects:
            if obj.type == "CAMERA":
                if not (context.space_data.region_3d.view_perspective == "CAMERA" and obj == context.scene.camera):
                    pos_2d = view3d_utils.location_3d_to_region_2d(
                        context.region, context.space_data.region_3d, mathutils.Vector(obj.location)
                    )
                    if pos_2d is not None:
                        # print("pos x:", pos_2d[0])
                        # print("pos y:", pos_2d[1])
                        draw_all_shots_names(context, obj, pos_2d[0], pos_2d[1], vertical=True)


def draw_all_shots_names(context, cam, pos_x, pos_y, vertical=False):
    props = context.scene.UAS_shot_manager_props
    current_shot = props.getCurrentShot()
    hud_offset_x = 19
    hud_offset_y = 0

    x_horizontal_offset = 80

    shotsList = props.getShotsUsingCamera(cam)
    if 0 == len(shotsList):
        return ()

    shot_names_by_camera = defaultdict(list)
    for shot in shotsList:
        shot_names_by_camera[shot.camera.name].append(shot)

    #
    # Filter out shots in order to restrict the number of shots to be displayed as a list
    #
    shot_trim_info = dict()
    shot_trim_length = 2  # Limit the display of x shot before and after the current_shot

    for c, shots in shot_names_by_camera.items():
        shot_trim_info[c] = [False, False]

        current_shot_index = 0
        if current_shot in shots:
            current_shot_index = shots.index(current_shot)

        before_range = max(current_shot_index - shot_trim_length, 0)
        after_range = min(current_shot_index + shot_trim_length + 1, len(shots))
        shot_names_by_camera[c] = shots[before_range:after_range]

        if before_range > 0:
            shot_trim_info[c][0] = True
        if after_range < len(shots):
            shot_trim_info[c][1] = True

    font_size = 10

    # For all camera which have a shot draw on the ui a list of shots associated with it
    blf.size(0, font_size, 72)

    blf.color(0, 0.9, 0.9, 0.9, 0.9)

    # Move underneath object name
    x_offset = hud_offset_x
    y_offset = hud_offset_y + int(cam.show_name) * -12

    # Draw ... if we don't display previous shots
    if shot_trim_info[cam.name][0]:
        blf.position(0, pos_x + x_offset, pos_y + y_offset, 0)
        blf.draw(0, "...")
        if vertical:
            y_offset -= font_size  # Seems to do the trick for this value
        else:
            x_offset += x_horizontal_offset

    # Draw the shot names.
    for s in shot_names_by_camera[cam.name]:
        drawShotName(
            pos_x + x_offset, pos_y + y_offset, s.name, s.color, is_current=current_shot == s, is_disabled=not s.enabled
        )
        if vertical:
            y_offset -= font_size  # Seems to do the trick for this value
        else:
            x_offset += x_horizontal_offset

    # Draw ... if we don't display next shots
    if shot_trim_info[cam.name][1]:
        blf.position(0, pos_x + x_offset, pos_y + y_offset, 0)
        blf.draw(0, "...")


def drawShotName(pos_x, pos_y, shot_name, shot_color, is_current=False, is_disabled=False):
    square_size = 4.0

    blf.position(0, pos_x, pos_y, 0)
    if is_current:
        blf.color(0, 0.4, 0.9, 0.1, 1)
    elif is_disabled:
        blf.color(0, 0.6, 0.6, 0.6, 1)
    else:
        blf.color(0, 0.9, 0.9, 0.9, 0.9)
    blf.draw(0, shot_name)

    gamma = 1.0 / 2.2
    linColor = (pow(shot_color[0], gamma), pow(shot_color[1], gamma), pow(shot_color[2], gamma), shot_color[3])
    Square(pos_x - 7, pos_y + 3, square_size, square_size, linColor).draw()


def view3d_camera_border(context):
    obj = context.scene.camera
    cam = obj.data

    frame = cam.view_frame(scene=context.scene)

    # move from object-space into world-space
    frame = [obj.matrix_world @ v for v in frame]

    # move into pixelspace
    from bpy_extras.view3d_utils import location_3d_to_region_2d

    frame_px = [location_3d_to_region_2d(context.region, context.space_data.region_3d, v) for v in frame]
    return frame_px


class UAS_ShotManager_DrawHUD(bpy.types.Operator):
    bl_idname = "uas_shot_manager.draw_hud"
    bl_label = "Shot Manager Draw HUD."
    bl_description = "Draw the shot manager hud."
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
        #    print(" *** Unregister Display HUD handler *** ")
        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")

        self.draw_handle = None
        self.draw_event = None

    def modal(self, context, event):
        if not context.scene.UAS_shot_manager_props.display_hud_in_3dviewport:
            # if not context.window_manager.UAS_shot_manager_display_timeline:
            self.unregister_handlers(context)
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def cancel(self, context):
        self.unregister_handlers(context)

    def draw(self, context):
        #    print("Draw lines persp")
        # wkip wkip wkip quick fix crado pour éviter un crash
        # if not bpy.context.space_data.overlay.show_overlays:
        #     # if not bpy.context.space_data.show_gizmo:
        #     return

        props = context.scene.UAS_shot_manager_props
        current_shot = props.getCurrentShot()
        if current_shot is None or context.space_data.region_3d.view_perspective != "CAMERA":
            return
        cam = context.scene.camera

        blf.color(0, 1, 1, 1, 1)
        blf.size(0, 12, 72)
        _, font_height = blf.dimensions(0, "A")  # Take maximum font height.
        line_separation = 3
        u_r_corner, d_r_corner, d_l_corner, u_l_corner = view3d_camera_border(context)
        line_position = u_l_corner
        line_position.x += 3
        # line_position.y -= font_height + line_separation

        #   print("Line pos x:", line_position.x)
        #   print("Line pos y:", line_position.y)
        draw_all_shots_names(context, cam, line_position.x, line_position.y + 5, vertical=False)

        # line_position.y -= font_height + line_separation

    # def draw(self, context):
    #     props = context.scene.UAS_shot_manager_props
    #     current_shot = props.getCurrentShot()
    #     if current_shot is None or context.space_data.region_3d.view_perspective != "CAMERA":
    #         return

    #     infos = dict()
    #     infos["Shot"] = current_shot.name
    #     infos["Camera"] = current_shot.camera.name

    #     blf.color(0, 1, 1, 1, 1)
    #     blf.size(0, 12, 72)
    #     _, font_height = blf.dimensions(0, "A")  # Take maximum font height.
    #     line_separation = 3
    #     u_r_corner, d_r_corner, d_l_corner, u_l_corner = view3d_camera_border(context)
    #     line_position = u_l_corner
    #     line_position.x += 3
    #     line_position.y -= font_height + line_separation

    #     for k, v in infos.items():
    #         blf.position(0, line_position.x, line_position.y, 0)
    #         blf.draw(0, f"{k}: {v}")
    #         line_position.y -= font_height + line_separation


_classes = (
    UAS_ShotManager_DrawCameras_UI,
    UAS_ShotManager_DrawHUD,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
