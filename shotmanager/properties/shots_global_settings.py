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
Shots global settings
"""

import bpy
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, BoolProperty, FloatProperty

from shotmanager.utils import utils


class UAS_ShotManager_ShotsGlobalSettings(PropertyGroup):

    alsoApplyToDisabledShots: BoolProperty(
        name="Also Apply to Disabled Shots",
        description="Apply Global Settings changes to disabled shots as well as to enabled ones",
        default=True,
    )

    #########################
    # Camera BG
    #########################

    def _update_backgroundAlpha(self, context):
        props = context.scene.UAS_shot_manager_props
        take = props.getCurrentTake()
        shotList = take.getShotsList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if shot.isCameraValid() and len(shot.camera.data.background_images):
                    # shot.camera.data.background_images[0].alpha = self.backgroundAlpha
                    gamma = 2.2
                    shot.camera.data.background_images[0].alpha = pow(self.backgroundAlpha, gamma)

    backgroundAlpha: FloatProperty(
        name="Background Images Alpha",
        description="Change the opacity of the camera backgrounds",
        soft_min=0.0,
        min=0.0,
        soft_max=1.0,
        max=1.0,
        step=0.1,
        update=_update_backgroundAlpha,
        default=0.9,
    )

    def _update_proxyRenderSize(self, context):
        props = context.scene.UAS_shot_manager_props
        take = props.getCurrentTake()
        shotList = take.getShotsList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if shot.isCameraValid() and len(shot.camera.data.background_images):
                    shot.camera.data.background_images[0].clip_user.proxy_render_size = self.proxyRenderSize

    proxyRenderSize: EnumProperty(
        name="Proxy Render Size",
        description="Draw preview using full resolution or different proxy resolution",
        items=(
            ("PROXY_25", "25%", ""),
            ("PROXY_50", "50%", ""),
            ("PROXY_75", "75%", ""),
            ("PROXY_100", "100%", ""),
            ("FULL", "None, Full render", ""),
        ),
        update=_update_proxyRenderSize,
        # default="PROXY_50",
        default="FULL",
    )

    #########################
    # Storyboard
    #########################

    stb_camPOV_forFreeGP: BoolProperty(
        name="Camera POV for Free Grease Pencil",
        description="Set the camera of the current shot in the viewport when\n"
        "a 2.5D grease pencil object is drawn, and force the stroke draw placement and drawing plane",
        default=True,
    )

    stb_strokePlacement_forFreeGP: EnumProperty(
        name="Stroke Placement for Free Grease Pencil",
        description="Set the stroke placement mode when starting to draw on a grease pencil object",
        items=(
            ("ORIGIN", "Origin", "", "OBJECT_ORIGIN", 0),
            ("CURSOR", "3D Cursor", "", "PIVOT_CURSOR", 1),
        ),
        default="ORIGIN",
    )

    stb_changeCursorPlacement_forFreeGP: BoolProperty(
        name="3D Cursor Placement for Free Grease Pencil",
        description="Place the 3D cursor when starting to draw on a grease pencil object",
        default=True,
    )

    def _update_stb_distanceFromOrigin(self, context):
        props = context.scene.UAS_shot_manager_props
        take = props.getCurrentTake()
        shotList = take.getShotsList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if "STORYBOARD" == shot.shotType:
                    gpProperties = shot.getGreasePencilProps(mode="STORYBOARD")
                    if gpProperties is not None:
                        gpProperties.distanceFromOrigin = self.stb_distanceFromOrigin
                    # if shot.isCameraValid():
                    #     gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)
                    #         if gp_child is not None:
                    #             gp_child.dista = self.stb_distanceFromOrigin

    stb_distanceFromOrigin: FloatProperty(
        name="Storyboard Global Frame Distance",
        description="Apply this distance to all shots of type storyboard between the storyboard frame and its parent camera",
        subtype="DISTANCE",
        soft_min=0.02,
        min=0.001,
        soft_max=10.0,
        # max=1.0,
        step=0.1,
        update=_update_stb_distanceFromOrigin,
        default=2.0,
    )

    def _update_stb_show_passepartout(self, context):
        props = context.scene.UAS_shot_manager_props
        take = props.getCurrentTake()
        shotList = take.getShotsList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                # if "STORYBOARD" == shot.shotType and shot.isCameraValid():
                if shot.isCameraValid():
                    shot.camera.data.show_passepartout = self.stb_show_passepartout

    stb_show_passepartout: BoolProperty(
        name="Storyboard Global Passepartout",
        description="Show passepartout opacity on storygoard frame cameras",
        update=_update_stb_show_passepartout,
        default=True,
    )

    def _update_stb_passepartout_alpha(self, context):
        props = context.scene.UAS_shot_manager_props
        take = props.getCurrentTake()
        shotList = take.getShotsList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                # if "STORYBOARD" == shot.shotType and shot.isCameraValid():
                if shot.isCameraValid():
                    shot.camera.data.show_passepartout = True
                    shot.camera.data.passepartout_alpha = pow(self.stb_passepartout_alpha, 0.3)

    stb_passepartout_alpha: FloatProperty(
        name="Storyboard Global Passepartout Alpha",
        description="Set the value of the passepartout opacity on storygoard frame cameras",
        min=0.0,
        max=1.0,
        step=0.05,
        update=_update_stb_passepartout_alpha,
        default=0.2,
    )

    #########################
    # Sound
    #########################

    def _update_backgroundVolume(self, context):
        props = context.scene.UAS_shot_manager_props
        take = props.getCurrentTake()
        shotList = take.getShotsList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if shot.isCameraValid() and len(shot.camera.data.background_images):
                    # shot.camera.data.background_images[0].alpha = self.backgroundAlpha
                    #   gamma = 2.2
                    #   shot.camera.data.background_images[0].alpha = pow(self.backgroundAlpha, gamma)
                    pass

    backgroundVolume: FloatProperty(
        name="Background Volume",
        description="Change the volume of the camera backgrounds sound",
        soft_min=0.0,
        min=0.0,
        soft_max=3.0,
        max=30.0,
        step=0.1,
        update=_update_backgroundVolume,
        default=1.0,
    )

    #########################
    # Grease Pencil
    #########################

    def _update_greasepencilAlpha(self, context):
        props = context.scene.UAS_shot_manager_props
        take = props.getCurrentTake()
        shotList = take.getShotsList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if shot.isCameraValid() and len(shot.camera.data.background_images):
                    # shot.camera.data.background_images[0].alpha = self.backgroundAlpha
                    gamma = 2.2
                    shot.camera.data.background_images[0].alpha = pow(self.backgroundAlpha, gamma)

    greasepencilAlpha: FloatProperty(
        name="Grease Pencil Alpha",
        description="Change the opacity of the grease pencils",
        soft_min=0.0,
        min=0.0,
        soft_max=1.0,
        max=1.0,
        step=0.1,
        update=_update_greasepencilAlpha,
        default=0.9,
    )


_classes = (UAS_ShotManager_ShotsGlobalSettings,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
