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
Shots global settings operators
"""

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

from shotmanager.utils import utils_greasepencil
from shotmanager.config import config


#####################################################################################
# Operators
#####################################################################################


class UAS_ShotsSettings_UseBackground(Operator):
    bl_idname = "uas_shots_settings.use_background"
    bl_label = "Use Background Images"
    bl_description = "Enable or disable the background images for the shot cameras"
    bl_options = {"INTERNAL", "UNDO"}

    useBackground: BoolProperty(default=False)

    def execute(self, context):
        props = config.getAddonProps(context.scene)

        take = props.getCurrentTake()
        shotList = take.getShotsList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if shot.isCameraValid():
                    shot.camera.data.show_background_images = self.useBackground

        return {"FINISHED"}


class UAS_ShotsSettings_UseBackgroundSound(Operator):
    bl_idname = "uas_shots_settings.use_background_sound"
    bl_label = "Use Background Sound"
    bl_description = "Enable or disable the background sound for the shot cameras"
    bl_options = {"INTERNAL", "UNDO"}

    useBackgroundSound: BoolProperty(default=False)

    def execute(self, context):
        props = config.getAddonProps(context.scene)

        props.useBGSounds = self.useBackgroundSound
        # if self.useBackgroundSound:
        props.enableBGSoundForShot(True, props.getCurrentShot())
        # else:
        #     props.enableBGSoundForShot(False, None)

        return {"FINISHED"}


class UAS_ShotsSettings_UseGreasePencil(Operator):
    bl_idname = "uas_shots_settings.use_greasepencil"
    bl_label = "Use Grease Pencil"
    bl_description = "Enable or disable the grease pencil for the shot cameras"
    bl_options = {"INTERNAL", "UNDO"}

    useGreasepencil: BoolProperty(default=False)

    def execute(self, context):
        props = config.getAddonProps(context.scene)

        take = props.getCurrentTake()
        shotList = take.getShotsList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if shot.isCameraValid():
                    gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)
                    if gp_child is not None:
                        gp_child.hide_viewport = not self.useGreasepencil
                        gp_child.hide_render = not self.useGreasepencil

        return {"FINISHED"}


# class UAS_ShotsSettings_BackgroundAlpha(Operator):
#     bl_idname = "uas_shots_settings.background_alpha"
#     bl_label = "Set Background Opacity"
#     bl_description = "Change the background images opacity for the shot cameras"
#     bl_options = {"INTERNAL", "UNDO"}

#     alpha: FloatProperty(default=0.75)

#     def execute(self, context):
#         props = config.getAddonProps(context.scene)
#         take = props.getCurrentTake()
#         shotList = take.getShotsList(ignoreDisabled=False)

#         for shot in shotList:
#             if shot.isCameraValid() and len(shot.camera.data.background_images):
#                 shot.camera.data.background_images[0].alpha = self.alpha  # globalSettings.backgroundAlpha

#         return {"FINISHED"}


# class UAS_ShotsSettings_BackgroundProxyRenderSize(Operator):
#     bl_idname = "uas_shots_settings.bg_proxy_render_size"
#     bl_label = "proxy Render Size"
#     bl_description = "proxy Render Size"
#     bl_options = {"INTERNAL", "UNDO"}

#     proxyRenderSize: bpy.props.EnumProperty(
#         name="Proxy Render Size",
#         description="Draw preview using full resolution or different proxy resolution",
#         items=(
#             ("PROXY_25", "25%", ""),
#             ("PROXY_50", "50%", ""),
#             ("PROXY_75", "75%", ""),
#             ("PROXY_100", "100%", ""),
#             ("FULL", "None, Full render", ""),
#         ),
#         default="PROXY_50",
#     )

#     def execute(self, context):
#         props = config.getAddonProps(context.scene)
#         take = props.getCurrentTake()
#         shotList = take.getShotsList(ignoreDisabled=False)

#         for shot in shotList:
#             if shot.isCameraValid() and len(shot.camera.data.background_images):
#                 shot.camera.data.background_images[0].clip_user.proxy_render_size = self.proxyRenderSize

#         return {"FINISHED"}


_classes = (
    UAS_ShotsSettings_UseBackground,
    UAS_ShotsSettings_UseBackgroundSound,
    UAS_ShotsSettings_UseGreasePencil,
    # UAS_ShotsSettings_BackgroundAlpha,
    # UAS_ShotsSettings_BackgroundProxyRenderSize,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
