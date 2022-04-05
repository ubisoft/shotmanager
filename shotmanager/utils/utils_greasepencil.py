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

import mathutils
from shotmanager.utils import utils

###################
# Grease Pencil
###################


def create_new_greasepencil(gp_name, parentCamera=None, location=None, locate_on_cursor=False):
    """Create a new grease pencil object that will be used as a storyboard frame
    Return this object
    Args:   parentCamera: the camera to parent to
    """
    new_gp_data = bpy.data.grease_pencils.new(gp_name)
    new_gp_obj = bpy.data.objects.new(new_gp_data.name, new_gp_data)
    new_gp_obj.name = new_gp_data.name

    new_gp_obj.use_grease_pencil_lights = False

    # add to main collection
    # bpy.context.collection.objects.link(new_gp_obj)

    # add to a collection named "Cameras"
    gpCollName = "GreasePencil"
    cpColl = None
    if gpCollName not in bpy.context.scene.collection.children:
        cpColl = bpy.data.collections.new(name=gpCollName)
        bpy.context.scene.collection.children.link(cpColl)
    else:
        cpColl = bpy.context.scene.collection.children[gpCollName]
    cpColl.objects.link(new_gp_obj)

    if parentCamera is not None:
        new_gp_obj.parent = parentCamera

    if location is None:
        new_gp_obj.location = [0, 0, 0]
    elif locate_on_cursor:
        new_gp_obj.location = bpy.context.scene.cursor.location
    else:
        new_gp_obj.location = location

    new_gp_obj.lock_location = [True, True, True]
    new_gp_obj.lock_rotation = [True, True, True]
    new_gp_obj.lock_scale = [True, True, True]

    from math import radians

    # align gp with camera axes
    new_gp_obj.rotation_euler = (radians(0.0), 0.0, radians(0.0))

    add_grease_pencil_draw_layers(new_gp_obj)
    create_grease_pencil_material(new_gp_obj, "LINES")
    create_grease_pencil_material(new_gp_obj, "FILLS")

    add_grease_pencil_canvas_layer(new_gp_obj, "GP_Canvas", order="BOTTOM", camera=parentCamera)

    new_gp_obj.data.layers.active = new_gp_obj.data.layers["Lines"]

    return new_gp_obj


def get_greasepencil_child(obj, name_filter=""):
    """Return the first child of the specifed object that is of type GPENCIL"""
    gpChild = None

    if obj is not None:
        if len(obj.children):
            for c in obj.children:
                if "GPENCIL" == c.type:
                    return c
    return gpChild


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

    # bpy.ops.gpencil.blank_frame_add()
    gp_frame = gpencil_layer.frames.new(0)

    # bpy.ops.gpencil.paintmode_toggle()  # need to trigger otherwise there is no frame

    return gpencil_layer


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


def add_grease_pencil_draw_layers(
    gpencil: bpy.types.GreasePencil, gpencil_layer_name="GP_Layer", clear_layer=False, order="TOP"
) -> bpy.types.GPencilLayer:
    gpencil_layer = add_grease_pencil_layer(gpencil, gpencil_layer_name="Fills", clear_layer=True)
    gpencil_layer = add_grease_pencil_layer(gpencil, gpencil_layer_name="Lines", clear_layer=True)


def get_grease_pencil_material(mat_name):
    gp_mat = None
    if mat_name in bpy.data.materials.keys():
        gp_mat = bpy.data.materials[mat_name]
    return gp_mat


