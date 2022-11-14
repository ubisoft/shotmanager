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
Global Render properties
"""

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_RenderGlobalContext(PropertyGroup):

    renderHardwareMode: EnumProperty(
        name="Render Mode",
        description="Use the specified render engine or the OpenGL mode",
        items=(
            ("SOFTWARE", "Software", "Use CPU renderer"),
            ("OPENGL", "OpenGL", "Use OpenGL hardware accelerated renderer"),
        ),
        default="OPENGL",
        options=set(),
    )

    # dev only
    renderFrameIterationMode: EnumProperty(
        name="Frame Iteration Mode",
        description="Use animation rendering mode or render each frame independently in a loop (*** Dev. purpose only ***)",
        items=(
            ("ANIM", "Anim.", "Images are rendered as a sequence"),
            ("LOOP", "Loop", "Images are computed independently, in a custom loop"),
        ),
        default="ANIM",
        options=set(),
    )

    def _update_renderEngine(self, context):
        pass

    renderEngine: EnumProperty(
        name="Render Engine",
        description="Set the Render Engine to use for the rendering",
        items=(
            ("BLENDER_EEVEE", "Eevee", ""),
            ("BLENDER_WORKBENCH", "Workbench", ""),
            ("CYCLES", "Cycles", ""),
            ("CUSTOM", "From Scene", "Use the settings present in the current scene. No other settings are applied"),
        ),
        default="BLENDER_EEVEE",
        update=_update_renderEngine,
    )

    renderEngineOpengl: EnumProperty(
        name="Render Engine Opengl",
        description="Set the Render Engine to use for the playblast rendering",
        items=(
            ("BLENDER_EEVEE", "Eevee", ""),
            ("BLENDER_WORKBENCH", "Workbench", ""),
            ("CUSTOM", "From Scene", "Use the settings present in the current scene. No other settings are applied"),
        ),
        default="BLENDER_EEVEE",
        # update=_update_renderEngine,
    )

    useOverlays: BoolProperty(
        name="With Overlays",
        description=(
            "Render overlays when the renderer is Eevee or the rendering is a playblast"
            "\nWarning: The overlay settings that will be used are the ones from THIS VIEWPORT,"
            "\neven if Shot Manager is set do be used on another target viewport"
        ),
        default=False,
        options=set(),
    )

    def _update_renderQuality(self, context):
        self.applyRenderQualitySettings(context, renderQuality=self.renderQuality)

    renderQuality: EnumProperty(
        name="Render Quality",
        description="Set the Render Quality settings to use for the rendering.\nSettings are applied immediatly.",
        items=(
            # ("VERY_LOW", "Very Low (faster)", ""),
            ("LOW", "Low (faster)", ""),
            ("MEDIUM", "Medium", ""),
            ("HIGH", "High (slower)", ""),
            ("CUSTOM", "From Scene", "Use the settings present in the current scene. No other settings are applied"),
        ),
        default="LOW",
        update=_update_renderQuality,
    )

    def _update_renderQualityOpengl(self, context):
        self.applyRenderQualitySettingsOpengl(context, renderQuality=self.renderQualityOpengl)

    renderQualityOpengl: EnumProperty(
        name="Render Quality OpenGL",
        description="Set the Render Quality settings to use for the rendering.\nSettings are applied immediatly.",
        items=(
            # ("VERY_LOW", "Very Low (faster)", ""),
            ("LOW", "Low (faster)", ""),
            ("MEDIUM", "Medium", ""),
            ("HIGH", "High (slower)", ""),
            ("CUSTOM", "From Scene", "Use the settings present in the current scene. No other settings are applied"),
        ),
        default="LOW",
        update=_update_renderQualityOpengl,
    )

    def applyRenderQualitySettings(self, context, renderQuality=None):
        # wkip les Quality Settings devraient etre globales au fichier

        if renderQuality is None:
            renderQuality = self.renderQuality

        # props = config.getAddonProps(context.scene)
        # bpy.context.space_data.overlay.show_overlays = props.useOverlays

        if "VERY_LOW" == renderQuality:
            # eevee
            context.scene.eevee.taa_render_samples = 1
            #    context.scene.eevee.taa_samples = 1

            # workbench
            # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
            context.scene.display.render_aa = "OFF"
            #    context.scene.display.viewport_aa = "OFF"

            # cycles
            context.scene.cycles.samples = 1
        #    context.scene.cycles.preview_samples = 1

        elif "LOW" == renderQuality:
            # eevee
            context.scene.eevee.taa_render_samples = 6
            #    context.scene.eevee.taa_samples = 2

            # workbench
            # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
            context.scene.display.render_aa = "FXAA"
            #    context.scene.display.viewport_aa = "OFF"

            # cycles
            context.scene.cycles.samples = 6
        #    context.scene.cycles.preview_samples = 2

        elif "MEDIUM" == renderQuality:
            # eevee
            context.scene.eevee.taa_render_samples = 32  # 64
            #    context.scene.eevee.taa_samples = 6  # 16

            # workbench
            # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
            context.scene.display.render_aa = "5"
            #    context.scene.display.viewport_aa = "FXAA"

            # cycles
            context.scene.cycles.samples = 64
        #    context.scene.cycles.preview_samples = 16

        elif "HIGH" == renderQuality:
            # eevee
            context.scene.eevee.taa_render_samples = 64  # 128
            #    context.scene.eevee.taa_samples = 12  # 32

            # workbench
            #            if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
            context.scene.display.render_aa = "16"
            #    context.scene.display.viewport_aa = "5"

            # cycles
            context.scene.cycles.samples = 128
        #    context.scene.cycles.preview_samples = 32

        # CUSTOM
        else:
            # we use the scene settings
            pass

        return

    def applyRenderQualitySettingsOpengl(self, context, renderQuality=None):
        # wkip les Quality Settings devraient etre globales au fichier

        if renderQuality is None:
            renderQuality = self.renderQualityOpengl

        # props = config.getAddonProps(context.scene)
        # bpy.context.space_data.overlay.show_overlays = props.useOverlays

        if "VERY_LOW" == renderQuality:
            # eevee
            #    context.scene.eevee.taa_render_samples = 1
            context.scene.eevee.taa_samples = 1

            # workbench
            # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
            #    context.scene.display.render_aa = "OFF"
            context.scene.display.viewport_aa = "OFF"

            # cycles
            #    context.scene.cycles.samples = 1
            context.scene.cycles.preview_samples = 1

        elif "LOW" == renderQuality:
            # eevee
            #    context.scene.eevee.taa_render_samples = 6
            context.scene.eevee.taa_samples = 2

            # workbench
            # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
            #    context.scene.display.render_aa = "FXAA"
            context.scene.display.viewport_aa = "OFF"

            # cycles
            #    context.scene.cycles.samples = 6
            context.scene.cycles.preview_samples = 2

        elif "MEDIUM" == renderQuality:
            # eevee
            #    context.scene.eevee.taa_render_samples = 32  # 64
            context.scene.eevee.taa_samples = 6  # 16

            # workbench
            # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
            #    context.scene.display.render_aa = "5"
            context.scene.display.viewport_aa = "FXAA"

            # cycles
            #    context.scene.cycles.samples = 64
            context.scene.cycles.preview_samples = 16

        elif "HIGH" == renderQuality:
            # eevee
            #    context.scene.eevee.taa_render_samples = 64  # 128
            context.scene.eevee.taa_samples = 12  # 32

            # workbench
            #            if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
            #    context.scene.display.render_aa = "16"
            context.scene.display.viewport_aa = "5"

            # cycles
            #    context.scene.cycles.samples = 128
            context.scene.cycles.preview_samples = 32

        # CUSTOM
        else:
            # we use the scene settings
            pass

        return

    def applyBurnInfos(self, context, enabled=True):
        context.scene.render.use_stamp = enabled
        if enabled:
            context.scene.render.use_stamp_scene = True
            context.scene.render.use_stamp_frame = True
            context.scene.render.use_stamp_date = True
            context.scene.render.use_stamp_time = True

        # scene.render.use_stamp_note = True
