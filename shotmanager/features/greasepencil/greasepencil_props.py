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
Grease pencil shot class
"""

import bpy
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, FloatProperty, FloatVectorProperty, BoolProperty, EnumProperty

# from shotmanager.properties.shot import UAS_ShotManager_Shot

from shotmanager.utils import utils_greasepencil, utils


class GreasePencilProperties(PropertyGroup):
    """Contains the grease pencil information and properties related to the shot.
    Each shot has an array of GreasePencilProperties items, the first one is used for storyboard frame"""

    # parentShot: PointerProperty(type=UAS_ShotManager_Shot)
    parentCamera: PointerProperty(
        name="Camera", description="Camera parent of the grease pencil object", type=bpy.types.Object
    )

    frameMode: EnumProperty(
        name="Frame Mode",
        description="grease Pencil usage",
        items=(("STORYBOARD", "Storyboard", "Storyboard frame properties"),),
        default="STORYBOARD",
    )

    def initialize(self, parentShot, mode="STORYBOARD"):
        """Set the parent camera of the Grease Pencil Properties"""
        prefs = bpy.context.preferences.addons["shotmanager"].preferences
        # print(f"\nInitializing new Grease Pencil Properties for shot {parentShot.name}...")

        self.parentCamera = parentShot.camera
        self.frameMode = mode
        self.canvasOpacity = prefs.storyboard_default_canvas_opacity

    def getParentShot(self):
        props = bpy.context.scene.UAS_shot_manager_props
        for take in props.takes:
            for shot in take.shots:
                for gpProps in shot.greasePencils:
                    if gpProps == self:
                        return shot
        return None

    def _update_distanceFromOrigin(self, context):
        # print("distanceFromOrigin")
        utils_greasepencil.fitGreasePencilToFrustum(self.parentCamera, self.distanceFromOrigin)

    distanceFromOrigin: FloatProperty(
        name="Distance",
        description="Distance between the storyboard frame and the parent camera",
        subtype="DISTANCE",
        soft_min=0.02,
        min=0.001,
        soft_max=10.0,
        # max=1.0,
        step=0.1,
        update=_update_distanceFromOrigin,
        default=0.5,
        options=set(),
    )

    def _update_visibility(self, context):
        self.getParentShot().showGreasePencil()

    visibility: EnumProperty(
        name="Frame Visibility",
        description="Visibility",
        items=(
            ("ALWAYS_VISIBLE", "Visible", "Storyboard frame is always visible"),
            ("ALWAYS_HIDDEN", "Hidden", "Storyboard frame is always hidden"),
            ("AUTO", "Auto", "Storyboard frame is automaticaly shown or hidden"),
        ),
        update=_update_visibility,
        default="AUTO",
        options=set(),
    )

    def _update_canvasOpacity(self, context):
        # print("canvasOpacity")
        gp_child = utils_greasepencil.get_greasepencil_child(self.parentCamera)
        if gp_child is not None:
            props = context.scene.UAS_shot_manager_props
            canvasPreset = props.stb_frameTemplate.getPresetByID("CANVAS")
            canvasName = "_Canvas_" if canvasPreset is None else canvasPreset.layerName

            canvasLayer = utils_greasepencil.get_grease_pencil_layer(
                gp_child, gpencil_layer_name=canvasName, create_layer=False
            )
            if canvasLayer is not None:
                canvasLayer.opacity = utils.to_sRGB(self.canvasOpacity)

    canvasOpacity: FloatProperty(
        name="Canvas Opacity",
        description="Opacity of the Canvas layer",
        min=0.0,
        max=1.0,
        step=0.05,
        update=_update_canvasOpacity,
        default=1.0,
        options=set(),
    )

    def _update_canvasSize(self, context):
        # print("_update_canvasSize")
        if self.getCanvasLayer() is not None:
            self.updateGreasePencil()

    canvasSize: FloatVectorProperty(
        name="Size",
        description="Canvas Size",
        min=0.02,
        soft_max=3.0,
        size=2,
        update=_update_canvasSize,
        default=(1.0, 1.0),
        options=set(),
    )

    def copyPropertiesFrom(self, sourceGpProps):
        """Copy the value of the properties of the specified GreasePencilProperties instance to this one
        Camera value will not be changed.
        """
        self.frameMode = sourceGpProps.frameMode
        self.visibility = sourceGpProps.visibility
        self.distanceFromOrigin = sourceGpProps.distanceFromOrigin
        self.canvasOpacity = sourceGpProps.canvasOpacity
        self.canvasSize = sourceGpProps.canvasSize

        self.updateGreasePencil()

    def updateGreasePencil(self):
        self.updateCanvas()
        self.updateGreasePencilToFrustum()

    def updateCanvas(self):
        props = bpy.context.scene.UAS_shot_manager_props

        # res = props.getRenderResolution()
        renderRatio = props.getRenderAspectRatio()
        # print(f"ResX: {res[0]}, resY: {res[1]}, ratio: {renderRatio}")

        # canvas opacity
        self.canvasOpacity = self.canvasOpacity

        # canvas size

        # we are in a fit width convention
        heightSize = self.canvasSize[1]
        heightChangesWithRatio = True
        if heightChangesWithRatio:
            heightSize = self.canvasSize[1] * 1.0 / renderRatio

        canvasLayer = self.getCanvasLayer()
        if canvasLayer is not None:
            if len(canvasLayer.frames):
                gpFrame = canvasLayer.frames[0]
                if len(gpFrame.strokes):
                    gpStroke = gpFrame.strokes[0]
                    if 4 == len(gpStroke.points):

                        # gpStroke.display_mode = "3DSPACE"  # allows for editing

                        top_left = (-1.0 * self.canvasSize[0] / 2.0, -1.0 * heightSize / 2.0, 0.0)
                        bottom_right = (self.canvasSize[0] / 2.0, heightSize / 2.0, 0.0)

                        gpStroke.points[0].co = top_left
                        gpStroke.points[1].co = (bottom_right[0], top_left[1], top_left[2])
                        gpStroke.points[2].co = bottom_right
                        gpStroke.points[3].co = (top_left[0], bottom_right[1], bottom_right[2])

    def updateGreasePencilToFrustum(self):
        utils_greasepencil.fitGreasePencilToFrustum(self.parentCamera, self.distanceFromOrigin)

    def getCanvasLayer(self):
        props = bpy.context.scene.UAS_shot_manager_props
        canvasPreset = props.stb_frameTemplate.getPresetByID("CANVAS")
        canvasName = "_Canvas_" if canvasPreset is None else canvasPreset.layerName

        gp_child = utils_greasepencil.get_greasepencil_child(self.parentCamera)

        canvasLayer = utils_greasepencil.get_grease_pencil_layer(
            gp_child, gpencil_layer_name=canvasName, create_layer=False
        )
        return canvasLayer

    # def __init__(self, parent, shot):
    #     self._distance = 0

    # @property
    # def distance(self):
    #     return self._distance

    # @distance.setter
    # def distance(self, value):
    #     self._distance = value

    # def get_grease_pencil(self):
    #     return utils_greasepencil


_classes = (GreasePencilProperties,)


def register():
    pass
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
