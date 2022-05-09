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
Grease pencil functions specific to Shot Manager
"""

import bpy

from shotmanager.utils import utils
from shotmanager.utils import utils_greasepencil


def createStoryboarFrameGP(gp_name, framePreset, parentCamera=None, location=None, locate_on_cursor=False):
    """Create a new grease pencil object that will be used as a storyboard frame
    Return this object
    Args:   parentCamera: the camera to parent to
    """
    scene = bpy.context.scene

    # empty intermediate object
    ####################
    # no data to specify for empty objects
    gpEmpty = bpy.data.objects.new("empty", None)
    scene.collection.objects.link(gpEmpty)
    gpEmpty.name = gp_name + "_empty"

    gpEmpty.empty_display_size = 0.5
    gpEmpty.empty_display_type = "ARROWS"  # "PLAIN_AXES"

    gpEmpty.lock_location = [True, True, True]
    gpEmpty.lock_rotation = [True, True, True]
    gpEmpty.lock_scale = [True, True, True]

    # add to main collection
    # bpy.context.collection.objects.link(gpencil)

    # add empty object to a specific collection
    emptyCollectionName = "SM_Storyboard_Empties"
    cpColl = None
    if emptyCollectionName not in scene.collection.children:
        cpColl = bpy.data.collections.new(name=emptyCollectionName)
        scene.collection.children.link(cpColl)
    else:
        cpColl = scene.collection.children[emptyCollectionName]
    utils.excludeLayerCollection(scene, emptyCollectionName, True)
    cpColl.objects.link(gpEmpty)

    # for some reason the empty also belongs to the scence collection, so we remove it from there
    scene.collection.objects.unlink(gpEmpty)

    # grease pencil frame
    ####################
    gpencil_data = bpy.data.grease_pencils.new(gp_name)
    gpencil = bpy.data.objects.new(gpencil_data.name, gpencil_data)
    gpencil.name = gpencil_data.name

    gpencil.use_grease_pencil_lights = False

    # add grease pencil object to a specific collection
    gpCollectionName = "SM_Storyboard_Frames"
    cpColl = None
    if gpCollectionName not in scene.collection.children:
        cpColl = bpy.data.collections.new(name=gpCollectionName)
        scene.collection.children.link(cpColl)
    else:
        cpColl = scene.collection.children[gpCollectionName]
    cpColl.objects.link(gpencil)

    if parentCamera is not None:
        gpEmpty.parent = parentCamera
    gpencil.parent = gpEmpty

    if location is None:
        gpencil.location = [0, 0, 0]
    elif locate_on_cursor:
        gpencil.location = scene.cursor.location
    else:
        gpencil.location = location

    gpencil.lock_location = [True, True, True]
    gpencil.lock_rotation = [True, True, True]
    gpencil.lock_scale = [True, True, True]
    # gpencil.lock_rotation[0] = True
    # gpencil.lock_rotation[1] = True

    # from math import radians

    # # align gp with camera axes
    # gpencil.rotation_euler = (radians(0.0), 0.0, radians(0.0))

    createStoryboarFrameLayers(gpencil, framePreset)
    utils_greasepencil.create_grease_pencil_material(gpencil, "LINES")
    utils_greasepencil.create_grease_pencil_material(gpencil, "FILLS")

    canvasPreset = framePreset.getPresetByID("CANVAS")
    utils_greasepencil.add_grease_pencil_canvas_layer(gpencil, canvasPreset, order="BOTTOM", camera=parentCamera)

    if len(gpencil.data.layers):
        gpencil.data.layers.active = gpencil.data.layers[len(gpencil.data.layers) - 1]

    return gpencil


def createStoryboarFrameLayers(gpencil: bpy.types.GreasePencil, framePreset, clear_layer=False, order="TOP"):
    """Canvas layer is not created here - Use utils_greasepencil.add_grease_pencil_canvas_layer"""
    for preset in framePreset.usagePresets:
        if "CANVAS" != preset.id and preset.used:
            gpencil_layer = utils_greasepencil.add_grease_pencil_layer(
                gpencil, gpencil_layer_name=preset.layerName, clear_layer=True, order=order
            )


def setInkLayerReadyToDraw(gpencil: bpy.types.GreasePencil):
    # wkipwkipwkip
    return
    inkLayer = None
    if gpencil.data.layers["Lines"] is not None:
        inkLayer = gpencil.data.layers["Lines"]

    gpencil.data.layers.active = inkLayer

    # create frame


# bpy.ops.gpencil.blank_frame_add(all_layers=False)