def create_grease_pencil_material(gpencil, mat_type="CANVAS"):
    """Create - or get if it already exists - the specified material type and assign it to the specified grease pencil object"""
    gp_mat = None

    if "LINES" == mat_type:
        if "Lines Mat" in bpy.data.materials.keys():
            gp_mat = bpy.data.materials["Lines Mat"]
        else:
            gp_mat = bpy.data.materials.new("Lines Mat")

        if not gp_mat.is_grease_pencil:
            bpy.data.materials.create_gpencil_data(gp_mat)
            gp_mat.grease_pencil.show_fill = False
            gp_mat.grease_pencil.show_stroke = True
            gp_mat.grease_pencil.color = utils.sRGBColor((0.1, 0.1, 0.1, 1))

    elif "FILLS" == mat_type:
        if "Fills Mat" in bpy.data.materials.keys():
            gp_mat = bpy.data.materials["Fills Mat"]
        else:
            gp_mat = bpy.data.materials.new("Fills Mat")

        if not gp_mat.is_grease_pencil:
            bpy.data.materials.create_gpencil_data(gp_mat)
            gp_mat.grease_pencil.show_fill = True
            gp_mat.grease_pencil.fill_color = utils.sRGBColor((0.3, 0.3, 0.3, 1))
            gp_mat.grease_pencil.show_stroke = False

    elif "CANVAS" == mat_type:
        if "Canvas Mat" in bpy.data.materials.keys():
            gp_mat = bpy.data.materials["Canvas Mat"]
        else:
            gp_mat = bpy.data.materials.new("Canvas Mat")

        if True or not gp_mat.is_grease_pencil:
            bpy.data.materials.create_gpencil_data(gp_mat)
            gp_mat.grease_pencil.show_fill = True
            gp_mat.grease_pencil.fill_color = (1, 1, 1, 1)
            gp_mat.grease_pencil.show_stroke = False

    # Assign the material to the grease pencil for drawing
    if gp_mat is not None:
        gpencil.data.materials.append(gp_mat)

    return gp_mat


def add_grease_pencil_canvas_layer(
    gpencil: bpy.types.GreasePencil, gpencil_layer_name="GP_Layer", clear_layer=False, order="TOP", camera=None
) -> bpy.types.GPencilLayer:
    """
    Return the grease-pencil layer with the given name. Create one if not already present.
    :param gpencil: grease-pencil object for the layer data
    :param gpencil_layer_name: name/key of the grease pencil layer
    :param clear_layer: whether to clear all previous layer data
    :param order: can be "TOP" or "BOTTOM"
    """

    # Create material for grease pencil
    gp_mat = create_grease_pencil_material(gpencil, "CANVAS")

    # get the material index in the grease pencil material list:
    # Create a lookup-dict for the object materials:
    mat_dict = {mat.name: i for i, mat in enumerate(gpencil.data.materials)}
    # then map names to indices:
    mat_index = mat_dict[gp_mat.name]

    # gpencil.active_material = gp_mat

    gpencil_layer = add_grease_pencil_layer(
        gpencil, gpencil_layer_name=gpencil_layer_name, clear_layer=clear_layer, order=order
    )

    zDistance = 0.0  # -5
    # ptTopLeft = (-1, -1, zDistance)
    # ptBottomRight = (1, 1, zDistance)
    ptTopLeft = (-0.5, -0.5, zDistance)
    ptBottomRight = (0.5, 0.5, zDistance)
    gpStroke = draw_canvas_rect(gpencil_layer.frames[0], ptTopLeft, ptBottomRight)
    gpStroke.material_index = mat_index

    fitCanvasToFrustum(gpStroke, camera)

    gpencil_layer.lock = True

    return gpencil_layer


def fitGreasePencilToFrustum(camera, distance=None):
    gpencil = get_greasepencil_child(camera)

    # method with canvas points modification ###
    # gpencil.location[2] = -1.0 * distance
    # canvas_bg_stroke = get_grease_pencil_canvas_stroke(gpencil)
    # applied_scale_factor = fitCanvasToFrustum(canvas_bg_stroke, camera, distance, zOffset=gpencil.location[2])
    # fitLayersToFrustum(gpencil, applied_scale_factor)

    # method with gpencil scaling ###

    # removed to allow frame panning
    # gpencil.location[0] = gpencil.location[1] = 0.0
    prevX = gpencil.location[0]
    prevY = gpencil.location[1]
    gpencil.location[0] = gpencil.location[1] = 0.0

    gpencil.location[2] = -1.0 * distance

    gpencil.rotation_euler = [0, 0, 0]
    gpencil.rotation_quaternion = [0, 0, 0, 0]
    distRef = getDistRef(camera)
    gpWidth = distance / distRef

    vec = mathutils.Vector((gpWidth, gpWidth, gpWidth))
    # gpencil.scale = vec
    gpencil.delta_scale = vec

    gpencil.location[0] = prevX * gpWidth
    gpencil.location[1] = prevY * gpWidth


