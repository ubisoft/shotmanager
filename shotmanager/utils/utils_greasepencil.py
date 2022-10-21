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

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


###################
# Grease Pencil
###################


def get_greasepencil_child(obj, childType="GPENCIL", name_filter=""):
    """Return the first child of the specifed object that is of type GPENCIL or EMPTY
    Args:
        childType: can be "GPENCIL" or "EMPTY"
    """
    gpChild = None

    if obj is not None:
        if len(obj.children):
            for c in obj.children:
                if "EMPTY" == c.type:
                    if "EMPTY" == childType:
                        return c
                    if len(c.children):
                        for cc in c.children:
                            if "GPENCIL" == cc.type:
                                return cc

    return gpChild
    # if obj is not None:
    #     if len(obj.children):
    #         for c in obj.children:
    #             if "GPENCIL" == c.type:
    #                 return c
    # return gpChild


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

    addLayerKeyFrameAtTime(gpencil_layer, 0)

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


def get_grease_pencil_material(mat_name):
    gp_mat = None
    if mat_name in bpy.data.materials.keys():
        gp_mat = bpy.data.materials[mat_name]
    return gp_mat


def create_grease_pencil_material(mat_type="CANVAS", mat_name="", gpencil=None):
    """Create - or get if it already exists - the specified material type and, if specified, assign it to a grease pencil object
    Args:
        mat_type:   can be "CANVAS", "LINES", "FILLS" """
    gp_mat = None

    if "LINES" == mat_type:
        matName = mat_name if mat_name and "" != mat_name else "Lines Mat"
    elif "FILLS" == mat_type:
        matName = mat_name if mat_name and "" != mat_name else "Fills Mat"
    elif "CANVAS" == mat_type:
        matName = mat_name if mat_name and "" != mat_name else "Canvas Mat"

    if matName in bpy.data.materials.keys():
        gp_mat = bpy.data.materials[matName]
    else:
        gp_mat = bpy.data.materials.new(matName)

    if "LINES" == mat_type:
        if not gp_mat.is_grease_pencil:
            bpy.data.materials.create_gpencil_data(gp_mat)
            gp_mat.grease_pencil.show_fill = False
            gp_mat.grease_pencil.show_stroke = True
            gp_mat.grease_pencil.color = utils.color_to_linear((0.1, 0.1, 0.1, 1))

    elif "FILLS" == mat_type:
        if not gp_mat.is_grease_pencil:
            bpy.data.materials.create_gpencil_data(gp_mat)
            gp_mat.grease_pencil.show_fill = True
            gp_mat.grease_pencil.fill_color = utils.color_to_linear((0.3, 0.3, 0.3, 1))
            gp_mat.grease_pencil.show_stroke = False

    elif "CANVAS" == mat_type:
        if True or not gp_mat.is_grease_pencil:
            bpy.data.materials.create_gpencil_data(gp_mat)
            gp_mat.grease_pencil.show_fill = True
            gp_mat.grease_pencil.fill_color = (1, 1, 1, 1)
            gp_mat.grease_pencil.show_stroke = False

    # Assign the material to the grease pencil for drawing
    if gp_mat and gpencil:
        gpencil.data.materials.append(gp_mat)

    return gp_mat


def add_grease_pencil_canvas_layer(
    gpencil: bpy.types.GreasePencil, canvasPreset, material=None, clear_layer=False, order="TOP", camera=None
) -> bpy.types.GPencilLayer:
    """
    Return the grease-pencil layer with the given name. Create one if not already present.
    :param gpencil: grease-pencil object for the layer data
    :param gpencil_layer_name: name/key of the grease pencil layer
    :param clear_layer: whether to clear all previous layer data
    :param order: can be "TOP" or "BOTTOM"
    """

    gpencil_layer_name = "_Canvas_" if canvasPreset is None else canvasPreset.layerName

    # Create material for grease pencil
    gp_mat = material if material else create_grease_pencil_material(mat_type="CANVAS")

    # get the material index in the grease pencil material list:
    # Create a lookup-dict for the object materials:
    mat_dict = {mat.name: i for i, mat in enumerate(gpencil.data.materials)}
    # then map names to indices:
    mat_index = mat_dict[gp_mat.name]

    # gpencil.active_material = gp_mat

    gpencil_layer = add_grease_pencil_layer(
        gpencil, gpencil_layer_name=gpencil_layer_name, clear_layer=clear_layer, order=order
    )

    gpStroke = create_grease_pencil_canvas_frame(gpencil_layer)
    gpStroke.material_index = mat_index

    fitCanvasToFrustum(gpStroke, camera)

    gpencil_layer.lock = True

    return gpencil_layer


