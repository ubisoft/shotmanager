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
Shot Manager grease pencil operators

For more information read: https://blender.stackexchange.com/questions/162459/access-viewport-overlay-options-using-python-api
"""

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty

from shotmanager.utils import utils

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def getOverlaysPropertyState(context, propName):
    """Return the state of the specified overlay property according to the viewport mode of the Shot Manager Properties
    used in the specified context.
    Args:
            propName:   the name of the property to check"""
    props = config.getAddonProps(context.scene)
    applyToAllViewports = "ALL" == props.shotsGlobalSettings.stb_overlaysViewportMode
    propState = False
    if applyToAllViewports:
        spaceDatas = utils.getViewportsSpaceData(context)
        for spaceDataViewport in spaceDatas:
            viewportPropState = getattr(spaceDataViewport.overlay, propName, None)
            if viewportPropState:
                return True
    else:
        spaceDataViewport = props.getValidTargetViewportSpaceData(context)
        if spaceDataViewport is not None:
            viewportPropState = getattr(spaceDataViewport.overlay, propName, None)
            if viewportPropState:
                return True
    return propState


class UAS_ShotManager_Overlays_ToggleOverlays(Operator):
    bl_idname = "uas_shot_manager.overlays_toggleoverlays"
    bl_label = "Overlays"
    bl_description = "Toggle Grease Pencil viewport overlays for the specifed viewports"
    bl_options = {"INTERNAL"}

    allViewports: BoolProperty(
        name="Apply to All Viewports",
        default=True,
    )
    newState: BoolProperty(
        name="New State",
        default=True,
    )

    def execute(self, context):
        if self.allViewports:
            spaceDatas = utils.getViewportsSpaceData(context)
            for spaceDataViewport in spaceDatas:
                spaceDataViewport.overlay.show_overlays = self.newState
        else:
            props = config.getAddonProps(context.scene)
            spaceDataViewport = props.getValidTargetViewportSpaceData(context)
            if spaceDataViewport is not None:
                spaceDataViewport.overlay.show_overlays = self.newState

        return {"FINISHED"}


class UAS_ShotManager_Overlays_ToggleOnionSkin(Operator):
    bl_idname = "uas_shot_manager.overlays_toggleonionskin"
    bl_label = "Onion Skin"
    bl_description = "Toggle Grease Pencil viewport overlay onion skin for the specifed viewports"
    bl_options = {"INTERNAL"}

    allViewports: BoolProperty(
        name="Apply to All Viewports",
        default=True,
    )
    newState: BoolProperty(
        name="New State",
        default=True,
    )

    def execute(self, context):
        if self.allViewports:
            spaceDatas = utils.getViewportsSpaceData(context)
            for spaceDataViewport in spaceDatas:
                # spaceDataViewport.overlay.use_gpencil_onion_skin = not spaceDataViewport.overlay.use_gpencil_onion_skin
                spaceDataViewport.overlay.use_gpencil_onion_skin = self.newState
        else:
            props = config.getAddonProps(context.scene)
            spaceDataViewport = props.getValidTargetViewportSpaceData(context)
            if spaceDataViewport is not None:
                # spaceDataViewport.overlay.use_gpencil_onion_skin = not spaceDataViewport.overlay.use_gpencil_onion_skin
                spaceDataViewport.overlay.use_gpencil_onion_skin = self.newState

        return {"FINISHED"}


class UAS_ShotManager_Overlays_ToggleGrid(Operator):
    bl_idname = "uas_shot_manager.overlays_togglegrid"
    bl_label = "Canvas"
    bl_description = "Toggle Grease Pencil viewport overlay grid for the specifed viewports"
    bl_options = {"INTERNAL"}

    allViewports: BoolProperty(
        name="Apply to All Viewports",
        default=True,
    )
    newState: BoolProperty(
        name="New State",
        default=True,
    )

    def execute(self, context):
        if self.allViewports:
            spaceDatas = utils.getViewportsSpaceData(context)
            for spaceDataViewport in spaceDatas:
                spaceDataViewport.overlay.use_gpencil_grid = self.newState
        else:
            props = config.getAddonProps(context.scene)
            spaceDataViewport = props.getValidTargetViewportSpaceData(context)
            if spaceDataViewport is not None:
                spaceDataViewport.overlay.use_gpencil_grid = self.newState

        return {"FINISHED"}


class UAS_ShotManager_Overlays_GridOpacity(Operator):
    bl_idname = "uas_shot_manager.overlays_gridopacity"
    bl_label = "Canvas Opacity"
    bl_description = "Set the Grease Pencil viewport overlay grid (or Canvas) value for the specifed viewports"
    bl_options = {"INTERNAL"}

    allViewports: BoolProperty(
        name="Apply to All Viewports",
        default=True,
    )
    opacity: FloatProperty(
        name="Opacity",
        default=1.0,
    )

    def execute(self, context):
        if self.allViewports:
            spaceDatas = utils.getViewportsSpaceData(context)
            for spaceDataViewport in spaceDatas:
                spaceDataViewport.overlay.gpencil_grid_opacity = self.opacity
        else:
            props = config.getAddonProps(context.scene)
            spaceDataViewport = props.getValidTargetViewportSpaceData(context)
            if spaceDataViewport is not None:
                spaceDataViewport.overlay.gpencil_grid_opacity = self.opacity

        return {"FINISHED"}


class UAS_ShotManager_Overlays_ToggleGridToFront(Operator):
    bl_idname = "uas_shot_manager.overlays_togglegridtofront"
    bl_label = "Canvas X-Ray"
    bl_description = "Toggle canvas grid between front and back for the specifed viewports"
    bl_options = {"INTERNAL"}

    allViewports: BoolProperty(
        name="Apply to All Viewports",
        default=True,
    )
    newState: BoolProperty(
        name="New State",
        default=True,
    )

    def execute(self, context):
        if self.allViewports:
            spaceDatas = utils.getViewportsSpaceData(context)
            for spaceDataViewport in spaceDatas:
                spaceDataViewport.overlay.use_gpencil_canvas_xray = self.newState
        else:
            props = config.getAddonProps(context.scene)
            spaceDataViewport = props.getValidTargetViewportSpaceData(context)
            if spaceDataViewport is not None:
                spaceDataViewport.overlay.use_gpencil_canvas_xray = self.newState

        return {"FINISHED"}


class UAS_ShotManager_Overlays_ToggleFadeLayers(Operator):
    bl_idname = "uas_shot_manager.overlays_togglefadelayers"
    bl_label = "Fade Layers"
    bl_description = "Toggle Grease Pencil viewport overlay fade layers for the specifed viewports"
    bl_options = {"INTERNAL"}

    allViewports: BoolProperty(
        name="Apply to All Viewports",
        default=True,
    )
    newState: BoolProperty(
        name="New State",
        default=True,
    )

    def execute(self, context):
        if self.allViewports:
            spaceDatas = utils.getViewportsSpaceData(context)
            for spaceDataViewport in spaceDatas:
                spaceDataViewport.overlay.use_gpencil_fade_layers = self.newState
        else:
            props = config.getAddonProps(context.scene)
            spaceDataViewport = props.getValidTargetViewportSpaceData(context)
            if spaceDataViewport is not None:
                spaceDataViewport.overlay.use_gpencil_fade_layers = self.newState

        return {"FINISHED"}


class UAS_ShotManager_Overlays_FadeLayersOpacity(Operator):
    bl_idname = "uas_shot_manager.overlays_fadelayersopacity"
    bl_label = "Fade Layers Opacity"
    bl_description = "Set the Grease Pencil viewport overlay fade layers value for the specifed viewports"
    bl_options = {"INTERNAL"}

    allViewports: BoolProperty(
        name="Apply to All Viewports",
        default=True,
    )
    opacity: FloatProperty(
        name="Opacity",
        default=1.0,
    )

    def execute(self, context):
        if self.allViewports:
            spaceDatas = utils.getViewportsSpaceData(context)
            for spaceDataViewport in spaceDatas:
                spaceDataViewport.overlay.gpencil_fade_layer = self.opacity
        else:
            props = config.getAddonProps(context.scene)
            spaceDataViewport = props.getValidTargetViewportSpaceData(context)
            if spaceDataViewport is not None:
                spaceDataViewport.overlay.gpencil_fade_layer = self.opacity

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_Overlays_ToggleOverlays,
    UAS_ShotManager_Overlays_ToggleOnionSkin,
    UAS_ShotManager_Overlays_ToggleGrid,
    UAS_ShotManager_Overlays_GridOpacity,
    UAS_ShotManager_Overlays_ToggleGridToFront,
    UAS_ShotManager_Overlays_ToggleFadeLayers,
    UAS_ShotManager_Overlays_FadeLayersOpacity,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