def getDistRef(camera):
    f = 1.0 if camera.type == "ORTHO" else 1.0
    corners = [(f * p) for p in camera.data.view_frame(scene=bpy.context.scene)]
    width = corners[0][0] - corners[2][0]
    dist = -1.0 * corners[2][2]
    #  print(f"getDistRef: width:{width}, dist:{dist}")
    return dist


def fitLayersToFrustum(gpencil, factor):
    for layer in gpencil.data.layers:
        if layer.info != "GP_Canvas":
            layer.scale[0] = factor
            layer.scale[1] = factor
            layer.scale[2] = factor


def fitCanvasToFrustum(gpStroke: bpy.types.GPencilStroke, camera, distance=None, zOffset=0.0):
    if camera is None:
        return

    top_left_previous_x = gpStroke.points[0].co[0]
    bottom_right_previous = gpStroke.points[2].co

    print(f"fitCanvasToFrustum: camera: {camera.name}, distance: {distance}")
    if distance is not None:
        corners = getCameraCorners(bpy.context, camera, -1.0 * distance)
    else:
        corners = getCameraCorners(bpy.context, camera)

    top_left = corners[0]
    top_left[2] = 0.0
    top_left[2] -= zOffset
    bottom_right = corners[2]
    bottom_right[2] = 0.0
    bottom_right[2] -= zOffset

    gpStroke.points[0].co = top_left
    gpStroke.points[1].co = (bottom_right[0], top_left[1], top_left[2])
    gpStroke.points[2].co = bottom_right
    gpStroke.points[3].co = (top_left[0], bottom_right[1], bottom_right[2])

    # wkipwkipwkip to fix
    applied_scale_factor = top_left_previous_x / top_left[0]

    return applied_scale_factor


def getCameraCorners(context, camera, distance=None):
    mw = camera.matrix_world

    # sizeRef is an arbitrary ref for the frustum width of the camera
    sizeRef = 1.0
    # point of the frustum when width is 1
    distRef = camera.data.view_frame(scene=context.scene)[0][2]

    # camera.data.display_size is the width of the frustum for a given lens
    # f = 1 if camera.type == "ORTHO" else distance if distance is not None else camera.data.display_size
    f = (
        1
        if camera.type == "ORTHO"
        else distance * sizeRef / distRef
        if distance is not None
        else camera.data.display_size
    )

    corners = [(f * p) for p in camera.data.view_frame(scene=context.scene)]
    # corners = [mw @ (f * p) for p in camera.data.view_frame(scene=context.scene)]

    """
    # add empties at corners
    for i, p in enumerate(corners):
        bpy.ops.object.empty_add(location=p)
        context.object.name = f"MT{i}"
    """

    # w = corners[3] - corners[0]
    # h = corners[1] - corners[0]

    # print(f"Camera: {camera.name} dimensions {w.length : .2f} x {h.length : .2f}")

    return corners


def get_grease_pencil_canvas_layer(gpencil: bpy.types.GreasePencil) -> bpy.types.GPencilLayer:
    canvas_layer = None
    if gpencil.data.layers:
        if gpencil.data.layers["GP_Canvas"] is not None:
            canvas_layer = gpencil.data.layers["GP_Canvas"]
    return canvas_layer


def get_grease_pencil_canvas_stroke(gpencil: bpy.types.GreasePencil) -> bpy.types.GPencilLayer:
    canvas_bg_stroke = None
    canvas_layer = get_grease_pencil_canvas_layer(gpencil)
    if canvas_layer is not None:
        if canvas_layer.frames:
            if canvas_layer.frames[0].strokes:
                canvas_bg_stroke = canvas_layer.frames[0].strokes[0]
    return canvas_bg_stroke