def create_grease_pencil_canvas_frame(gpencil_layer):
    keyFrame = addLayerKeyFrameAtTime(gpencil_layer, 0)

    zDistance = 0.0  # -5
    # ptTopLeft = (-1, -1, zDistance)
    # ptBottomRight = (1, 1, zDistance)
    ptTopLeft = (-0.5, -0.5, zDistance)
    ptBottomRight = (0.5, 0.5, zDistance)
    gpStroke = draw_canvas_rect(keyFrame, ptTopLeft, ptBottomRight)
    return gpStroke


def fitGreasePencilToFrustum(camera, distance=None):

    gpencil = get_greasepencil_child(camera, "GPENCIL")
    gpEmpty = get_greasepencil_child(camera, "EMPTY")

    # method with canvas points modification ###
    # gpencil.location[2] = -1.0 * distance
    # canvas_bg_stroke = get_grease_pencil_canvas_stroke(gpencil)
    # applied_scale_factor = fitCanvasToFrustum(canvas_bg_stroke, camera, distance, zOffset=gpencil.location[2])
    # fitLayersToFrustum(gpencil, applied_scale_factor)

    # method with gpencil scaling ###

    # removed to allow frame panning
    # gpencil.location[0] = gpencil.location[1] = 0.0

    ######################################
    # prevX = gpencil.location[0]
    # prevY = gpencil.location[1]
    # gpencil.location[0] = gpencil.location[1] = 0.0

    # gpencil.location[2] = -1.0 * distance

    # gpencil.rotation_euler = [0, 0, 0]
    # gpencil.rotation_quaternion = [0, 0, 0, 0]
    # distRef = getDistRef(camera)
    # gpWidth = distance / distRef

    # vec = mathutils.Vector((gpWidth, gpWidth, gpWidth))
    # # gpencil.scale = vec
    # gpencil.delta_scale = vec

    # gpencil.location[0] = prevX * gpWidth
    # gpencil.location[1] = prevY * gpWidth
    # ############################################

    gpEmpty.location[0] = gpEmpty.location[1] = gpEmpty.location[2] = 0.0
    gpEmpty.rotation_euler = [0, 0, 0]
    gpEmpty.rotation_quaternion = [0, 0, 0, 0]
    distRef = getDistRef(camera)
    gpWidth = distance / distRef

    vec = mathutils.Vector((gpWidth, gpWidth, gpWidth))
    gpEmpty.scale = vec
    # gpEmpty.delta_scale = vec

    gpencil.location[2] = -1.0 * distRef


def getDistRef(camera):
    f = 1.0 if camera.type == "ORTHO" else 1.0
    corners = [(f * p) for p in camera.data.view_frame(scene=bpy.context.scene)]
    width = corners[0][0] - corners[2][0]
    dist = -1.0 * corners[2][2]
    #  print(f"getDistRef: width:{width}, dist:{dist}")
    return dist


# def fitLayersToFrustum(gpencil, factor):
#     for layer in gpencil.data.layers:
#         if layer.info != "GP_Canvas":
#             layer.scale[0] = factor
#             layer.scale[1] = factor
#             layer.scale[2] = factor


def fitCanvasToFrustum(gpStroke: bpy.types.GPencilStroke, camera, distance=None, zOffset=0.0):
    if camera is None:
        return

    top_left_previous_x = gpStroke.points[0].co[0]
    bottom_right_previous = gpStroke.points[2].co

    # print(f"fitCanvasToFrustum: camera: {camera.name}, distance: {distance}")
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


