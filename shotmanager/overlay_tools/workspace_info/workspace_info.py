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
Workspace info: display info in bgl on workspace areas
Code initially coming from https://blender.stackexchange.com/questions/61699/how-to-draw-geometry-in-3d-view-window-with-bgl
"""

import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader

from mathutils import Vector


def toggle_workspace_info_display(self, context):
    # print("  toggle_workspace_info_display:  self.UAS_shot_manager_display_overlay_tools: ", self.UAS_shot_manager_display_overlay_tools)
    if self.UAS_shot_manager_identify_3dViews:
        bpy.ops.shot_manager.workspace_info("INVOKE_DEFAULT")
        return
    else:
        return


def draw_typo_2d(color, text, position, font_size):
    font_id = 0
    dpi = 72
    z_detph = 0

    blf.position(font_id, position.x, position.y, z_detph)
    blf.color(font_id, color[0], color[1], color[2], color[3])
    blf.size(font_id, font_size, dpi)
    blf.draw(font_id, text)


def getViewportAreaView(context):
    for screen_area in context.screen.areas:
        if screen_area.type == "VIEW_3D":
            v3d = screen_area.spaces[0]
            rv3d = v3d.region_3d
            return rv3d

    return None


def draw_callback__viewport_info(self, context):
    # return

    # areaView = getViewportAreaView(context)
    # if areaView is not None:
    screens3D = []
    for screen_area in context.screen.areas:
        if screen_area.type == "VIEW_3D":
            screens3D.append(screen_area)

    # ok but not looping
    # if context.area == screens3D[0]:
    #     # areaIndStr = "Add-on Launcher Area"
    #     areaIndStr = "0"
    # elif context.area == screens3D[1]:
    #     areaIndStr = "1"
    # elif context.area == screens3D[2]:
    #     areaIndStr = "2"

    areaIndStr = "?"
    for i, screen_area in enumerate(screens3D):
        if context.area == screens3D[i]:
            areaIndStr = str(i)
            break

    if len(screens3D):
        # bgl.glEnable(bgl.GL_BLEND)
        position = Vector([70, 70])
        size = 50
        draw_typo_2d((1.0, 0.0, 0.0, 1.0), f"3D View: {areaIndStr}", position, size)
        # draw_typo_2d((1.0, 0.0, 0.0, 1.0), str(i))
        # bgl.glEnd()

        # restore opengl defaults
        # bgl.glLineWidth(1)
        # bgl.glDisable(bgl.GL_BLEND)
        # bgl.glEnable(bgl.GL_DEPTH_TEST)


class ShotManager_WorkspaceInfo(bpy.types.Operator):
    bl_idname = "shot_manager.workspace_info"
    bl_label = "Simple Modal View3D Operator"

    def invoke(self, context, event):

        #        for i, screen_area in enumerate(context.screen.areas):
        # if screen_area.type == "VIEW_3D" and i == 0:
        # get the list of 3D areas
        screens3D = []
        for screen_area in context.screen.areas:
            if screen_area.type == "VIEW_3D":
                screens3D.append(screen_area)

        if context.area.type == "VIEW_3D":  # and context.area == screens3D[0]:

            # the arguments we pass the the callback
            args = (self, context)
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            #   self._handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, args, "WINDOW", "POST_VIEW")
            # self._handle_2d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_2d, args, "WINDOW", "POST_PIXEL")
            self._handle_2d = bpy.types.SpaceView3D.draw_handler_add(
                draw_callback__viewport_info, args, "WINDOW", "POST_PIXEL"
            )

            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        else:
            self.report({"WARNING"}, "View3D not found, cannot run operator")
            return {"CANCELLED"}

    def modal(self, context, event):
        context.area.tag_redraw()

        if not context.window_manager.UAS_shot_manager_identify_3dViews or event.type in {"RIGHTMOUSE", "ESC"}:
            #   bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, "WINDOW")
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_2d, "WINDOW")
            return {"CANCELLED"}

        return {"PASS_THROUGH"}
        # return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(ShotManager_WorkspaceInfo)


def unregister():
    bpy.utils.unregister_class(ShotManager_WorkspaceInfo)


# if __name__ == "__main__":
#     register()
