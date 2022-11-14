# GPLv3 License
#
# Copyright (C) 2022 Ubisoft
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
General settings
"""

# import os
from pathlib import Path

import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty

from ..properties import stamper
from ..properties import infoImage
from ..properties.stamper import (
    getRenderResolutionForStampInfo,
    getInnerHeight,
)
from shotmanager.utils import utils

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

# global vars
if "gbWkDebug" not in vars() and "gbWkDebug" not in globals():
    gbWkDebug = False

if gbWkDebug:
    if "gbWkDebug_DontDeleteTmpFiles" not in vars() and "gbWkDebug_DontDeleteTmpFiles" not in globals():
        gbWkDebug_DontDeleteTmpFiles = True

    if "gbWkDebug_DrawTextLines" not in vars() and "gbWkDebug_DrawTextLines" not in globals():
        gbWkDebug_DrawTextLines = True

else:
    if "gbWkDebug_DontDeleteTmpFiles" not in vars() and "gbWkDebug_DontDeleteTmpFiles" not in globals():
        gbWkDebug_DontDeleteTmpFiles = False

    if "gbWkDebug_DrawTextLines" not in vars() and "gbWkDebug_DrawTextLines" not in globals():
        gbWkDebug_DrawTextLines = False


class UAS_SMStampInfoSettings(bpy.types.PropertyGroup):
    def initialize_stamp_info(self):
        print(f"\nInitializing Stamp Info in the current scene ({bpy.context.scene.name})...")

        # prefs = config.getAddonPrefs()
        # if not prefs.isInitialized:
        #     prefs.initialize_stamp_info_prefs()

        self.isInitialized = True

    def get_isInitialized(self):
        #    print(" get_isInitialized")
        val = self.get("isInitialized", False)

        if not val:
            self.initialize_stamp_info()

        return val

    def set_isInitialized(self, value):
        #  print(" set_isInitialized: value: ", value)
        self["isInitialized"] = value

    isInitialized: BoolProperty(
        get=get_isInitialized,
        set=set_isInitialized,
        default=False,
        options=set(),
    )

    renderRootPathUsed: BoolProperty(default=False)
    renderRootPath: StringProperty(
        name="Render Root Path",
        description="Directory where the temporary images having the stamped information are rendered.\nThis directory must be manually cleaned after the use of the images",
        default="",
    )

    # innerImageRatio : FloatProperty(
    #     name="Inner Ratio",
    #     description="Inner Image Aspect Ratio (Eg: 16/9, 4/3...).\nIf this line is red then the rendered image ratio\nis the same as the framed image ratio and the\nborders will not be visible; consider\nincreasing the height of the rendered images",
    #     min = 1.0, max = 20.0, step = 0.05, default = 1.777, precision = 3 )

    #   For OVER mode
    stampRenderResOver_percentage: FloatProperty(
        name="Frame Inner Height",
        subtype="PERCENTAGE",
        description="Height (in percentage) of the rendered image that will be visible between the top and bottom borders of the frame",
        min=1.0,
        # soft_min=30.0,
        # soft_max=90.0,
        max=100.0,
        precision=1,
        default=86.0,
    )

    #   For OUTSIDE mode
    stampRenderResYOutside_percentage: FloatProperty(
        name="Frame Outer Height",
        subtype="PERCENTAGE",
        description="Height (in percentage) of the rendered image that will be visible between the top and bottom borders of the frame",
        min=0.0,
        # soft_min=30.0,
        soft_max=33.34,
        max=40.0,
        precision=1,
        default=33.34,
    )

    # ----------------------------------

    def activateStampInfo(self, activated):
        # _logger.debug_ext(f"*** StampInfo is now:  {activated}")
        self.stampInfoUsed = activated

    def stampInfoUsed_StateChanged(self, context):
        # _logger.debug_ext(f"*** Stamp Info updated. New state: {self.stampInfoUsed}")
        pass

    def get_stampInfoUsed(self):
        val = self.get("stampInfoUsed", True)
        return val

    def set_stampInfoUsed(self, value):
        # _logger.debug_ext(f"*** set_stampInfoUsed: value: {value}")
        self["stampInfoUsed"] = value

    stampInfoUsed: BoolProperty(
        name="Stamp Info",
        description="Toggle the use of Stamp Info on rendered images",
        get=get_stampInfoUsed,
        set=set_stampInfoUsed,
        update=stampInfoUsed_StateChanged,
        default=True,
    )

    def get_stampInfoRenderMode(self):
        val = self.get("stampInfoRenderMode", 1)
        return val

    # values are integers
    def set_stampInfoRenderMode(self, value: int):
        _logger.debug(f" set_stampInfoRenderMode: value: {value}")

        self["stampInfoRenderMode"] = value

    stampInfoRenderMode: EnumProperty(
        name="Mode",
        items=[
            (
                "OVER",
                "Over Rendered Images",
                "The stamped image will have the same height as the rendered image.\n"
                "It will then hide a part of it. Helpful when borders are not completely opaque.",
                0,
            ),
            (
                "OUTSIDE",
                "Outside Rendered Images",
                "The stamped image will have a greater height than the rendered image and its frame will.\n"
                "NOT cover it. This can gain time when rendered images are computed since no part of them will be hidden.",
                1,
            ),
        ],
        get=get_stampInfoRenderMode,
        set=set_stampInfoRenderMode,
        default=1,
    )

    # ---------- project properties -------------

    projectUsed: BoolProperty(name="Project", description="Stamp project name", default=False, options=set())

    projectName: StringProperty(name="", description="Project name", default="My Project", options=set())

    # ---------- Logo properties -------------

    logoUsed: BoolProperty(name="Logo", description="Set and draw the specified logo", default=True)

    def buildLogosList(self, context):
        dir = self.getBuiltInLogosPath()
        items = list()
        for img in dir.glob("*.png"):
            # print ("    buildLogosList img.stem: " + img.stem )
            #  items.append ( ( img.stem, img.stem, "" ) )
            items.append((img.name, img.name, ""))

        return items

    def getBuiltInLogosPath(self):
        return Path(utils.addonPath() + "\\icons\\logos")

    # def updateLogoPath(self, context):
    #     #  print("updateLogoPath")
    #     dir = self.getBuiltInLogosPath()
    #     #  print("  dir: " + str(dir))
    #     logoFilepath = str(dir) + "\\" + str(self.logoBuiltinName)
    #     #  print("  logoFilepath: " + logoFilepath)
    #     self.logoFilepath = logoFilepath

    logoMode: EnumProperty(
        name="Logo Mode",
        description="Use built-in or custom logo",
        items=(("BUILTIN", "Built-In", ""), ("CUSTOM", "From File", "")),
        default="BUILTIN",
    )

    logoBuiltinName: EnumProperty(
        name="Built-In Logo List",
        description="List of the logo files installed with this add-on",
        items=buildLogosList,
        #   update=updateLogoPath,
        default=0,
    )

    logoFilepath: StringProperty(name="", description="File path of the specified logo", default="")

    logoScaleH: FloatProperty(
        name="Scale", description="Set logo scale", min=0.001, max=2.0, step=0.01, default=0.06, precision=3
    )

    logoPosNormX: FloatProperty(
        name="Pos X", description="Logo Position X", min=-1.0, max=1.0, step=0.01, default=0.012, precision=3
    )

    logoPosNormY: FloatProperty(
        name="Pos Y", description="Logo Position Y", min=-1.0, max=1.0, step=0.01, default=0.01, precision=3
    )

    # ------------------------------------
    # ---------- time and frames ---------
    # ------------------------------------

    # ---------- shared settings ---------
    animRangeUsed: BoolProperty(
        name="Frame Range",
        description="Stamp the range of the animation, in frames",
        default=True,
    )
    handlesUsed: BoolProperty(
        name="Frame Handles",
        description="***Advanced parameter ***"
        "\nStamp the shot handle values in the animation ranges."
        "\n\nIt is recommended to let the add-on Ubisoft Shot Manager automatically cope with handles."
        "\nRead the online documentation for details",
        default=False,
    )

    animDurationUsed: BoolProperty(
        name="Animation Duration",
        description="Total number of frames in the output sequence (handles included)",
        default=False,
        options=set(),
    )

    # ---------- video image -------------

    outputImgIndicesMode: EnumProperty(
        name="Output Images Indices",
        description="Specify the time context to use for the indices of the output file names."
        "\nWhen the output image sequence is used in a compositing or editing software"
        "\nthen using the Video Frame mode makes the exchanges more robust",
        items=[
            (
                "VIDEO_FRAME",
                "Video Time",
                "The time stamped as the Video Frame is used." "\nIt usually starts at 0.",
                0,
            ),
            (
                "3D_FRAME",
                "3D Time",
                "The time stamped as the 3D Frame is used." "\nIt will use the same indices as in a standard rendering",
                1,
            ),
        ],
        default=1,
        options=set(),
    )

    frameDigitsPadding: IntProperty(
        name="Digits Padding",
        description="Number of digits to use for the index of the frames and" "\nin the output image names",
        min=3,
        max=6,
        default=3,
        options=set(),
    )

    videoFrameUsed: BoolProperty(
        name="Video Frame",
        description="Stamp the index of the current image in the image sequence",
        default=False,
        options=set(),
    )

    videoFirstFrameIndexUsed: BoolProperty(
        name="Use Video First Frame Index",
        description="Use the Video First Frame Index." "\nIf not used then the first used frame for videos is 0",
        default=False,
        options=set(),
    )

    videoFirstFrameIndex: IntProperty(
        name="Video First Frame Index",
        description="Value given to the first frame of the rendered image sequence."
        "\nThis is 0 in most editing applications, sometimes 1. Can sometimes be a very custom"
        "\nvalue such as 1000 or 1001.",
        min=0,
        soft_max=50,
        default=1,
        options=set(),
    )

    # ---------- 3d edit frame -------------
    edit3DFrameUsed: BoolProperty(
        name="3D Edit Frame",
        description="Stamp the index of the current image in the 3D edit sequence provided by Shot Manager add-on",
        default=False,
        options=set(),
    )

    edit3DFrame: FloatProperty(
        name="3D Edit Frame Value",
        description="Stamp the index of the current image in the 3D edit sequence provided by Shot Manager add-on",
        default=-1,
    )

    edit3DTotalNumberUsed: BoolProperty(
        name="3D Edit Duration",
        description="Stamp the total number of images in the 3D edit sequence provided by Shot Manager add-on",
        default=False,
        options=set(),
    )

    edit3DTotalNumber: FloatProperty(
        name="3D Edit Duration Value",
        description="Stamp the index of the current image in the 3D edit sequence provided by Shot Manager add-on",
        default=-1,
    )

    framerateUsed: BoolProperty(name="Framerate", description="Stamp current framerate", default=True, options=set())

    # ---------- Scene Frame properties -------------

    currentFrameUsed: BoolProperty(
        name="3D Frame",
        description="Stamp current rendered frame in the 3D scene time context",
        default=True,
        options=set(),
    )

    # ---------- file properties -------------
    filenameUsed: BoolProperty(name="File", description="Stamp file name", default=True, options=set())

    filepathUsed: BoolProperty(name="Path", description="Stamp file path", default=True, options=set())

    # used by production scripts to specify another file than the current one
    # if set to "" then it is ignored and the current file name is used
    customFileFullPath: StringProperty(
        name="Custom File Name",
        description="Enter a path and name of the file to display",
        default="",
        options=set(),
    )

    # ---------- shot manager -------------
    sceneUsed: BoolProperty(name="Scene", description="Stamp scene name", default=True, options=set())
    sequenceUsed: BoolProperty(name="Sequence", description="Stamp sequence name", default=False, options=set())
    shotUsed: BoolProperty(name="Shot", description="Stamp shot name", default=False, options=set())
    takeUsed: BoolProperty(name="Take", description="Stamp take name", default=False, options=set())

    # To be filled by a production script or by Shot Manager
    sequenceName: StringProperty(
        name="Sequence Name",
        description="Enter the name of the sequence the shot belongs to",
        default="Sequence Name",
        options=set(),
    )
    shotName: StringProperty(
        name="Shot Name", description="Enter the name of the current shot", default="Shot Name", options=set()
    )
    takeName: StringProperty(
        name="Take Name", description="Enter the name of the current take", default="Take Name", options=set()
    )

    shotHandles: IntProperty(
        name="Shot Handles Duration",
        description="Duration of the handles of the shot",
        default=10,
        min=0,
        soft_max=50,
    )

    # ---------- Camera properties -------------
    cameraUsed: BoolProperty(name="Camera", description="Stamp camera name", default=True, options=set())

    cameraLensUsed: BoolProperty(name="Lens", description="Stamp camera lens", default=True, options=set())

    # ---------- Shot duration -------------
    shotDurationUsed: BoolProperty(
        name="Shot Duration",
        description="Duration of the shot (in frames) as defined in the 3D edit (= WITHOUT the handles)",
        default=False,
        options=set(),
    )

    # ---------- Top Right Corner Note -------------
    cornerNoteUsed: BoolProperty(
        name="Corner Note", description="User note at the top right corner of the frame", default=False, options=set()
    )
    cornerNote: StringProperty(name="Corner Note Line", description="Enter note here", default="Note...", options=set())

    # ---------- Bottom Note -------------
    bottomNoteUsed: BoolProperty(
        name="Bottom Note", description="User note at the bottom of the frame", default=False, options=set()
    )
    bottomNote: StringProperty(name="Bottom Note Line", description="Enter note here", default="Note...", options=set())

    # ---------- Notes properties -------------
    notesUsed: BoolProperty(name="Notes", description="User notes", default=False, options=set())

    notesLine01: StringProperty(name="Notes Line 01", description="Enter notes here", default="Notes...", options=set())
    notesLine02: StringProperty(name="Notes Line 02", description="Enter notes here", options=set())
    notesLine03: StringProperty(name="Notes Line 03", description="Enter notes here", options=set())

    # ---------- Border properties -------------

    borderUsed: BoolProperty(name="Borders", description="Stamp borders", default=True, options=set())

    # regarder https://blender.stackexchange.com/questions/141333/how-controll-rgb-node-with-floatvectorproperty-blender-2-8
    borderColor: bpy.props.FloatVectorProperty(
        name="",
        subtype="COLOR_GAMMA",
        size=4,
        description="Stamp borders",
        min=0.0,
        max=1.0,
        precision=2,
        default=(0.0, 0.0, 0.0, 1.0),
        options=set(),
    )

    # ---------- Date properties -------------

    dateUsed: BoolProperty(name="Date", description="Stamp rendering date", default=True, options=set())
    timeUsed: BoolProperty(name="Time", description="Stamp rendering time", default=True, options=set())

    # ---------- User properties -------------

    userNameUsed: BoolProperty(
        name="User Name", description="Name of the current user of the OS session", default=False, options=set()
    )
    # userName: StringProperty(
    #     name="User Name", description="Name of the current user of the OS session", default="", options=set()
    # )

    # ---------- Settings properties -------------
    # https://devtalk.blender.org/t/how-to-change-the-color-picker/9666/7
    # https://docs.blender.org/api/current/bpy.props.html?highlight=floatvectorproperty#bpy.props.FloatVectorProperty

    textColor: bpy.props.FloatVectorProperty(
        name="Text Color",
        subtype="COLOR_GAMMA",
        size=4,
        description="Stamp borders",
        default=(0.55, 0.55, 0.55, 1.0),
        min=0.0,
        max=1.0,
        precision=2,
    )

    fontScaleHNorm: FloatProperty(
        name="Font Size",
        description="Set font size. The scale of the font is normalized relatively to the height of the rendered image",
        min=0.001,
        max=1.0,
        step=0.01,
        default=0.02,
        precision=3,
    )

    interlineHNorm: FloatProperty(
        name="Interline Size",
        description="Set the size of the space between 2 text lines. This size is normalized relatively to the height of the rendered image",
        min=0.000,
        max=0.1,
        step=0.01,
        default=0.015,
        precision=3,
    )

    extPaddingNorm: FloatProperty(
        name="Vertical Exterior Padding",
        description="Set the distance between the text and the top and bottom sides of the frame bands of the image. This size is normalized relatively to the height of the rendered image",
        min=0.000,
        max=0.1,
        step=0.01,
        default=0.015,
        precision=3,
    )

    extPaddingHorizNorm: FloatProperty(
        name="Horizontal Exterior Padding",
        description="Set the distance between the text and the left and right sides of the frame bands of the image. This size is normalized relatively to the height of the rendered image",
        min=0.000,
        max=0.1,
        step=0.01,
        default=0.02,
        precision=3,
    )

    automaticTextSize: BoolProperty(
        name="Automatic Text Size",
        description="Text size is automatically calculated according to the size of the border",
        default=True,
        options=set(),
    )

    # linkTextToBorderEdge : BoolProperty(
    #     name="Link Text to Border",
    #     description="Link the text position to the edge of the borders.\nIf not linked then the text position is relative to the image top and bottom",
    #     default = True )

    offsetToCenterHNorm: FloatProperty(
        name="Offset To Center",
        description="Offset To Center. The offset of the border and text is normalized relatively to the height of the rendered image",
        min=0.000,
        max=1.0,
        step=0.001,
        default=0.0,
        precision=3,
    )

    # settings ###
    stampPropertyLabel: BoolProperty(
        name="Stamp Property Label", description="Stamp Property Label", default=True, options=set()
    )

    stampPropertyValue: BoolProperty(
        name="Stamp Property Value", description="Stamp Property Value", default=True, options=set()
    )

    # debug properties -------------

    def set_debugMode(self, value):
        # self.debugMode = value
        global gbWkDebug
        global gbWkDebug_DontDeleteTmpFiles
        global gbWkDebug_DrawTextLines

        gbWkDebug = value
        self.debug_DontDeleteCompoNodes = value
        gbWkDebug_DontDeleteTmpFiles = value
        gbWkDebug_DrawTextLines = value

    def get_debugMode(self):
        return self.debugMode

    debugMode: BoolProperty(name="Debug Mode", description="Debug Mode", default=gbWkDebug)
    #    set = set_debugMode,
    #    get = get_debugMode )

    debug_DrawTextLines: BoolProperty(
        name="Debug - Draw Text Lines", description="Debug - Draw Text Lines", default=gbWkDebug_DrawTextLines
    )

    debug_DontDeleteCompoNodes: BoolProperty(default=False)

    def renderTmpImageWithStampedInfo(
        self,
        scene,
        currentFrame,
        resolution=None,
        innerHeight=None,
        renderPath=None,
        renderFilename=None,
        verbose=False,
    ):
        """Args:
        resolution: the resolution frame"""

        if resolution is None or innerHeight is None:
            renderW = getRenderResolutionForStampInfo(scene, forceMultiplesOf2=True)[0]
            renderH = getRenderResolutionForStampInfo(scene, forceMultiplesOf2=True)[1]
            innerH = getInnerHeight(scene)
        else:
            renderW = resolution[0]
            renderH = resolution[1]
            innerH = innerHeight

        infoImage.renderStampedImage(
            scene,
            currentFrame,
            renderW,
            renderH,
            innerH,
            renderPath=renderPath,
            renderFilename=renderFilename,
            verbose=verbose,
        )

    def getRenderResolutionForStampInfo(self, scene, usePercentage=True, forceMultiplesOf2=True):
        return stamper.getRenderResolutionForStampInfo(
            scene, usePercentage=usePercentage, forceMultiplesOf2=forceMultiplesOf2
        )