def getCanvasCorners(context, camera, distance=None, coordSys=None, zOffset=0.0):
    if distance is not None:
        corners = getCameraCorners(bpy.context, camera, -1.0 * distance, coordSys=coordSys)
    else:
        corners = getCameraCorners(bpy.context, camera)

    top_left = corners[2]
    # top_left[2] = 0.0
    # top_left[2] -= zOffset
    bottom_right = corners[0]
    # bottom_right[2] = 0.0
    # bottom_right[2] -= zOffset

    # gpStroke.points[0].co = top_left
    # gpStroke.points[1].co = (bottom_right[0], top_left[1], top_left[2])
    # gpStroke.points[2].co = bottom_right
    # gpStroke.points[3].co = (top_left[0], bottom_right[1], bottom_right[2])

    # wkipwkipwkip to fix
    #  applied_scale_factor = top_left_previous_x / top_left[0]

    # return applied_scale_factor

    distRef = getDistRef(camera)
    gpWidth = distance / distRef

    vec = mathutils.Vector((gpWidth, gpWidth, gpWidth))

    CanvasCorners = list()
    CanvasCorners.append(top_left)
    CanvasCorners.append((bottom_right[0], top_left[1], top_left[2]))
    CanvasCorners.append(bottom_right)
    CanvasCorners.append((top_left[0], bottom_right[1], bottom_right[2]))

    return CanvasCorners


def getCameraCorners(context, camera, distance=None, coordSys=None, fixRotation=True):
    mw = camera.matrix_world

    # point of the frustum when width is 1
    # distRef = camera.data.view_frame(scene=context.scene)[0][2]
    distRef = 1.0
    if distance is not None:
        distRef = getDistRef(camera)
        sizeAtDistance = distance / distRef

    # camera.data.display_size is the width of the frustum for a given lens
    # f = 1 if camera.type == "ORTHO" else distance if distance is not None else camera.data.display_size
    f = (
        1
        if camera.type == "ORTHO"
        # else distance * sizeRef / distRef
        else sizeAtDistance
        if distance is not None
        else camera.data.display_size
    )

    import math

    if coordSys is None:
        corners = [(f * p) for p in camera.data.view_frame(scene=context.scene)]
    else:
        if fixRotation:
            mat_rot = mathutils.Matrix.Rotation(math.radians(180.0), 4, "Y")
            corners = [mw @ mat_rot @ (f * p) for p in camera.data.view_frame(scene=context.scene)]
        else:
            corners = [mw @ (f * p) for p in camera.data.view_frame(scene=context.scene)]

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


# def get_grease_pencil_canvas_layer(gpencil: bpy.types.GreasePencil) -> bpy.types.GPencilLayer:
#     canvas_layer = None
#     if gpencil.data.layers:
#         if gpencil.data.layers["GP_Canvas"] is not None:
#             canvas_layer = gpencil.data.layers["GP_Canvas"]
#     return canvas_layer


# def get_grease_pencil_canvas_stroke(gpencil: bpy.types.GreasePencil) -> bpy.types.GPencilLayer:
#     canvas_bg_stroke = None
#     canvas_layer = get_grease_pencil_canvas_layer(gpencil)
#     if canvas_layer is not None:
#         if canvas_layer.frames:
#             if canvas_layer.frames[0].strokes:
#                 canvas_bg_stroke = canvas_layer.frames[0].strokes[0]
#     return canvas_bg_stroke


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


def switchToObjectMode():
    """Switch from any mode back to Object mode"""
    # NOTE: we use context.object here instead of context.active_object because
    # when the eye icon of the object is closed (meaning object.hide_get() == True)
    # then context.active_object is None
    if bpy.context.object is not None and "OBJECT" != bpy.context.object.mode:
        previous_hide_select = bpy.context.object.hide_select
        previous_hide_viewport = bpy.context.object.hide_viewport
        previous_hide_get = bpy.context.object.hide_get()

        bpy.context.object.hide_select = False
        bpy.context.object.hide_viewport = False
        bpy.context.object.hide_set(False)
        bpy.ops.object.mode_set(mode="OBJECT")

        bpy.context.object.hide_select = previous_hide_select
        bpy.context.object.hide_viewport = previous_hide_viewport
        bpy.context.object.hide_set(previous_hide_get)


