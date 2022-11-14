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
Shot Manager properties
"""

import re
import sys
from pathlib import Path, PurePath

import bpy
from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import (
    CollectionProperty,
    IntProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    PointerProperty,
)

from .montage_interface import MontageInterface

from shotmanager.rendering.rendering_settings_props import UAS_ShotManager_RenderSettings
from shotmanager.rendering.rendering_global_props import UAS_ShotManager_RenderGlobalContext

from .output_params import UAS_ShotManager_OutputParams_Resolution

from .shot import UAS_ShotManager_Shot
from .shots_global_settings import UAS_ShotManager_ShotsGlobalSettings
from .take import UAS_ShotManager_Take
from .layout_settings import UAS_ShotManager_LayoutSettings

from shotmanager.warnings import warnings
from ..retimer.retimer_props import UAS_Retimer_Properties
from ..features.greasepencil.greasepencil_frame_template import UAS_GreasePencil_FrameTemplate
from shotmanager.feature_panels.greasepencil_25D.greasepencil_25D_props import UAS_GreasePencil_Tools_Properties

from shotmanager.utils import utils
from shotmanager.utils import utils_os
from shotmanager.utils.utils_shot_manager import getStampInfo
from shotmanager.utils import utils_greasepencil

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def list_greasepencil_layer_modes(self, context):
    # warning: use context.object, not context.active_object cause active_object can be None if
    # the active object is not visible in the viewport
    res = list()
    res.append(("ALL", "All", "", 0))
    res.append(("ACTIVE", "Active", "", 1))

    # _logger.debug_ext(
    #     f"Layers Mode: context.object: {context.object.name}, context.active_object: {context.active_object}",
    #     col="RED",
    # )

    # if context.object is not None and "GPENCIL" == context.object.type:

    #     _logger.debug_ext(f"toto", col="RED")
    #     numLayers = len(context.object.data.layers)
    #     if numLayers:
    #         for i, layer in reversed(list(enumerate(context.object.data.layers))):
    #             res.append((layer.info, layer.info, "", numLayers - 1 - i + 2))
    #     else:
    #         res = (("NOLAYER", "No Layer", "", 0),)

    # framePreset = self.stb_frameTemplate
    usedPresets = self.stb_frameTemplate.getUsedPresets()
    numPresets = len(usedPresets)
    if numPresets:
        for i, preset in reversed(list(enumerate(usedPresets))):
            res.append((preset.id, preset.layerName, "", numPresets - 1 - i + 2))
    else:
        res = (("NOLAYER", "No Layer", "", 0),)

    # # canvas layer #####
    # preset_canvas = framePreset.getPresetByID("CANVAS")
    # if preset_lines.used
    # # BG layers #########
    # preset_lines = framePreset.getPresetByID("BG_LINES")
    # preset_fills = framePreset.getPresetByID("BG_FILLS")
    # # MG layers #########
    # preset_lines = framePreset.getPresetByID("MG_LINES")
    # preset_fills = framePreset.getPresetByID("MG_FILLS")
    # # FG layers #########
    # preset_lines = framePreset.getPresetByID("FG_LINES")
    # preset_fills = framePreset.getPresetByID("FG_FILLS")
    #  # Rough layer #######
    # preset_lines = framePreset.getPresetByID("ROUGH")

    # res = [
    #     ("ALL", "All", "", 0),
    #     ("ACTIVE", "Active", "", 1),
    #     ("Rough", "Rough", "", 2),
    #     ("FG Lines", "FG Lines", "", 3),
    #     ("FG Fills", "FG Fills", "", 4),
    #     ("MiddleG Lines", "MiddleG Lines", "", 5),
    #     ("MiddleG Fills", "MiddleG Fills", "", 6),
    #     ("BG Lines", "BG Lines", "", 7),
    #     ("BG Fills", "BG Fills", "", 8),
    #     ("_Canvas_", "_Canvas_", "", 9),
    # ]
    #   _logger.debug_ext(f"Presets Layers Mode: res: {res}", col="RED")
    return res


def list_greasepencil_layer_modesB(self, context):
    res = list()
    res.append(("ALL", "All", "", 0))
    res.append(("ACTIVE", "Active", "", 1))

    #  _logger.debug_ext(f"Layers Mode: context.object: {context.object.name}", col="RED")

    if context.active_object is not None and "GPENCIL" == context.active_object.type:
        numLayers = len(context.active_object.data.layers)
        if numLayers:
            for i, layer in reversed(list(enumerate(context.active_object.data.layers))):
                res.append((layer.info, layer.info, "", numLayers - 1 - i + 2))
        else:
            res = (("NOLAYER", "No Layer", "", 0),)

    # res = [
    #     ("ALL", "All", "", 0),
    #     ("ACTIVE", "Active", "", 1),
    #     ("Rough", "Rough", "", 2),
    #     ("FG Lines", "FG Lines", "", 3),
    #     ("FG Fills", "FG Fills", "", 4),
    #     ("MiddleG Lines", "MiddleG Lines", "", 5),
    #     ("MiddleG Fills", "MiddleG Fills", "", 6),
    #     ("BG Lines", "BG Lines", "", 7),
    #     ("BG Fills", "BG Fills", "", 8),
    #     ("_Canvas_", "_Canvas_", "", 9),
    # ]
    #    _logger.debug_ext(f"Layers Mode: res: {res}", col="RED")
    return res


class UAS_ShotManager_Props(MontageInterface, PropertyGroup):
    # marche pas
    # def __init__(self):
    #     self._characteristics = dict()
    #     print("\n\n */*/*/*/*/*/*/*/*/*/*/ Init shot manager !!! \n\n")

    def version(self):
        """Return the add-on version in the form of a tupple made by:
            - a string x.y.z (eg: "1.21.3")
            - an integer. x.y.z becomes xxyyyzzz (eg: "1.21.3" becomes 1021003)
        Return None if the addon has not been found
        """
        return utils.addonVersion("Ubisoft Shot Manager")

    dataVersion: IntProperty(
        """ Data Version is of the form xxyyyzzz, integer generated from the string version "xx.yyy.zzz"
            Use functions convertVersionStrToInt and convertVersionIntToStr in the module utils.py to manipulate it.
        """,
        name="Data Version",
        description="Version of Shot Manager used to generate the data of the current scene.",
        default=-1,
        options=set(),
    )

    def initialize_shot_manager(self):
        _logger.info_ext(f"\nInitializing Ubisoft Shot Manager in the current scene ({bpy.context.scene.name})...")
        prefs = config.getAddonPrefs()

        # self.parentScene = self.getParentScene()

        if not prefs.isInitialized:

            prefs.initialize_shot_manager_prefs()

        if self.parentScene is None:
            self.parentScene = self.findParentScene()
        # _logger.info(f"\n  self.parentScene : {self.parentScene}")

        # not used - for Otio compatibility somehow
        self.initialize()

        self.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
        self.createDefaultTake()
        self.createRenderSettings()

        # layout and features
        ############################
        self.createLayoutSettings()
        self.setCurrentLayout(prefs.layout_mode)
        # self.layout_mode = prefs.layout_mode
        # self.getCurrentLayout().updateUI(self)

        # self.display_storyboard_in_properties = prefs.display_storyboard_in_properties
        # self.display_notes_in_properties = prefs.display_notes_in_properties
        # self.display_cameraBG_in_properties = prefs.display_cameraBG_in_properties
        # self.display_takerendersettings_in_properties = prefs.display_takerendersettings_in_properties
        # self.display_editmode_in_properties = prefs.display_editmode_in_properties
        # self.display_globaleditintegr_in_properties = prefs.display_globaleditintegr_in_properties
        # self.display_advanced_infos = prefs.display_advanced_infos

        # retimer
        self.retimer.initialize()

        # storyboard
        self.stb_frameTemplate.initialize()

        # activate camera hud
        # bpy.ops.uas_shot_manager.draw_camera_hud_in_viewports("INVOKE_DEFAULT")
        # bpy.ops.uas_shot_manager.draw_camera_hud_in_pov("INVOKE_DEFAULT")
        self.camera_hud_display_in_viewports = True
        self.camera_hud_display_in_pov = True

        self.isInitialized = True

    def get_isInitialized(self):
        #    print(" get_isInitialized")
        val = self.get("isInitialized", False)

        if not val:
            self.initialize_shot_manager()

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

    parentScene: PointerProperty(
        type=Scene,
        options=set(),
    )

    def findParentScene(self):
        for scene in bpy.data.scenes:
            if "UAS_shot_manager_props" in scene:
                props = config.getAddonProps(scene)
                if self == props:
                    #    print("findParentScene: Scene found")
                    return scene
        # print("findParentScene: Scene NOT found")
        return None

    def getParentScene(self):
        parentScn = None
        try:
            parentScn = self.parentScene
        except Exception:  # as e
            print("Error - parentScene property is None in props.getParentScene():", sys.exc_info()[0])

        # if parentScn is not None:
        #     return parentScn
        if parentScn is None:
            _logger.error("\n\n WkError: parentScn is None in Props !!! *** ")
            self.parentScene = self.findParentScene()
        else:
            self.parentScene = parentScn

        if self.parentScene is None:
            print("\n\n Re WkError: self.parentScene in still None in Props !!! *** ")
        # findParentScene is done in initialize function

        return self.parentScene

    retimer: PointerProperty(
        type=UAS_Retimer_Properties,
    )

    greasepencil25DTools: PointerProperty(
        type=UAS_GreasePencil_Tools_Properties,
    )

    def getWarnings(self, scene):
        """Check if some warnings are to be mentioned to the user/
        A warning message can be on several lines when the separator \n is used.

        Return:
            An array of tupples made of the warning message and the warning index
            eg: [("Current file in Read-Only", 1), ("Current scene fps and project fps are different !!", 2)]
        """
        return warnings.getWarnings(self, scene)

    def sceneIsReady(self, displayDialogMessage=True):
        renderWarnings = ""
        if self.renderRootPath.startswith("//") and "" == bpy.data.filepath:
            renderWarnings = "*** Save file first ***"

        elif "" == self.renderRootPath:
            renderWarnings = "*** Invalid Output File Name ***"

        elif not self.isRenderRootPathValid():
            renderWarnings = "*** Invalid Render Root Path ***"

        elif 0 != bpy.context.scene.render.resolution_x % 2 or 0 != bpy.context.scene.render.resolution_y % 2:
            renderWarnings = "*** Output resolution must use multiples of 2 ***"

        elif len(self.get_shots()) <= 0:
            renderWarnings = "*** No shots in the current take ***"

        if "" != renderWarnings and displayDialogMessage:
            utils.ShowMessageBox(renderWarnings, "Render Aborted", "ERROR")
            print("Render aborted before start: " + renderWarnings)
            return False

        return True

    def dontRefreshUI(self):
        prefs = config.getAddonPrefs()
        res = False
        if (
            bpy.context.screen.is_animation_playing
            and not bpy.context.screen.is_scrubbing
            and bpy.context.window_manager.UAS_shot_manager_use_best_perfs
            and prefs.best_play_perfs_turnOff_mainUI
        ):
            res = True
        return res

    sequence_name: StringProperty(
        name="Sequence Name",
        description="Name of the sequence edited in the scene",
        default="My Sequence",
        options=set(),
    )

    # wkip rrs specific
    #############

    rrs_useRenderRoot: BoolProperty(
        name="Use Render Root",
        default=True,
        options=set(),
    )
    rrs_rerenderExistingShotVideos: BoolProperty(
        name="Force Re-render",
        default=True,
        options=set(),
    )
    rrs_fileListOnly: BoolProperty(
        name="File List Only",
        default=True,
        options=set(),
    )
    rrs_renderAlsoDisabled: BoolProperty(
        name="Render Also Disabled Shots",
        default=False,
        options=set(),
    )

    #############
    # project settings
    #############

    use_project_settings: BoolProperty(name="Use Project Settings", default=False, options=set())

    ############
    # settings coming from production:
    ############

    ############
    # naming
    ############

    project_name: StringProperty(
        name="Project Name",
        default="My Project",
        options=set(),
    )
    project_default_take_name: StringProperty(
        name="Default Take Name",
        default="Main Take",
        options=set(),
    )

    project_use_shot_handles: BoolProperty(
        name="Use Handles",
        description="Use or not shot handles for the project.\nWhen not used, not reference to the handles will appear in Shot Manager user interface",
        default=True,
        options=set(),
    )
    project_shot_handle_duration: IntProperty(
        name="Project Handles Duration",
        description="Duration of the handles used by the project, in number of frames",
        min=0,
        soft_max=50,
        default=10,
        options=set(),
    )

    ############
    # sequence and shot name template
    ############

    project_naming_project_format: StringProperty(
        name="Project Naming Format",
        description="Name of the project (eg: MyProject)"
        "\nor the identifier for the act and the number of digits of its index (eg: Act##)",
        default="Act##",
        options=set(),
    )

    project_naming_sequence_format: StringProperty(
        name="Sequence Naming Format",
        description="Identifier for the sequence and the number of digits of its index" "\neg: Seq####",
        default="Seq####",
        options=set(),
    )

    project_naming_shot_format: StringProperty(
        name="Shot Naming Format",
        description="Identifier for the shot and the number of digits of its index" "\neg: Sh####",
        default="Sh####",
        options=set(),
    )

    project_naming_separator_char: StringProperty(
        name="Naming Separator",
        description="Character used to separate the identifiers in the shot full name eg: _",
        default="_",
        options=set(),
    )

    project_naming_project_index: IntProperty(
        description="Set to -1 if not defined",
        min=-1,
        default=1,
        options=set(),
    )
    project_naming_sequence_index: IntProperty(
        description="Set to -1 if not defined",
        min=-1,
        step=10,
        default=1,
        options=set(),
    )

    ############
    # stamp info
    ############
    project_use_stampinfo: BoolProperty(
        name="Use Stamp Info Add-on",
        description="Use UAS Stamp Info add-on - if available - to write data on rendered images.\nNote: If Stamp Info is not installed then warnings will be displayed",
        default=True,
        options=set(),
    )
    project_logo_path: StringProperty(
        name="Project Logo",
        description="If defined uses the project logo otherwise uses the logo specified in the Stamp Info panel",
        default="",
        options=set(),
    )

    ############
    # resolution
    ############
    project_fps: FloatProperty(
        name="Project Fps",
        min=0.5,
        max=200.0,
        default=25.0,
        options=set(),
    )
    project_resolution_x: IntProperty(
        name="Res. X",
        min=0,
        default=1280,
        options=set(),
    )
    project_resolution_y: IntProperty(
        name="Res. Y",
        min=0,
        default=720,
        options=set(),
    )
    project_resolution_framed_x: IntProperty(
        name="Res. Framed X",
        min=0,
        default=1280,
        options=set(),
    )
    project_resolution_framed_y: IntProperty(
        name="Res. Framed Y",
        min=0,
        default=960,
        options=set(),
    )

    ############
    # camera assets
    ############
    project_cameraAssets_path: StringProperty(
        name="Camera Assets File",
        description="Path to an asset library Blender file containing customized cameras",
        default="",
        options=set(),
    )

    ############
    # outputs
    ############

    project_color_space: StringProperty(
        name="Color Space",
        default="",
        options=set(),
    )
    project_asset_name: StringProperty(
        name="Asset Name",
        default="",
        options=set(),
    )

    # built-in project settings
    project_images_output_format: StringProperty(
        name="Image Output Format",
        description="File format for the rendered output images, BEFORE composition with the Stamp Info framing images."
        "\nExpected values: PNG, OPEN_EXR",
        default="PNG",
        options=set(),
    )

    project_output_format: StringProperty(
        name="Video Output Format",
        default="mp4",
        options=set(),
    )

    project_sounds_output_format: StringProperty(
        name="Sound Output Format",
        default="",
        options=set(),
    )

    project_renderSingleFrameShotAsImage: BoolProperty(
        name="Project Render Single Frame Shot as Image",
        description="Render single frame shot as an image, not as a video",
        default=True,
        options=set(),
    )

    # add-on preferences overriden by project settings
    project_output_first_frame: IntProperty(
        name="Project Output First Frame Index",
        description="Index of the first frame for rendered image sequences and videos."
        "\nThis is 0 in most editing applications, sometimes 1. Can sometimes be a very custom"
        "\nvalue such as 1000 or 1001."
        "\nThis setting overrides the related Add-on Preference",
        min=0,
        subtype="TIME",
        default=0,
        options=set(),
    )

    project_img_name_digits_padding: IntProperty(
        name="Image Name Digit Padding",
        description="Number of digits to use for the index of an output image in its name."
        "\nThis setting overrides the related Add-on Preference",
        min=0,
        default=4,
        options=set(),
    )

    # built-in settings
    use_handles: BoolProperty(
        name="Use Handles",
        description="Use or not shot handles.\nWhen not used, not reference to the handles will appear in Shot Manager user interface",
        default=False,
        options=set(),
    )
    handles: IntProperty(
        name="Handles Duration",
        description="Duration of the handles, in number of frames",
        default=10,
        min=0,
        options=set(),
    )

    naming_shot_format: StringProperty(
        name="Shot Naming Format",
        description="Identifier for the shot and the number of digits of its index used for the creation of new shots"
        "\neg: Sh####",
        default="Sh####",
        options=set(),
    )

    renderSingleFrameShotAsImage: BoolProperty(
        name="Render Single Frame Shot as Image",
        description="Render single frame shot as an image, not as a video",
        default=True,
        options=set(),
    )

    # shot manager per scene instance properties overriden by project settings
    render_sequence_prefix: StringProperty(
        name="Render Sequence Prefix",
        description="Prefix added to the very beginning of the shot names, before the sequence name, at render time"
        "\nExamples: Act01_, MyMovie_...",
        default="",
        options=set(),
    )

    #############
    # general
    # Functions to call whenever you need a property value that can be overriden by the projects settings
    #############

    def getRenderResolution(self):
        """Return the resolution used by Shot Manager in the current context.
        It is the resolution of the images resulting from the scene rendering, not the one resulting
        from these renderings composited with the Stamp Info frames, which can be bigger.
        Use getRenderResolutionForStampInfo() for the final composited images resolution.

        This resolution is specified by:
            - the current take resolution if it overrides the scene or project render settings,
            - the project, if project settings are used,
            - or by the current scene if none of the specifications above

        This resolution should be (but it may not always be the case according to the refreshment of the scene)
        the same as the current scene one.

        Returns:
            tupple with the render resolution x and y of the take
        """
        res = None
        currentTake = self.getCurrentTake()
        if currentTake is not None:
            res = currentTake.getRenderResolution()
        else:
            if self.use_project_settings:
                res = (self.project_resolution_x, self.project_resolution_y)
            else:
                # wkip temp fix
                if self.parentScene is None:
                    self.getParentScene()
                res = (self.parentScene.render.resolution_x, self.parentScene.render.resolution_y)
        return res

    def getRenderAspectRatio(self):
        res = self.getRenderResolution()
        return res[0] / res[1]

    def setResolutionToScene(self):
        """
        Check the current resolution and change it if necessary to match either the project
        one or the current take one if project mode is not activated.
        A take can override a project settings render resolution if it is configured as so.
        """
        res = self.getRenderResolution()

        if res is not None:
            if self.parentScene.render.resolution_x != res[0]:
                self.parentScene.render.resolution_x = res[0]
            if self.parentScene.render.resolution_y != res[1]:
                self.parentScene.render.resolution_y = res[1]

    # FIXME: add support for take custom res
    def getRenderResolutionForStampInfo(self):
        """Return the resolution of the images resulting from the compositing of the rendered images and
        the frames from Stamp Info.
        If Stamp Info is not used then the returned resolution is the one of the rendered images, which
        can also be obtained by calling getRenderResolution().

        The scene render resolution percentage is NOT involved here.

        This resolution is specified by:
            - the current take resolution if it overrides the scene or project render settings,
            - the project, if project settings are used,
            - or by the current scene if none of the specifications above

        Returns:
            tupple with the render resolution x and y of the take
        """
        scene = self.parentScene

        # if getattr(scene, "UAS_SM_StampInfo_Settings", None) is None:
        stampInfoSettings = getStampInfo()
        if stampInfoSettings is None:
            return self.getRenderResolution()

        # stampInfoSettings = scene.UAS_SM_StampInfo_Settings
        if not stampInfoSettings.stampInfoUsed:
            return self.getRenderResolution()

        if self.use_project_settings:
            if not self.project_use_stampinfo:
                return self.getRenderResolution()

            renderResolutionFramedFull = [self.project_resolution_framed_x, self.project_resolution_framed_y]
            return (renderResolutionFramedFull[0], renderResolutionFramedFull[1])
        else:
            renderResolutionFramedFull = stampInfoSettings.getRenderResolutionForStampInfo(scene)
            return (renderResolutionFramedFull[0], renderResolutionFramedFull[1])

    # FIXME: add support for take custom res
    def getOutputResolution(self, scene, renderPreset, mode, forceMultiplesOf2=False):
        """Just compute the expected resolution

        Note: the stamp info is involved here only if the project settings are not used

        Args:
            mode:
                RENDERED_IMG_RES:       do not include Res Percentage
                FINAL_RENDERED_IMG_RES: include Res Percentage
                FRAMED_IMG_RES:         do not include Res Percentage
                FINAL_FRAMED_IMG_RES:   include Res Percentage
            forceMultiplesOf2
        """
        renderResolution = None
        renderResolutionFramed = None

        # if no project settings used we take the info from the scene
        if not self.use_project_settings:
            renderResolution = [scene.render.resolution_x, scene.render.resolution_y]
            renderResolutionFramed = [scene.render.resolution_x, scene.render.resolution_y]

            if "PLAYBLAST" == renderPreset.renderMode:
                renderResolution[0] = int(renderResolution[0] * renderPreset.resolutionPercentage / 100)
                renderResolution[1] = int(renderResolution[1] * renderPreset.resolutionPercentage / 100)

                if renderPreset.stampRenderInfo and renderPreset.useStampInfo:
                    if self.isStampInfoAvailable():
                        stampInfoSettings = getStampInfo()
                        renderResolutionFramed = stampInfoSettings.getRenderResolutionForStampInfo(
                            scene, usePercentage=False
                        )

                        renderResolutionFramed[0] = int(
                            renderResolutionFramed[0] * renderPreset.resolutionPercentage / 100
                        )
                        renderResolutionFramed[1] = int(
                            renderResolutionFramed[1] * renderPreset.resolutionPercentage / 100
                        )
                    else:
                        renderResolutionFramed = [renderResolution[0], renderResolution[1]]
                else:
                    renderResolutionFramed = [renderResolution[0], renderResolution[1]]

            else:
                if self.isStampInfoAvailable():
                    stampInfoSettings = getStampInfo()
                    if renderPreset.useStampInfo:
                        renderResolutionFramed = stampInfoSettings.getRenderResolutionForStampInfo(
                            scene, usePercentage=False
                        )

                if "FINAL" in mode:
                    renderResolution[0] = int(renderResolution[0] * renderPreset.resolutionPercentage / 100)
                    renderResolution[1] = int(renderResolution[1] * renderPreset.resolutionPercentage / 100)
                    renderResolutionFramed[0] = int(renderResolutionFramed[0] * renderPreset.resolutionPercentage / 100)
                    renderResolutionFramed[1] = int(renderResolutionFramed[1] * renderPreset.resolutionPercentage / 100)

        # use project settings
        else:
            if "PLAYBLAST" == renderPreset.renderMode:
                renderResolution = [-1, -1]
                renderResolution[0] = int(self.project_resolution_x * renderPreset.resolutionPercentage / 100)
                renderResolution[1] = int(self.project_resolution_y * renderPreset.resolutionPercentage / 100)

                if renderPreset.stampRenderInfo and renderPreset.useStampInfo:
                    renderResolutionFramed = [-1, -1]
                    renderResolutionFramed[0] = int(
                        self.project_resolution_framed_x * renderPreset.resolutionPercentage / 100
                    )
                    renderResolutionFramed[1] = int(
                        self.project_resolution_framed_y * renderPreset.resolutionPercentage / 100
                    )
                else:
                    renderResolutionFramed = [renderResolution[0], renderResolution[1]]

            else:
                renderResolution = [self.project_resolution_x, self.project_resolution_y]
                if self.project_use_stampinfo:
                    renderResolutionFramed = [self.project_resolution_framed_x, self.project_resolution_framed_y]
                else:
                    renderResolutionFramed = [self.project_resolution_x, self.project_resolution_y]

                # override project settings variables if bypass project settings is enabled
                if renderPreset.bypass_rendering_project_settings:
                    if "FINAL" in mode:
                        renderResolution[0] = int(renderResolution[0] * renderPreset.resolutionPercentage / 100)
                        renderResolution[1] = int(renderResolution[1] * renderPreset.resolutionPercentage / 100)

                    if "FINAL_FRAMED_IMG_RES" == mode:
                        if renderPreset.useStampInfo:
                            renderResolutionFramed = [
                                self.project_resolution_framed_x,
                                self.project_resolution_framed_y,
                            ]
                            renderResolutionFramed[0] = int(
                                renderResolutionFramed[0] * renderPreset.resolutionPercentage / 100
                            )
                            renderResolutionFramed[1] = int(
                                renderResolutionFramed[1] * renderPreset.resolutionPercentage / 100
                            )
                        else:
                            renderResolutionFramed[0] = renderResolution[0]
                            renderResolutionFramed[1] = renderResolution[1]

        # make the resolutions valid for video rendering
        if forceMultiplesOf2:
            renderResolution = utils.convertToSupportedRenderResolution(renderResolution)
            renderResolutionFramed = utils.convertToSupportedRenderResolution(renderResolutionFramed)

        if "FRAMED" in mode:
            return renderResolutionFramed
        return renderResolution

    # FIXME: add support for take custom res
    def getRenderResolutionForFinalOutput(self, resPercentage=100, useStampInfo=None):
        """Return the resolution of the images resulting from the compositing of the rendered images and
        the frames from Stamp Info.
        If Stamp Info is not used then the returned resolution is the one of the rendered images, which
        can also be obtained by calling getRenderResolution().

        This resolution is specified by:
            - the current take resolution if it overrides the scene or project render settings,
            - the project, if project settings are used,
            - or by the current scene if none of the specifications above

        Args:
            resPercentage: use the scene render property named resolutionPercentage, or 100 to ignore it
            useStampInfo: if None then uses the context to define if used or not, if True then integrates it in the computation
            and if False then don't take it in account. This is required by the Project Bypass property in the SM Render Settings.

        Returns:
            tupple with the render resolution x and y of the take
        """

        _logger.debug_ext("getRenderResolutionForFinalOutput", tag="DEPRECATED")
        if useStampInfo is None:
            renderResolutionFramedFull = self.getRenderResolutionForStampInfo()
        elif useStampInfo:
            scene = self.parentScene

            stampInfoSettings = getStampInfo()
            if stampInfoSettings is None:
                renderResolutionFramedFull = self.getRenderResolution()
            else:
                renderResolutionFramedFull = stampInfoSettings.getRenderResolutionForStampInfo(scene)

            # if getattr(scene, "UAS_SM_StampInfo_Settings", None) is None:
            #     renderResolutionFramedFull = self.getRenderResolution()
            # else:
            #     stampInfoSettings = scene.UAS_SM_StampInfo_Settings
            #     renderResolutionFramedFull = stampInfoSettings.getRenderResolutionForStampInfo(scene)
        else:
            renderResolutionFramedFull = self.getRenderResolution()

        if 100 != resPercentage:
            finalRenderResolutionFramed = []
            finalRenderResolutionFramed.append(int(renderResolutionFramedFull[0] * resPercentage / 100))
            finalRenderResolutionFramed.append(int(renderResolutionFramedFull[1] * resPercentage / 100))
            return (finalRenderResolutionFramed[0], finalRenderResolutionFramed[1])
        else:
            return (renderResolutionFramedFull[0], renderResolutionFramedFull[1])

    def areShotHandlesUsed(self):
        """Return true if the shot handles are used by Shot Manager in the current context. This value is specified by:
        - the project, if project settings are used,
        - the settings of the current instance of Shot Manager otherwise
        """
        return self.project_use_shot_handles if self.use_project_settings else self.use_handles

    def getHandlesDuration(self):
        """Return the duration of the handles if handles are used by Shot Manager in the current context. This duration is specified by:
            - the project, if project settings are used and handles are also used there,
            - the settings of the current instance of Shot Manager otherwise
        Before calling this function check if the instance of Shot Manager uses handles by calling areShotHandlesUsed()
        Return 0 if the handles are not used.
        """
        handles = 0
        if self.areShotHandlesUsed():
            handles = self.project_shot_handle_duration if self.use_project_settings else self.handles
            handles = max(0, handles)
        return handles

    # playbar
    #############
    restartPlay: BoolProperty(
        default=False,
        options=set(),
    )

    # edit
    #############

    editStartFrame: IntProperty(
        name="Edit Start Frame",
        description="Index of the first frame of the edit.Default is 0.\nMost editing software start at 0, some at 1. \
            \nIt is possible to use a custom value when the current scene is not the first one of the edit in this file",
        default=0,
        options=set(),
    )

    # shots
    #############

    display_selectbut_in_shotlist: BoolProperty(
        name="Display Camera Selection Button in Shot List", default=True, options=set()
    )

    display_name_in_shotlist: BoolProperty(name="Display Name in Shot List", default=True, options=set())

    display_camera_in_shotlist: BoolProperty(name="Display Camera in Shot List", default=False, options=set())

    display_lens_in_shotlist: BoolProperty(name="Display Camera Lens in Shot List", default=False, options=set())

    display_duration_in_shotlist: BoolProperty(name="Display Shot Duration in Shot List", default=True, options=set())
    display_duration_after_time_range: BoolProperty(
        name="Display Shot Duration After Time Range", default=True, options=set()
    )

    display_color_in_shotlist: BoolProperty(name="Display Color in Shot List", default=True, options=set())

    display_enabled_in_shotlist: BoolProperty(name="Display Enabled State in Shot List", default=True, options=set())

    display_cameraBG_in_shotlist: BoolProperty(name="Display Camera BG in Shot List", default=True, options=set())

    display_greasepencil_in_shotlist: BoolProperty(
        name="Display Grease Pencil in Shot List", default=True, options=set()
    )

    display_getsetcurrentframe_in_shotlist: BoolProperty(
        name="Display Get/Set current frame buttons in Shot List", default=True, options=set()
    )

    display_edit_times_in_shotlist: BoolProperty(
        name="Display Edit Times in Shot List",
        description="Display start and end frames of the shots in the time of the edit",
        default=False,
        options=set(),
    )

    def _update_camera_hud_display_in_viewports(self, context):
        if self.camera_hud_display_in_viewports:
            bpy.ops.uas_shot_manager.draw_camera_hud_in_viewports("INVOKE_DEFAULT")

    camera_hud_display_in_viewports: BoolProperty(
        name="Display shot name on cameras in 3D Viewports",
        description="Display the name of the shots near the camera object or frame in the 3D viewport",
        default=False,
        update=_update_camera_hud_display_in_viewports,
        options=set(),
    )

    def _update_camera_hud_display_in_pov(self, context):
        if self.camera_hud_display_in_pov:
            bpy.ops.uas_shot_manager.draw_camera_hud_in_pov("INVOKE_DEFAULT")

    camera_hud_display_in_pov: BoolProperty(
        name="Display Camera HUD in POV view mode in the 3D viewports",
        description="Display global infos in the 3D viewport",
        default=False,
        update=_update_camera_hud_display_in_pov,
        options=set(),
    )

    def getTargetViewportIndex(self, context, only_valid=False):
        """Return the index of the viewport where all the actions of the Shot Manager should occur,
        -1 if no suitable viewport is found.
        This viewport is called the target viewport and is defined in the UI by the user thanks
        to the variable props.target_viewport_index.
        A viewport is an area of type VIEW_3D.

        Args:
        only_valid:
            Since there may have more items in the list than viewports in the considered workspace the target viewport index
            may refer to a viewport that doesn't exist.
            To get a valid target viewport use the argument only_valid: if set to True it will return the index of the current
            context area, which should be the viewport with the calling Shot Manager.
            Return -1 if no viewport is available

        wkip props.target_viewport_index should be stored in the scene, per layout
        """
        ind = -1
        item = self.target_viewport_index
        # print(f"--- getTargetViewportIndex item: {item}")
        viewportsList = utils.getAreasByType(context, "VIEW_3D")

        # can be -1 if the context area is not a viewport or if no viewport is available in the workspace
        current_area_ind = utils.getAreaIndex(context, context.area, "VIEW_3D")
        if -1 == current_area_ind:
            # we try to get the first viewport, if one is available
            if 0 < len(viewportsList):
                current_area_ind = 0

        if "SELF" == item:
            ind = current_area_ind
        elif "AREA_00" == item:
            ind = 0
        elif "AREA_01" == item:
            ind = 1
        elif "AREA_02" == item:
            ind = 2
        elif "AREA_03" == item:
            ind = 3

        if only_valid:
            if 0 == len(viewportsList):
                ind = -1
            elif len(viewportsList) <= ind:
                ind = current_area_ind

        return ind

    def getValidTargetViewport(self, context):
        """Return a valid (= existing in the context) target viewport (= 3D view area)
        Return None if no valid viewport exists in the screen
        """
        valid_target = None
        valid_target_ind = self.getTargetViewportIndex(context, only_valid=True)
        if -1 < valid_target_ind:
            valid_target = utils.getAreaFromIndex(context, valid_target_ind, "VIEW_3D")
        return valid_target

    def getValidTargetViewportSpaceData(self, context):
        """Return a valid (= existing in the context) target viewport space data (= 3D view in 3D view area)
        Return None if no valid viewport exists in the screen
        """
        viewportArea = self.getValidTargetViewport(context)
        spaceData = None
        if viewportArea is not None:
            for space_data in viewportArea.spaces:
                if space_data.type == "VIEW_3D":
                    spaceData = space_data
                    break
        return spaceData

    def list_target_viewports(self, context):
        # res = config.gSeqEnumList
        res = None
        # res = list()
        nothingList = list()
        nothingList.append(
            ("SELF", "Me", "Target 3D View is the viewport where Shot Manager is used, 0 if not found", 0)
        )
        nothingList.append(("AREA_00", "0", "Target 3D View is viewport 0", 1))
        nothingList.append(("AREA_01", "1", "Target 3D View is viewport 1", 2))
        nothingList.append(("AREA_02", "2", "Target 3D View is viewport 2", 3))
        nothingList.append(("AREA_03", "3", "Target 3D View is viewport 3", 4))

        # seqList = getSequenceListFromOtioTimeline(config.gMontageOtio)
        # for i, item in enumerate(seqList):
        #     res.append((item, item, "My seq", i + 1))

        # res = getSequenceListFromOtio()
        # res.append(("NEW_CAMERA", "New Camera", "Create new camera", 0))
        # for i, cam in enumerate([c for c in context.scene.objects if c.type == "CAMERA"]):
        #     res.append(
        #         (cam.name, cam.name, 'Use the exising scene camera named "' + cam.name + '"\nfor the new shot', i + 1)
        #     )

        if res is None or 0 == len(res):
            res = nothingList
        return res

    def _update_target_viewport_index(self, context):
        prev = context.window_manager.UAS_shot_manager_display_overlay_tools
        context.window_manager.UAS_shot_manager_display_overlay_tools = False
        if prev:
            # bpy.ops.uas_shot_manager.interactive_shots_stack.unregister_handlers(context)
            context.window_manager.UAS_shot_manager_display_overlay_tools = True

        # from shotmanager.overlay_tools.interact_shots_stack.shots_stack_toolbar import display_state_changed_intShStack

        # display_state_changed_intShStack(context)

    # Get the target index with the function props.getTargetViewportIndex(context)
    target_viewport_index: EnumProperty(
        name="Target 3D Viewport",
        description="Index of the target viewport of the current workspace that will"
        "\nreceive all the actions set in the Shot Manager panel",
        items=(list_target_viewports),
        update=_update_target_viewport_index,
        options=set(),
        # default=0,
    )

    ####################
    # grease pencil
    # storyboard
    ####################

    # NOTE: call isContinuousGPEditingModeActive() to query the state of this value
    useContinuousGPEditing: BoolProperty(
        name="Continuous Drawing Mode",
        description="When used, the Storyboard Frame of each shot set to be the current"
        "\none will be automaticaly selected and switched to Draw mode",
        default=True,
    )

    isEditingStoryboardFrame: BoolProperty(
        name="Editing Storyboard Frame",
        description="If True, the storyboard frame of any shot that becomes current will be set to Draw Mode."
        "\n*** Do NOT change it directly ***"
        "\nThis is changed by the operators uas_shot_manager.toggle_continuous_gp_editing_mode and"
        "\nuas_shot_manager.greasepencil_select_and_draw",
        default=False,
    )

    def isContinuousGPEditingModeActive(self):
        """Return True if the context required to enter in a continuous drawing session is valid: the button
        has to be visible and checked.
        Note that the returned value is not dependent on the fact that a Grease Pencil object is being edited or not.
        Query props.getEditedGPShot() for that.
        Call this to get the state of continuous editing instead of directly using useContinuousGPEditing"""

        state = False
        currentLayout = self.getCurrentLayout()
        if currentLayout:
            state = currentLayout.display_storyboard_in_properties and self.useContinuousGPEditing
        # state = state and "STORYBOARD" == self.currentLayoutMode()
        return state

    def getParentShotFromGpChild(self, obj):
        """Return the shot using the specified object as achild of its camera, None if nothing found.
        Args:
            obj: can be a gp object or an empty or even whatever"""

        # wkip case where a cam has a parent cam is not taken into account here
        parentShot = None

        def _rec_getCamParent(obj):
            if "CAMERA" == obj.type:
                return obj
            if obj.parent is None:
                return None
            return _rec_getCamParent(obj.parent)

        if obj is not None:
            shotCam = _rec_getCamParent(obj)
            if shotCam is not None:
                # search for the shot in the current take
                shotsUsingCam = self.getShotsUsingCamera(shotCam)
                if len(shotsUsingCam):
                    parentShot = shotsUsingCam[0]
        return parentShot

    def isStoryboardFrame(self, obj):
        """Return True if the specified object is a storyboard frame, whatever the take it belongs to."""
        gpIsStoryboardFrame = False
        if obj is not None and "GPENCIL" == obj.type:
            parentShot = self.getParentShotFromGpChild(obj)
            gpIsStoryboardFrame = parentShot is not None
        return gpIsStoryboardFrame

    use_greasepencil: BoolProperty(
        name="Use Grease Pencil",
        description="Toggle the display of storyboard frames in the scene",
        #  update=_update_use_greasepencil,
        default=True,
        options=set(),
    )

    stb_displayCameras: BoolProperty(
        name="Display Storyboard Cameras",
        description=(
            "Toggle the display of the cameras of shots of type Storyboard Shot in the scene for the current take."
            "\nCameras of shots from takes that are not the current one will be hidden"
        ),
        default=True,
        options=set(),
    )

    def displayStoryboardFramesCameras(self, visible):
        """Toggle the display of the cameras of shots of type Storyboard shots.
        Only the cameras of the current take will be set to be displayed. Frames from other takes will be hidden."""

        self.stb_displayCameras = visible
        currentTakeInd = self.getCurrentTakeIndex()

        # first all the stb frame cameras of all the takes are hidden
        for take in self.getTakes():
            for sh in take.shots:
                if "STORYBOARD" == sh.shotType and sh.isCameraValid():
                    sh.camera.hide_select = True
                    sh.camera.hide_viewport = True

        # then we display only frames for the current take
        # Things have to be done in this order to support the fact that a camera (and hence its frame)
        # can be shared between one shot in the current take and a shot in another take
        if visible:
            for tInd, take in enumerate(self.getTakes()):
                if tInd == currentTakeInd:
                    for sh in take.shots:
                        if "STORYBOARD" == sh.shotType and sh.isCameraValid():
                            sh.camera.hide_select = False
                            sh.camera.hide_viewport = False

    def updateStoryboardFramesDisplay(
        self,
        forceHide=False,
        alsoForceHideAlwaysVisible=True,
        alsoForceHideCurrent=True,
        #   applyToAllTakes=True,
        takeIndex=-1,
    ):
        """Update the display of the storyboard frame (= grease pencil object) of the shots for the specified take.
        Only the frames of the current take will be set to be displayed. Frames from other takes will be hidden.

        Args:
            forceHide:  Force all the gp to be hidden (EVEN those explicitely set to Always Visible)
                        This argument is used by the renderer to hide all the gp of shots other than the rendered one.
            alsoForceHideCurrent: Used only when forceHide is True. Forces the current shot gp to hide. If False
                        then it is updated to match the visibility state of its visibility property.
            alsoForceHideAlwaysVisible: Used only when forceHide is True. Forces the shots with a gp set to
                        Always Visible to hide
            takeIndex:  if unspecified or -1 then the toggle is applied to the current take

            See the Visibility rules in the documentation: storyboard-frames-visibility.rst
        """
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            return ()

        currentTakeInd = self.getCurrentTakeIndex()
        currentShotInd = self.getCurrentShotIndex()

        # first all the stb frames of all the takes are hidden
        for tInd, take in enumerate(self.getTakes()):
            for shotInd, sh in enumerate(take.shots):
                sh.showGreasePencil(forceHide=True)

        # then we display only frames for the current take
        # Things have to be done in this order to support the fact that a camera (and hence its frame)
        # can be shared between one shot in the current take and a shot in another take
        for tInd, take in enumerate(self.getTakes()):
            #     if applyToAllTakes or tInd == takeInd:
            if tInd == currentTakeInd:
                for shotInd, sh in enumerate(take.shots):
                    if forceHide:
                        if not alsoForceHideCurrent and tInd == currentTakeInd and shotInd == currentShotInd:
                            sh.showGreasePencil()
                        else:
                            if not alsoForceHideAlwaysVisible:
                                # TOFIX: Replace this by a call to a property: sh.stbFrame for instance
                                forceHideAlwaysVisib = True
                                if sh.isCameraValid():
                                    gp_child = utils_greasepencil.get_greasepencil_child(sh.camera)
                                    if gp_child is not None:
                                        gpProps = sh.getGreasePencilProps(mode="STORYBOARD")
                                        if gpProps is not None and "ALWAYS_VISIBLE" == gpProps.visibility:
                                            forceHideAlwaysVisib = False

                                sh.showGreasePencil(forceHide=forceHideAlwaysVisib)
                            else:
                                sh.showGreasePencil(forceHide=True)
                    else:
                        sh.showGreasePencil()
                break

    # def updateGreasePencilVisibility(self, take):
    #     """Update the display of grease pencil objects of the specified take"""
    #     for sh in take.shots:
    #         sh.showGreasePencil()

    def enableGreasePencil(self, enable, takeIndex=-1):
        """Toggle the display of grease pencil objects for every shots of the specified take.
        Args:
            enable:     if True then disable the GP of every shots in every takes and turn only the
                        shots GP of the specified take visible
                        if False then disable the GP of every shots in every takes
            takeIndex:  if unspecified or -1 then the toggle is applied to the current take
        """
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            return ()

        self.use_greasepencil = enable
        self.updateStoryboardFramesDisplay(takeIndex=takeInd)

    stb_hasPinnedObject: BoolProperty(
        name="Pin Grease Pencil",
        description="Pin grease pencil object",
        default=False,
        options=set(),
    )
    stb_editedGPencilName: StringProperty(
        name="Edited Grease Pencil",
        description="Edited or pinned grease pencil object. Empty string if no grease pencil is being edited",
        default="",
        options=set(),
    )

    def getPinnedGPObjectName(self):
        """Return the name of the pinned object, an empty string if no object is currently pinned
        If the pinned object appears to be invalid then an empty string is returned"""
        pinnedGpencilName = ""
        if self.stb_hasPinnedObject:
            if "" != self.stb_editedGPencilName:
                if (
                    self.stb_editedGPencilName in self.parentScene.objects
                    and "GPENCIL" == self.parentScene.objects[self.stb_editedGPencilName].type
                ):
                    pinnedGpencilName = self.parentScene.objects[self.stb_editedGPencilName].name
                else:
                    self.stb_editedGPencilName = ""
                    self.stb_hasPinnedObject = False
            else:
                self.stb_hasPinnedObject = False

        return pinnedGpencilName

    stb_frameTemplate: PointerProperty(
        type=UAS_GreasePencil_FrameTemplate,
        options=set(),
    )

    def updateStoryboardGrid(self):
        """Set the camera of the storyboard frames on the 3D grid
        Only cameras related to storyboard frames, and not shots, are affected"""

        grid = self.stb_frameTemplate.frameGrid
        stbShots = self.getStoryboardShots(ignoreDisabled=False)

        # clear camera animation
        for shot in stbShots:
            if shot.isCameraValid():
                utils.clearTransformAnimation(shot.camera)

        grid.updateStoryboardGrid(stbShots)

    def getStoryboardShots(self, ignoreDisabled=False, takeIndex=-1):
        """Return a list of the shots that are of the type storyboard shot"""
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        shotList = []
        if -1 == takeInd:
            return shotList

        for shot in self.takes[takeInd].shots:
            # if shot.enabled or self.context.scene.UAS_shot_manager_props.seqTimeline_displayDisabledShots:
            if not ignoreDisabled or shot.enabled:
                if "STORYBOARD" == shot.shotType:
                    shotList.append(shot)

        return shotList

    def getEditedGPShot(self, shotType=None, onlyInCurrentTake=True):  # , takeIndex=-1):
        """Return the edited grease pencil parent shot, None if no grease pencil child is currently being edited.
        If onlyInCurrentTake is set to True then if the edited shot is not in the current take the returned value
        is None.
        Args:
            shotType: can be None to get the shot no matter which type it is, PREVIZ or STORYBOARD
            onlyInCurrentTake: if True, the edited shot is returned only if it belongs to the current shot
        """
        # takeInd = (
        #     self.getCurrentTakeIndex()
        #     if -1 == takeIndex
        #     else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        # )
        # if -1 == takeInd:
        #     return None

        editedGP = utils_greasepencil.getObjectInSubMode()

        # NOTE: we don't ckeck if the editing mode is Draw, Edit, Sculpt... this in order to
        # still navigate between edited objects without changing the mode
        if editedGP is not None and "GPENCIL" == editedGP.type:
            parentShot = self.getParentShotFromGpChild(editedGP)
            if parentShot is not None:
                if not onlyInCurrentTake or parentShot.getParentTakeIndex() == self.getCurrentTakeIndex():
                    if shotType is None:
                        return parentShot
                    elif shotType == parentShot.shotType:
                        return parentShot
        return None

    def getEditedStoryboardFrame(self):  # , takeIndex=-1):
        """Return the edited storyboard frame, None if not are currently being edited"""
        # takeInd = (
        #     self.getCurrentTakeIndex()
        #     if -1 == takeIndex
        #     else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        # )
        # if -1 == takeInd:
        #     return None

        return self.getEditedGPShot(shotType="STORYBOARD")

    ########################################################################
    # layout   ###
    ########################################################################

    # can be STORYBOARD or PREVIZ
    # not visible in the UI because radiobuttons are more suitable

    # def _update_layout_mode(self, context):
    #     prefs = config.getAddonPrefs()
    #     # print("\n*** Props _update_layout_mode updated. New state: ", self._update_layout_mode)
    #     # self.layout_but_storyboard = "STORYBOARD" == self._update_layout_mode
    #     # self.layout_but_previez = "PREVIZ" == self._update_layout_mode
    #     if "STORYBOARD" == self.layout_mode:
    #         self.display_storyboard_in_properties = True
    #         self.display_notes_in_properties = True
    #     #  prefs.display_25D_greasepencil_panel = True
    #     else:
    #         #   self.display_storyboard_in_properties = False
    #         self.display_notes_in_properties = False
    #     # prefs.display_25D_greasepencil_panel = False
    #     pass

    # layout_mode: EnumProperty(
    #     name="Layout Mode",
    #     description="Defines the layout used by the Shot Manager panel",
    #     items=(
    #         ("STORYBOARD", "Storyboard", "Storyboard layout"),
    #         ("PREVIZ", "Previz", "Previz layout"),
    #     ),
    #     update=_update_layout_mode,
    #     default="PREVIZ",
    # )

    # NOTE:
    # layout_but_storyboard and layout_but_previz behave as radiobuttons and control
    # the state of layout_mode
    def _get_layout_but_storyboard(self):
        # val = "STORYBOARD" == self.layout_mode
        val = "STORYBOARD" == self.currentLayoutMode()
        return val

    def _set_layout_but_storyboard(self, value):
        if value:
            # self.layout_mode = "STORYBOARD"
            self.setCurrentLayout("STORYBOARD")
            self.setCurrentLayoutByIndex(0)
        self["layout_but_storyboard"] = value

    def _update_layout_but_storyboard(self, context):
        print("\n*** layout_but_storyboard updated. New state: ", self.layout_but_storyboard)
        #         self.layout_mode = "PREVIZ"
        # self.setCurrentLayoutByIndex(0)
        for region in context.area.regions:
            if region.type == "UI":
                region.tag_redraw()

    layout_but_storyboard: BoolProperty(
        name="Storyboard",
        description="Set the Shot Manager panel layout to Storyboard",
        get=_get_layout_but_storyboard,
        set=_set_layout_but_storyboard,
        update=_update_layout_but_storyboard,
        default=False,
    )

    def _get_layout_but_previz(self):
        # val = "PREVIZ" == self.layout_mode
        val = "PREVIZ" == self.currentLayoutMode()
        return val

    def _set_layout_but_previz(self, value):
        if value:
            # self.layout_mode = "PREVIZ"
            self.setCurrentLayout("PREVIZ")
            self.setCurrentLayoutByIndex(1)
        self["layout_but_previz"] = value

    def _update_layout_but_previz(self, context):
        print("\n*** layout_but_previz updated. New state: ", self.layout_but_previz)
        #         self.layout_mode = "PREVIZ"
        # self.setCurrentLayoutByIndex(1)
        for region in context.area.regions:
            if region.type == "UI":
                region.tag_redraw()

    layout_but_previz: BoolProperty(
        name="Previz",
        description="Set the Shot Manager panel layout to Previz",
        get=_get_layout_but_previz,
        set=_set_layout_but_previz,
        update=_update_layout_but_previz,
        default=True,
    )

    ####################
    # Features
    ####################

    layouts: CollectionProperty(type=UAS_ShotManager_LayoutSettings)
    current_layout_index: IntProperty(default=0)

    def currentLayoutMode(self):
        """Equivalent to props.getCurrentLayout().layoutMode"""
        if -1 < self.current_layout_index < len(self.layouts):
            return self.layouts[self.current_layout_index].layoutMode
        return None

    def getCurrentLayout(self):
        if -1 < self.current_layout_index < len(self.layouts):
            return self.layouts[self.current_layout_index]
        return None

    def getCurrentLayoutIndex(self):
        return self.current_layout_index

    def setCurrentLayout(self, layoutMode):
        """Args:
        layoutMode: Can be "STORYBOARD or PREVIZ"""
        for ind, layout in enumerate(self.layouts):
            if layoutMode == layout.layoutMode:
                self.current_layout_index = ind
                break

    def setCurrentLayoutByIndex(self, layoutIndex):
        """Args:
        layoutMode: Can be 0 for "STORYBOARD or 1 for PREVIZ"""
        if 0 <= layoutIndex < len(self.layouts):
            self.current_layout_index = layoutIndex
        else:
            self.current_layout_index = -1

    def getLayout(self, layoutMode):
        """Args:
        layoutMode: Can be "STORYBOARD or PREVIZ"""
        for layout in self.layouts:
            if layoutMode == layout.layoutMode:
                return layout
        return None

    def createLayoutSettings(self):
        _logger.debug_ext("createLayerSettings", col="GREEN", tag="LAYOUT")

        stbLayout = self.layouts.add()
        stbLayout.initialize("STORYBOARD")

        pvzLayout = self.layouts.add()
        pvzLayout.initialize("PREVIZ")

    def resetLayoutSettingsToDefault(self, layoutMode):
        layout = self.getLayout(layoutMode)
        layout.initialize(layoutMode)

    # hidden UI parameter
    def _get_expand_shot_properties(self):
        val = self.get("expand_shot_properties", False)
        return val

    def _set_expand_shot_properties(self, value):
        self["expand_shot_properties"] = value

    def _update_expand_shot_properties(self, context):
        # print("\n*** expand_shot_properties updated. New state: ", self.expand_shot_properties)
        if self.expand_shot_properties:
            self.expand_notes_properties = False
            self.expand_cameraBG_properties = False
            self.expand_storyboard_properties = False

    expand_shot_properties: BoolProperty(
        name="Properties  ",
        description="Expand the Properties panel for the selected shot",
        default=False,
        get=_get_expand_shot_properties,
        set=_set_expand_shot_properties,
        update=_update_expand_shot_properties,
        options=set(),
    )

    display_camerabgtools_in_properties: BoolProperty(
        # name="Display Camera Background Image Tools in Shot Properties",
        description="Display the Camera Background Image Tools in the Shot Properties panel",
        default=False,
        # get=_get_expand_shot_properties,
        # set=_set_expand_shot_properties,
        # update=_update_expand_shot_properties,
        options=set(),
    )

    display_notes_in_properties: BoolProperty(
        # name="Display Shot Notes in Shot Properties",
        description="Display shot notes in the Shot Properties panels",
        default=False,
        options=set(),
    )

    # hidden UI parameter
    def _get_expand_notes_properties(self):
        val = self.get("expand_notes_properties", False)
        return val

    def _set_expand_notes_properties(self, value):
        self["expand_notes_properties"] = value

    def _update_expand_notes_properties(self, context):
        #    print("\n*** expand_notes_properties updated. New state: ", self.expand_notes_properties)
        if self.expand_notes_properties:
            self.expand_shot_properties = False
            self.expand_cameraBG_properties = False
            self.expand_storyboard_properties = False

    expand_notes_properties: BoolProperty(
        name="Notes",
        description="Expand the Notes Properties panel for the selected shot",
        default=False,
        get=_get_expand_notes_properties,
        set=_set_expand_notes_properties,
        update=_update_expand_notes_properties,
        options=set(),
    )

    display_cameraBG_in_properties: BoolProperty(
        name="Camera Background Tools",
        description="Display the camera background image tools and controls in the Shot Properties panel",
        default=False,
    )

    # hidden UI parameter
    def _get_expand_cameraBG_properties(self):
        val = self.get("expand_cameraBG_properties", False)
        return val

    def _set_expand_cameraBG_properties(self, value):
        self["expand_cameraBG_properties"] = value

    def _update_expand_cameraBG_properties(self, context):
        #    print("\n*** expand_cameraBG_properties updated. New state: ", self.expand_cameraBG_properties)
        if self.expand_cameraBG_properties:
            self.expand_shot_properties = False
            self.expand_notes_properties = False
            self.expand_storyboard_properties = False

    expand_cameraBG_properties: BoolProperty(
        name="Camera BG",
        description="Expand the Camera Background Properties panel for the selected shot",
        default=False,
        get=_get_expand_cameraBG_properties,
        set=_set_expand_cameraBG_properties,
        update=_update_expand_cameraBG_properties,
        options=set(),
    )

    # display_storyboard_in_properties: BoolProperty(
    #     name="Storyboard Frames and Grease Pencil Tools",
    #     description="Display the storyboard frames properties and tools in the Shot properties panel."
    #     "\nA storyboard frame is a Grease Pencil drawing surface associated to the camera of each shot",
    #     default=False,
    #     options=set(),
    # )

    # hidden UI parameter
    def _get_expand_storyboard_properties(self):
        val = self.get("expand_storyboard_properties", False)
        return val

    def _set_expand_storyboard_properties(self, value):
        self["expand_storyboard_properties"] = value

    def _update_expand_storyboard_properties(self, context):
        #    print("\n*** expand_storyboard_properties updated. New state: ", self.expand_storyboard_properties)
        if self.expand_storyboard_properties:
            self.expand_shot_properties = False
            self.expand_notes_properties = False
            self.expand_cameraBG_properties = False

    expand_storyboard_properties: BoolProperty(
        name="Storyboard Frames",
        description="Expand the Storyboard Frame Properties panel for the selected shot",
        default=False,
        get=_get_expand_storyboard_properties,
        set=_set_expand_storyboard_properties,
        update=_update_expand_storyboard_properties,
        options=set(),
    )

    display_takerendersettings_in_properties: BoolProperty(
        name="Take Render Settings",
        description="Display the take render settings in the Take Properties panel."
        "\nThese options allow each take to be rendered with its own output resolution",
        default=False,
        options=set(),
    )

    display_editmode_in_properties: BoolProperty(
        name="Display Global Edit Integration Tools",
        description="Display the advanced properties of the takes used to specify their position in a global edit",
        default=False,
        options=set(),
    )

    display_globaleditintegr_in_properties: BoolProperty(
        name="Display Global Edit Integration Tools",
        description="Display the advanced properties of the takes used to specify their position in a global edit",
        default=False,
        options=set(),
    )

    # display_retimer_panel: BoolProperty(
    #     name="Display Retimer sub-Panel",
    #     description="Display Retimer sub-panel in the Shot Manager panel",
    #     default=False,
    #     options=set(),
    # )

    display_notes_in_shotlist: BoolProperty(name="Display Color in Shot List", default=True, options=set())

    display_advanced_infos: BoolProperty(
        name="Display Advanced Infos",
        description="Display technical information and feedback in the UI",
        default=False,
        options=set(),
    )

    # def list_greasepencil_layer_modes(self, context):
    #     res = list()
    #     res.append(("ALL", "All", "", 0))
    #     res.append(("ACTIVE", "Active", "", 1))

    #     #  _logger.debug_ext(f"Layers Mode: context.object: {context.object.name}", col="RED")

    #     if context.active_object is not None and "GPENCIL" == context.active_object.type:
    #         numLayers = len(context.active_object.data.layers)
    #         if numLayers:
    #             for i, layer in reversed(list(enumerate(context.active_object.data.layers))):
    #                 res.append((layer.info, layer.info, "", numLayers - 1 - i + 2))
    #         else:
    #             res = (("NOLAYER", "No Layer", "", 0),)

    #     # res = [
    #     #     ("ALL", "All", "", 0),
    #     #     ("ACTIVE", "Active", "", 1),
    #     #     ("Rough", "Rough", "", 2),
    #     #     ("FG Lines", "FG Lines", "", 3),
    #     #     ("FG Fills", "FG Fills", "", 4),
    #     #     ("MiddleG Lines", "MiddleG Lines", "", 5),
    #     #     ("MiddleG Fills", "MiddleG Fills", "", 6),
    #     #     ("BG Lines", "BG Lines", "", 7),
    #     #     ("BG Fills", "BG Fills", "", 8),
    #     #     ("_Canvas_", "_Canvas_", "", 9),
    #     # ]
    #     #    _logger.debug_ext(f"Layers Mode: res: {res}", col="RED")
    #     return res

    def _get_greasePencil_layersModeB(self):
        #  val = self.get("greasePencil_layersMode", 0)
        # return val
        # print(f" context.object.name: {bpy.context.object.name}")
        val = 0  # "NOLAYER"
        if bpy.context.active_object is not None and "GPENCIL" == bpy.context.active_object.type:
            gpencil = bpy.context.active_object
            if len(gpencil.data.layers):
                pass
                val = self.get("greasePencil_layersModeB", 0)
                print(f" gpencil.name: {gpencil.name}, val:{val}")
                # gpSettings = self.stb_frameTemplate.getEditedGPByName(gpencil.name)
            # if gpSettings is not None:
            #     # Create a lookup-dict for the object layers
            #     # layers_dict = {layer.info: i for i, layer in enumerate(gpencil.data.layers)}
            #     layers_list = list()
            #     layers_list.append("ALL")
            #     layers_list.append("ACTIVE")
            #     for i, layer in reversed(list(enumerate(gpencil.data.layers))):
            #         layers_list.append(layer.info)

            #         ind = -1
            #         for i, name in enumerate(layers_list):
            #             if gpSettings.refLayerName == name:
            #                 ind = i
            #                 break
            #         if -1 != ind:
            #             val = ind
            # print(mat_dict["Material"]) # 0
        #  print(f"Val: {val}")
        return val

    def _set_greasePencil_layersModeB(self, value):
        self["greasePencil_layersModeB"] = value
        print(f" set Value: {value}")

    def _update_greasePencil_layersModeB(self, context):
        # print("\n*** greasePencil_layersModeB updated. New state: ", self.greasePencil_layersModeB)
        pass
        # if context.active_object is not None and "GPENCIL" == context.active_object.type:
        #     if len(context.active_object.data.layers):
        #         self.stb_frameTemplate.storeEditedGPSettings(
        #             context.active_object.name, context.active_object.data.layers.active.info
        #         )

    greasePencil_layersModeB: EnumProperty(
        name="Apply to:",
        items=(list_greasepencil_layer_modesB),
        # get=_get_greasePencil_layersModeB,
        # set=_set_greasePencil_layersModeB,
        update=_update_greasePencil_layersModeB,
        default=0,
        options=set(),
    )

    def _get_greasePencil_layersMode(self):
        # warning: use context.object, not context.active_object cause active_object can be None if
        # the active object is not visible in the viewport

        val = self.get("greasePencil_layersMode", 0)
        if bpy.context.object is not None and "GPENCIL" == bpy.context.object.type:
            gpencil = bpy.context.object
            if val >= len(gpencil.data.layers):
                val = 0

        # return val
        # print(f" context.object.name: {bpy.context.object.name}")
        # val = 0  # "NOLAYER"
        if bpy.context.object is not None and "GPENCIL" == bpy.context.object.type:
            gpencil = bpy.context.object
            if len(gpencil.data.layers):
                pass
                #         val = self.get("greasePencil_layersMode", 0)
                #         print(f" gpencil.name: {gpencil.name}, val:{val}")
                gpSettings = self.stb_frameTemplate.getEditedGPByName(gpencil.name)
                if gpSettings is not None:
                    #     # Create a lookup-dict for the object layers
                    #     # layers_dict = {layer.info: i for i, layer in enumerate(gpencil.data.layers)}
                    layers_list = list()
                    layers_list.append("ALL")
                    layers_list.append("ACTIVE")
                    for i, layer in reversed(list(enumerate(gpencil.data.layers))):
                        layers_list.append(layer.info)

                        ind = -1
                        for i, name in enumerate(layers_list):
                            if gpSettings.refLayerName == name:
                                ind = i
                                break
                        if -1 != ind:
                            val = ind

                    if val >= len(gpencil.data.layers):
                        val = 1
        # print(mat_dict["Material"]) # 0
        #  print(f"Val: {val}")
        return val

    def _set_greasePencil_layersMode(self, value):
        self["greasePencil_layersMode"] = value
        print(f" set Value: {value}")

    def _update_greasePencil_layersMode(self, context):
        print("\n*** greasePencil_layersMode updated. New state: ", self.greasePencil_layersMode)
        # warning: use context.object, not context.active_object cause active_object can be None if
        # the active object is not visible in the viewport

        # if context.object is not None and "GPENCIL" == context.object.type:
        #     gpencil = context.object
        #     if len(gpencil.data.layers):
        #         self.stb_frameTemplate.storeEditedGPSettings(
        #             gpencil.name, gpencil.data.layers.active.info
        #         )

    greasePencil_layersMode: EnumProperty(
        name="Apply to:",
        items=(list_greasepencil_layer_modes),
        # get=_get_greasePencil_layersMode,
        # set=_set_greasePencil_layersMode,
        update=_update_greasePencil_layersMode,
        default=0,
        options=set(),
    )

    def getLayerModeFromID(self, layerID):
        layerMode = layerID
        if "ALL" != layerID and "ACTIVE" != layerID and "NOLAYER" != layerID:
            preset = self.stb_frameTemplate.getPresetByID(layerID)
            if preset is not None:
                layerMode = preset.layerName
            else:
                layerMode = "ALL"
        return layerMode

    def list_greasepencil_materials(self, context):
        res = list()

        #  _logger.debug_ext(f"Updating DP mat list", col="PURPLE")
        if context.object is not None and "GPENCIL" == context.object.type:
            #   if len(context.object.data.layers):
            if len(context.object.material_slots):
                for i, mat in list(enumerate(context.object.material_slots)):
                    res.append((mat.name, mat.name, "", i))
                # res.append(
                #     ("DEBUG", "No Material Debug", "", len(res)),
                # )
            #      _logger.debug_ext(f"Updating DP mat list: num items: {len(context.object.material_slots)}", col="RED")
            else:
                res = (("NOMAT", "No Material", "", 0),)
        return res

    def _get_greasePencil_activeMaterial(self):
        val = self.get("greasePencil_activeMaterial", 0)
        #  print(" _get_greasePencil_activeMaterial")
        # props = config.getAddonProps(bpy.context.scene)
        # spaceDataViewport = props.getValidTargetViewportSpaceData(bpy.context)
        # if spaceDataViewport is not None:
        #     val = spaceDataViewport.overlay.gpencil_fade_layer
        # else:
        #     val = 1.0
        val = 0  # "NOMAT"
        if bpy.context.object is not None and "GPENCIL" == bpy.context.object.type:
            # if len(bpy.context.object.data.layers):
            # mats = list_greasepencil_materials()
            # mats = list()
            # for i, mat in list(enumerate(bpy.context.object.material_slots)):
            #     mats.append((mat.name, mat.name, "", i))
            # mat_dict = {mat.name: i for i, mat in enumerate(bpy.context.object.data.materials)}
            # val = mat_dict[self.greasePencil_activeMaterial]
            # print(f"bpy.context.object.active_material_index: {bpy.context.object.active_material_index}")

            obj = bpy.context.object
            # res = self.list_greasepencil_materials(bpy.context)

            # mat_dict = {mat.name: i for i, mat in enumerate(obj.material_slots)}
            # val = mat_dict[obj.active_material.name]
            val = obj.active_material_index
            # val = min(val, len(res) - 1)

            # val = 4
            # if max(val - 1, 0) != val - 1:
            #     val = val - 1
            # items = self.list_greasepencil_materials(bpy.context)
            # if len(items) == val:
            #     val = "_Canvas_Mat"

            # val = min(val - 1, len(bpy.context.object.material_slots) - 1)
        # else:
        #     _logger.debug_ext(f"No Mat ind found", col="RED")

        return val
        return min(val, len(context.object.material_slots))
        return max(val - 1, 0)

    def _set_greasePencil_activeMaterial(self, value):
        #  print(" _set_greasePencil_activeMaterial: value: ", value)
        self["greasePencil_activeMaterial"] = value

    def _update_greasePencil_activeMaterial(self, context):
        return
        if self.greasePencil_activeMaterial != "NOMAT":
            if context.object is not None and "GPENCIL" == context.object.type:
                # Create a lookup-dict for the object materials:
                # mat_dict = {mat.name: i for i, mat in enumerate(context.object.data.materials)}
                mat_dict = {mat.name: i for i, mat in enumerate(context.object.material_slots)}
                # then map names to indices:
                context.object.active_material_index = mat_dict[self.greasePencil_activeMaterial]

    greasePencil_activeMaterial: EnumProperty(
        name="Active Material",
        items=(list_greasepencil_materials),
        get=_get_greasePencil_activeMaterial,
        set=_set_greasePencil_activeMaterial,
        update=_update_greasePencil_activeMaterial,
        default=0,
        options=set(),
    )

    def list_greasepencil_materialsB(self, context):
        res = list()

        if context.object is not None and "GPENCIL" == context.object.type:
            #   if len(context.object.data.layers):
            if len(context.object.material_slots):
                for i, mat in list(enumerate(context.object.material_slots)):
                    res.append((mat.name, mat.name, "", i))
            else:
                res = (("NOMAT", "No Material", "", 0),)
        return res

    def _get_greasePencil_activeMaterialB(self):
        val = self.get("_get_greasePencil_activeMaterialB", 0)
        # print(" _get_greasePencil_activeMaterial")
        # props = config.getAddonProps(bpy.context.scene)
        # spaceDataViewport = props.getValidTargetViewportSpaceData(bpy.context)
        # if spaceDataViewport is not None:
        #     val = spaceDataViewport.overlay.gpencil_fade_layer
        # else:
        #     val = 1.0
        val = 0  # "NOMAT"
        if bpy.context.object is not None and "GPENCIL" == bpy.context.object.type:
            # if len(bpy.context.object.data.layers):
            # mats = list_greasepencil_materials()
            # mats = list()
            # for i, mat in list(enumerate(bpy.context.object.material_slots)):
            #     mats.append((mat.name, mat.name, "", i))
            # mat_dict = {mat.name: i for i, mat in enumerate(bpy.context.object.data.materials)}
            # val = mat_dict[self.greasePencil_activeMaterial]
            val = bpy.context.object.active_material_index

        return val

    def _set_greasePencil_activeMaterialB(self, value):
        #  print(" _set_greasePencil_activeMaterial: value: ", value)
        self["greasePencil_activeMaterialB"] = value

    def _update_greasePencil_activeMaterialB(self, context):
        if self.greasePencil_activeMaterialB != "NOMAT":
            if context.object is not None and "GPENCIL" == context.object.type:
                # Create a lookup-dict for the object materials:
                # mat_dict = {mat.name: i for i, mat in enumerate(context.object.data.materials)}
                mat_dict = {mat.name: i for i, mat in enumerate(context.object.material_slots)}
                # then map names to indices:
                context.object.active_material_index = mat_dict[self.greasePencil_activeMaterialB]

    greasePencil_activeMaterialB: EnumProperty(
        name="Active Material B",
        items=(list_greasepencil_materialsB),
        get=_get_greasePencil_activeMaterialB,
        set=_set_greasePencil_activeMaterialB,
        update=_update_greasePencil_activeMaterialB,
        default=0,
        options=set(),
    )

    def _get_useLockCameraView(self):
        # Can also use area.spaces.active to get the space assoc. with the area
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        realVal = space.lock_camera

        # not used, normal it's the fake property
        self.get("useLockCameraView", realVal)

        return realVal

    def _set_useLockCameraView(self, value):
        self["useLockCameraView"] = value
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.lock_camera = value

    # fake property: value never used in itself, its purpose is to update ofher properties
    useLockCameraView: BoolProperty(
        name="Lock Camera to View",
        description="Enable view navigation within the camera view",
        get=_get_useLockCameraView,
        set=_set_useLockCameraView,
        # update=_update_useLockCameraView,
        options=set(),
    )

    # shots global settings
    #############

    shotsGlobalSettings: PointerProperty(type=UAS_ShotManager_ShotsGlobalSettings)

    # prefs
    #############

    use_camera_color: BoolProperty(
        name="Use Camera Color",
        description="If True the color used by a shot is based on the color of its camera (default).\n"
        "Othewise the shot uses its own color",
        default=True,
        options=set(),
    )

    # bgImages_Alpha: FloatProperty(
    #     name="BG Image Alpha",
    #     description="Opacity of the camera background images",
    #     min=0.0,
    #     max=1.0,
    #     default=0.9,
    #     options=set(),
    # )

    # shots list
    #############

    current_shot_index: IntProperty(default=-1)

    selected_shot_index_call_update__flag: BoolProperty(default=True)

    def selectedShotShouldBecomeCurrent(self):
        """Return True if, according to the Preference settings and the current UI and scene context,
        the actualy selected shot should be set as the current one.
        Call this function just after the considered shot has been selected."""
        prefs = config.getAddonPrefs()

        setCurrentShot = False
        # if False:
        # if "STORYBOARD" == self.layout_mode:
        if "STORYBOARD" == self.currentLayoutMode():
            if prefs.shot_selected_from_shots_stack__flag:
                # print("   call from shots stack")
                if prefs.stb_selected_shot_in_shots_stack_changes_current_shot:
                    #    print("   sel in shots stack")
                    setCurrentShot = True
            else:
                if self.isContinuousGPEditingModeActive():
                    setCurrentShot = True
                elif prefs.stb_selected_shot_changes_current_shot:
                    _logger.debug_ext("  Stb _update_selected_shot_index from shot list")
                    # print("\n*** selected_shot_index. New state: ", self.selected_shot_index)
                    setCurrentShot = True
        # PREVIZ
        else:
            if prefs.shot_selected_from_shots_stack__flag:
                # print("   call from shots stack")
                if prefs.pvz_selected_shot_in_shots_stack_changes_current_shot:
                    #    print("   sel in shots stack")
                    setCurrentShot = True
            else:
                if self.isContinuousGPEditingModeActive():
                    setCurrentShot = True
                elif prefs.pvz_selected_shot_changes_current_shot:
                    _logger.debug_ext("  Pvz _update_selected_shot_index from shot list")
                    # print("\n*** selected_shot_index. New state: ", self.selected_shot_index)
                    setCurrentShot = True

        return setCurrentShot

    def _update_selected_shot_index(self, context):
        if self.selected_shot_index_call_update__flag:
            if -1 != self.selected_shot_index:
                _logger.debug_ext(f"\n*** selected_shot_index. New state: {self.selected_shot_index}")

                if self.selectedShotShouldBecomeCurrent():
                    bpy.ops.uas_shot_manager.set_current_shot("INVOKE_DEFAULT", index=self.selected_shot_index)

    selected_shot_index: IntProperty(name="Shot Name", update=_update_selected_shot_index, default=-1)

    current_shot_properties_mode: bpy.props.EnumProperty(
        name="Display Shot Properties Mode",
        description="Update the content of the Shot Properties panel either on the current shot\nor on the shot seleted in the shots list",
        items=(("CURRENT", "Current Shot", ""), ("SELECTED", "Selected Shot", "")),
        default="SELECTED",
        options=set(),
    )

    highlight_all_shot_frames: BoolProperty(
        description="Highlight Framing Values When Equal to Current Time", default=True, options=set()
    )

    # timeline
    #############

    # def toggle_overlay_tools_display( self, context ):
    #     if self.display_timeline:
    #         bpy.ops.uas_shot_manager.sequence_timeline ( "INVOKE_DEFAULT" )

    # display_timeline: BoolProperty (    default = False,
    #                                     options = set ( ),
    #                                     update = toggle_overlay_tools_display )

    change_time: BoolProperty(default=True, options=set())

    # sequence timeline properties
    #################################
    def _update_seqTimeline_displayDisabledShots(self, context):
        config.gRedrawShotStack = True

    seqTimeline_displayDisabledShots: BoolProperty(
        default=False, update=_update_seqTimeline_displayDisabledShots, options=set()
    )

    # interact shots stack properties
    #################################

    def _update_interactShotsStack_displayDisabledShots(self, context):
        config.gRedrawShotStack = True

    interactShotsStack_displayDisabledShots: BoolProperty(
        default=False, update=_update_interactShotsStack_displayDisabledShots, options=set()
    )
    interactShotsStack_displayInCompactMode: BoolProperty(default=False, options=set())

    def list_target_dopesheets(self, context):
        # res = config.gSeqEnumList
        res = None
        # res = list()
        nothingList = list()
        nothingList.append(
            (
                "SELF",
                "Me",
                "Target Dopesheet is the editor where the Interactive Shots Stack is used, 0 if not found",
                0,
            )
        )
        nothingList.append(("AREA_00", "0", "Target Dopesheet is 0", 1))
        nothingList.append(("AREA_01", "1", "Target Dopesheet is 1", 2))
        nothingList.append(("AREA_02", "2", "Target Dopesheet is 2", 3))
        nothingList.append(("AREA_03", "3", "Target Dopesheet is 3", 4))

        # seqList = getSequenceListFromOtioTimeline(config.gMontageOtio)
        # for i, item in enumerate(seqList):
        #     res.append((item, item, "My seq", i + 1))

        # res = getSequenceListFromOtio()
        # res.append(("NEW_CAMERA", "New Camera", "Create new camera", 0))
        # for i, cam in enumerate([c for c in context.scene.objects if c.type == "CAMERA"]):
        #     res.append(
        #         (cam.name, cam.name, 'Use the exising scene camera named "' + cam.name + '"\nfor the new shot', i + 1)
        #     )

        if res is None or 0 == len(res):
            res = nothingList
        return res

    def _update_interactShotsStack_target_dopesheet_index(self, context):
        prev = context.window_manager.UAS_shot_manager_display_overlay_tools
        context.window_manager.UAS_shot_manager_display_overlay_tools = False
        if prev:
            # bpy.ops.uas_shot_manager.interactive_shots_stack.unregister_handlers(context)
            context.window_manager.UAS_shot_manager_display_overlay_tools = True

        # from shotmanager.overlay_tools.interact_shots_stack.shots_stack_toolbar import display_state_changed_intShStack

        # display_state_changed_intShStack(context)

    # Get the target index with the function props.getTargetViewportIndex(context)
    interactShotsStack_target_dopesheet_index: EnumProperty(
        name="Target Dopesheet",
        description="Index of the target dopesheet of the current workspace that will"
        "\nreceive the Interactive Shots Stack tool."
        "\nThe dopesheet target index will be displayed in green",
        items=(list_target_dopesheets),
        update=_update_interactShotsStack_target_dopesheet_index,
        options=set(),
        # default=0,
    )

    def getTargetDopesheetIndex(self, context, only_valid=False):
        """Return the index of the viewport where all the actions of the Shot Manager should occur.
        This viewport is called the target viewport and is defined in the UI by the user thanks
        to the variable props.target_viewport_index.
        A viewport is an area of type VIEW_3D.

        Args:
        only_valid:
            Since there may have more items in the list than viewports in the considered workspace the target viewport index
            may refer to a viewport that doesn't exist.
            To get a valid target viewport use the argument only_valid: if set to True it will return the index of the current
            context area, which should be the viewport with the calling Shot Manager.
            Return -1 if no viewport is available

        wkip props.target_viewport_index should be stored in the scene, per layout
        """
        ind = -1
        item = self.interactShotsStack_target_dopesheet_index
        # print(f"--- getTargetViewportIndex item: {item}")
        dopesheetsList = utils.getDopesheets(context)

        # can be -1 if the context area is not a viewport or if no viewport is available in the workspace
        current_area_ind = utils.getDopesheetIndex(context, context.area)
        if -1 == current_area_ind:
            # we try to get the first viewport, if one is available
            if 0 < len(dopesheetsList):
                # try to get the first dopesheet with a timeline
                timelines = utils.getDopesheets(context, "TIMELINE")
                if len(timelines):
                    current_area_ind = utils.getDopesheetIndex(context, timelines[0])
                else:
                    current_area_ind = 0

        if "SELF" == item:
            ind = current_area_ind
        elif "AREA_00" == item:
            ind = 0
        elif "AREA_01" == item:
            ind = 1
        elif "AREA_02" == item:
            ind = 2
        elif "AREA_03" == item:
            ind = 3

        if only_valid:
            if 0 == len(dopesheetsList):
                ind = -1
            elif len(dopesheetsList) <= ind:
                ind = current_area_ind

        return ind

    def getValidTargetDopesheet(self, context):
        """Return a valid (= existing in the context) target dopesheet
        Return None if no valid dopesheet exists in the screen
        """
        valid_target = None
        valid_target_ind = self.getTargetDopesheetIndex(context, only_valid=True)
        if -1 < valid_target_ind:
            valid_target = utils.getDopesheetFromIndex(context, valid_target_ind)
        return valid_target

    #################################
    #################################
    def _get_playSpeedGlobal(self):
        val = self.get("playSpeedGlobal", 1.0)
        val = 100.0 / bpy.context.scene.render.fps_base
        return val

    def _set_playSpeedGlobal(self, value):
        self["playSpeedGlobal"] = value

    def _update_playSpeedGlobal(self, context):
        bpy.context.scene.render.fps_base = 100.0 / self["playSpeedGlobal"]

    playSpeedGlobal: FloatProperty(
        name="Play Speed",
        description="Change the global play speed of the scene",
        subtype="PERCENTAGE",
        soft_min=10,
        soft_max=200,
        precision=0,
        get=_get_playSpeedGlobal,
        set=_set_playSpeedGlobal,
        update=_update_playSpeedGlobal,
        default=100.0,
        options=set(),
    )

    # display_prev_next_buttons: BoolProperty (
    #     default = True,
    #     options = set ( ) )

    # takes
    #############

    def _list_takes(self, context):
        res = list()
        takes = self.takes
        for i, take in enumerate([t.name for t in takes]):
            res.append((take, take, "", i))

        return res

    def _update_current_take_name(self, context):
        # print(f"_update_current_take_name: {self.getCurrentTakeIndex()}, {self.getCurrentTakeName()}")
        # _logger.debug("Change current take")

        self.setResolutionToScene()
        self.setCurrentShotByIndex(0)
        self.setSelectedShotByIndex(0)

    current_take_name: EnumProperty(
        name="Takes",
        description="Select a take",
        items=_list_takes,
        update=_update_current_take_name,
    )

    takes: CollectionProperty(type=UAS_ShotManager_Take)

    ####################
    # takes
    ####################

    # wkip deprecated
    def getUniqueTakeName(self, nameToMakeUnique):
        uniqueName = nameToMakeUnique
        takes = self.getTakes()

        dup_name = False
        for take in takes:
            if uniqueName == take.name:
                dup_name = True
        if dup_name:
            uniqueName = f"{uniqueName}_1"

        return uniqueName

    def getTakes(self):
        return self.takes

    def getNumTakes(self):
        return len(self.takes)

    def getTakeByIndex(self, takeIndex):
        """Return the take corresponding to the specified index"""
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        take = None
        if -1 == takeInd:
            return take
        return self.takes[takeInd]

    def getTakeByName(self, takeName):
        """Return the first take with the specified name, None if not found"""
        for t in self.takes:
            if t.name == takeName:
                return t
        return None

    def getTakeIndex(self, take):
        takeInd = -1

        if 0 < len(self.takes):
            takeInd = 0
            while takeInd < len(self.takes) and self.takes[takeInd] != take:
                takeInd += 1
            if takeInd >= len(self.takes):
                takeInd = -1

        return takeInd

    def getTakeIndexByName(self, takeName):
        """Return the index of the first take with the specified name, -1 if not found"""
        if len(self.takes):
            for i in range(0, len(self.takes) + 1):
                if self.takes[i].name == takeName:
                    return i
        return -1

    def getCurrentTakeIndex(self):
        takeInd = -1
        if 0 < len(self.takes):
            takeInd = 0
            #      print(" self.takes[0]: " + str(self.takes[takeInd].name) + ", type: " + str(type(self.takes[takeInd])) )
            #     print(" self.current_take_name: " + str(self.current_take_name) + ", type: " + str(type(self.current_take_name)) )
            while takeInd < len(self.takes) and self.takes[takeInd].name != self.current_take_name:
                takeInd += 1
            if takeInd >= len(self.takes):
                takeInd = -1
        #    self.current_take_name = self.takes[takeInd].name

        return takeInd

    def setCurrentTakeByIndex(self, currentTakeIndex):
        currentTakeInd = min(currentTakeIndex, len(self.takes) - 1)
        if -1 < currentTakeInd:
            self.current_take_name = self.takes[currentTakeInd].name

            #   already in current_take_name._update:
            # self.setCurrentShotByIndex(0)
            # self.setSelectedShotByIndex(0)
            # self.setResolutionToScene()
        else:
            self.current_take_name = ""

        # print(f" ---- currentTakeByIndex: {currentTakeInd}, {self.getTakeByIndex(currentTakeInd)}")

    def getCurrentTake(self):
        currentTakeInd = self.getCurrentTakeIndex()
        if -1 == currentTakeInd:
            return None
        return self.getTakes()[currentTakeInd]

    def getCurrentTakeName(self):
        """Return the name of the current take,"""
        #    print("getCurrentTakeName")
        #    currentTakeInd = self.getCurrentTakeIndex()
        #    if -1 == currentTakeInd: return None
        #    return (self.getTakes()[currentTakeInd].name)
        currentTakeName = self.current_take_name
        return currentTakeName

    def getTakeName_PathCompliant(self, takeIndex=-1):
        """Return the name of the current take with spaces replaced by a non-space separator"""
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        takeName = ""
        if -1 == takeInd:
            return takeName

        takeName = self.takes[takeInd].getName_PathCompliant()

        return takeName

    def createDefaultTake(self):
        takes = self.getTakes()
        defaultTake = None
        if 0 >= len(takes):
            defaultTake = takes.add()
            defaultName = "Main Take"
            if self.use_project_settings:
                defaultName = self.project_default_take_name
            defaultTake.initialize(self, name=defaultName)
            self.setCurrentTakeByIndex(0)
            # self.setCurrentShotByIndex(-1)
            # self.setSelectedShotByIndex(-1)

        else:
            defaultTake = takes[0]
        return defaultTake

    def addTake(self, atIndex=-1, name="New Take"):
        """Add a new take after the current take if possible or at the end of the take list otherwise
        Return the newly added take
        """
        takes = self.getTakes()
        newTake = None
        if len(takes) <= 0:
            newTake = self.createDefaultTake()
        else:
            newTakeName = self.getUniqueTakeName(name)

            #######
            # important note: newTake points to the slot in takes array, not to the take itself
            newTake = takes.add()
            newTake.initialize(self, name="" + newTakeName)

        # self.current_take_name = newTake.name
        # print(f"new added take name: {newTake.name}")

        # move take at specified index
        # !!! warning: newTake has to be updated !!!
        if -1 != atIndex:
            atValidIndex = max(atIndex, 0)
            atValidIndex = min(atValidIndex, len(takes) - 1)
            takes.move(len(takes) - 1, atValidIndex)
            newTake = takes[atValidIndex]

        # after a move newTake is different!
        # print(f"new added take name02: {newTake.name}")

        return newTake

    def copyTake(self, take, atIndex=-1, copyCamera=False, ignoreDisabled=False):
        """Copy a take after the current take if possible or at the end of the takes list otherwise
        Return the newly added take
        """

        newTake = self.addTake(atIndex=atIndex, name=take.name + "_copy")

        newTake.copyPropertiesFrom(take)

        newTakeInd = self.getTakeIndex(newTake)

        shots = take.getShotsList(ignoreDisabled=ignoreDisabled)
        for shot in shots:
            self.copyShot(shot, targetTakeIndex=newTakeInd, copyCamera=copyCamera, copyGreasePencil=True)

        return newTake

    def moveTakeToIndex(self, take, newIndex, setAsMainTake=False):
        """Return the new take index if the move is done, -1 otherwise"""
        if take is None:
            return -1

        currentTakeInd = self.getCurrentTakeIndex()
        takeInd = self.getTakeIndex(take)
        newInd = max(0, newIndex)
        newInd = min(newInd, len(self.takes) - 1)

        # Main Take cannot be moved by design
        if not setAsMainTake:
            if 0 == currentTakeInd or 0 == newInd:
                return -1

        self.takes.move(takeInd, newInd)
        self.setCurrentTakeByIndex(newInd)

        return newInd

    #############
    # render
    #############
    # Those properties are overriden by the project settings if use_project_settings is true

    def get_useStampInfoDuringRendering(self):
        #  return self.useStampInfoDuringRendering
        val = self.get("useStampInfoDuringRendering", True)
        # print("*** get_useStampInfoDuringRendering: value: ", val)
        return val

    def set_useStampInfoDuringRendering(self, value):
        print("*** set_useStampInfoDuringRendering: value: ", value)
        self["useStampInfoDuringRendering"] = value

        if getattr(bpy.context.scene, "UAS_SM_StampInfo_Settings", None) is not None:
            # bpy.context.scene.UAS_SM_StampInfo_Settings.activateStampInfo(value)
            bpy.context.scene.UAS_SM_StampInfo_Settings.stampInfoUsed = value

    useStampInfoDuringRendering: BoolProperty(
        name="Stamp Info on Output",
        description="Stamp render information on rendered images thanks to Stamp Info add-on",
        default=True,
        get=get_useStampInfoDuringRendering,  # removed cause the use of Stamp Info in this add-on is independent from the one of Stamp Info add-on itself
        set=set_useStampInfoDuringRendering,
        options=set(),
    )

    ############
    # render properties for UI

    def reset_render_properties(self):
        # from ..utils.utils_inspectors import resetAttrs

        # print("stampInfo_resetProperties...")
        # print(f"Scene name: {bpy.context.scene.name}")

        # resetAttrs(self.renderSettingsStill)
        # resetAttrs(self.renderSettingsAnim)
        # resetAttrs(self.renderSettingsAll)
        # resetAttrs(self.renderSettingsOtio)
        # resetAttrs(self.renderSettingsPlayblast)

        self.createRenderSettings()

    renderRootPath: StringProperty(
        name="Render Root Path",
        description="Directory where the rendered files will be placed.\n"
        "Relative path must be set directly in the text field and must start with ''//''",
        default="//",
    )

    def isRenderRootPathValid(self, renderRootFilePath=None, ignoreRelativePathIfFileNotSaved=True):
        """Args:
        ignoreRelativePathIfFileNotSaved: if True, return True as long as the file is not saved, otherwhise the path
        is tested using the current Blender file path as parent for the path"""
        rootPath = self.renderRootPath if renderRootFilePath is None else renderRootFilePath

        if "" == rootPath:
            return False

        pathIsValid = False

        if rootPath.startswith("//"):
            if ignoreRelativePathIfFileNotSaved:
                return True

            currentFilePath = bpy.path.abspath(bpy.data.filepath)
            # file not saved
            if "" == currentFilePath:
                return False

            rootPathAbs = Path(currentFilePath).parent + rootPath[2:]
            if rootPathAbs.exist():
                pathIsValid = True
        else:
            # if os.path.exists(rootPath) or :
            if Path(rootPath).exists():
                pathIsValid = True
        return pathIsValid

    def isStampInfoAvailable(self):
        """Return True if the add-on UAS Stamp Info is available, registred and ready to be used"""
        readyToUse = getattr(bpy.context.scene, "UAS_SM_StampInfo_Settings", None) is not None

        try:
            import PIL
        except ImportError as error:
            readyToUse = False

        # stampInfoSettings = getStampInfo()
        # readyToUse = stampInfoSettings is not None
        return readyToUse

    def isStampInfoAllowed(self):
        """Return True if the add-on UAS Stamp Info is available and allowed to be used"""
        allowed = self.isStampInfoAvailable()
        # wkipwkipwkip temp while fixing stamp info...
        allowed = allowed and False
        return allowed

    def stampInfoUsed(self):
        """Return True if the add-on UAS Stamp Info is available and allowed to be used and checked for use,
        either from the UI or by the project settings
        """
        used = False
        if self.use_project_settings:
            used = self.project_use_stampinfo
        else:
            used = False  # self.useProjectRenderSettings

        used = used and self.isStampInfoAvailable()

        return used

    def addRenderSettings(self):
        newRenderSettings = self.renderSettingsList.add()
        return newRenderSettings

    renderContext: PointerProperty(type=UAS_ShotManager_RenderGlobalContext)

    # renderSettingsStill: CollectionProperty (
    #   type = UAS_ShotManager_RenderSettings )
    renderSettingsStill: PointerProperty(type=UAS_ShotManager_RenderSettings)

    renderSettingsAnim: PointerProperty(type=UAS_ShotManager_RenderSettings)

    renderSettingsAll: PointerProperty(type=UAS_ShotManager_RenderSettings)

    renderSettingsOtio: PointerProperty(type=UAS_ShotManager_RenderSettings)

    renderSettingsPlayblast: PointerProperty(type=UAS_ShotManager_RenderSettings)

    def get_displayStillProps(self):
        val = self.get("displayStillProps", True)
        return val

    def set_displayStillProps(self, value):
        # print(" set_displayStillProps: value: ", value)
        self["displayStillProps"] = True
        self["displayAnimationProps"] = False
        self["displayAllEditsProps"] = False
        self["displayOtioProps"] = False
        self["displayPlayblastProps"] = False

    def get_displayAnimationProps(self):
        val = self.get("displayAnimationProps", False)
        return val

    def set_displayAnimationProps(self, value):
        self["displayStillProps"] = False
        self["displayAnimationProps"] = True
        self["displayAllEditsProps"] = False
        self["displayOtioProps"] = False
        self["displayPlayblastProps"] = False

    def get_displayProjectProps(self):
        val = self.get("displayAllEditsProps", False)
        return val

    def set_displayProjectProps(self, value):
        print(" set_displayProjectProps: value: ", value)
        self["displayStillProps"] = False
        self["displayAnimationProps"] = False
        self["displayAllEditsProps"] = True
        self["displayOtioProps"] = False
        self["displayPlayblastProps"] = False

    def get_displayOtioProps(self):
        val = self.get("displayOtioProps", False)
        return val

    def set_displayOtioProps(self, value):
        # print(" set_displayOtioProps: value: ", value)
        self["displayStillProps"] = False
        self["displayAnimationProps"] = False
        self["displayAllEditsProps"] = False
        self["displayOtioProps"] = True
        self["displayPlayblastProps"] = False

    def get_displayPlayblastProps(self):
        val = self.get("displayPlayblastProps", False)
        return val

    def set_displayPlayblastProps(self, value):
        _logger.debug(f" set_displayPlayblastProps: value: {value}")
        self["displayStillProps"] = False
        self["displayAnimationProps"] = False
        self["displayAllEditsProps"] = False
        self["displayOtioProps"] = False
        self["displayPlayblastProps"] = True

    displayStillProps: BoolProperty(
        name="Display Still Preset Properties", get=get_displayStillProps, set=set_displayStillProps, default=True
    )
    displayAnimationProps: BoolProperty(
        name="Display Animation Preset Properties",
        get=get_displayAnimationProps,
        set=set_displayAnimationProps,
        default=False,
    )
    displayAllEditsProps: BoolProperty(
        name="Display Project Preset Properties",
        get=get_displayProjectProps,
        set=set_displayProjectProps,
        default=False,
    )
    displayOtioProps: BoolProperty(
        name="Display OpenTimelineIO Export Preset Properties",
        get=get_displayOtioProps,
        set=set_displayOtioProps,
        default=False,
    )
    displayPlayblastProps: BoolProperty(
        name="Display Playblast Preset Properties",
        get=get_displayPlayblastProps,
        set=set_displayPlayblastProps,
        default=False,
    )

    ####################
    # editing
    ####################

    def getEditDuration(self, ignoreDisabled=True, takeIndex=-1):
        """Return edit duration in frames"""
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        duration = -1
        if -1 == takeInd:
            return -1

        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)

        if 0 < len(shotList):
            duration = 0
            for sh in shotList:
                duration += sh.getDuration()

        return duration

    def getEditTime(self, referenceShot, frameIndexIn3DTime, referenceLevel="TAKE", ignoreDisabled=True):
        """Return edit current time in frames, -1 if no shots or if current shot is disabled
        Works on the take from which referenceShot is coming from.
        If ignoreDisabled is True disabled shots are always ignored and considered as not belonging to the edit.
        wkip negative times issues coming here... :/
        referenceLevel can be "TAKE" or "GLOBAL_EDIT"
        """
        frameIndInEdit = -1
        if referenceShot is None:
            return frameIndInEdit

        takeInd = referenceShot.getParentTakeIndex()
        # ignoreDisabled = True

        # case where specified shot is disabled -- current shot may not be in the shot list if shotList is not the whole list
        if ignoreDisabled and not referenceShot.enabled:
            return -1

        # specified time must be in the range of the specifed shot!!!
        # get the whole shots list
        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeInd)

        if 0 < len(shotList):
            if referenceShot.start <= frameIndexIn3DTime and frameIndexIn3DTime <= referenceShot.end:
                frameIndInEdit = 0
                shotInd = 0
                while shotInd < len(shotList) and referenceShot != shotList[shotInd]:
                    #         print("    While: shotInd: " + str(shotInd) + ", referenceShot: " + str(referenceShot) + ", shotList[shotInd]: " + str(shots[shotInd]))
                    #         print("    frameIndInEdit: ", frameIndInEdit)
                    if not ignoreDisabled or shotList[shotInd].enabled:
                        frameIndInEdit += shotList[shotInd].getDuration()
                    shotInd += 1

                frameIndInEdit += frameIndexIn3DTime - referenceShot.start

                if "GLOBAL_EDIT" == referenceLevel:
                    frameIndInEdit += referenceShot.getParentTake().startInGlobalEdit
                else:
                    # at take level
                    frameIndInEdit += self.editStartFrame  # at project level

        return frameIndInEdit

    def getEditCurrentTime(self, referenceLevel="TAKE", ignoreDisabled=True):
        """Return edit current time in frames, -1 if no shots or if current shot is disabled and ignoreDisabled is True
        works only on current take
        wkip negative times issues coming here... :/
        """
        # print(f"_update_current_take_name: {self.getCurrentTakeIndex()}, {self.getCurrentTakeName()}")
        # works only on current take
        takeInd = self.getCurrentTakeIndex()
        editCurrentTime = -1
        if -1 == takeInd:
            return editCurrentTime

        # current time must be in the range of the current shot!!!
        # get the whole shots list
        #        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeInd)
        shot = self.getCurrentShot()

        return self.getEditTime(
            shot, bpy.context.scene.frame_current, referenceLevel=referenceLevel, ignoreDisabled=ignoreDisabled
        )

        # # works only on current take
        # takeInd = self.getCurrentTakeIndex()
        # editCurrentTime = -1
        # if -1 == takeInd:
        #     return editCurrentTime

        # # current time must be in the range of the current shot!!!
        # # get the whole shots list
        # shotList = self.getShotsList(ignoreDisabled=False, takeIndex=takeInd)

        # if 0 < len(shotList):
        #     # case where current shot is disabled -- current shot may not be in the shot list if shotList is not the whole list
        #     currentShot = self.getCurrentShot()

        #     if currentShot is not None:
        #         currentTime = bpy.context.scene.frame_current

        #         if currentShot.enabled and currentShot.start <= currentTime and currentTime <= currentShot.end:
        #             editCurrentTime = 0
        #             shotInd = 0
        #             while shotInd < len(shotList) and currentShot != shotList[shotInd]:
        #                 #         print("    While: shotInd: " + str(shotInd) + ", currentShot: " + str(currentShot) + ", shotList[shotInd]: " + str(shots[shotInd]))
        #                 #         print("    editCurrentTime: ", editCurrentTime)
        #                 if not ignoreDisabled or shotList[shotInd].enabled:
        #                     editCurrentTime += shotList[shotInd].getDuration()
        #                 shotInd += 1

        #             editCurrentTime += currentTime - currentShot.start
        #         # if shotInd == len(shotList): editCurrentTime = -1

        # return editCurrentTime

    def getEditCurrentTimeForSelectedShot(self, referenceLevel="TAKE", ignoreDisabled=True):
        """Return edit current time in frames, -1 if no shots or if current shot is disabled
        works only on current take
        wkip negative times issues coming here... :/
        """
        # works only on current take
        takeInd = self.getCurrentTakeIndex()
        editCurrentTime = -1
        if -1 == takeInd:
            return editCurrentTime

        # current time must be in the range of the current shot!!!
        # get the whole shots list
        #        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeInd)
        shot = self.getSelectedShot()

        return self.getEditTime(shot, bpy.context.scene.frame_current, referenceLevel=referenceLevel)

    def getEditShots(self, ignoreDisabled=True):
        return self.getShotsList(ignoreDisabled=ignoreDisabled)

    ####################
    # shots
    ####################

    def getUniqueShotName(self, nameToMakeUnique, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            return uniqueName

        shotList = self.getShotsList(ignoreDisabled=False, takeIndex=takeIndex)
        uniqueName = nameToMakeUnique
        ind = 1
        restartLoop = True
        while restartLoop:
            restartLoop = False
            for s in shotList:
                if uniqueName.lower() == s.name.lower():
                    uniqueName = f"{nameToMakeUnique}.{ind:03}"
                    ind += 1
                    restartLoop = True
                    break

        # dup_name = False
        # for shot in shotList:
        #     if uniqueName == shot.name:
        #         dup_name = True
        # if dup_name:
        #     uniqueName = f"{uniqueName}_1"

        return uniqueName

    def addShot(
        self,
        shotType="PREVIZ",
        atIndex=-1,
        takeIndex=-1,
        name="defaultShot",
        start=10,
        end=20,
        durationLocked=False,
        camera=None,
        color=(0.2, 0.6, 0.8, 1),
        enabled=True,
        addGreasePencilStoryboard=False,
    ):
        """Add a new shot after the current shot if possible or at the end of the shot list otherwise (case of an add in a take
        that is not the current one)
        Return the newly added shot
        Since this function works also with takes that are not the current one the current shot is not taken into account not modified
        """

        currentTakeInd = self.getCurrentTakeIndex()
        takeInd = (
            currentTakeInd
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            print("AddShot: Failed")
            return None

        newShot = None
        shots = self.get_shots(takeIndex=takeInd)

        newShot = shots.add()  # shot is added at the end
        newShot.parentScene = self.getParentScene()
        # newShot.parentTakeIndex = takeInd
        newShot.shotType = shotType
        newShot.initialize(self.getTakeByIndex(currentTakeInd))
        newShot.name = name
        newShot.enabled = enabled
        newShot.end = 9999999  # mandatory cause start is clamped by end
        newShot.start = start
        newShot.end = end
        newShot.durationLocked = durationLocked
        newShot.camera = camera
        newShot.color = color

        # move shot at specified index
        # !!! warning: newShot has to be updated !!!
        newShotInd = len(shots) - 1
        if -1 != atIndex:
            atValidIndex = max(atIndex, 0)
            atValidIndex = min(atValidIndex, len(shots) - 1)
            shots.move(len(shots) - 1, atValidIndex)
            newShot = shots[atValidIndex]
            newShotInd = atValidIndex

        if addGreasePencilStoryboard:
            # newShot.addGreasePencil(mode=shotType)
            newShot.addStoryboardFrame()

        # update the current take if needed
        if takeInd == currentTakeInd:
            self.setCurrentShotByIndex(newShotInd)
            self.setSelectedShotByIndex(newShotInd)

        # warning: by reordering the shots it looks like newShot is not pointing anymore on the new shot
        # we then get it again
        # newShot = self.getShotByIndex(newShotInd)

        return newShot

    def copyCameraFromShot(self, sourceShot, targetShot=None, duplicateHierarchy=False):
        """Copy the camera from the given shot
        Return the copied camera
        Args:
                sourceShot: the shot holding the camera to be copied
                targetShot: the target shot (can be None (default), can also be sourceShot.
                            if not None then the name of the camera will reflect the target shot name
        """
        newCam = None

        if sourceShot.isCameraValid():
            newCam = utils.duplicateObject(sourceShot.camera, duplicateHierarchy=duplicateHierarchy)

            if targetShot is not None and sourceShot.getParentTake() == targetShot.getParentTake():
                newCam.name = sourceShot.camera.name + "_copy"
                newCam.color = utils.color_to_linear(
                    utils.slightlyRandomizeColor(utils.color_to_sRGB(sourceShot.camera.color))
                )

            if targetShot is not None:
                targetShot.setCamera(newCam)

        return newCam

    def copyShot(self, shot, atIndex=-1, targetTakeIndex=-1, copyCamera=False, copyGreasePencil=False):
        """Copy a shot after the current shot if possible or at the end of the shot list otherwise (case of an add in a take
        that is not the current one)
        Return the newly added shot
        Since this function works also with takes that are not the current one the current shot is not taken into account not modified
        Specifying a value to targetTakeIndex allows the copy of a shot to another take
        When a shot is copied in the same take its name will be suffixed by "_copy". When copied to another take its name is not modified.

        Args:
            copyCamera: when True then the camera as well as all its children (storyboard gp, gp, others) are copied too
            copyGreasePencil: when false then an empty grease pencil will be created. When true the GP will be copied too
        """

        #  currentTakeInd = self.getCurrentTakeIndex()
        sourceTakeInd = shot.getParentTakeIndex()
        takeInd = (
            sourceTakeInd
            if -1 == targetTakeIndex
            else (targetTakeIndex if 0 <= targetTakeIndex and targetTakeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            return None

        # newShot = None
        # shots = self.get_shots(takeIndex=takeInd)

        cam = shot.camera
        newCam = None
        if copyCamera and shot.isCameraValid():
            # newCam = utils.duplicateObject(cam, duplicateHierarchy=copyGreasePencil)
            # if targetTakeIndex == sourceTakeInd:
            #     newCam.name = cam.name + "_copy"
            # newCam.color = utils.color_to_linear(utils.slightlyRandomizeColor(utils.color_to_sRGB(cam.color)))

            newCam = self.copyCameraFromShot(shot, duplicateHierarchy=copyGreasePencil)
            cam = newCam

            utils.select_object(cam)
            # if copyGreasePencil:
            #     gpencil = utils_greasepencil.get_greasepencil_child(cam, childType="EMPTY")
            #     if gpencil is not None:
            #         new_gpencil = utils_greasepencil.copy_greasepencil()
            #         new_gpencil = utils.duplicateObject(gpencil, duplicateHierarchy=True)
            #         new_gpencil.parent = cam

        nameSuffix = ""
        if targetTakeIndex == sourceTakeInd:
            nameSuffix = "_copy"

        newShot = self.addShot(
            atIndex=atIndex,
            takeIndex=targetTakeIndex,
            name=shot.name + nameSuffix,
            start=shot.start,
            end=shot.end,
            durationLocked=shot.durationLocked,
            camera=cam,
            color=cam.color,
            enabled=shot.enabled,
            addGreasePencilStoryboard=False,
        )

        newShot.shotType = shot.shotType
        newShot.bgImages_offset = shot.bgImages_offset
        newShot.bgImages_linkToShotStart = shot.bgImages_linkToShotStart

        newShot.note01 = shot.note01
        newShot.note03 = shot.note02
        newShot.note03 = shot.note03

        if len(shot.greasePencils):

            # if the source has a gp then the new shot will have one
            gpProps = newShot.greasePencils.add()
            # initialize do not create a new gp object if it exits, in this case it will just update
            gpProps.initialize(newShot, "STORYBOARD")

            # the new gp is a copy of the source gp only if copyGreasePencil is true
            if copyGreasePencil and newCam is not None:
                sourceGpProps = shot.getGreasePencilProps("STORYBOARD")
                if sourceGpProps is not None:
                    gpProps.copyPropertiesFrom(sourceGpProps)

        # newShot = shots.add()  # shot is added at the end
        # newShot.parentScene = shot.parentScene
        # newShot.parentTakeIndex = takeInd
        # newShot.name = shot.name
        # newShot.enabled = shot.enabled
        # newShot.end = 9999999  # mandatory cause start is clamped by end
        # newShot.start = shot.start
        # newShot.end = shot.end
        # newShot.camera = shot.camera
        # newShot.color = shot.color

        # newShotInd = len(shots) - 1
        # if -1 != atIndex:  # move shot at specified index
        #     shots.move(newShotInd, atIndex)
        #     newShotInd = self.getShotIndex(newShot)

        # update the current take if needed
        # if takeInd == currentTakeInd:
        #     self.setCurrentShotByIndex(newShotInd)
        #     self.setSelectedShotByIndex(newShotInd)

        return newShot

    def removeShotByIndex(self, shotIndex, deleteCamera=False, takeIndex=-1):
        """Remove the shot at the specified index from the specifed take
        If deleteCamera is True the camera is deleted only if it is not shared with any other shots
        """
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            return None

        shots = self.get_shots(takeIndex=takeInd)
        if shotIndex < len(shots):
            shots[shotIndex].removeGreasePencil()
            if deleteCamera:
                self.deleteShotCamera(shots[shotIndex])
            shots.remove(shotIndex)

    def removeShot(self, shot, deleteCamera=False):
        """Remove the shot from its parent take
        If deleteCamera is True the camera is deleted only if it is not shared with any other shots
        """
        shotInd = self.getShotIndex(shot)
        self.removeShotByIndex(shotInd, deleteCamera=deleteCamera, takeIndex=shot.getParentTakeIndex())

    def removeShot_UIupdate(self, shot, deleteCamera=False):
        # TODO: Need refactorisation to put the UI part in an operator

        currentTakeInd = self.getCurrentTakeIndex()
        takeInd = shot.getParentTakeIndex()
        shots = self.get_shots(takeIndex=takeInd)
        shotInd = self.getShotIndex(shot)

        # update the current take if needed
        if takeInd == currentTakeInd:
            currentShotInd = self.current_shot_index
            #   currentShot = shots[currentShotInd]
            selectedShotInd = self.getSelectedShotIndex()
            previousSelectedShotInd = selectedShotInd
            #   selectedShot = shots[selectedShotInd]

            if shotInd != selectedShotInd:
                self.setSelectedShotByIndex(shotInd)
                selectedShotInd = self.getSelectedShotIndex()

            # case of the last shot
            if selectedShotInd == len(shots) - 1:
                if currentShotInd == selectedShotInd:
                    self.setCurrentShotByIndex(selectedShotInd - 1, setCamToViewport=False)

                self.removeShot(shot, deleteCamera=deleteCamera)
                # shots.remove(selectedShotInd)
                self.setSelectedShotByIndex(selectedShotInd - 1)
            else:
                if currentShotInd >= selectedShotInd:
                    self.setCurrentShotByIndex(-1, setCamToViewport=False)
                self.removeShot(shot, deleteCamera=deleteCamera)
                #  shots.remove(selectedShotInd)

                if currentShotInd == selectedShotInd:
                    self.setCurrentShotByIndex(self.selected_shot_index, setCamToViewport=False)
                elif currentShotInd > selectedShotInd:
                    self.setCurrentShotByIndex(min(currentShotInd - 1, len(shots) - 1), setCamToViewport=False)

                if selectedShotInd < len(shots):
                    self.setSelectedShotByIndex(selectedShotInd)
                else:
                    self.setSelectedShotByIndex(selectedShotInd - 1)

            # restore selected item
            if shotInd != previousSelectedShotInd:
                if shotInd < previousSelectedShotInd:
                    self.setSelectedShotByIndex(previousSelectedShotInd - 1)
                else:
                    self.setSelectedShotByIndex(previousSelectedShotInd)
        else:
            # print(f"La: takeInd: {takeInd}, currentTakeInd: {currentTakeInd}, shot Ind: {shotInd}")
            self.removeShot(shot, deleteCamera=deleteCamera)
            shots.remove(shotInd)

    def moveShotToIndex(self, shot, newIndex):
        """
        Move a shot to the specified index. The shot stays in the same take.
        Return the shot moved at the specified place.
        Once moved, the variable "shot" doesn't refer to the same shot anymore, hence:
            *** it is VERY IMPORTANT to get the returned shot back ***
        """
        # currentTakeInd = self.getCurrentTakeIndex()
        # takeInd = (
        #     currentTakeInd
        #     if -1 == takeIndex
        #     else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        # )
        # if -1 == takeInd:
        #     print("moveShotToIndex: Failed")
        #     return None

        if shot is None:
            return None

        takeInd = shot.getParentTakeIndex()
        shots = self.get_shots(takeIndex=takeInd)
        # currentShotInd = self.getCurrentShotIndex()
        # selectedShotInd = self.getSelectedShotIndex()
        shotInd = self.getShotIndex(shot)
        newInd = max(0, newIndex)
        newInd = min(newInd, len(shots) - 1)

        shots.move(shotInd, newInd)

        # wkipwkipwkip test if shot and current shot are from the same take!!
        # if currentShotInd == shotInd:
        #     self.setCurrentShotByIndex(newInd)
        # self.setSelectedShotByIndex(newInd)

        return self.getShotByIndex(newInd, takeIndex=takeInd)

    def getShotParentTakeIndex(self, shot):
        for i, take in enumerate(self.takes):
            for j, sh in enumerate(take.shots):
                if sh == shot:
                    return i
        return None

    def getShotParentTake(self, shot):
        for i, take in enumerate(self.takes):
            for j, sh in enumerate(take.shots):
                if sh == shot:
                    return take
        return -1

    def getShotIndex(self, shot):
        """Return the shot index in its parent take"""
        # takeInd = shot.getParentTakeIndex()
        # shotInd = -1

        # # wkip a optimiser
        # shotList = self.getShotsList(ignoreDisabled=False, takeIndex=takeInd)

        # shotInd = 0
        # while shotInd < len(shotList) and shot != shotList[shotInd]:  # wkip mettre shotList[shotInd].name?
        #     shotInd += 1
        # if shotInd == len(shotList):
        #     shotInd = -1

        # return shotInd
        for i, take in enumerate(self.takes):
            for j, sh in enumerate(take.shots):
                if sh == shot:
                    return j
        return -1

    def getShotByIndex(self, shotIndex, ignoreDisabled=False, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        shot = None
        if -1 == takeInd:
            return None

        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)

        # if ignoreDisabled:
        #     if 0 < len(shotList) and shotIndex < len(shotList):
        #         shot = shotList[shotIndex]
        # else if 0 < shotNumber and shotIndex < shotNumber:
        #     shot = self.takes[takeIndex].shots[shotIndex]

        if 0 < len(shotList) and shotIndex < len(shotList):
            shot = shotList[shotIndex]

        return shot

    def getShotByName(self, shotName, ignoreDisabled=False, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        shot = None
        if -1 == takeInd:
            return None

        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)

        for sh in shotList:
            if shotName == sh.name:
                return sh

        return shot

    def get_shots(self, takeIndex=-1):
        """Return the actual shots array of the specified take"""
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        shotList = []
        if -1 == takeInd:
            return shotList

        shotList = self.takes[takeInd].shots

        return shotList

    def getShotsList(self, ignoreDisabled=False, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        shotList = []
        if -1 == takeInd:
            return shotList

        # for shot in self.takes[takeInd].shots:
        #     # if shot.enabled or self.context.scene.UAS_shot_manager_props.seqTimeline_displayDisabledShots:
        #     if not ignoreDisabled or shot.enabled:
        #         shotList.append(shot)

        return self.takes[takeInd].getShotsList(ignoreDisabled=ignoreDisabled)

    def getNumShots(self, ignoreDisabled=False, takeIndex=-1):
        """Return the number of shots of the specified take"""
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            return 0

        return self.takes[takeInd].getNumShots(ignoreDisabled=ignoreDisabled)

    def getCurrentShotIndex(self, ignoreDisabled=False, takeIndex=-1):
        """Return the index of the current shot in the enabled shot list of the current take
        Use this function instead of a direct call to self.current_shot_index

        if ignoreDisabled is false (default) then the shot index is relative to the whole shot list,
           otherwise it is relative to the list of the enabled shots
        can return -1 if all the shots are disabled!!
        if takeIndex is different from the current take then it returns -1 because other takes than the current one are not supposed to
        have a current shot
        """
        #   print(" *** getCurrentShotIndex")

        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        currentShotInd = -1
        if -1 == takeInd:
            return currentShotInd

        # other takes than the current one are not supposed to have a current shot
        if self.current_take_name != self.takes[takeInd].name:
            return -1

        if ignoreDisabled and 0 < len(self.takes[takeInd].shots):
            # for i, shot in enumerate ( self.context.scene.UAS_shot_manager_props.takes[self.context.scene.UAS_shot_manager_props.current_take_name].shots ):
            currentShotInd = self.current_shot_index
            for i in range(self.current_shot_index + 1):
                if not self.takes[takeInd].shots[i].enabled:
                    currentShotInd -= 1
        #      print("  in ignoreDisabled, currentShotInd: ", currentShotInd)
        else:
            if 0 < len(self.takes[takeInd].shots):

                if len(self.takes[takeInd].shots) > self.current_shot_index:
                    #          print("    in 01")
                    currentShotInd = self.current_shot_index
                else:
                    #          print("    in 02")
                    currentShotInd = len(self.takes[takeInd].shots) - 1
                    self.setCurrentShotByIndex(currentShotInd)

        # print("  NOT in ignoreDisabled, currentShotInd: ", currentShotInd)

        return currentShotInd

    def getCurrentShot(self, ignoreDisabled=False, takeIndex=-1):
        currentShot = None
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        currentShotInd = -1
        if -1 == takeInd:
            return currentShot

        currentShotInd = self.getCurrentShotIndex(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        #   print("getCurrentShot: currentShotInd: ", currentShotInd)
        if -1 != currentShotInd:
            currentShot = self.takes[takeInd].shots[currentShotInd]

        return currentShot

    def setCurrentShotByIndex(self, currentShotIndex, changeTime=None, source_area=None, setCamToViewport=True):
        """Changing the current shot:
          - doesn't affect the selected one
          - changes the current time if specifed
        Args:
            changeTime:
                - None(default): depends on the state of prefs.current_shot_changes_current_time_to_start
                - True: set current time to the start of the new shot
                - False: current time is not changed
            setCamToViewport: If set to True then the shot camera is set to the viewport
        """
        scene = bpy.context.scene

        # was required to set the camera to the target viewport
        # target_area_index = self.getTargetViewportIndex(bpy.context, only_valid=False)
        # target_area = utils.getAreaFromIndex(bpy.context, target_area_index, "VIEW_3D")
        # if source_area is None:
        #     # source_area = bpy.context.area
        #     # source_area = utils.getViewportAreaView(
        #     #     bpy.context, viewport_index=bpy.context.window_manager.shotmanager_target_viewport
        #     # )
        #     source_area = utils.getViewportAreaView(bpy.context, viewport_index=target_area_index)

        shotList = self.get_shots()

        if not len(shotList):
            self.current_shot_index = -1
        elif -1 < currentShotIndex < len(shotList):
            self.current_shot_index = currentShotIndex

            prefs = config.getAddonPrefs()
            currentShot = shotList[currentShotIndex]

            if changeTime is None:
                if prefs.current_shot_changes_current_time_to_start:
                    scene.frame_current = currentShot.start
            elif changeTime:
                scene.frame_current = currentShot.start

            # removed: timeline zoom should not be changed here but in uas_shot_manager.set_current_shot
            # if prefs.current_shot_changes_time_range:
            #     zoom_dopesheet_view_to_range(bpy.context, currentShot.start, currentShot.end)

            if setCamToViewport:
                currentShot.setCameraToViewport()
            # if setCamToViewport and currentShot.camera is not None and bpy.context.screen is not None:
            #     # set the current camera in the 3D view: [‘PERSP’, ‘ORTHO’, ‘CAMERA’]
            #     scene.camera = currentShot.camera
            #     utils.setCurrentCameraToViewport2(bpy.context, target_area)

            ##########################
            # storyboard
            ##########################
            # if "STORYBOARD" == self.layout_mode and prefs.current_shot_changes_edited_frame_in_stb:
            if self.isContinuousGPEditingModeActive() and self.isEditingStoryboardFrame:
                # if self.getEditedStoryboardFrame() is not None:
                if True:
                    # self.getEditedGPShot() is not None:
                    bpy.ops.uas_shot_manager.greasepencil_select_and_draw(
                        index=currentShotIndex,
                        action="SELECT_AND_DRAW",
                        ignoreSetCurrentShot=True,
                        toggleDrawEditing=False,
                    )

            #    self.updateGreasePencilVisibility(self.getCurrentTake())
            self.updateStoryboardFramesDisplay(
                takeIndex=self.getCurrentTakeIndex(),
                forceHide=False,
                alsoForceHideAlwaysVisible=False,
                alsoForceHideCurrent=False,
            )

            #  set current edit gp
            if not self.stb_hasPinnedObject:
                # if bpy.context.active_object is not None and "GPENCIL" == bpy.context.active_object.type:
                shotGp = currentShot.getGreasePencilObject(mode="STORYBOARD")
                if shotGp is not None:
                    self.stb_editedGPencilName = shotGp.name

            # wkip use if
            # if prefs.toggleCamsSoundBG:
            # self.enableBGSoundForShot(prefs.toggleCamsSoundBG, currentShot)
            if self.useBGSounds:
                self.enableBGSoundForShot(True, currentShot)

    def setCurrentShot(self, currentShot, changeTime=None, source_area=None, setCamToViewport=True):
        shotInd = self.getShotIndex(currentShot)
        # print("setCurrentShot: shotInd:", shotInd)
        self.setCurrentShotByIndex(
            shotInd, changeTime=changeTime, source_area=source_area, setCamToViewport=setCamToViewport
        )

    def getSelectedShotIndex(self):
        """Return the index of the selected shot in the enabled shot list of the current take
        Use this function instead of a direct call to self.selected_shot_index
        """
        if 0 >= len(self.takes) or 0 >= len(self.get_shots()):
            try:
                self.selected_shot_index = -1
            except Exception:
                pass
            return -1

        return self.selected_shot_index

    def getSelectedShot(self):
        """Return the shot currently selected in the current take, None otherwise"""
        selectedShotInd = self.getSelectedShotIndex()
        selectedShot = None
        if -1 != selectedShotInd:
            selectedShot = (self.get_shots())[selectedShotInd]

        return selectedShot

    def setSelectedShotByIndex(self, selectedShotIndex, callUpdateFunc=True):
        """Args:
        callUpdateFunc: if True (default), the update function for the property self.selected_shot_index
        is called
        """
        # print("setSelectedShotByIndex: selectedShotIndex:", selectedShotIndex)
        self.selected_shot_index_call_update__flag = callUpdateFunc
        self.selected_shot_index = selectedShotIndex
        self.selected_shot_index_call_update__flag = True

    def setSelectedShot(self, selectedShot):
        shotInd = self.getShotIndex(selectedShot)
        self.setSelectedShotByIndex(shotInd)

    # # can return -1 if all the shots are disabled!!
    # def getCurrentShotIndexInEnabledList( self ):
    #     currentIndexInEnabledList = self.current_shot_index
    #     #for i, shot in enumerate ( self.context.scene.UAS_shot_manager_props.takes[self.context.scene.UAS_shot_manager_props.current_take_name].shots ):
    #     for i in range(self.current_shot_index + 1):
    #         if not self.takes[self.current_take_name].shots[i].enabled:
    #             currentIndexInEnabledList -= 1

    #     return currentIndexInEnabledList

    def getFirstShotIndex(self, ignoreDisabled=False, takeIndex=-1):
        """ """
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        firstShotInd = -1
        if -1 == takeInd:
            return firstShotInd

        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        #   print(" getFirstShotIndex: shotList: ", shotList)

        #  not required cause shotList is already filtered!
        # if ignoreDisabled and 0 < len(shotList):
        #     firstShotInd = 0
        #     while firstShotInd < len(shotList) and not shotList[firstShotInd].enabled:
        #         firstShotInd += 1
        #     if firstShotInd >= len(shotList): firstShotInd = 0
        # else:
        if 0 < len(shotList):
            firstShotInd = 0

        return firstShotInd

    # # can return -1 if all the shots are disabled!!
    # def getCurrentShotIndexInEnabledList( self ):
    #     currentIndexInEnabledList = self.current_shot_index
    #     #for i, shot in enumerate ( self.context.scene.UAS_shot_manager_props.takes[self.context.scene.UAS_shot_manager_props.current_take_name].shots ):
    #     for i in range(self.current_shot_index + 1):
    #         if not self.takes[self.current_take_name].shots[i].enabled:
    #             currentIndexInEnabledList -= 1

    #     return currentIndexInEnabledList
    def getLastShotIndex(self, ignoreDisabled=False, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        lastShotInd = -1
        if -1 == takeInd:
            return lastShotInd

        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        # print(" getLastShotIndex: shotList: ", shotList)

        if 0 < len(shotList):
            lastShotInd = len(shotList) - 1

        return lastShotInd

    def getFirstShot(self, ignoreDisabled=False, takeIndex=-1):
        firstShotInd = self.getFirstShotIndex(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        # print(" getFirstShot: firstShotInd: ", firstShotInd)
        firstShot = (
            None
            if -1 == firstShotInd
            else self.getShotByIndex(firstShotInd, ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        )

        return firstShot

    def getLastShot(self, ignoreDisabled=False, takeIndex=-1):
        lastShotInd = self.getLastShotIndex(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        print(" getLastShot: lastShotInd: ", lastShotInd)
        lastShot = (
            None
            if -1 == lastShotInd
            else self.getShotByIndex(lastShotInd, ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        )

        return lastShot

    # currentShotIndex is given in the WHOLE list of shots (including disabled)
    # returns the index of the previous enabled shot in the WHOLE list, -1 if none
    def getPreviousEnabledShotIndex(self, currentShotIndex, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        previousShotInd = -1
        if -1 == takeInd:
            return previousShotInd

        shotList = self.getShotsList(takeIndex=takeIndex)

        previousShotInd = currentShotIndex - 1
        isPreviousFound = shotList[previousShotInd].enabled
        while 0 <= previousShotInd and not isPreviousFound:
            previousShotInd -= 1
            isPreviousFound = shotList[previousShotInd].enabled

        return previousShotInd

    # currentShotIndex is given in the WHOLE list of shots (including disabled)
    # returns the index of the next enabled shot in the WHOLE list, -1 if none
    def getNextEnabledShotIndex(self, currentShotIndex, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        nextShotInd = -1
        if -1 == takeInd:
            return nextShotInd

        shotList = self.getShotsList(takeIndex=takeIndex)

        nextShotInd = currentShotIndex + 1
        if len(shotList) > nextShotInd:
            isNextFound = shotList[nextShotInd].enabled
            while len(shotList) > nextShotInd and not isNextFound:
                nextShotInd += 1
                if len(shotList) > nextShotInd:
                    isNextFound = shotList[nextShotInd].enabled

        if len(shotList) <= nextShotInd:
            nextShotInd = -1

        return nextShotInd

    # works only on current take
    # TODO make this function work for any take
    def getFirstShotIndexContainingFrame(self, frameIndex, ignoreDisabled=False):
        """Return the first shot containing the specifed frame, -1 if not found"""
        firstShotInd = -1

        shotList = self.get_shots()
        shotFound = False

        if len(shotList):
            firstShotInd = 0
            while firstShotInd < len(shotList) and not shotFound:
                if not ignoreDisabled or shotList[firstShotInd].enabled:
                    shotFound = shotList[firstShotInd].start <= frameIndex and frameIndex <= shotList[firstShotInd].end
                firstShotInd += 1

        if shotFound:
            firstShotInd = firstShotInd - 1
        else:
            firstShotInd = -1

        return firstShotInd

    # works only on current take
    # TODO make this function work for any take
    def getFirstShotIndexBeforeFrame(self, frameIndex, ignoreDisabled=False):
        """Return the first shot before the specifed frame (supposing thanks to getFirstShotIndexContainingFrame than
        frameIndex is not in a shot), -1 if not found
        """
        firstShotInd = -1

        shotList = self.get_shots()
        shotFound = False

        if len(shotList):
            firstShotInd = len(shotList) - 1
            while 0 <= firstShotInd and not shotFound:
                if not ignoreDisabled or shotList[firstShotInd].enabled:
                    shotFound = shotList[firstShotInd].end < frameIndex
                firstShotInd -= 1

        if shotFound:
            firstShotInd = firstShotInd + 1
        else:
            firstShotInd = -1

        return firstShotInd

    # works only on current take
    # TODO make this function work for any take
    def getFirstShotIndexAfterFrame(self, frameIndex, ignoreDisabled=False):
        """Return the first shot after the specifed frame (supposing thanks to getFirstShotIndexContainingFrame than
        frameIndex is not in a shot), -1 if not found
        """
        firstShotInd = -1

        shotList = self.get_shots()
        shotFound = False

        if len(shotList):
            firstShotInd = 0
            while firstShotInd < len(shotList) and not shotFound:
                if not ignoreDisabled or shotList[firstShotInd].enabled:
                    shotFound = frameIndex < shotList[firstShotInd].start
                firstShotInd += 1

        if shotFound:
            firstShotInd = firstShotInd - 1
        else:
            firstShotInd = -1

        return firstShotInd

    #############################################
    # shot cameras
    #############################################

    def getCameras(self, fromAllTakes=False, ignoreDisabled=False, takeIndex=-1, onlyShotsOfType=None):
        """Return the list of all the valid cameras used by the shots of the specified take
        Cameras are present only 1 time in the returned list
        Args:
            fromAllTakes: If True, then takeIndex is ignored
            onlyShotOfType: Can be None, "STORYBOARD" or "PREVIZ"
        """
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            return None

        takes = self.takes if fromAllTakes else [self.takes[takeInd]]

        shotCameras = list()
        for take in takes:
            for shot in take.shots:
                if shot.enabled or ignoreDisabled:
                    if onlyShotsOfType is None or onlyShotsOfType == shot.shotType:
                        if shot.isCameraValid():
                            cam = shot.camera
                            if cam not in shotCameras:
                                shotCameras.append(cam)

        return shotCameras

    def getShotsUsingCamera(self, cam, ignoreDisabled=False, takeIndex=-1):
        """Return the list of all the shots used by the specified camera in the specified take"""
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        shotList = []
        if -1 == takeInd:
            return shotList

        return self.takes[takeInd].getShotsUsingCamera(cam, ignoreDisabled=ignoreDisabled)

    def getShotsSharingCamera(self, cam, ignoreDisabled=False, takeIndex=-1, inAllTakes=True):
        """Return a dictionary with all the shots using the specified camera in the specified takes
        The dictionary is made of "take name" / Shots array
        """
        shotsDict = dict()

        if cam is None:
            return shotsDict

        if not inAllTakes:
            takeInd = (
                self.getCurrentTakeIndex()
                if -1 == takeIndex
                else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
            )
            if -1 == takeInd:
                return shotsDict

            shotList = self.takes[takeInd].getShotsUsingCamera(cam, ignoreDisabled=ignoreDisabled)
            if len(shotList):
                shotsDict[self.takes[takeInd].getName_PathCompliant()] = shotList

        else:
            if len(self.takes):
                for take in self.takes:
                    shotList = []
                    shotList = take.getShotsUsingCamera(cam, ignoreDisabled=ignoreDisabled)
                    if len(shotList):
                        shotsDict[take.getName_PathCompliant()] = shotList

        return shotsDict

    def getShotsSharingCameraCount(self, cam, ignoreDisabled=False):
        """Return a tupple made by the number of shots, in all takes, using the camera and the number
        of takes that have at least one shot using this camera
        """
        sharedCams = self.getShotsSharingCamera(cam, ignoreDisabled=ignoreDisabled, inAllTakes=True)
        numSharedCams = 0
        for k in sharedCams:
            numSharedCams += len(sharedCams[k])

        return (numSharedCams, len(sharedCams))

    def isThereSharedCamerasInTake(self, ignoreDisabled=False, takeIndex=-1, inAllTakes=True):
        """Return True if there is at least 1 camera shared in the specified take, False otherwise"""
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            return -1

        for shot in self.takes[takeInd].shots:
            if ignoreDisabled or shot.enabled:
                if 1 < self.getNumSharedCamera(shot.camera, ignoreDisabled=ignoreDisabled, takeIndex=takeInd):
                    return True
        return False

    def getNumSharedCamera(self, cam, ignoreDisabled=False, takeIndex=-1, inAllTakes=True):
        """Return the number of times the specified camera is used by the shots of the specified takes
        0 means the camera is not used at all, -1 that the specified take is not valid
        """
        if not inAllTakes:
            takeInd = (
                self.getCurrentTakeIndex()
                if -1 == takeIndex
                else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
            )
            if -1 == takeInd:
                return -1

        sharedCams = self.getShotsSharingCamera(
            cam, ignoreDisabled=ignoreDisabled, takeIndex=takeIndex, inAllTakes=inAllTakes
        )
        numSharedCams = 0
        for k in sharedCams:
            numSharedCams += len(sharedCams[k])

        return numSharedCams

    def deleteShotCamera(self, shot):
        """Check in all takes if the camera is used by another shot and if not then delete it"""
        deleteOk = False

        # if shot.camera is None:
        if not shot.isCameraValid():
            return False

        for t in self.takes:
            for s in t.shots:
                if shot != s and s.camera is not None and shot.camera == s.camera:
                    return False

        # bpy.ops.object.select_all(action="DESELECT")
        cam = shot.camera
        shot.camera = None

        cam.select_set(False)
        bpy.data.objects.remove(cam, do_unlink=True)

        # https://wiki.blender.org/wiki/Reference/Release_Notes/2.80/Python_API/Scene_and_Object_API
        #  cam.select_set(True)
        #  bpy.ops.object.delete()

        return deleteOk

    ###############
    # sounds BG
    ###############

    useBGSounds: BoolProperty(default=False)
    meta_bgSoundsName01: StringProperty(default="")

    def getBGSoundsMetaContainingClip(self, clip):
        # wkip wkip wkip finir ici pour tester qu'on a le bon meta
        return self.getBGSoundsMeta()

    def getBGSoundsMeta(self):
        """Get the first meta strip dedicated to the bg sounds and with some room in it (ie that has less than 32 tracks occupied)
        Meta strips for sounds are placed on tracks 30 to 32
        """
        scene = self.parentScene
        bgSoundsMeta = None
        newMetaTrackInd = 10  # 30

        # a stocker dans une propriété
        if "" != self.meta_bgSoundsName01:
            if self.meta_bgSoundsName01 not in scene.sequence_editor.sequences:
                self.meta_bgSoundsName01 = ""
            else:
                # bgSoundsMeta = bpy.context.sequences[self.meta_bgSoundsName01]
                bgSoundsMeta = bpy.context.scene.sequence_editor.sequences_all[self.meta_bgSoundsName01]

        if bgSoundsMeta is None:
            # close any meta opened:
            while len(scene.sequence_editor.meta_stack) > 0:
                bpy.ops.sequencer.meta_toggle()

            # create meta
            bpy.ops.sequencer.select_all(action="DESELECT")
            # get effect tmpClip
            scene.sequence_editor.sequences.new_effect(
                "_tmp_clip-to_delete", "COLOR", newMetaTrackInd, frame_start=0, frame_end=45000
            )
            # tmpClip is selected so we can call meta_make()
            bpy.ops.sequencer.meta_make()
            # bpy.ops.sequencer.meta_toggle()  # close meta
            bgSoundsMeta = scene.sequence_editor.active_strip
            bgSoundsMeta.name = "ShotMan--BGSounds"

            # go back inside the meta to delete the temp strip
            bpy.ops.sequencer.meta_toggle()  # open meta
            # scene.sequence_editor.sequences_all[tmpClip.name]
            bpy.ops.sequencer.select_all(action="SELECT")
            bpy.ops.sequencer.delete()

            bpy.ops.sequencer.meta_toggle()  # close meta
            # scene.sequence_editor.sequences.remove(tmpClip)

            self.meta_bgSoundsName01 = bgSoundsMeta.name

        return bgSoundsMeta

    def openMetaStrip(self, context, metaClip):
        self.closeAllMetaStrips(context)

        bpy.ops.sequencer.select_all(action="DESELECT")
        context.scene.sequence_editor.sequences_all[metaClip.name].select = True
        bpy.ops.sequencer.meta_toggle()

    def closeAllMetaStrips(self, context):
        # close meta if one is opened:
        while len(context.scene.sequence_editor.meta_stack) > 0:
            bpy.ops.sequencer.meta_toggle()

    def getFirstEmptyTrack(self, context, bgSoundsMeta):
        """Return the first empty track index of the specified meta strip"""
        firstEmptyTrackInd = -1
        self.openMetaStrip(context, bgSoundsMeta)
        channelsList = list(range(1, 33))
        for seq in context.sequences:
            if seq.channel in channelsList:
                channelsList.remove(seq.channel)
        # print(f"channelsList: {channelsList}")
        if len(channelsList):
            firstEmptyTrackInd = channelsList[0]
        self.closeAllMetaStrips(context)
        return firstEmptyTrackInd

    def addBGSoundToShot(self, sound_path, shot):
        """Add the sound of the specified media (sound or video) into one of the meta strips of the VSE reserved for shot Manager (from 30 to 32)
        Return the sound clip
        """
        context = bpy.context
        scene = self.parentScene
        newSoundClip = None

        bgSoundsMeta = self.getBGSoundsMeta()
        if bgSoundsMeta is None:
            print("Pb in addBGSoundToShot: no bgSoundsMeta strip")
        else:
            # # close meta if opened:
            # while len(scene.sequence_editor.meta_stack) > 0:
            #     bpy.ops.sequencer.meta_toggle()

            # bpy.ops.sequencer.select_all(action="DESELECT")
            # scene.sequence_editor.sequences_all[bgSoundsMeta.name].select = True

            targetTrackInd = self.getFirstEmptyTrack(bpy.context, bgSoundsMeta)

            if -1 < targetTrackInd:
                self.openMetaStrip(context, bgSoundsMeta)

                vse_render = context.window_manager.UAS_vse_render

                clipName = "myBGSound"
                newSoundClip = vse_render.createNewClip(
                    scene,
                    str(sound_path),
                    targetTrackInd,
                    0,
                    importVideo=False,
                    importAudio=True,
                    clipName=clipName,
                )

                shot.bgSoundClipName = newSoundClip.name

        self.closeAllMetaStrips(context)

        return newSoundClip

    #################
    #################
    #################
    #################
    #################
    #################
    #################
    # to do:
    # fonction clear orphans in tracks
    # fonction enable seulement le clip actif
    # move clip doit bien mettre a jour le son
    #################
    #################
    #################
    #################
    #################
    #################
    #################
    #################
    #################

    def removeBGSoundFromShot(self, shot):
        context = bpy.context
        # scene = self.parentScene
        metaSeq = self.getBGSoundsMetaContainingClip(shot.bgSoundClipName)
        if metaSeq is not None:
            self.openMetaStrip(context, metaSeq)
            bpy.ops.sequencer.select_all(action="DESELECT")
            print(f"removeBGSoundFromShot 01, shot.bgSoundClipName: {shot.bgSoundClipName} ")
            # for i, c in enumerate(context.scene.sequence_editor.sequences):
            for i, c in enumerate(context.sequences):
                print(f"   seq {i + 1}  {c.name}")
            # if shot.bgSoundClipName in context.scene.sequence_editor.sequences:

            for i in context.sequences:
                if shot.bgSoundClipName == i.name:
                    # if shot.bgSoundClipName in context.sequences:  # name and seq, marche pas
                    print("removeBGSoundFromShot 02")
                    # context.scene.sequence_editor.sequences[shot.bgSoundClipName].select = True
                    i.select = True
                    bpy.ops.sequencer.delete()
                    break
                #    self.closeAllMetaStrips(context)
            shot.bgSoundClipName = ""

    def disableAllShotsBGSounds(self):
        """Turn off all the sounds of all the shots of all the takes"""
        for clip in self.parentScene.sequence_editor.sequences:
            clip.mute = True

    def enableBGSoundForShot(self, useBgSound, shot):
        """Turn off all the sounds of all the shots of all the takes and enable only the one of the specified shot"""
        # print("----++++ enableBGSoundForShot")
        self.disableAllShotsBGSounds()

        if self.useBGSounds and shot is not None:
            bgSoundClip = shot.getSoundSequence()
            if bgSoundClip is not None:
                bgSoundClip.mute = not useBgSound

    ###############
    # functions working only on current take !!!
    ###############

    def goToPreviousShotBoundary(self, currentFrame, ignoreDisabled=False, boundaryMode="ANY"):
        """
        works only on current take
        behavior of this button:
        if current shot is enabled:
        - first click: put current time at the start of the current enabled shot
        else:
        - fisrt click: put current time at the end of the previous enabled shot

        - boundaryMode: can be "ANY", "START", "END"
        """
        # print(" ** -- ** goToPreviousShotBoundary")

        if not len(self.get_shots()):
            return ()

        previousShotInd = -1
        newFrame = currentFrame

        # in shots play mode the current frame is supposed to be in the current shot
        # if True or bpy.context.window_manager.UAS_shot_manager_shots_play_mode:
        if "ANY" == boundaryMode:
            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShotByIndex(currentShotInd)
            # _logger.debug_ext(f"    current Shot: {currentShotInd}")
            if not currentShot.enabled:
                print("    current Shot is disabled")
                previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                if -1 < previousShotInd:
                    #        print("    previous Shot ind is ", previousShotInd)
                    newFrame = self.getShotByIndex(previousShotInd).end
            else:
                #    print("    current Shot is ENabled")
                if currentFrame == currentShot.start:
                    #        print("      current frame is start")
                    previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                    if -1 < previousShotInd:
                        #            print("      previous Shot ind is ", previousShotInd)
                        newFrame = self.getShotByIndex(previousShotInd).end
                    else:  # case of the very first shot
                        previousShotInd = currentShotInd
                        newFrame = currentFrame
                #  elif currentFrame == currentShot.end:
                #      newFrame = currentShot.start
                else:
                    #        print("      current frame is middle or end")
                    previousShotInd = currentShotInd
                    newFrame = currentShot.start

        elif "START" == boundaryMode:
            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShotByIndex(currentShotInd)
            # print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                # print("    current Shot is disabled")
                previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                if -1 < previousShotInd:
                    #     print("    previous Shot ind is ", previousShotInd)
                    newFrame = self.getShotByIndex(previousShotInd).start
            else:
                # print("    current Shot is ENabled")

                previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                if -1 < previousShotInd:
                    #   print("      previous Shot ind is ", previousShotInd)
                    newFrame = self.getShotByIndex(previousShotInd).start
                else:  # case of the very first shot
                    previousShotInd = currentShotInd
                    newFrame = currentFrame

        elif "END" == boundaryMode:
            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShotByIndex(currentShotInd)
            #  print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                #     print("    current Shot is disabled")
                previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                if -1 < previousShotInd:
                    #        print("    previous Shot ind is ", previousShotInd)
                    newFrame = self.getShotByIndex(previousShotInd).end
            else:
                #   print("    current Shot is ENabled")
                # if currentFrame == currentShot.start:
                #     print("      current frame is start")
                previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                if -1 < previousShotInd:
                    #     print("      previous Shot ind is ", previousShotInd)
                    newFrame = self.getShotByIndex(previousShotInd).end
                else:  # case of the very first shot
                    previousShotInd = currentShotInd
                    newFrame = currentFrame
                #  elif currentFrame == currentShot.end:
                #      newFrame = currentShot.start
                # else:
                #     print("      current frame is middle or end")
                #     previousShotInd = currentShotInd
                #     newFrame = currentShot.end

        self.setCurrentShotByIndex(previousShotInd)
        self.setSelectedShotByIndex(previousShotInd)
        bpy.context.scene.frame_set(newFrame)

        return newFrame

    # works only on current take
    def goToNextShotBoundary(self, currentFrame, ignoreDisabled=False, boundaryMode="ANY"):
        # print(" ** -- ** goToNextShotBoundary")
        if not len(self.get_shots()):
            return ()

        #   nextShot = None
        nextShotInd = -1
        newFrame = currentFrame

        # in shots play mode the current frame is supposed to be in the current shot
        # if True or bpy.context.window_manager.UAS_shot_manager_shots_play_mode:

        if "ANY" == boundaryMode:
            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShotByIndex(currentShotInd)
            #    print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                #       print("    current Shot is disabled")
                nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                if -1 < nextShotInd:
                    #          print("    next Shot ind is ", nextShotInd)
                    newFrame = self.getShotByIndex(nextShotInd).start
            else:
                #     print("    current Shot is ENabled")
                if currentFrame == currentShot.end:
                    #        print("      current frame is end")
                    nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                    if -1 < nextShotInd:
                        #         print("      next Shot ind is ", nextShotInd)
                        newFrame = self.getShotByIndex(nextShotInd).start
                    else:  # case of the very last shot
                        nextShotInd = currentShotInd
                        newFrame = currentFrame
                #  elif currentFrame == currentShot.end:
                #      newFrame = currentShot.start
                else:
                    #      print("      current frame is middle or start")
                    nextShotInd = currentShotInd
                    newFrame = currentShot.end

        elif "START" == boundaryMode:
            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShotByIndex(currentShotInd)
            #    print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                #        print("    current Shot is disabled")
                nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                if -1 < nextShotInd:
                    #           print("    next Shot ind is ", nextShotInd)
                    newFrame = self.getShotByIndex(nextShotInd).start
            else:
                #      print("    current Shot is ENabled")
                # if currentFrame == currentShot.end:
                #    print("      current frame is end")
                nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                if -1 < nextShotInd:
                    #         print("      next Shot ind is ", nextShotInd)
                    newFrame = self.getShotByIndex(nextShotInd).start
                else:  # case of the very last shot
                    nextShotInd = currentShotInd
                    newFrame = currentFrame

        elif "END" == boundaryMode:
            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShotByIndex(currentShotInd)
            # print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                #    print("    current Shot is disabled")
                nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                if -1 < nextShotInd:
                    #       print("    next Shot ind is ", nextShotInd)
                    newFrame = self.getShotByIndex(nextShotInd).end
            else:
                #    print("    current Shot is ENabled")
                if currentFrame == currentShot.end:
                    #       print("      current frame is end")
                    nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                    if -1 < nextShotInd:
                        #          print("      next Shot ind is ", nextShotInd)
                        newFrame = self.getShotByIndex(nextShotInd).end
                    else:  # case of the very last shot
                        nextShotInd = currentShotInd
                        newFrame = currentFrame
                #  elif currentFrame == currentShot.end:
                #      newFrame = currentShot.start
                else:
                    #     print("      current frame is middle or start")
                    nextShotInd = currentShotInd
                    newFrame = currentShot.end

        self.setCurrentShotByIndex(nextShotInd)
        self.setSelectedShotByIndex(nextShotInd)
        bpy.context.scene.frame_set(newFrame)

        return newFrame

    # works only on current take
    # behavior of this button:
    #  if current shot is enabled:
    #   - first click: put current time at the start of the current enabled shot
    #  else:
    #   - fisrt click: put current time at the end of the previous enabled shot

    # wkip ignoreDisabled pas encore implémenté ici!!!!
    def goToPreviousFrame(self, currentFrame, ignoreDisabled=False):
        #  print(" ** -- ** goToPreviousFrame")
        if not len(self.get_shots()):
            return ()

        #  previousShot = None
        previousShotInd = -1
        newFrame = currentFrame

        # in shots play mode the current frame is supposed to be in the current shot
        if bpy.context.window_manager.UAS_shot_manager_shots_play_mode:

            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShotByIndex(currentShotInd)
            #    print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                #       print("    current Shot is disabled")
                previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                if -1 < previousShotInd:
                    #           print("    previous Shot ind is ", previousShotInd)
                    newFrame = self.getShotByIndex(previousShotInd).end
            else:
                #        print("    current Shot is ENabled")
                if currentFrame == currentShot.start:
                    #           print("      current frame is start")
                    previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                    if -1 < previousShotInd:
                        #              print("      previous Shot ind is ", previousShotInd)
                        newFrame = self.getShotByIndex(previousShotInd).end
                    else:  # case of the very first shot
                        previousShotInd = currentShotInd
                        newFrame = currentFrame
                #  elif currentFrame == currentShot.end:
                #      newFrame = currentShot.start
                else:
                    print("      current frame is middle or end")
                    previousShotInd = currentShotInd
                    newFrame = currentFrame - 1

            self.setCurrentShotByIndex(previousShotInd)
            self.setSelectedShotByIndex(previousShotInd)
            bpy.context.scene.frame_set(newFrame)

        # in standard play mode behavior is the classic one
        else:
            newFrame = currentFrame - 1
            bpy.context.scene.frame_set(newFrame)

        return newFrame

    # works only on current take
    def goToNextFrame(self, currentFrame, ignoreDisabled=False):
        #   print(" ** -- ** goToNextShotBoundary")
        if not len(self.get_shots()):
            return ()

        #  nextShot = None
        nextShotInd = -1
        newFrame = currentFrame

        # in shots play mode the current frame is supposed to be in the current shot
        if bpy.context.window_manager.UAS_shot_manager_shots_play_mode:

            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShotByIndex(currentShotInd)
            #    print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                #        print("    current Shot is disabled")
                nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                if -1 < nextShotInd:
                    #            print("    next Shot ind is ", nextShotInd)
                    newFrame = self.getShotByIndex(nextShotInd).start
            else:
                #        print("    current Shot is ENabled")
                if currentFrame == currentShot.end:
                    #           print("      current frame is end")
                    nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                    if -1 < nextShotInd:
                        #              print("      next Shot ind is ", nextShotInd)
                        newFrame = self.getShotByIndex(nextShotInd).start
                    else:  # case of the very last shot
                        nextShotInd = currentShotInd
                        newFrame = currentFrame
                #  elif currentFrame == currentShot.end:
                #      newFrame = currentShot.start
                else:
                    #         print("      current frame is middle or start")
                    nextShotInd = currentShotInd
                    newFrame = currentFrame + 1

            self.setCurrentShotByIndex(nextShotInd)
            self.setSelectedShotByIndex(nextShotInd)
            bpy.context.scene.frame_set(newFrame)

        # in standard play mode behavior is the classic one
        else:
            newFrame = currentFrame + 1
            bpy.context.scene.frame_set(newFrame)

        return newFrame

    ##############################

    def getFramePadding(self, frame=None):
        """Return a string with the specified frame index formated with the preferences or project padding
        Args: frame:    If provided then the result is a string of zeros followed by this value
                        If not provided then the returned string is made of #
        """
        prefs = config.getAddonPrefs()
        formatedFrame = ""
        padding = self.project_img_name_digits_padding if self.use_project_settings else prefs.img_name_digits_padding

        if frame is None:
            formatedFrame = formatedFrame.rjust(padding, "#")
        else:
            formatedFrame = str(frame).rjust(padding, "0")

        return formatedFrame

    def getRenderShotPrefix(self):
        """Deprecated - Use getSequenceName instead"""
        _logger.debug_ext("getRenderShotPrefix is Deprecated", tag="DEPRECATED")
        shotPrefix = ""

        if self.use_project_settings:
            # wkipwkipwkip to improve with project_shot_format!!!
            # scene name is used but it may be weak. Replace by take name??
            # shotPrefix = self.getParentScene().name

            shotPrefix = self.parentScene.name
            shotPrefix = self.getSequenceName("FULL", addSeparator=True)

            # cf getProjectOutputMediaName
            # shotPrefix = self._replaceHashByNumber(self.project_naming_project_format, projInd)
            # shotPrefix += self.project_naming_separator_char
            # shotPrefix += self._replaceHashByNumber(self.project_naming_sequence_format, seqInd)
            # shotPrefix += self.project_naming_separator_char
            # shotPrefix += self._replaceHashByNumber(self.project_naming_shot_format, shotInd)
        else:
            shotPrefix = self.render_sequence_prefix
            shotPrefix += self.sequence_name + "_"

        return shotPrefix

    def removeSequenceName(self, prefixedName):
        """Remove the name of the sequence, if found, that is at the beginning of the provided name
        *** Warning: The returned value depends on the Project Settings context! ***
        """
        seqName = self.getSequenceName("FULL", addSeparator=True)
        ind = prefixedName.find(seqName)
        if 0 == ind:
            name = prefixedName[len(seqName) :]
        else:
            name = prefixedName
        return name

    def getOutputFileFormat(self, isVideo=True):
        #   _logger.debug(f"  /// isVideo: {isVideo}")
        outputFileFormat = ""
        if self.use_project_settings:
            if isVideo:
                # outputFileFormat = "mp4"  # wkipwkipwkipself.project_output_format.lower()
                outputFileFormat = self.project_output_format.lower()
                if "" == outputFileFormat:
                    print("\n---------------------------")
                    print(
                        "*** Shot Manager: Project video output file format not correctly set in the Preferences ***\n"
                    )
            #   _logger.debug(f"  /// outputFileFormat vid: {outputFileFormat}")
            else:
                outputFileFormat = self.project_images_output_format.lower()
                if "" == outputFileFormat:
                    print("\n---------------------------")
                    print(
                        "*** Shot Manager: Project image output file format not correctly set in the Preferences ***\n"
                    )
            #    _logger.debug(f"  /// outputFileFormat: {outputFileFormat}")
        else:
            if isVideo:
                outputFileFormat = "mp4"
            else:
                outputFileFormat = "png"
        return outputFileFormat

    def _replaceHashByNumber(self, name, index):
        newStr = name
        if index is not None:
            numHashes = len([n for n in name if n == "#"])
            if 0 < numHashes:
                newStr = name.replace("#", "") + "{:0" + str(numHashes) + "}"
                if index != -2:
                    # print(f"Format: {newStr}: {newStr.format(2)}")
                    newStr = newStr.format(int(abs(index)))

        return newStr

    def getProjectOutputMediaName(self, projInd=-1, seqInd=-1, shotInd=-1):
        """Used with project settings activated. Return a formated name for the sequence or shot name.
        Args:
            projInd, seqInd, shotInd:   provide -1 (default) to hide these values from the resulting name,
                                        provide an integer to get a numbered format,
                                        provide None to get a ### format,
                                        provide -2 to get a {:00} format based on the number of hashes,
        """
        mediaName = ""

        projNumHashes = len([n for n in self.project_naming_project_format if n == "#"])

        if "" != self.project_naming_project_format or 0 < projNumHashes:
            if -1 != projInd:
                mediaName += self._replaceHashByNumber(self.project_naming_project_format, projInd)
                mediaName += self.project_naming_separator_char
        if -1 != seqInd:
            mediaName += self._replaceHashByNumber(self.project_naming_sequence_format, seqInd)
            if -1 != shotInd:
                mediaName += self.project_naming_separator_char
        if -1 != shotInd:
            mediaName += self._replaceHashByNumber(self.project_naming_shot_format, shotInd)
        return mediaName

    def getShotPrefix(self, index=None):
        return self._replaceHashByNumber(self.project_naming_shot_format, index)

    def getSequenceName(self, mode="FULL", addSeparator=False):
        """Return the sequence name formated as specified.
        *** Warning: The returned value depends on the Project Settings context! ***
        if project settings are used then the sequence name is defined there, otherwise it is given
        by props.sequence_name and props.render_sequence_prefix

        Args:
            mode: "FULL", "SHORT", "FORMATED"
            addSeparator: If True, add the separator suffix to the end of the returned sequence name
        """

        # if "" != props.project_naming_project_format or 0 < numHashes:
        #     seqName = props.getProjectOutputMediaName(
        #         projInd=self.naming_project_index, seqInd=self.naming_sequence_index
        #     )
        # else:
        #     seqName = props.getProjectOutputMediaName(seqInd=self.naming_sequence_index)

        # return self._replaceHashByNumber(self.project_naming_sequence_format, index)

        if self.use_project_settings:
            if "FORMATED" == mode:
                name = "Formated proj settings seq name to do"
            elif "SHORT" == mode:
                name = self.getProjectOutputMediaName(projInd=-1, seqInd=self.project_naming_sequence_index, shotInd=-1)
            # FULL
            else:
                name = self.getProjectOutputMediaName(
                    projInd=self.project_naming_project_index, seqInd=self.project_naming_sequence_index, shotInd=-1
                )

            if addSeparator:
                name += self.project_naming_separator_char

        else:
            if "FORMATED" == mode:
                name = "Formated seq name to do"
            elif "SHORT" == mode:
                name = self.sequence_name
            # FULL
            else:
                name = self.render_sequence_prefix
                name += self.sequence_name

            if addSeparator:
                name += "_"

        return name

    # def getSequencePrefix(self, index=None):
    #     return self._replaceHashByNumber(self.project_naming_sequence_format, index)

    def getProjectName(self):
        """Return the name of the project if Project Settings are used, an empty string otherwise
        since there is no project notion in free mode
        *** Warning: The returned value depends on the Project Settings context! ***
        """
        return self.project_name if self.use_project_settings else ""

    def getProjectPrefix(self, index=None):
        """Return the project identifier if Project Settings are used, an empty string otherwise
        since there is no project notion in free mode
        *** Warning: The returned value depends on the Project Settings context! ***
        """
        return self._replaceHashByNumber(self.project_naming_project_format, index) if self.use_project_settings else ""

    def getOutputMediaPath(
        self,
        outputMedia,
        entity,
        rootPath=None,
        insertSeqPrefix=False,
        providePath=True,
        provideName=True,
        provideExtension=True,
        specificFrame=None,
        genericFrame=False,
    ):
        """
        Return the path of the media that is generated for the specified shot.
        It is made of: <root path>/<shot take name>/<prefix>_<shot name>[_<specific frame index (if specified)].<extention>

        Args:
            outputMedia: can be:
                - for an entity shot:
                    SH_STILL:
                    SH_IMAGE_SEQ:
                    SH_IMAGE_SEQ_PLAYBLAST:
                    SH_VIDEO:
                    SH_AUDIO:
                    SH_INTERM_IMAGE_SEQ:
                    SH_INTERM_STAMPINFO_SEQ:
                    SH_INTERM_IMAGE_SEQ_PLAYBLAST:
                    SH_INTERM_STAMPINFO_SEQ_PLAYBLAST:
                - for an entity take:
                    TK_IMAGE_SEQ:
                    TK_VIDEO:
                    TK_EDIT_IMAGE_SEQ:
                    TK_EDIT_VIDEO:
                    TK_PLAYBLAST:
                - for an entity sequence (or montage):
                    SEQ_ROOT: root to the sequence files and folders

            entity: can be a shot, a take or a sequence (ie the montage)

            rootPath: start of the path, if specified. Otherwise the current file folder is used

            providePath: if True then the returned file name starts with the full path
                if providePath is True:
                    if rootPath is provided then the start of the path is the root, otherwise props.renderRootPath is used
                    if insertTakeName is True then the name of the take is added to the path
                    if provideName is False then the returned path ends with '\\'
            provideName: if True then the returned file name contains the name
            provideExtension: if True then the returned file name ends with the file extention

            genericFrame: if genericFrame is True then #### is used instead of the specific frame index
        """

        prefs = config.getAddonPrefs()
        filePath = ""
        fileName = ""
        fileExtension = ""

        # intermediate directory name. Used in the directory name of the shot renderings
        INTERM_DIR = "_Intermediate"
        # intermediate playblast directory name. Used in the directory name of the playblast renderings
        INTERM_PLAYBLAST_DIR = "_IntermPlayblast"

        #  FOLDER_SEPARATOR = "\\"
        FOLDER_SEPARATOR = utils_os.get_dir_separator_char()

        # file path
        if providePath:
            if rootPath is not None:
                filePath += bpy.path.abspath(rootPath)
            else:
                #   filePath += bpy.path.abspath(bpy.data.filepath)     # current blender file path
                filePath += bpy.path.abspath(self.renderRootPath)

            if not (filePath.endswith("/") or filePath.endswith("\\")):
                filePath += FOLDER_SEPARATOR

            # if insertTakeName or insertShotFolder or insertTempFolder or insertStampInfoPrefix:
            #     filePath += shot.getParentTake().getName_PathCompliant() + FOLDER_SEPARATOR

            if "SH_" == outputMedia[0:3]:
                # entity is a shot
                filePath += entity.getParentTake().getName_PathCompliant() + FOLDER_SEPARATOR

                if "SH_VIDEO" != outputMedia:
                    filePath += f"{entity.getName_PathCompliant()}"

                    # if "INTERM_" == outputMedia[3:10]:
                    if "_INTERM" in outputMedia:
                        if "_PLAYBLAST" in outputMedia:
                            filePath += INTERM_PLAYBLAST_DIR
                        else:
                            filePath += INTERM_DIR
                    if "AUDIO" == outputMedia[3:8]:
                        if "_PLAYBLAST" in outputMedia:
                            filePath += INTERM_PLAYBLAST_DIR
                        else:
                            filePath += INTERM_DIR

                    filePath += FOLDER_SEPARATOR

            # if insertShotFolder or insertTempFolder:
            #     filePath += f"{shot.getName_PathCompliant()}"
            #     if insertTempFolder:
            #         filePath += "_Intermediate"
            #     filePath += FOLDER_SEPARATOR

            elif "TK_" == outputMedia[0:3]:
                # entity is a take
                filePath += entity.getName_PathCompliant() + FOLDER_SEPARATOR
            # elif "EDIT_" == outputMedia[0:5]:

        # file name
        if provideName:
            if "SH_" == outputMedia[0:3]:
                if "SH_INTERM_STAMPINFO_SEQ" in outputMedia:
                    fileName += "_tmp_StampInfo_"
                    # entity is a shot
                    fileName += entity.getName_PathCompliant(withPrefix=insertSeqPrefix)
                elif "SH_VIDEO" == outputMedia:
                    fileName += entity.getName_PathCompliant(withPrefix=True)
                else:
                    fileName += entity.getName_PathCompliant(withPrefix=insertSeqPrefix)

                # wkip hack degueu
                if "SH_IMAGE_SEQ" in outputMedia and not genericFrame and specificFrame is None:
                    # required by the OTIO edit file for img seq generation
                    fileName += "_" + self.getFramePadding(frame=0)
                else:
                    if genericFrame:
                        fileName += "_"
                        # we add "#####"
                        fileName += self.getFramePadding()
                    elif specificFrame is not None:
                        fileName += "_" + self.getFramePadding(frame=specificFrame)

            elif "TK_" == outputMedia[0:3]:
                if "TK_PLAYBLAST" == outputMedia:
                    fileName += "_playblast_"

                # entity is a take
                fileName += entity.getName_PathCompliant(withPrefix=insertSeqPrefix)

                if "TK_EDIT_IMAGE_SEQ" == outputMedia:
                    fileName += "_ImgSq"

            # file extension
            if provideExtension:
                if "SH_" == outputMedia[0:3]:
                    if "SH_INTERM_STAMPINFO_SEQ" == outputMedia:
                        fileExtension += ".png"
                    elif "SH_IMAGE_SEQ" in outputMedia or "SH_INTERM_IMAGE_SEQ" == outputMedia:
                        if "_PLAYBLAST" in outputMedia:
                            fileExtension += "."
                            if "jpeg" == prefs.playblastImagesOutputFormat.lower():
                                fileExtension += "jpg"
                            elif "png" == prefs.playblastImagesOutputFormat.lower():
                                fileExtension += "png"
                            else:
                                _logger.warning_ext(
                                    f"Invalid Playblast image output format in Prefs: {prefs.playblastImagesOutputFormat} - Using JPEG"
                                )
                                fileExtension += "jpg"
                        else:
                            if self.use_project_settings:
                                fileExtension += "."
                                if "png" == self.project_images_output_format.lower():
                                    fileExtension += "png"
                                elif "open_exr" == self.project_images_output_format.lower():
                                    fileExtension += "exr"
                                else:
                                    _logger.warning_ext(
                                        f"Invalid project image output format: {self.project_images_output_format} - Using PNG"
                                    )
                                    fileExtension += "png"
                            else:
                                fileExtension += "."
                                sceneFileFormat = self.parentScene.render.image_settings.file_format.lower()
                                if "jpeg" == sceneFileFormat:
                                    fileExtension += "jpg"
                                elif "png" == sceneFileFormat:
                                    fileExtension += "png"
                                elif "open_exr" == sceneFileFormat:
                                    fileExtension += "exr"
                                else:
                                    # output file is PNG otherwise
                                    _logger.warning_ext(f"Invalid image output format: {sceneFileFormat} - Using PNG")
                                    fileExtension += "png"
                    else:
                        fileExtension += "." + self.getOutputFileFormat(
                            isVideo=specificFrame is None and not genericFrame
                        )

                elif "TK_" == outputMedia[0:3]:
                    if "TK_VIDEO" in outputMedia:
                        if self.use_project_settings:
                            fileExtension += "."
                            if "mp4" == self.project_output_format.lower():
                                fileExtension += "mp4"
                            else:
                                _logger.warning_ext(
                                    f"Invalid project video output format: {self.project_output_format} - Using MP4"
                                )
                                fileExtension += "mp4"
                        else:
                            fileExtension += "."
                            sceneFileFormat = self.parentScene.render.image_settings.file_format.lower()
                            if "ffmpeg" == sceneFileFormat:
                                fileExtension += "mp4"
                            else:
                                # output file is MP4 otherwise
                                _logger.info_ext(
                                    f"Invalid scene video output format: {sceneFileFormat} - Using FFMPEG - MP4"
                                )
                                fileExtension += "mp4"
                    elif "TK_EDIT_" in outputMedia:
                        fileExtension += "." + "xml"
                    elif "TK_PLAYBLAST" == outputMedia:
                        fileExtension += "." + "mp4"

        resultStr = ""
        # used to get a path with \\ for Windows, with / for Mac and Linux
        # unfortunately it removes the separator char at the end of the path
        if providePath:
            # formattedFilePath = str(PurePath(filePath)) + utils_os.get_dir_separator_char()
            formattedFilePath = utils_os.format_path_for_os(filePath, addSeparatorAtTheEnd=True)
            resultStr += formattedFilePath

        resultStr += fileName + fileExtension

        return resultStr

    def getSceneCameras(self):
        """Return the list of the cameras in the current scene"""
        cameras = []
        for obj in bpy.context.scene.objects:
            # if str(type(bpy.context.view_layer.objects.active.data)) == "<class 'bpy.types.Camera'>"
            if str(type(obj.data)) == "<class 'bpy.types.Camera'>":
                cameras.append(obj)

        return cameras

    def selectCamera(self, shotIndex):
        shot = self.getShotByIndex(shotIndex)
        if shot is not None:
            bpy.ops.object.select_all(action="DESELECT")
            if shot.isCameraValid():
                if bpy.context.active_object is not None and bpy.context.active_object.mode != "OBJECT":
                    bpy.ops.object.mode_set(mode="OBJECT")
                    # if bpy.context.active_object is None or bpy.context.active_object.mode == "OBJECT":
                camObj = bpy.context.scene.objects[shot.camera.name]
                bpy.context.view_layer.objects.active = camObj
                camObj.select_set(True)

    def getActiveCameraName(self):
        cameras = self.getSceneCameras()
        # selectedObjs = []  #bpy.context.view_layer.objects.active    # wkip get the selection
        currentCam = None
        currentCamName = ""

        if bpy.context.view_layer.objects.active and (bpy.context.view_layer.objects.active).type == "CAMERA":
            # if len(selectedObjs) == 1 and selectedObjs.name == bpy.context.scene.objects[self.cameraName]:
            #    currentCam =  bpy.context.scene.objects[self.cameraName]
            currentCam = bpy.context.view_layer.objects.active
        if currentCam:
            currentCamName = currentCam.name
        elif 0 < len(cameras):
            currentCamName = cameras[0].name

        return currentCamName

    # wkip traiter cas quand aps de nom de fichier
    def getRenderFileName(self):
        #   print("\n getRenderFileName ")
        # filename is parsed in order to remove the last block in case it doesn't finish with \ or / (otherwise it is
        # the name of the file)
        filename = bpy.context.scene.render.filepath
        lastOccSeparator = filename.rfind("\\")
        if -1 != lastOccSeparator:
            filename = filename[lastOccSeparator + 1 :]

        #   print("    filename: " + filename)
        return filename

    ##############################

    # Project ###

    ##############################

    def setProjectSettings(
        self,
        use_project_settings=None,
        project_name=None,
        project_fps=-1,
        project_resolution=None,
        project_resolution_framed=None,
        project_use_shot_handles=None,
        project_shot_handle_duration=-1,
        project_output_format=None,
        project_color_space=None,
        project_asset_name=None,
    ):
        """Set only the specified properties
        Shot format must use "_" as separators. It is of the template: Act{:02}_Seq{:04}_Sh{:04}
        """

        print("    * setProjectSettings *")

        if use_project_settings is not None:
            self.use_project_settings = use_project_settings

        if project_name is not None:
            self.project_name = project_name
        if -1 != project_fps:
            self.project_fps = project_fps
        if project_resolution is not None:
            self.project_resolution_x = project_resolution[0]
            self.project_resolution_y = project_resolution[1]
        if project_resolution_framed is not None:
            self.project_resolution_framed_x = project_resolution_framed[0]
            self.project_resolution_framed_y = project_resolution_framed[1]

        if project_use_shot_handles is not None:
            self.project_use_shot_handles = project_use_shot_handles
        if -1 != project_shot_handle_duration:
            self.project_shot_handle_duration = project_shot_handle_duration

        if project_output_format is not None:
            self.project_output_format = project_output_format
        if project_color_space is not None:
            self.project_color_space = project_color_space
        if project_asset_name is not None:
            self.project_asset_name = project_asset_name

        self.applyProjectSettings()

    def applyProjectSettings(self, settingsListOnly=False):

        settingsList = []

        settingsList.append(["Project Name", '"' + self.project_name + '"'])

        # framerate
        ################
        fps, fps_base = utils.convertFramerateToSceneFPS(self.project_fps)
        settingsList.append(["Project Framerate", f"fps: {fps}, fps_base: {fps_base}"])

        settingsList.append(["Shot Full Name", f"{self.getProjectOutputMediaName(projInd=-2, seqInd=-2, shotInd=-2)}"])

        settingsList.append(["Resolution", str(self.project_resolution_x) + " x " + str(self.project_resolution_y)])
        settingsList.append(
            [
                "Resolution Framed",
                str(self.project_resolution_framed_x) + " x " + str(self.project_resolution_framed_y),
            ]
        )
        settingsList.append(["Use Shot Handles", str(self.project_use_shot_handles)])
        settingsList.append(["Shot Handle Duration", str(self.project_shot_handle_duration)])
        settingsList.append(["Project Output Format", str(self.project_output_format)])
        settingsList.append(["Project Color Space", str(self.project_color_space)])
        settingsList.append(["Project Asset Name", str(self.project_asset_name)])

        # applying project settings to parent scene
        ################

        if not settingsListOnly:
            if self.use_project_settings:
                parentScn = self.getParentScene()
                utils.setSceneFps(parentScn, self.project_fps)

                # parentScn.render.resolution_x = self.project_resolution_x
                # parentScn.render.resolution_y = self.project_resolution_y
                parentScn.render.resolution_percentage = 100

                # wkip both should not be there
                # self.use_handles = self.project_use_shot_handles
                # self.handles = self.project_shot_handle_duration

                # path
                self.setProjectRenderFilePath()

            self.setResolutionToScene()

        return settingsList

    def createRenderSettings(self):
        _logger.debug_ext("createRenderSettings", col="GREEN", tag="RENDER")

        self.renderSettingsStill.initialize("STILL")
        self.renderSettingsAnim.initialize("ANIMATION")
        self.renderSettingsAll.initialize("ALL")
        self.renderSettingsOtio.initialize("OTIO")
        self.renderSettingsPlayblast.initialize("PLAYBLAST")

    def setProjectRenderFilePath(self):
        # if '' == bpy.data.filepath:

        bpy.context.scene.render.filepath = f"//{self.getTakeName_PathCompliant()}"

    ##############################
    # Montage ###
    ##############################

    # def rebuildMontage(self):
    #     self._montage = MontageShotManager()
    #     self._montage.initialize(context.scene, props.getCurrentTake())

    # def get_montage(self):
    #     return self._montage

    def __init__(self):
        super().__init__()

    # def initialize(self, scene, take):
    def initialize(self):
        # self.sequencesList =
        #        UAS_ShotManager_Props.montageType = property(lambda self: "SHOTMANAGER")

        pass

    def get_montage_type(self):
        return "SHOTMANAGER"

    def get_montage_characteristics(self):
        """
        Return a dictionary with the characterisitics of the montage.
        This is required to export it as xml edit file.
        """
        # dict cannot be set as a property for Props :S
        characteristics = dict()

        if self.use_project_settings:
            characteristics["resolution_x"] = self.project_resolution_framed_x  # width
            characteristics["resolution_y"] = self.project_resolution_framed_y  # height
        else:
            # wkipwkipwkip export issue
            characteristics["resolution_x"] = self.parentScene.render.resolution_x  # width
            characteristics["resolution_y"] = self.parentScene.render.resolution_y  # height
        characteristics["framerate"] = self.get_fps()
        characteristics["duration"] = self.get_frame_duration()

        return characteristics

    def set_montage_characteristics(self, resolution_x=-1, resolution_y=-1, framerate=-1, duration=-1):
        """ """
        # self._characteristics = dict()
        # # self._characteristics["framerate"] = framerate  # timebase
        # self._characteristics["resolution_x"] = resolution_x  # width
        # self._characteristics["resolution_y"] = resolution_y  # height
        # self._characteristics["framerate"] = self.get_fps()  # timebase
        # self._characteristics["duration"] = self.get_frame_duration()  # wkip may change afterwards...
        # # self._characteristics["duration"] = duration  # wkip may change afterwards...
        pass

    def getInfoAsDictionnary(self, dictMontage=None, shotsDetails=True):
        if dictMontage is None:
            dictMontage = dict()
            dictMontage["montage"] = self.get_name()

        for take in self.takes:
            dictMontage[take.get_name()] = take.getInfoAsDictionnary(shotsDetails=shotsDetails)
        return dictMontage

    def printChildrenInfo(self):
        self.getCurrentTake().printInfo()

    def get_name(self):
        """Return the name of the montage, which is also the name of the sequence
        *** Warning: The returned value depends on the Project Settings context! ***
        """
        return self.getSequenceName("FULL")
        # return self.parentScene.name + "_" + self.takes[self.getCurrentTakeIndex()].get_name()

    def get_fps(self):
        """Return the fps of the montage
        *** Warning: The returned value depends on the Project Settings context! ***
        """
        return self.project_fps if self.use_project_settings else utils.getSceneEffectiveFps(self.parentScene)

    def get_frame_start(self):
        props = config.getAddonProps(self.parentScene)
        return props.editStartFrame

    def get_frame_end(self):
        """get_frame_end is exclusive in order to follow the Blender implementation of get_frame_end for its clips"""
        # editShotsList = self.getShotsList(ignoreDisabled=True)
        # if len(self.takes) and len(editShotsList):
        #     return self.sequencesList[len(self.sequencesList) - 1].get_frame_end()
        # else:
        #     return -1
        return self.get_frame_start() + self.getEditDuration()

    def get_frame_duration(self):
        return self.getEditDuration()

    def get_num_sequences(self):
        return 1

    def get_sequences(self):
        return [self.getCurrentTake()]

    def newSequence(self):
        # if self.sequencesList is None:
        #     self.sequencesList = list()
        # newSeq = SequenceShotManager(self)
        # self.sequencesList.append(newSeq)
        # return newSeq
        return None

    ###########################

    # TOFIX: wkipwkipwkip pb with old naming conventions
    def sortShotsVersions(self, takeIndex=-1):
        """Sorts shots ending with '_a', '_b'...
        *** Only sort disabled shots by default ***
        """
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            return ()

        # get the disabled shots
        shotList = self.takes[takeInd].shots

        disabledShotNames = list()
        for i in range(0, len(shotList)):
            if not shotList[i].enabled:
                disabledShotNames.append(shotList[i].name)

        # sort the list
        disabledShotNames.sort()

        # print("\nSorted list:")
        # for nam in disabledShotNames:
        #     print(f"  {nam}")

        # shot_re = re.compile(r"sh_?(\d+)", re.IGNORECASE)
        # shot_re = re.compile(r"Sh_?(\d+)")
        shot_re = re.compile(r"^Sh\d\d\d\d")

        def _baseName(name):
            """We are based on the name template Shxxxx"""
            return name[:6]

        def _isValidShotName(name):
            res = False
            match = shot_re.search(name)
            if match:
                res = True
            return res

        #  print("\nTreated list:")
        for shName in disabledShotNames:
            # if it is a basename or a version name
            if _isValidShotName(shName):
                #         print(f"\n - {shName}, basename: {_baseName(shName)}")

                # check the shots list from begining and insert at first place where names are matching
                for i in range(0, len(shotList)):
                    # ignore self
                    shotFromName = self.getShotByName(shName)
                    shotFromNameInd = self.getShotIndex(shotFromName)

                    #       print(f"  i:{i} ")
                    if shotList[i].name == shName:
                        pass
                    elif (shotList[i].name).startswith(_baseName(shName)):
                        #  print(f"   ici:  shotList[i].name: {shotList[i].name}")

                        if shName < shotList[i].name:
                            #       print(f"     before, i:{i}, shotFromName:{shotFromName}")
                            #       self.takes[takeInd].debugDisplayShots()
                            if shotFromNameInd < i:
                                if 0 < i:
                                    self.moveShotToIndex(shotFromName, i - 1)
                            else:
                                self.moveShotToIndex(shotFromName, i)
                            #       self.takes[takeInd].debugDisplayShots()
                            break
                        else:
                            #    print(f"   lu")
                            if len(shotList) > i + 1:
                                #        print(f"   lulu")
                                if (shotList[i + 1].name).startswith(_baseName(shName)):
                                    if shName < shotList[i + 1].name:
                                        #                print(f"     lu")
                                        self.moveShotToIndex(shotFromName, i + 1)
                                        break
                                else:
                                    #            print("lo")
                                    self.moveShotToIndex(shotFromName, i + 1)
                                    break


###########################


_classes = (
    UAS_ShotManager_OutputParams_Resolution,
    UAS_ShotManager_Shot,
    UAS_ShotManager_Take,
    UAS_ShotManager_LayoutSettings,
    UAS_ShotManager_Props,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.UAS_shot_manager_props = PointerProperty(type=UAS_ShotManager_Props)


def unregister():
    del bpy.types.Scene.UAS_shot_manager_props
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
