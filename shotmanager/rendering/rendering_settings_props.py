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
Render Settings properties
"""

import bpy

from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


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

    def _get_useStampInfo(self):
        val = self.get("useStampInfo", True)

        # warning! Maybe the returned props is not the right one!!
        props = bpy.context.scene.UAS_shot_manager_props
        if "PLAYBLAST" != self.renderMode and props.use_project_settings:
            if not self.bypass_rendering_project_settings:
                #     val = self.useStampInfo
                # else:
                val = props.project_use_stampinfo
        return val

    def _set_useStampInfo(self, value):
        self["useStampInfo"] = value

    useStampInfo: BoolProperty(name="Use Stamp Info", get=_get_useStampInfo, set=_set_useStampInfo, default=True)

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