def isAnotherObjectInSubMode(obj):
    """Return True if another object that specified one is currently being edited (= in another mode
    that OBJECT mode), False otherwise
    Possible edit modes: 'EDIT', 'POSE', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT',
                'TEXTURE_PAINT', 'PARTICLE_EDIT', 'EDIT_GPENCIL', 'SCULPT_GPENCIL',
                'PAINT_GPENCIL', 'WEIGHT_GPENCIL', 'VERTEX_GPENCIL'
                Not 'OBJECT'
    """
    # NOTE: we use context.object here instead of context.active_object because
    # when the eye icon of the object is closed (meaning object.hide_get() == True)
    # then context.active_object is None
    isAnyObjInSubMode = False
    if bpy.context.object is not None:
        if obj != bpy.context.object:
            if "OBJECT" != bpy.context.object.mode:
                isAnyObjInSubMode = True
    # return bpy.context.object is not None and obj != bpy.context.object and "OBJECT" != bpy.context.object.mode
    return isAnyObjInSubMode


def getObjectInSubMode():
    """Return the object currently being edited (= in another mode
    that OBJECT mode), None otherwise
    Possible edit modes: 'EDIT', 'POSE', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT',
                'TEXTURE_PAINT', 'PARTICLE_EDIT', 'EDIT_GPENCIL', 'SCULPT_GPENCIL',
                'PAINT_GPENCIL', 'WEIGHT_GPENCIL', 'VERTEX_GPENCIL'
                Not 'OBJECT'
    """
    # NOTE: we use context.object here instead of context.active_object because
    # when the eye icon of the object is closed (meaning object.hide_get() == True)
    # then context.active_object is None

    if bpy.context.object is not None and "OBJECT" != bpy.context.object.mode:
        return bpy.context.object
    else:
        return None


def switchToDrawMode(context, gpencil: bpy.types.GreasePencil):
    """Set the specified grease pencil object in Draw mode
    Return True if the operation succeeded
    It the current object is not the specified one then the current selection is modified
    to switch to the current object.
    """
    if gpencil is None or "GPENCIL" != gpencil.type:
        return False

    # if another object is edited it is switched to OBJECT mode
    if isAnotherObjectInSubMode(gpencil):
        switchToObjectMode()

    # clear selection
    # bpy.ops.object.select_all(action="DESELECT")

    gpencil.hide_select = False
    gpencil.hide_viewport = False
    gpencil.hide_set(False)
    gpencil.select_set(True)
    bpy.context.view_layer.objects.active = gpencil
    gpencil.select_set(True)

    if "PAINT_GPENCIL" != gpencil.mode:
        # bpy.ops.gpencil.paintmode_toggle()
        # print("riri - here bug paint cause current tool not set in the viewport")
        bpy.ops.object.mode_set(mode="PAINT_GPENCIL")

        #################
        # Bug fix: required to set the pen tool by default, otherwise we cannot paint cause there is no tool selected:

        # we get the type of tool currently used in the viewport
        toolName = bpy.context.workspace.tools.from_space_view3d_mode("PAINT_GPENCIL", create=False).idname

        # we change it if it is not valid
        if toolName not in ["builtin_brush.Draw", "builtin_brush.Fill", "builtin_brush.Erase", "builtin_brush.Tint"]:
            _logger.warning_ext("SM: Current tool in Grease Pencil Draw mode was not valid - Changed to Draw")
            bpy.ops.wm.tool_set_by_id(name="builtin_brush.Draw")
            # bpy.ops.wm.tool_set_by_id(name="builtin_brush.Fill", as_fallback=True, space_type="VIEW_3D")

    context.scene.tool_settings.gpencil_stroke_placement_view3d = "ORIGIN"
    context.scene.tool_settings.gpencil_sculpt.lock_axis = "VIEW"
    return True