def draw_line(gp_frame, p0: tuple, p1: tuple) -> bpy.types.GPencilStroke:
    # Init new stroke
    gpStroke = gp_frame.strokes.new()
    gpStroke.display_mode = "3DSPACE"  # allows for editing

    # Define stroke geometry
    gpStroke.points.add(count=2)
    gpStroke.points[0].co = p0
    gpStroke.points[1].co = p1
    return gpStroke


def draw_canvas_rect(gp_frame, top_left: tuple, bottom_right: tuple) -> bpy.types.GPencilStroke:
    # Init new stroke
    gpStroke = gp_frame.strokes.new()
    gpStroke.display_mode = "3DSPACE"  # allows for editing

    # Define stroke geometry
    gpStroke.points.add(count=4)
    gpStroke.points[0].co = top_left
    gpStroke.points[1].co = (bottom_right[0], top_left[1], top_left[2])
    gpStroke.points[2].co = bottom_right
    gpStroke.points[3].co = (top_left[0], bottom_right[1], bottom_right[2])
    return gpStroke


def switchToDrawMode(gpencil: bpy.types.GreasePencil):
    """Set the specified grease pencil object in Draw mode
    It the current object is not the specified one then the current selection is modified
    to switch to the current object.
    """
    # if another object is edited it is switched to OBJECT mode
    if bpy.context.active_object is not None and bpy.context.active_object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    # clear selection
    bpy.ops.object.select_all(action="DESELECT")

    if "GPENCIL" == gpencil.type:

        gpencil.select_set(True)
        bpy.context.view_layer.objects.active = gpencil
        gpencil.select_set(True)
        gpencil.hide_select = False
        gpencil.hide_viewport = False
        
        bpy.ops.gpencil.paintmode_toggle()
        bpy.context.scene.tool_settings.gpencil_stroke_placement_view3d = "ORIGIN"
        bpy.context.scene.tool_settings.gpencil_sculpt.lock_axis = "VIEW"


