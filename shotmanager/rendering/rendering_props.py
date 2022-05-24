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
Render properties
"""

from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty

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
        description="Also render overlays when the rendering is a playblast",
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

        # props = context.scene.UAS_shot_manager_props
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

        # props = context.scene.UAS_shot_manager_props
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

    def applyBurnInfos(self, context):
        context.scene.render.use_stamp = True
        context.scene.render.use_stamp_scene = True
        context.scene.render.use_stamp_frame = True
        context.scene.render.use_stamp_date = True
        context.scene.render.use_stamp_time = True

        # scene.render.use_stamp_note = True


class UAS_ShotManager_RenderSettings(PropertyGroup):

    name: StringProperty(name="Name", default="Render Settings")

    renderMode: EnumProperty(
        name="Render Mode",
        description="Render Mode",
        items=(
            ("STILL", "Still", ""),
            ("ANIMATION", "Animation", ""),
            ("ALL", "All Edits", ""),
            ("OTIO", "Otio", ""),
            ("PLAYBLAST", "PLAYBLAST", ""),
        ),
        default="STILL",
    )

    # properties are initialized according to their use in the function props.createRenderSettings()

    renderAllTakes: BoolProperty(name="Render All Takes", default=False)

    renderAllShots: BoolProperty(name="Render All Shots", default=True)

    renderAlsoDisabled: BoolProperty(name="Render Also Disabled Shots", default=False)

    renderHandles: BoolProperty(name="Render With Handles", default=False)

    renderSound: BoolProperty(
        name="Render Sound",
        description="Also generate sound in rendered media",
        default=True,
    )

    disableCameraBG: BoolProperty(
        name="Disable Camera BG",
        description="Disable camera background images for openGl rendering, when overlay is activated",
        default=True,
    )

    # only used by STILL
    writeToDisk: BoolProperty(name="Write to Disk", default=False)

    # used by EDIT, ANIMATION and ALL
    renderOtioFile: BoolProperty(
        name="Generate Edit File",
        description="Generate edit file for the current take." "\nOnly videos are supported at the moment",
        default=False,
    )

    useStampInfo: BoolProperty(name="Use Stamp Info", default=True)

    rerenderExistingShotVideos: BoolProperty(name="Re-render Exisiting Shot Videos", default=True)

    bypass_rendering_project_settings: BoolProperty(
        name="Bypass Project Settings",
        description="When Project Settings are used this allows the use of custom rendering settings",
        default=False,
        #    options=set(),
    )

    # used by ANIMATION and ALL
    # wkipwkipwkip not used!!!
    generateImageSequence: BoolProperty(
        name="Generate Image Sequence",
        description="Generate an image sequence per rendered shot",
        default=False,
    )

    outputMediaMode: EnumProperty(
        name="Output Media Format",
        description="Output media to generate during the rendering process",
        items=(
            ("IMAGE_SEQ", "Image Sequences", ""),
            ("VIDEO", "Videos", ""),
            ("IMAGE_SEQ_AND_VIDEO", "Image Sequences and Videos", ""),
        ),
        default="VIDEO",
    )

    # used by ANIMATION and ALL
    keepIntermediateFiles: BoolProperty(
        name="Keep Intermediate Rendering Images",
        description="Keep the rendered and Stamp Info temporary image files when the composited output is generated."
        "\nIf set to True these files are kept on disk up to the next rendering of the shot",
        default=False,
    )
    # deleteIntermediateFiles: BoolProperty(
    #     name="Delete Intermediate Image Files",
    #     description="Delete the rendered and Stamp Info temporary image files when the composited output is generated."
    #     "\nIf set to False these files are kept on disk up to the next rendering of the shot",
    #     default=True,
    # )

    # only used by ANIMATION
    generateShotVideo: BoolProperty(
        name="Generate Shot Video",
        description="Generate the video of the rendered shot",
        default=True,
    )

    # only used by ALL
    generateEditVideo: BoolProperty(
        name="Generate Edit Video(s)",
        description="Generate the edit video of the take with all the specified shot videos",
        default=False,
    )

    otioFileType: EnumProperty(
        name="File Type",
        description="Export the edit either in an OpenTimelineIO file format or a Final Cut XML",
        items=(("OTIO", "Otio", ""), ("XML", "Xml (Final Cut)", "")),
        default="XML",
    )

    # file format
    # image_settings_file_format = 'FFMPEG'
    # scene.render.ffmpeg.format = 'MPEG4'

    # only used by PLAYBLAST
    resolutionPercentage: IntProperty(
        name="Resolution Percentage", min=10, soft_max=100, max=300, subtype="PERCENTAGE", default=100
    )

    updatePlayblastInVSM: BoolProperty(
        name="Open in Video Shot Manager",
        description="Open the rendered playblast in the VSE",
        default=False,
        #    options=set(),
    )

    openPlayblastInPlayer: BoolProperty(
        name="Open in Player",
        description="Open the rendered playblast in the default OS media player",
        default=False,
        #    options=set(),
    )

    stampRenderInfo: BoolProperty(
        name="Stamp Render Info",
        description="Open the rendered playblast in the default OS media player",
        default=True,
        #    options=set(),
    )

    # renderCameraBG: BoolProperty(
    #     name="Render Camera Backgrounds",
    #     description="Render Camera Backgrounds (available only with Overlay)",
    #     default=False,
    #     options=set(),
    # )

    def initialize(self, renderMode):
        """
        Args:
            renderMode: the rendering mode of the settings. Can be STILL, ANIMATION, ALL, OTIO, PLAYBLAST
        """
        _logger.debug_ext(f"initialize Render Settings {renderMode}", col="GREEN")

        # common values
        self.renderAllTakes = False
        self.renderAllShots = True
        self.renderAlsoDisabled = False
        self.renderHandles = False
        self.renderSound = True
        self.disableCameraBG = True
        self.writeToDisk = False
        self.renderOtioFile = False
        self.useStampInfo = True
        self.rerenderExistingShotVideos = True
        self.bypass_rendering_project_settings = False
        self.generateImageSequence = False
        self.outputMediaMode = "VIDEO"
        self.keepIntermediateFiles = False
        self.generateShotVideo = True
        self.generateEditVideo = False
        self.otioFileType = "XML"
        self.resolutionPercentage = 100
        self.updatePlayblastInVSM = False
        self.openPlayblastInPlayer = False
        self.stampRenderInfo = True

        # Still
        if "STILL" == renderMode:
            self.name = "Still Preset"
            self.renderMode = "STILL"

        # Animation
        elif "ANIMATION" == renderMode:
            self.name = "Animation Preset"
            self.renderMode = "ANIMATION"
            self.renderHandles = True

        # All shots
        elif "ALL" == renderMode:
            self.name = "All Shots Preset"
            self.renderMode = "ALL"

            self.renderAllTakes = False
            self.renderAllShots = False
            self.renderAlsoDisabled = False
            self.renderHandles = True
            self.renderOtioFile = True
            self.otioFileType = "XML"
            self.generateEditVideo = True

        # Otio
        elif "OTIO" == renderMode:
            self.name = "Otio Preset"
            self.renderMode = "OTIO"
            self.renderOtioFile = True  # not used in this preset
            self.otioFileType = "XML"

        # Playblast
        elif "PLAYBLAST" == renderMode:
            self.name = "Playblast Preset"
            self.renderMode = "PLAYBLAST"
            self.useStampInfo = False
            self.openPlayblastInPlayer = False