def getLayerPreviousFrame(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Return the time frame value of the previous key of the specified layer
    Args:
        layerMode: Can be "NOLAYER", "ACTIVE", "ALL" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """

    def _getPrevFrame(gpLayer, frame):
        for kf in reversed(gpLayer.frames):
            if kf.frame_number < frame:
                return kf.frame_number
        return frame

    previousFrame = currentFrame
    if "NOLAYER" == layerMode:
        pass
    elif "ALL" == layerMode:
        mins = list()
        for layer in gpencil.data.layers:
            prevKeyFrame = _getPrevFrame(layer, currentFrame)
            if prevKeyFrame < currentFrame:
                mins.append(prevKeyFrame)
        if len(mins):
            previousFrame = max(mins)
    elif "ACTIVE" == layerMode:
        gpLayer = gpencil.data.layers.active
        previousFrame = _getPrevFrame(gpLayer, currentFrame)
    else:
        gpLayer = gpencil.data.layers[layerMode]
        previousFrame = _getPrevFrame(gpLayer, currentFrame)

    return previousFrame


def getLayerNextFrame(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Return the frame value of the next key of the specified layer
    Args:
        layerMode: Can be "NOLAYER", "ACTIVE", "ALL" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """

    def _getNextFrame(gpLayer, frame):
        for kf in gpLayer.frames:
            if kf.frame_number > frame:
                return kf.frame_number
        return frame

    nextFrame = currentFrame
    if "NOLAYER" == layerMode:
        pass
    elif "ALL" == layerMode:
        maxs = list()
        for layer in gpencil.data.layers:
            nextKeyFrame = _getNextFrame(layer, currentFrame)
            if currentFrame < nextKeyFrame:
                maxs.append(nextKeyFrame)
        if len(maxs):
            nextFrame = min(maxs)
    elif "ACTIVE" == layerMode:
        gpLayer = gpencil.data.layers.active
        nextFrame = _getNextFrame(gpLayer, currentFrame)
    else:
        gpLayer = gpencil.data.layers[layerMode]
        nextFrame = _getNextFrame(gpLayer, currentFrame)

    return nextFrame


def getLayerKeyFrameAtTime(gpLayer, frame):
    for kf in gpLayer.frames:
        if kf.frame_number == frame:
            return kf
    return None


def addLayerKeyFrameAtTime(gpLayer, frame):
    # bpy.ops.gpencil.blank_frame_add()
    keyFrame = getLayerKeyFrameAtTime(gpLayer, frame)
    if keyFrame is None:
        keyFrame = gpLayer.frames.new(frame)

        # refresh viewport
        gpLayer.hide = not gpLayer.hide
        gpLayer.hide = not gpLayer.hide

    return keyFrame


def isCurrentFrameOnLayerKeyFrame(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Return True if the specifed layer has a key at the specified time frame
    Args:
        layerMode: Can be "NOLAYER", "ACTIVE", "ALL" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """

    def _isCurrentFrameOnFrame(gpLayer, frame):
        for kf in gpLayer.frames:
            if kf.frame_number == frame:
                return True
        return False

    currentFrameIsOnGPFrame = False
    if "" == layerMode or "NOLAYER" == layerMode:
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
        if layerMode in gpencil.data.layers:
            gpLayer = gpencil.data.layers[layerMode]
            currentFrameIsOnGPFrame = _isCurrentFrameOnFrame(gpLayer, currentFrame)

    return currentFrameIsOnGPFrame


def getLayerKeyFrameAtFrame(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Return the layer key frame that is at the specified time frame, None if the
    specifed layer has no key frame at that time
    Args:
        layerMode: Can be "ACTIVE" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """
    if "NOLAYER" == layerMode or "ALL" == layerMode:
        return None

    def _getKeyFrameAtFrame(gpLayer, frame):
        for kf in gpLayer.frames:
            if kf.frame_number == frame:
                return kf
        return None

    keyFrame = None
    if "ACTIVE" == layerMode:
        gpLayer = gpencil.data.layers.active
        keyFrame = _getKeyFrameAtFrame(gpLayer, currentFrame)
    else:
        gpLayer = gpencil.data.layers[layerMode]
        keyFrame = _getKeyFrameAtFrame(gpLayer, currentFrame)

    return keyFrame


def getLayerKeyFrameIndexAtFrame(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Return the index of the layer key frame at the specified time frame.
    If no layer frame matches the time frame then -1 is returned
    Args:
        layerMode: Can be "NOLAYER", "ACTIVE", "ALL" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """
    if not isCurrentFrameOnLayerKeyFrame(gpencil, currentFrame, layerMode):
        return -1

    def _getLayerFrameIndexAtFrame(layer, currentFrame):
        for ind, kf in enumerate(layer.frames):
            if kf.frame_number == currentFrame:
                return ind
        return -1

    layerFrameInd = -1
    if "NOLAYER" == layerMode:
        return -1
    elif "ALL" == layerMode:
        # TODO
        # for layer in gpencil.data.layers:
        #     if not layer.lock:
        #         if not isCurrentFrameOnLayerKeyFrame(gpencil, currentFrame, layer.info):
        #             layer.frames.new(currentFrame)
        _logger.debug_ext("getLayerKeyFrameIndexAtFrame TODO", col="RED")
        # not working: it duplicates existing frames
        # bpy.ops.gpencil.blank_frame_add(all_layers=True)
        pass
    elif "ACTIVE" == layerMode:
        layerFrameInd = _getLayerFrameIndexAtFrame(gpencil.data.layers.active, currentFrame)
    else:
        gpLayer = gpencil.data.layers[layerMode]
        layerFrameInd = _getLayerFrameIndexAtFrame(gpLayer, currentFrame)

    return layerFrameInd


def addKeyFrameToLayer(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Add a new key frame to the specified layer at the specified time frame
    Return the key frame
    Args:
        layerMode: Can be "NOLAYER", "ACTIVE", "ALL" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """
    # NOTE: operators are not working as expected: blank_frame_add duplicates existing frames
    # bpy.ops.gpencil.blank_frame_add(all_layers=True)
    newLayerKeyFrame = None
    if "NOLAYER" == layerMode:
        return None
    elif "ALL" == layerMode:
        for layer in gpencil.data.layers:
            if not layer.lock:
                if not isCurrentFrameOnLayerKeyFrame(gpencil, currentFrame, layer.info):
                    newLayerKeyFrame = layer.frames.new(currentFrame)
                    # refresh viewport
                    layer.hide = not layer.hide
                    layer.hide = not layer.hide
    else:
        if "ACTIVE" == layerMode:
            gpLayer = gpencil.data.layers.active
        else:
            gpLayer = gpencil.data.layers[layerMode]

        if not gpLayer.lock and not isCurrentFrameOnLayerKeyFrame(gpencil, currentFrame, gpLayer.info):
            newLayerKeyFrame = gpLayer.frames.new(currentFrame)
            # refresh viewport
            gpLayer.hide = not gpLayer.hide
            gpLayer.hide = not gpLayer.hide

    return newLayerKeyFrame


def duplicateLayerKeyFrame(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Duplicate an existing key frame of the specified layer at the specified time frame
    Return the key frame or None when already on a key
    Args:
        layerMode: Can be "NOLAYER", "ACTIVE", "ALL" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """
    newLayerKeyFrame = None
    if "NOLAYER" == layerMode:
        return None
    elif "ALL" == layerMode:
        for layer in gpencil.data.layers:
            if not layer.lock:
                if not isCurrentFrameOnLayerKeyFrame(gpencil, currentFrame, layer.info):
                    prevFrame = getLayerPreviousFrame(gpencil, currentFrame, layer.info)
                    if prevFrame < currentFrame:
                        newLayerKeyFrame = layer.frames.copy(getLayerKeyFrameAtFrame(gpencil, prevFrame, layer.info))
                        newLayerKeyFrame.frame_number = currentFrame
    else:
        if "ACTIVE" == layerMode:
            gpLayer = gpencil.data.layers.active
        else:
            gpLayer = gpencil.data.layers[layerMode]

        if not gpLayer.lock and not isCurrentFrameOnLayerKeyFrame(gpencil, currentFrame, gpLayer.info):
            prevFrame = getLayerPreviousFrame(gpencil, currentFrame, gpLayer.info)
            if prevFrame < currentFrame:
                newLayerKeyFrame = gpLayer.frames.copy(getLayerKeyFrameAtFrame(gpencil, prevFrame, gpLayer.info))
                newLayerKeyFrame.frame_number = currentFrame

    return newLayerKeyFrame


def deleteLayerKeyFrame(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Delete an existing key frame of the specified layer at the specified time frame
    Return the key frame or None when already on a key
    Args:
        layerMode: Can be "NOLAYER", "ACTIVE", "ALL" or the name of the layer
        Usually comes from props.greasePencil_layersMode
    """
    if "NOLAYER" == layerMode:
        return None
    elif "ALL" == layerMode:
        for layer in gpencil.data.layers:
            if not layer.lock:
                layerKeyFrame = getLayerKeyFrameAtFrame(gpencil, currentFrame, layer.info)
                if layerKeyFrame is not None:
                    layer.frames.remove(layerKeyFrame)
    else:
        if "ACTIVE" == layerMode:
            gpLayer = gpencil.data.layers.active
        else:
            gpLayer = gpencil.data.layers[layerMode]

        if not gpLayer.lock:
            layerKeyFrame = getLayerKeyFrameAtFrame(gpencil, currentFrame, gpLayer.info)
            if layerKeyFrame is not None:
                gpLayer.frames.remove(layerKeyFrame)

    return


#################################
# active layers
#################################


def activateGpLayerAndMat(gpencil: bpy.types.GreasePencil, layerName, materialName):
    """If the specified layer is found then activate it on the specified grease pencil object"""

    if layerName in gpencil.data.layers:
        gpencil.data.layers.active = gpencil.data.layers[layerName]

    # Create a lookup-dict for the object materials:
    # mat_dict = {mat.name: i for i, mat in enumerate(context.object.data.materials)}
    mat_dict = {mat.name: i for i, mat in enumerate(gpencil.material_slots)}

    if materialName not in mat_dict:
        _logger.debug_ext(f"SM: Material {materialName} not found in gp materials", col="ORANGE")
        # check in material exist in scene
        gp_mat = bpy.data.materials[materialName] if materialName in bpy.data.materials.keys() else None

        if gp_mat and gpencil:
            gpencil.data.materials.append(gp_mat)
            _logger.debug_ext(f"SM: Material {materialName} ADDED to gp materials", col="ORANGE")
            mat_dict = {mat.name: i for i, mat in enumerate(gpencil.material_slots)}
            # gpencil.active_material = gp_mat
            # return

    if materialName in mat_dict:
        #    _logger.debug_ext(f"SM: Material {materialName} actvated on GP, ind: {mat_dict[materialName]}", col="YELLOW")
        gpencil.active_material_index = mat_dict[materialName]
    else:
        _logger.debug_ext(f"SM: Material {materialName} not found in scene", col="ORANGE")

    # wkip do more generic
    # if "GP_Canvas" == layerName:
    #     if "Canvas Mat" in mat_dict:
    #         gpencil.active_material_index = mat_dict["Canvas Mat"]
    # elif "Lines" == layerName:
    #     if "Lines Mat" in mat_dict:
    #         gpencil.active_material_index = mat_dict["Lines Mat"]
    # elif "Fills" == layerName:
    #     if "Fills Mat" in mat_dict:
    #         gpencil.active_material_index = mat_dict["Fills Mat"]


def toggleLayerVisibility(gpencil: bpy.types.GreasePencil, layerName):
    if layerName in gpencil.data.layers:
        gpencil.data.layers[layerName].hide = not gpencil.data.layers[layerName].hide


def isLayerVisibile(gpencil: bpy.types.GreasePencil, layerName):
    if layerName in gpencil.data.layers:
        return not gpencil.data.layers[layerName].hide
    return False


def gpLayerExists(gpencil: bpy.types.GreasePencil, layerName):
    """Return True if the specified layer is foundon the specified grease pencil object
    Args:
        layerID:    Can be "CANVAS", "BG_INK", "BG_FILL"
    """
    layerExists = False
    if layerName in gpencil.data.layers:
        layerExists = True

    return layerExists


def gpLayerIsActive(gpencil: bpy.types.GreasePencil, layerName):
    """Return True if the specified layer is found and active on the specified grease pencil object
    Args:
        layerID:    Can be "CANVAS", "BG_INK", "BG_FILL"
    """
    layerIsActive = False
    if layerName in gpencil.data.layers and gpencil.data.layers[layerName] == gpencil.data.layers.active:
        layerIsActive = True

    return layerIsActive


# def activeGpLayer(gpencil: bpy.types.GreasePencil, layerID):
#     """If the specified layer is found then active it on the specified grease pencil object
#     Args:
#         layerID:    Can be "CANVAS", "BG_INK", "BG_FILL"
#     """

#     # Create a lookup-dict for the object materials:
#     # mat_dict = {mat.name: i for i, mat in enumerate(context.object.data.materials)}
#     mat_dict = {mat.name: i for i, mat in enumerate(gpencil.material_slots)}

#     if "CANVAS" == layerID:
#         if "GP_Canvas" in gpencil.data.layers:  # or gpencil.data.layers["GP_Canvas"]:
#             gpencil.data.layers.active = gpencil.data.layers["GP_Canvas"]
#             gpencil.active_material_index = mat_dict["Canvas Mat"]

#     elif "BG_INK" == layerID:
#         if "Lines" in gpencil.data.layers:
#             gpencil.data.layers.active = gpencil.data.layers["Lines"]
#             gpencil.active_material_index = mat_dict["Lines Mat"]

#     elif "BG_FILL" == layerID:
#         if "Fills" in gpencil.data.layers:
#             gpencil.data.layers.active = gpencil.data.layers["Fills"]
#             gpencil.active_material_index = mat_dict["Fills Mat"]


# def gpLayerIsActive(gpencil: bpy.types.GreasePencil, layerID):
#     """Return True if the specified layer is found and active on the specified grease pencil object
#     Args:
#         layerID:    Can be "CANVAS", "BG_INK", "BG_FILL"
#     """
#     layerIsActive = False

#     if "CANVAS" == layerID:
#         if "GP_Canvas" in gpencil.data.layers and gpencil.data.layers["GP_Canvas"] == gpencil.data.layers.active:
#             layerIsActive = True
#     elif "BG_INK" == layerID:
#         if "Lines" in gpencil.data.layers and gpencil.data.layers["Lines"] == gpencil.data.layers.active:
#             layerIsActive = True
#     elif "BG_FILL" == layerID:
#         if "Fills" in gpencil.data.layers and gpencil.data.layers["Fills"] == gpencil.data.layers.active:
#             layerIsActive = True

#     return layerIsActive


def place3DCursor(gpencil, currentFrame, layerName):
    from mathutils import Vector

    if layerName in gpencil.data.layers:
        if isCurrentFrameOnLayerKeyFrame(gpencil, currentFrame, layerName):
            timeOfFrame = currentFrame
        else:
            prevFrame = getLayerPreviousFrame(gpencil, currentFrame, layerName)
            if prevFrame != currentFrame:
                timeOfFrame = prevFrame
            else:
                # no key frame exists
                return

        gp_frame = getLayerKeyFrameAtFrame(gpencil, timeOfFrame, layerName)

        # get the average center of mass, optimized by everyNPoints

        everyNPoints = 4
        totalNumPoints = 0
        for s in gp_frame.strokes:
            #    totalNumPoints += len(s.points)
            totalNumPoints += len(s.points) // everyNPoints

        # numStrokes = len(gp_frame.strokes)
        averagePos = Vector([0, 0, 0])
        for s in gp_frame.strokes:
            # numPoints = len(s.points)
            for ind in range(0, len(s.points), everyNPoints):
                averagePos += s.points[ind].co / totalNumPoints

        # newLoc = [0, 0, 0]
        newLoc = averagePos + gpencil.location
        bpy.context.scene.cursor.location = newLoc