def getLayerPreviousFrame(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Return the previous key of the specified layer
    Args:
        layerMode: Can be "NOLAYER", "ACTIVE", "ALL" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """

    def _getPrevFrame(gpLayer, frame):
        for f in reversed(gpLayer.frames):
            if f.frame_number < frame:
                return f.frame_number
        return frame

    gpFrame = currentFrame
    if "NOLAYER" == layerMode:
        pass
    elif "ALL" == layerMode:
        mins = list()
        for layer in gpencil.data.layers:
            prevKeyFrame = _getPrevFrame(layer, currentFrame)
            if prevKeyFrame < currentFrame:
                mins.append(prevKeyFrame)
        if len(mins):
            gpFrame = max(mins)
    elif "ACTIVE" == layerMode:
        gpLayer = gpencil.data.layers.active
        gpFrame = _getPrevFrame(gpLayer, currentFrame)
    else:
        gpLayer = gpencil.data.layers[layerMode]
        gpFrame = _getPrevFrame(gpLayer, currentFrame)

    return gpFrame


def getLayerNextFrame(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Return the next key of the specified layer
    Args:
        layerMode: Can be "NOLAYER", "ACTIVE", "ALL" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """

    def _getNextFrame(gpLayer, frame):
        for f in gpLayer.frames:
            if f.frame_number > frame:
                return f.frame_number
        return frame

    gpFrame = currentFrame
    if "NOLAYER" == layerMode:
        pass
    elif "ALL" == layerMode:
        maxs = list()
        for layer in gpencil.data.layers:
            nextKeyFrame = _getNextFrame(layer, currentFrame)
            if currentFrame < nextKeyFrame:
                maxs.append(nextKeyFrame)
        if len(maxs):
            gpFrame = min(maxs)
    elif "ACTIVE" == layerMode:
        gpLayer = gpencil.data.layers.active
        gpFrame = _getNextFrame(gpLayer, currentFrame)
    else:
        gpLayer = gpencil.data.layers[layerMode]
        gpFrame = _getNextFrame(gpLayer, currentFrame)

    return gpFrame


def isCurrentFrameOnLayerFrame(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Return True if the specifed layer has a key at the specified frame
    Args:
        layerMode: Can be "NOLAYER", "ACTIVE", "ALL" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """

    def _isCurrentFrameOnFrame(gpLayer, frame):
        for f in gpLayer.frames:
            if f.frame_number == frame:
                return True
        return False

    currentFrameIsOnGPFrame = False
    if "NOLAYER" == layerMode:
        pass
    elif "ALL" == layerMode:
        for layer in gpencil.data.layers:
            if _isCurrentFrameOnFrame(layer, currentFrame):
                currentFrameIsOnGPFrame = True
                continue
    elif "ACTIVE" == layerMode:
        gpLayer = gpencil.data.layers.active
        currentFrameIsOnGPFrame = _isCurrentFrameOnFrame(gpLayer, currentFrame)
    else:
        gpLayer = gpencil.data.layers[layerMode]
        currentFrameIsOnGPFrame = _isCurrentFrameOnFrame(gpLayer, currentFrame)

    return currentFrameIsOnGPFrame


def addFrameToLayer(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Add a new key to the specified layer at the specified frame
    Args:
        layerMode: Can be "NOLAYER", "ACTIVE", "ALL" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """

    if "NOLAYER" == layerMode:
        return
    elif "ALL" == layerMode:
        for layer in gpencil.data.layers:
            if not layer.lock:
                if not isCurrentFrameOnLayerFrame(gpencil, currentFrame, layer.info):
                    layer.frames.new(currentFrame)

        # not working: it duplicates existing frames
        # bpy.ops.gpencil.blank_frame_add(all_layers=True)
    elif "ACTIVE" == layerMode:
        currentFrameIsOnGPFrame = isCurrentFrameOnLayerFrame(gpencil, currentFrame, "ACTIVE")
        if not currentFrameIsOnGPFrame and not gpencil.data.layers.active.lock:
            # bpy.ops.gpencil.blank_frame_add(all_layers=False)
            gpencil.data.layers.active.frames.new(currentFrame)
    else:
        gpLayer = gpencil.data.layers[layerMode]
        currentFrameIsOnGPFrame = isCurrentFrameOnLayerFrame(gpencil, currentFrame, layerMode)
        if not currentFrameIsOnGPFrame and not gpLayer.lock:
            # prevActiveLayer = gpencil.data.layers.active
            # gpencil.data.layers.active = gpLayer
            # bpy.ops.gpencil.blank_frame_add(all_layers=False)
            gpLayer.frames.new(currentFrame)
            # gpencil.data.layers.active = prevActiveLayer

    return


def getLayerFrameIndexAtFrame(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Return the index of the layer frame at the specified time frame.
    If no layer frame matches the time frame then -1 is returned
    Args:
        layerMode: Can be "NOLAYER", "ACTIVE", "ALL" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """
    if not isCurrentFrameOnLayerFrame(gpencil, currentFrame, layerMode):
        return -1

    def _getLayerFrameIndexAtFrame(layer, currentFrame):
        for ind, f in enumerate(layer.frames):
            if f.frame_number == currentFrame:
                return ind
        return -1

    layerFrameInd = -1
    if "NOLAYER" == layerMode:
        return -1
    elif "ALL" == layerMode:
        # TODO
        # for layer in gpencil.data.layers:
        #     if not layer.lock:
        #         if not isCurrentFrameOnLayerFrame(gpencil, currentFrame, layer.info):
        #             layer.frames.new(currentFrame)

        # not working: it duplicates existing frames
        # bpy.ops.gpencil.blank_frame_add(all_layers=True)
        pass
    elif "ACTIVE" == layerMode:
        layerFrameInd = _getLayerFrameIndexAtFrame(gpencil.data.layers.active, currentFrame)
    else:
        gpLayer = gpencil.data.layers[layerMode]
        layerFrameInd = _getLayerFrameIndexAtFrame(gpLayer, currentFrame)

    return layerFrameInd
