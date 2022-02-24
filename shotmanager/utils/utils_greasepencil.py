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
Useful functions related to the use of Grease Pencil
"""

# https://towardsdatascience.com/blender-2-8-grease-pencil-scripting-and-generative-art-cbbfd3967590

import bpy


def get_grease_pencil(gpencil_obj_name="GPencil") -> bpy.types.GreasePencil:
    """
    Return the grease-pencil object with the given name. Initialize one if not already present.
    :param gpencil_obj_name: name/key of the grease pencil object in the scene
    """

    # If not present already, create grease pencil object
    if gpencil_obj_name not in bpy.context.scene.objects:
        bpy.ops.object.gpencil_add(view_align=False, location=(0, 0, 0), type="EMPTY")
        # rename grease pencil
        bpy.context.scene.objects[-1].name = gpencil_obj_name

    # Get grease pencil object
    gpencil = bpy.context.scene.objects[gpencil_obj_name]

    return gpencil


def get_grease_pencil_layer(
    gpencil: bpy.types.GreasePencil, gpencil_layer_name="GP_Layer", create_layer=True, clear_layer=False
) -> bpy.types.GPencilLayer:
    """
    Return the grease-pencil layer with the given name. Create one if not already present.
    :param gpencil: grease-pencil object for the layer data
    :param gpencil_layer_name: name/key of the grease pencil layer
    :param clear_layer: whether to clear all previous layer data
    """
    gpencil_layer = None

    # Get grease pencil layer or create one if none exists
    if gpencil.data.layers and gpencil_layer_name in gpencil.data.layers:
        gpencil_layer = gpencil.data.layers[gpencil_layer_name]
    else:
        if create_layer:
            # gpencil_layer = gpencil.data.layers.new(gpencil_layer_name, set_active=True)
            add_grease_pencil_layer(gpencil, gpencil_layer_name=gpencil_layer_name)

    if clear_layer:
        gpencil_layer.clear()  # clear all previous layer data

    # bpy.ops.gpencil.paintmode_toggle()  # need to trigger otherwise there is no frame

    return gpencil_layer


def add_grease_pencil_layer(
    gpencil: bpy.types.GreasePencil, gpencil_layer_name="GP_Layer", clear_layer=False, order="TOP"
) -> bpy.types.GPencilLayer:
    """
    Return the grease-pencil layer with the given name. Create one if not already present.
    :param gpencil: grease-pencil object for the layer data
    :param gpencil_layer_name: name/key of the grease pencil layer
    :param clear_layer: whether to clear all previous layer data
    :param order: can be "TOP" or "BOTTOM"
    """
    gpencil_layer = None

    # Get grease pencil layer or create one if none exists
    if gpencil.data.layers and gpencil_layer_name in gpencil.data.layers:
        gpencil_layer = gpencil.data.layers[gpencil_layer_name]
    else:
        gpencil_layer = gpencil.data.layers.new(gpencil_layer_name, set_active=True)

    if clear_layer:
        gpencil_layer.clear()  # clear all previous layer data

    if "BOTTOM" == order:
        # < len(gpencil.data.layers)
        while 0 < gpencil.data.layers.find(gpencil_layer_name):
            gpencil.data.layers.move(gpencil_layer, "DOWN")

    #bpy.ops.gpencil.blank_frame_add()
    gp_frame = gpencil_layer.frames.new(0)

    # bpy.ops.gpencil.paintmode_toggle()  # need to trigger otherwise there is no frame

    return gpencil_layer


def add_grease_pencil_canvas_layer(
    gpencil: bpy.types.GreasePencil, gpencil_layer_name="GP_Layer", clear_layer=False, order="TOP"
) -> bpy.types.GPencilLayer:
    """
    Return the grease-pencil layer with the given name. Create one if not already present.
    :param gpencil: grease-pencil object for the layer data
    :param gpencil_layer_name: name/key of the grease pencil layer
    :param clear_layer: whether to clear all previous layer data
    :param order: can be "TOP" or "BOTTOM"
    """
    gpencil_layer = add_grease_pencil_layer(
        gpencil, gpencil_layer_name=gpencil_layer_name, clear_layer=clear_layer, order=order
    )

    zDistance = -5
    draw_canvas_rect(gpencil_layer.frames[0], (-1, zDistance, -1), (1, zDistance, 1))

    return gpencil_layer


def draw_line(gp_frame, p0: tuple, p1: tuple):
    # Init new stroke
    gp_stroke = gp_frame.strokes.new()
    gp_stroke.display_mode = "3DSPACE"  # allows for editing

    # Define stroke geometry
    gp_stroke.points.add(count=2)
    gp_stroke.points[0].co = p0
    gp_stroke.points[1].co = p1
    return gp_stroke


def draw_canvas_rect(gp_frame, top_left: tuple, bottom_right: tuple):
    # Init new stroke
    gp_stroke = gp_frame.strokes.new()
    gp_stroke.display_mode = "3DSPACE"  # allows for editing

    # Define stroke geometry
    gp_stroke.points.add(count=4)
    gp_stroke.points[0].co = top_left
    gp_stroke.points[1].co = (top_left[0], top_left[1], bottom_right[2])
    gp_stroke.points[2].co = bottom_right
    gp_stroke.points[3].co = (bottom_right[0], top_left[1], top_left[2])
    return gp_stroke


def switchToDrawMode(gp_obj):
    # if another object is edited it is switched to OBJECT mode
    if bpy.context.active_object is not None and bpy.context.active_object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    # clear selection
    bpy.ops.object.select_all(action="DESELECT")

    bpy.context.view_layer.objects.active = gp_obj
    gp_obj.select_set(True)
    gp_obj.hide_select = False
    gp_obj.hide_viewport = False

    if "GPENCIL" == gp_obj.type:
        bpy.ops.gpencil.paintmode_toggle()
