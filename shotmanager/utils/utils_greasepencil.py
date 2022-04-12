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
            gpencil_layer = gpencil.data.layers.new(gpencil_layer_name, set_active=True)

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

    ######################################""""""
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


def getLayerPreviousFrame(gpencil: bpy.types.GreasePencil, currentFrame, layerMode):
    """Return the frame value of the previous key of the specified layer
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


def activeGpLayerAndMat(gpencil: bpy.types.GreasePencil, layerName):
    """If the specified layer is found then active it on the specified grease pencil object"""

    # Create a lookup-dict for the object materials:
    # mat_dict = {mat.name: i for i, mat in enumerate(context.object.data.materials)}
    mat_dict = {mat.name: i for i, mat in enumerate(gpencil.material_slots)}

    if layerName in gpencil.data.layers:
        gpencil.data.layers.active = gpencil.data.layers[layerName]

    # wkip do more generic
    if "GP_Canvas" == layerName:
        if "Canvas Mat" in mat_dict:
            gpencil.active_material_index = mat_dict["Canvas Mat"]
    elif "Lines" == layerName:
        if "Lines Mat" in mat_dict:
            gpencil.active_material_index = mat_dict["Lines Mat"]
    elif "Fills" == layerName:
        if "Fills Mat" in mat_dict:
            gpencil.active_material_index = mat_dict["Fills Mat"]


def gpLayerIsActive(gpencil: bpy.types.GreasePencil, layerName):
    """Return True if the specified layer is found and active on the specified grease pencil object
    Args:
        layerID:    Can be "CANVAS", "BG_INK", "BG_FILL"
    """
    layerIsActive = False
    if layerName in gpencil.data.layers and gpencil.data.layers[layerName] == gpencil.data.layers.active:
        layerIsActive = True

    return layerIsActive


def getGpLayerNameFromID(gpencil: bpy.types.GreasePencil, layerID):
    """Return the layer name if the specified layer is found on the specified grease pencil object
    Args:
        layerID:    Can be "CANVAS", "BG_INK", "BG_FILL"
    """
    gpLayerName = None

    if "CANVAS" == layerID:
        if "GP_Canvas" in gpencil.data.layers:
            gpLayerName = "GP_Canvas"
            # gpLayer = gpencil.data.layers["GP_Canvas"]
    elif "BG_INK" == layerID:
        if "Lines" in gpencil.data.layers:
            gpLayerName = "Lines"
            # gpLayer = gpencil.data.layers["Lines"]
    elif "BG_FILL" == layerID:
        if "Fills" in gpencil.data.layers:
            gpLayerName = "Fills"
            # gpLayer = gpencil.data.layers["Fills"]

    return gpLayerName


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
