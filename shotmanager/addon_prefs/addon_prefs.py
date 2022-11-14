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
add-on global preferences
"""

import platform
import ctypes

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty


from .addon_prefs_ui import draw_addon_prefs

from shotmanager.features.greasepencil.greasepencil_frame_template import UAS_GreasePencil_FrameTemplate
from shotmanager.utils import utils
from shotmanager.utils.utils_os import get_latest_release_version

from shotmanager.utils.utils_operators_overlays import getOverlaysPropertyState

from shotmanager.tools.frame_range.frame_range_operators import display_frame_range_in_editor
from shotmanager.tools.markers_nav_bar.markers_nav_bar import display_markersNavBar_in_editor

from shotmanager.keymaps import playbar_keymaps

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def list_greasepencil_layers(self, context):
    res = list()
    if context.object is not None and "GPENCIL" == context.object.type:
        if len(context.object.data.layers):
            for i, layer in enumerate(context.object.data.layers):
                res.append((layer.info, layer.info, "", i))
        else:
            res = (("NOLAYER", "No Layer", "", 0),)
    else:
        res = (("ALL", "ALL", "", 0), ("DISABLED", "DISABLED", "", 1))
    return res


class UAS_ShotManager_AddonPrefs(AddonPreferences):
    """
    Use this to get these prefs:
    prefs = config.getAddonPrefs()
    """

    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package
    bl_idname = "shotmanager"

    previousInstalledVersion: IntProperty(
        description="Internal setting"
        "\nStore (as an integer) the version of the release of the add-on that was installed before this release."
        "\nIf there was none then the value is 0"
        "\nThis version is updated when self.initialize_shot_manager_prefs() is called, which should occur"
        "\nwhen the add-on is installed. So after the installation of a new version the value of previousInstalledVersion"
        "\nshould be the same as self.version()[1]",
        default=0,
    )

    def isPrefsVersionUpToDate(self):
        """Used in the __init__() of the add-on to see if a call to initialize_shot_manager_prefs() is required.
        This allows the prefs update to be done only when necessary (= when the add-on is updated), and not
        at every register of the add-on.
        """
        return self.version()[1] == self.previousInstalledVersion

    install_failed: BoolProperty(
        name="Install failed",
        default=False,
    )

    def version(self):
        """Return the add-on version in the form of a tuple made by:
            - a string x.y.z (eg: "1.21.3")
            - an integer. x.y.z becomes xxyyyzzz (eg: "1.21.3" becomes 1021003)
        Return None if the addon has not been found
        """
        return utils.addonVersion("Ubisoft Shot Manager")

    # def isReleaseVersion(self):
    #     """Return True if the current version is a released on"""

    newAvailableVersion: IntProperty(
        description="Store the version of the latest release of the add-on as an integer if there is an online release"
        "\nthat is more recent than this version. If there is none then the value is 0",
        # default=2005001,
        default=1007016,
    )

    checkForNewAvailableVersion: BoolProperty(
        name="Check for Updates",
        description=(
            "If checked then the add-on automaticaly see if a new release\n"
            "is available online, and if so then a red world icon is displayed at the\n"
            "top right corner of the main panel"
        ),
        default=True,
    )

    # not used anymore since Stamp Info has been integrated
    def dependency_min_supported_version(self, addon_name):
        """Return a tuple with the version minimum of a dependency add-on supported by this add-on:
            - a string x.y.z (eg: "1.21.3")
            - an integer. x.y.z becomes xxyyyzzz (eg: "1.21.3" becomes 1021003)
        Return None if the addon has not been found in the listed dependencies
        """
        # if "Stamp Info" == addon_name:
        #     return config.STAMP_INFO_MIN_VERSION

        return None

    isInitialized: BoolProperty(
        name="Preferences Initialization State",
        description=(
            "Flag to validate that Shot Manager preferences have been correctly initialized"
            "\nThis flag can be changed for debug purpose: activate the debug mode and go to the add-on Preferences, in the Debug tab"
        ),
        default=False,
    )

    def initialize_shot_manager_prefs(self):
        print("\nInitializing Ubisoft Shot Manager Preferences...")

        self.stb_frameTemplate.initialize(mode="ADDON_PREFS")
        self.newAvailableVersion = 0

        if self.checkForNewAvailableVersion and not config.devDebug:
            versionStr = None
            _logger.debug_ext("Checking for updates online...", col="BLUE")
            versionStr = get_latest_release_version(
                "https://github.com/ubisoft/shotmanager/releases/latest", verbose=True
            )

            if versionStr is not None:
                # version string from the tags used by our releases on GitHub is formated as this: v<int>.<int>.<int>
                version = utils.convertVersionStrToInt(versionStr)

                _logger.debug_ext(f"   Latest version of Ubisoft Shot Manager online is: {versionStr}", col="BLUE")
                if self.version()[1] < version:
                    _logger.debug_ext("   New version available online...", col="BLUE")
                    self.newAvailableVersion = version
                else:
                    self.newAvailableVersion = 0
            else:
                self.newAvailableVersion = 0

        # *** layouts initialization ***
        ####################################

        # storyboard layout default values
        ##########################
        self.stb_selected_shot_changes_current_shot = True
        self.stb_selected_shot_in_shots_stack_changes_current_shot = False
        self.stb_current_stb_shot_changes_time_zoom = True
        self.stb_current_pvz_shot_changes_time_zoom = True

        self.stb_display_storyboard_in_properties = True
        self.stb_display_notes_in_properties = True
        self.stb_display_cameraBG_in_properties = False
        self.stb_display_takerendersettings_in_properties = False
        self.stb_display_editmode_in_properties = False
        self.stb_display_globaleditintegr_in_properties = False
        self.stb_display_advanced_infos = False

        # previz layout default values
        ##########################
        self.pvz_selected_shot_changes_current_shot = False
        self.pvz_selected_shot_in_shots_stack_changes_current_shot = False
        self.pvz_current_stb_shot_changes_time_zoom = True
        self.pvz_current_pvz_shot_changes_time_zoom = False

        self.pvz_display_storyboard_in_properties = False
        self.pvz_display_notes_in_properties = False
        self.pvz_display_cameraBG_in_properties = False
        self.pvz_display_takerendersettings_in_properties = False
        self.pvz_display_editmode_in_properties = False
        self.pvz_display_globaleditintegr_in_properties = False
        self.pvz_display_advanced_infos = False

        # self.display_25D_greasepencil_panel = True

        self.previousInstalledVersion = self.version()[1]
        self.isInitialized = True

    ########################################################################
    # general ###
    ########################################################################

    # ****** settings exposed to the user in the prefs panel:
    # ------------------------------

    output_first_frame: IntProperty(
        name="Output First Frame Index",
        description="Index of the first frame for rendered image sequences and videos."
        "\nThis is 0 in most editing applications, sometimes 1. Can sometimes be a very custom"
        "\nvalue such as 1000 or 1001."
        "\nIf the Project Settings are active then the value provided there is used instead",
        min=0,
        soft_max=1001,
        subtype="TIME",
        default=0,
    )

    img_name_digits_padding: IntProperty(
        name="Image Name Digit Padding",
        description="Number of digits to use for the index of an output image in its name."
        "\nIf the Project Settings are active then the value provided there is used instead",
        min=1,
        max=8,
        default=5,
    )

    new_shot_duration: IntProperty(
        name="Default Shot Duration",
        description="Default duration (in frames) for new shots",
        min=1,
        soft_max=250,
        subtype="TIME",
        default=50,
    )

    storyboard_default_canvasOpacity: FloatProperty(
        name="Storyboard Default Canvas Opacity",
        description="Opacity of the Canvas layer for new storyboard frames",
        min=0.0,
        max=1.0,
        step=0.1,
        default=1.0,
    )

    storyboard_default_distanceFromOrigin: FloatProperty(
        name="Storyboard Default Frame Distance",
        description="Distance between a new storyboard frame and its parent camera",
        subtype="DISTANCE",
        soft_min=0.02,
        min=0.001,
        soft_max=10.0,
        # max=1.0,
        step=0.1,
        default=2.0,
    )

    storyboard_default_start_frame: IntProperty(
        name="Storyboard Default Start Time",
        description="Time (in frames) at which a new storyboard frame starts",
        min=0,
        soft_max=250,
        step=1,
        subtype="TIME",
        default=100,
    )

    storyboard_new_shot_duration: IntProperty(
        name="Storyboard Default Shot Duration",
        description="Default duration (in frames) for new storyboard frames",
        min=1,
        soft_max=250,
        subtype="TIME",
        default=100,
    )

    displaySMDebugPanel: BoolProperty(
        name="Display Debug Panel",
        description="Display the debug panel and debug tools of Shot Manager.\nIt will be as a tab in the viewport N-Panel",
        default=False,
    )

    # ****** hidden settings:
    # ------------------------------

    general_warning_expanded: BoolProperty(
        name="Expand Warnings",
        default=False,
    )

    def _get_take_properties_expanded(self):
        val = self.get("take_properties_expanded", False)
        return val

    def _set_take_properties_expanded(self, value):
        # print(f"*** _set_take_properties_expanded: {self.take_properties_expanded}, value: {value}")
        # close other panels
        if self.take_properties_expanded != value and not value:
            prefs = config.getAddonPrefs()
            prefs.take_renderSettings_expanded = False
            prefs.take_notes_expanded = False
        self["take_properties_expanded"] = value

    take_properties_expanded: BoolProperty(
        name="Expand Take Properties",
        get=_get_take_properties_expanded,
        set=_set_take_properties_expanded,
        default=False,
    )

    take_renderSettings_expanded: BoolProperty(
        name="Expand Take Render Settings",
        description="*** This take has its own render settings ***",
        default=False,
    )
    take_notes_expanded: BoolProperty(
        name="Expand Take Notes",
        default=False,
    )

    shot_properties_expanded: BoolProperty(
        name="Expand Shot Properties",
        default=True,
    )
    shot_global_props_expanded: BoolProperty(
        name="Expand Shots Global Properties",
        default=False,
    )
    shot_notes_expanded: BoolProperty(
        name="Expand Shot Notes",
        default=False,
    )
    shot_cameraBG_expanded: BoolProperty(
        name="Expand Shot Camera BG",
        default=False,
    )
    shot_greasepencil_expanded: BoolProperty(
        name="Expand Shot Grease Pencil",
        default=False,
    )

    ##############################
    # storyboard panel
    ##############################
    stb_canvas_props_expanded: BoolProperty(
        name="Expand Canvas Properties",
        default=False,
    )

    stb_anim_props_expanded: BoolProperty(
        name="Expand Animation Properties",
        default=False,
    )

    stb_global_props_expanded: BoolProperty(
        name="Expand Global Properties",
        default=False,
    )

    ##############################
    # grease pencil frame template
    ##############################
    stb_frameTemplate: PointerProperty(
        type=UAS_GreasePencil_FrameTemplate,
    )

    # hidden UI properties
    def _get_stb_global_visibility(self):
        val = self.get("stb_global_visibility", 0)
        return val

    def _set_stb_global_visibility(self, value):
        # "NO_CHANGE"
        if 0 != value:
            props = config.getAddonProps(bpy.context.scene)
            currentTake = props.getCurrentTake()
            if currentTake is not None:
                for sh in currentTake.shots:
                    if sh.enabled or props.shotGlobalSettings.alsoApplyToDisabledShots:
                        gpProps = sh.getGreasePencilProps()
                        if gpProps is not None:
                            if 1 == value:
                                gpProps.visibility = "ALWAYS_VISIBLE"
                            elif 2 == value:
                                gpProps.visibility = "ALWAYS_HIDDEN"
                            elif 3 == value:
                                gpProps.visibility = "AUTO"
        self["stb_global_visibility"] = 0

    # def _update_stb_global_visibility(self, context):
    #     props = config.getAddonProps(context.scene)
    #     currentTake = props.getCurrentTake()
    #     if currentTake is not None:
    #         for sh in currentTake.shots:
    #             gpProps = sh.getGreasePencilProps()
    #             if gpProps is not None:
    #                 gpProps.visibility = self.stb_global_visibility

    stb_global_visibility: EnumProperty(
        name="Global Frame Visibility",
        description="Visibility",
        items=(
            (
                "NO_CHANGE",
                "Set Visibility",
                "Select the new visibility state to apply to all the storyboard frames of the current take\n"
                "Change is applied immediatly",
            ),
            ("ALWAYS_VISIBLE", "All to Visible", "Storyboard frame is always visible"),
            ("ALWAYS_HIDDEN", "All to Hidden", "Storyboard frame is always hidden"),
            ("AUTO", "All to Auto", "Storyboard frame is automaticaly shown or hidden"),
        ),
        get=_get_stb_global_visibility,
        set=_set_stb_global_visibility,
        # update=_update_stb_global_visibility,
        default="NO_CHANGE",
    )

    ###############################
    # layers use
    ###############################

    # stb_useLayer_Canvas: BoolProperty(
    #     name="Canvas Layer",
    #     description="Use Canvas layer",
    #     default=True,
    # )

    # stb_useLayer_BG_Ink: BoolProperty(
    #     name="BG Ink Layer",
    #     description="use BG Ink Layer",
    #     default=True,
    # )

    # stb_useLayer_BG_Fill: BoolProperty(
    #     name="BG Fill Layer",
    #     description="use BG Fill Layer",
    #     default=True,
    # )

    # prefs panels
    ######################
    addonPrefs_settings_expanded: BoolProperty(
        name="Expand Settings Preferences",
        default=False,
    )
    addonPrefs_ui_expanded: BoolProperty(
        name="Expand UI Preferences",
        default=False,
    )
    addonPrefs_shotManips_expanded: BoolProperty(
        name="Expand Shot Manipulations Preferences",
        default=False,
    )
    addonPrefs_features_expanded: BoolProperty(
        name="Expand Features Preferences",
        default=False,
    )
    addonPrefs_tools_expanded: BoolProperty(
        name="Expand Tools Preferences",
        default=False,
    )
    addonPrefs_render_expanded: BoolProperty(
        name="Expand Render Preferences",
        default=False,
    )
    addonPrefs_stampInfo_expanded: BoolProperty(
        name="Expand Stamp Info Preferences",
        default=False,
    )
    addonPrefs_keymapping_expanded: BoolProperty(
        name="Expand Key Mapping Preferences",
        default=False,
    )
    addonPrefs_debug_expanded: BoolProperty(
        name="Expand Debug Preferences",
        default=False,
    )

    current_shot_changes_current_time_to_start: BoolProperty(
        name="Set Current Frame To Shot Start",
        description="Set the current time to the start of the shot when the current shot is changed.\n(Add-on preference)",
        default=True,
    )
    current_shot_changes_time_range: BoolProperty(
        name="Set Time Range To Shot Range",
        description="Set the animation range to match the shot range when the current shot is changed.\n(Add-on preference)",
        default=False,
    )

    # split to 2 properties, one for the storyboard layout mode and the other for the previz mode
    # current_shot_changes_time_zoom: BoolProperty(
    #     name="Zoom Timeline to Shot Range",
    #     description="Automatically zoom the timeline content to frame the shot when the current shot is changed.\n(Add-on preference)",
    #     default=False,
    # )

    # NOTE: these 2 settings are related to the SHOT TYPE, not to the current layout mode
    # changed to current_stb_shot_select_stb_frame and current_pvz_shot_select_stb_frame
    # current_shot_select_stb_frame: BoolProperty(
    #     name="Select Storyboard Frame of the Current Short",
    #     description="Automatically select the storyboard frame (= grease pencil) of the shot when the current shot is changed.\n(Add-on preference)",
    #     default=True,
    # )
    current_stb_shot_select_stb_frame: BoolProperty(
        name="Select Storyboard Frame of the Current Storyboard Short",
        description="For shots of type Storyboard Shot: Automatically select the Storyboard Frame (= grease pencil) of the shot when the current shot is changed.\n(Add-on preference)",
        default=True,
    )
    current_pvz_shot_select_stb_frame: BoolProperty(
        name="Select Storyboard Frame of the Current Camera Short",
        description="For shots of type Camera Shot: Automatically select the Storyboard Frame (= grease pencil) of the shot when the current shot is changed.\n(Add-on preference)",
        default=True,
    )

    # current_shot_changes_edited_frame_in_stb: BoolProperty(
    #     name="Set selected shot to edited",
    #     description="When a shot is selected in the shot list, in Storyboard layout mode, and another one is being edited, then"
    #     "\nthe shot becomes the new edited one",
    #     default=True,
    # )

    # def _get_useLockCameraView(self):
    #     # Can also use area.spaces.active to get the space assoc. with the area
    #     for area in bpy.context.screen.areas:
    #         if area.type == "VIEW_3D":
    #             for space in area.spaces:
    #                 if space.type == "VIEW_3D":
    #                     realVal = space.lock_camera

    #     # not used, normal it's the fake property
    #     self.get("useLockCameraView", realVal)

    #     return realVal

    # def _set_useLockCameraView(self, value):
    #     self["useLockCameraView"] = value
    #     for area in bpy.context.screen.areas:
    #         if area.type == "VIEW_3D":
    #             for space in area.spaces:
    #                 if space.type == "VIEW_3D":
    #                     space.lock_camera = value

    # # fake property: value never used in itself, its purpose is to update ofher properties
    # useLockCameraView: BoolProperty(
    #     name="Lock Cameras to View",
    #     description="Enable view navigation within the camera view",
    #     get=_get_useLockCameraView,
    #     set=_set_useLockCameraView,
    #     # update=_update_useLockCameraView,
    #     options=set(),
    # )

    ########################################################################
    # layout   ###
    ########################################################################

    # can be STORYBOARD or PREVIZ
    # not visible in the UI because radiobuttons are more suitable

    # def _update_layout_mode(self, context):
    #     #   print("\n*** Prefs _update_layout_mode updated. New state: ", self._update_layout_mode)
    #     # self.layout_but_storyboard = "STORYBOARD" == self.layout_mode
    #     # self.layout_but_previz = "PREVIZ" == self.layout_mode
    #     if "STORYBOARD" == self.layout_mode:
    #         self.stb_display_storyboard_in_properties = True
    #         self.stb_display_notes_in_properties = True
    #     #    self.display_25D_greasepencil_panel = True
    #     else:
    #         self.pvz_display_storyboard_in_properties = False
    #         self.pvz_display_notes_in_properties = False
    #     #    self.display_25D_greasepencil_panel = False
    #     pass

    layout_mode: EnumProperty(
        name="Layout Mode",
        description="Defines if Shot Manager panel should be appropriate for storyboarding or for previz",
        items=(
            ("STORYBOARD", "Storyboard", "Storyboard layout"),
            ("PREVIZ", "Previz", "Previz layout"),
        ),
        #  update=_update_layout_mode,
        # default="PREVIZ",
        # default="STORYBOARD",
        default=config.defaultLayout,
    )

    # NOTE:
    # layout_but_storyboard and layout_but_previz behave as radiobuttons and control
    # the state of layout_mode
    def _get_layout_but_storyboard(self):
        val = "STORYBOARD" == self.layout_mode
        return val

    def _set_layout_but_storyboard(self, value):
        # if not self["layout_but_storyboard"]:
        #     if value:
        #         self.layout_mode = "STORYBOARD"
        #         self["layout_but_storyboard"] = True
        #         self["layout_but_previz"] = False
        if value:
            self.layout_mode = "STORYBOARD"
        self["layout_but_storyboard"] = "STORYBOARD" == value

    layout_but_storyboard: BoolProperty(
        name="Storyboard",
        description="Set the Shot Manager panel layout to Storyboard",
        get=_get_layout_but_storyboard,
        set=_set_layout_but_storyboard,
        default=False,
    )

    def _get_layout_but_previz(self):
        val = "PREVIZ" == self.layout_mode
        return val

    def _set_layout_but_previz(self, value):
        if value:
            self.layout_mode = "PREVIZ"
        self["layout_but_previz"] = "PREVIZ" == value

    def _update_layout_but_previz(self, context):
        print("\n*** layout_but_storyboard updated. New state: ", self.layout_but_previz)
        self.layout_mode = "PREVIZ"

    layout_but_previz: BoolProperty(
        name="Previz",
        description="Set the Shot Manager panel layout to Previz",
        get=_get_layout_but_previz,
        set=_set_layout_but_previz,
        default=True,
    )

    ########################################################################
    # features panel   ###
    ########################################################################

    features_layoutSettings_expanded: BoolProperty(
        name="Expand Layout Settings",
        default=False,
    )

    ########################################################################
    # features to display by default   ###
    ########################################################################

    #########################
    # storyboard LAYOUT
    #
    # NOTE:
    # Settings prefixed by "stb_" are contextual to the STORYBOARD LAYOUT mode (not to the camera type!)
    # They are all initialized in the initialize_shot_manager_prefs() function. Search for: *** layouts initialization ***
    #########################

    # NOTE: behaviors with (*) are automatically applied when the Continuous Editing mode is used

    stb_selected_shot_changes_current_shot: BoolProperty(
        name="Set Shot Selected in the Shots List to Current  (*)",
        description="When a shot is selected in the Shot List, in Storyboard layout mode, the shot is also set to be the current one",
        default=False,
    )
    stb_selected_shot_in_shots_stack_changes_current_shot: BoolProperty(
        name="Set Shot Selected in the Interactive Shots Stack to Current  (*)",
        description="When a shot is selected in the Interactive Shots Stack, in Storyboard layout mode, the shot is also set to be the current one",
        default=False,
    )

    stb_current_stb_shot_changes_time_zoom: BoolProperty(
        name="Storyboard Shot: Zoom Timeline to Shot Range",
        description="When the current layout is Storyboard: automatically zoom the timeline content to frame the shot when the current shot is changed"
        "\nand if the shot type is Storyboard",
        default=False,
    )
    stb_current_pvz_shot_changes_time_zoom: BoolProperty(
        name="Camera Shot: Zoom Timeline to Shot Range",
        description="When the current layout is Storyboard: automatically zoom the timeline content to frame the shot when the current shot is changed"
        "\nand if the shot type is Camera",
        default=False,
    )

    ####
    # Following settings are also created in the layout class UAS_ShotManager_LayoutSettings
    ####

    stb_display_storyboard_in_properties: BoolProperty(
        name="Storyboard Frames and Grease Pencil Tools",
        description="Display the storyboard frames properties and tools in the Shot properties panel."
        "\nA storyboard frame is a Grease Pencil drawing surface associated to the camera of each shot",
        default=False,
    )

    stb_display_notes_in_properties: BoolProperty(
        name="Takes and Shots Notes",
        description="Display the takes and shots notes in the Shot Properties panels",
        default=False,
    )

    stb_display_cameraBG_in_properties: BoolProperty(
        name="Camera Background Tools",
        description="Display the camera background image tools and controls in the Shot Properties panel",
        default=False,
    )

    stb_display_takerendersettings_in_properties: BoolProperty(
        name="Take Render Settings",
        description="Display the take render settings in the Take Properties panel."
        "\nThese options allow each take to be rendered with its own output resolution",
        default=False,
    )

    stb_display_editmode_in_properties: BoolProperty(
        name="Display Global Edit Integration Tools",
        description="Display the advanced properties of the takes used to specify their position in a global edit",
        default=False,
    )

    stb_display_globaleditintegr_in_properties: BoolProperty(
        name="Display Global Edit Integration Tools",
        description="Display the advanced properties of the takes used to specify their position in a global edit",
        default=False,
    )

    stb_display_advanced_infos: BoolProperty(
        name="Display Advanced Infos",
        description="Display technical information and feedback in the UI",
        default=False,
    )

    #########################
    # previz
    #
    # NOTE:
    # Settings prefixed by "pvz_" are contextual to the PREVIZ LAYOUT mode (not to the camera type!)
    # They are all initialized in the initialize_shot_manager_prefs() function. Search for: *** layouts initialization ***
    #########################

    # NOTE: behaviors with (*) are automatically applied when the Continuous Editing mode is used

    pvz_selected_shot_changes_current_shot: BoolProperty(
        name="Set Shot Selected in the Shots List to Current  (*)",
        description="When a shot is selected in the Shot List, in Previz layout mode, the shot is also set to be the current one",
        default=False,
    )
    pvz_selected_shot_in_shots_stack_changes_current_shot: BoolProperty(
        name="Set Shot Selected in the Interactive Shots Stack to Current  (*)",
        description="When a shot is selected in the Interactive Shots Stack, in Previz layout mode, the shot is also set to be the current one",
        default=False,
    )

    pvz_current_stb_shot_changes_time_zoom: BoolProperty(
        name="Storyboard Shot: Zoom Timeline to Shot Range",
        description="When the current layout is Previz: automatically zoom the timeline content to frame the shot when the current shot is changed"
        "\nand if the shot type is Storyboard",
        default=False,
    )
    pvz_current_pvz_shot_changes_time_zoom: BoolProperty(
        name="Camera Shot: Zoom Timeline to Shot Range",
        description="When the current layout is Previz: automatically zoom the timeline content to frame the shot when the current shot is changed"
        "\nand if the shot type is Camera",
        default=False,
    )

    ####
    # Following settings are also created in the layout class UAS_ShotManager_LayoutSettings
    ####
    pvz_display_storyboard_in_properties: BoolProperty(
        name="Storyboard Frames and Grease Pencil Tools",
        description="Display the storyboard frames properties and tools in the Shot properties panel."
        "\nA storyboard frame is a Grease Pencil drawing surface associated to the camera of each shot",
        default=False,
    )

    pvz_display_notes_in_properties: BoolProperty(
        name="Takes and Shots Notes",
        description="Display the takes and shots notes in the Shot Properties panels",
        default=False,
    )

    pvz_display_cameraBG_in_properties: BoolProperty(
        name="Camera Background Tools",
        description="Display the camera background image tools and controls in the Shot Properties panel",
        default=False,
    )

    pvz_display_takerendersettings_in_properties: BoolProperty(
        name="Take Render Settings",
        description="Display the take render settings in the Take Properties panel."
        "\nThese options allow each take to be rendered with its own output resolution",
        default=False,
    )

    pvz_display_editmode_in_properties: BoolProperty(
        name="Display Global Edit Integration Tools",
        description="Display the advanced properties of the takes used to specify their position in a global edit",
        default=False,
    )

    pvz_display_globaleditintegr_in_properties: BoolProperty(
        name="Display Global Edit Integration Tools",
        description="Display the advanced properties of the takes used to specify their position in a global edit",
        default=False,
    )

    pvz_display_advanced_infos: BoolProperty(
        name="Display Advanced Infos",
        description="Display technical information and feedback in the UI",
        default=False,
    )

    ########################################################################
    # grease pencil tools ui   ###
    ########################################################################

    # ****** settings exposed to the user in the prefs panel:
    # ------------------------------

    display_25D_greasepencil_panel: BoolProperty(
        name="Display 2.5D Grease Pencil Panel",
        description="Display the 2.5D Grease Pencil sub-panel in the Shot Manager panel.\n\n(saved in the add-on preferences)",
        default=False,
    )

    ########################################################################
    # rendering ui   ###
    ########################################################################

    # ****** settings exposed to the user in the prefs panel:
    # ------------------------------

    display_render_panel: BoolProperty(
        name="Display Render Panel",
        description="Display the Render sub-panel in the Shot Manager panel.\n\n(saved in the add-on preferences)",
        default=True,
    )

    separatedRenderPanel: BoolProperty(
        name="Separated Render Panel",
        description="If checked, the Render panel will be a tab separated from Shot Manager panel",
        default=True,
    )

    # ****** hidden settings:
    # ------------------------------

    renderMode: EnumProperty(
        name="Display Shot Properties Mode",
        description="Update the content of the Shot Properties panel either on the current shot\nor on the shot selected in the shots list",
        items=(
            ("STILL", "Still", ""),
            ("ANIMATION", "Animation", ""),
            ("ALL", "All Edits", ""),
            ("OTIO", "OTIO", ""),
            ("PLAYBLAST", "PLAYBLAST", ""),
        ),
        default="STILL",
    )

    # items=(list_target_takes)
    # targetTakes = list_target_takes(self, context)
    #     self.targetTake = targetTakes[0][0]
    # layersListDropdown: EnumProperty(name="Layers", items=(("ALL", "ALL", ""), ("DISABLED", "DISABLED", "")))
    def _get_layersListDropdown(self):
        # val = self.get("layersListDropdown", 0)
        val = 0
        # if bpy.context.object is not None and "GPENCIL" == bpy.context.object.type:
        #     if len(bpy.context.object.data.layers):
        #         for i, layer in enumerate(bpy.context.object.data.layers):
        #             print(f"layer: {layer.info}, {i}")
        #             if layer.info == bpy.context.object.data.layers.active.info:
        #                 self["layersListDropdown"] = layer.info
        #                 print(f"layer ret: {layer.info}, {i}")
        #                 return 0
        return val

    def _set_layersListDropdown(self, value):
        self["layersListDropdown"] = value

    def _update_layersListDropdown(self, context):
        if bpy.context.object is not None and "GPENCIL" == bpy.context.object.type:
            if len(bpy.context.object.data.layers):
                bpy.context.object.data.layers.active = bpy.context.object.data.layers[self.layersListDropdown]
        print("\n*** layersListDropdown updated. New state: ", self.layersListDropdown)

    layersListDropdown: EnumProperty(
        name="Layers",
        items=(list_greasepencil_layers),
        # get=_get_layersListDropdown,
        # set=_set_layersListDropdown,
        update=_update_layersListDropdown,
    )

    ########################################################################
    # overlay tools
    ########################################################################

    # tools disabled during play
    best_play_perfs_turnOff_sequenceTimeline: BoolProperty(
        name="Turn Off Sequence Timeline",
        description="Disable Sequence Timeline display in the 3d viewport when animation is playing",
        default=True,
    )

    best_play_perfs_turnOff_interactiveShotsStack: BoolProperty(
        name="Turn Off Interactive Shots Stack",
        description="Disable Interactive Shots Stack display in the Timeline editor when animation is playing",
        default=True,
    )

    best_play_perfs_turnOff_mainUI: BoolProperty(
        name="Prevent Refreshing UI During Play",
        description="Stop refresh the information displayed in the Shot Manager UI during"
        "\nthe play with the Shots Play Mode on, this in order to improve play performances",
        default=True,
        options=set(),
    )

    seqTimeline_not_disabled_with_overlays: BoolProperty(
        name="Display Sequence Timeline Even If Overlays Are Hidden",
        description="Display Sequence Timeline Even If Overlays Are Hidden",
        default=True,
        options=set(),
    )

    ########################################################################
    # retimer
    ########################################################################

    retimer_applyTo_expanded: BoolProperty(
        name="Expand Layout Settings",
        default=True,
    )

    display_retimer_panel: BoolProperty(
        name="Display Retimer",
        description="Display the Retimer sub-panel in the Shot Manager panel.\n\n(saved in the add-on preferences)",
        default=True,
    )
    # applyToTimeCursor: BoolProperty(
    #     name="Apply to Time Cursor",
    #     description="Apply retime operation to the time cursor.\n\n(saved in the add-on preferences)",
    #     default=True,
    # )
    # applyToSceneRange: BoolProperty(
    #     name="Apply to Scene Range",
    #     description="Apply retime operation to the animation start and end of the scene.\n\n(saved in the add-on preferences)",
    #     default=True,
    # )

    ########################################################################
    # additional tools ###
    ########################################################################

    ###################################
    # sequence timeline ###############
    ###################################

    # displayed when toggle overlays button is on
    def _update_toggle_overlays_turnOn_sequenceTimeline(self, context):
        _logger.debug_ext("_update_toggle_overlays_turnOn_sequenceTimeline")

        # toggle on or off the overlay tools mode
        if self.toggle_overlays_turnOn_sequenceTimeline:
            if not context.window_manager.UAS_shot_manager_display_overlay_tools:
                context.window_manager.UAS_shot_manager_display_overlay_tools = True
            else:
                bpy.ops.uas_shot_manager.sequence_timeline("INVOKE_DEFAULT")
        else:
            if context.window_manager.UAS_shot_manager_display_overlay_tools:
                pass

    # displayed when toggle overlays button is on
    toggle_overlays_turnOn_sequenceTimeline: BoolProperty(
        name="Turn On Sequence Timeline",
        description="Display Sequence Timeline in the 3d viewport when Toggle Overlay Tools button is pressed",
        update=_update_toggle_overlays_turnOn_sequenceTimeline,
        default=True,
    )

    seqTimeline_settings_expanded: BoolProperty(
        name="Expand Panel Settings",
        default=False,
    )

    ###################################
    # interactive shots stack #########
    ###################################

    # displayed when toggle overlays button is on
    def _update_toggle_overlays_turnOn_interactiveShotsStack(self, context):
        _logger.debug_ext("_update_toggle_overlays_turnOn_interactiveShotsStack")

        # toggle on or off the overlay tools mode
        if self.toggle_overlays_turnOn_interactiveShotsStack:
            if not context.window_manager.UAS_shot_manager_display_overlay_tools:
                context.window_manager.UAS_shot_manager_display_overlay_tools = True
            else:
                bpy.ops.uas_shot_manager.interactive_shots_stack("INVOKE_DEFAULT")
        else:
            if context.window_manager.UAS_shot_manager_display_overlay_tools:
                pass

    toggle_overlays_turnOn_interactiveShotsStack: BoolProperty(
        name="Turn Off Interactive Shots Stack",
        description="Display Interactive Shots Stack in the Timeline editor when Toggle Overlay Tools button is pressed",
        update=_update_toggle_overlays_turnOn_interactiveShotsStack,
        default=True,
    )

    shtStack_settings_expanded: BoolProperty(
        name="Expand Panel Settings",
        default=False,
    )

    shot_selected_from_shots_stack__flag: BoolProperty(
        description="Flag property (= not exposed in the UI) used When a shot is selected in the Interactive Shots Stack,"
        "\nin Storyboard layout mode, the shot is also set to be the current one",
        default=False,
    )

    def _update_display_shtStack_toolbar(self, context):
        # print("\n*** _update_display_frame_range_tool. New state: ", self.display_frame_range_tool)
        from shotmanager.overlay_tools.interact_shots_stack.shots_stack_toolbar import (
            display_shots_stack_toolbar_in_editor,
        )

        display_shots_stack_toolbar_in_editor(self.display_shtStack_toolbar)

    display_shtStack_toolbar: BoolProperty(
        name="Display Interactive Shots Stack Toolbar",
        description="Display Interactive Shots Stack toolbar in the Timeline editor",
        update=_update_display_shtStack_toolbar,
        default=True,
    )

    shtStack_display_info_widget: BoolProperty(
        name="Display Information Widget",
        description="Display the Information Widget with the modifier tips in the Shots Stack",
        default=True,
    )

    shtStack_link_stb_clips_to_keys: BoolProperty(
        name="Link Storyboard Frame Content to Storyboard Clips",
        description="Link the Storyboard Frame content and the animation keys to the manipulated Storyboard shot clip",
        default=True,
    )

    shtStack_opacity: FloatProperty(
        name="Shots Stack Opacity",
        description="Opacity of the Interactive Shots Stack clips in the dopesheet editor",
        min=0.0,
        max=1.0,
        step=0.05,
        default=0.7,
    )

    shtStack_firstLineIndex: IntProperty(
        name="Shots Stack Fisrt Row",
        description=(
            "Set the line at which the first shot of the stack is placed."
            "\nDefault is 1 in order to let the keys of the Summary line visible"
        ),
        min=0,
        max=10,
        default=1,
    )

    def _update_shtStack_screen_display_factor_mode(self, context):
        # read also:
        # https://stackoverflow.com/questions/53889520/getting-screen-pixels-taking-into-account-the-scale-factor
        if "Windows" == platform.system():
            if "AUTO" == self.shtStack_screen_display_factor_mode:
                self.shtStack_screen_display_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
            elif "100" == self.shtStack_screen_display_factor_mode:
                self.shtStack_screen_display_factor = 1.0
            elif "125" == self.shtStack_screen_display_factor_mode:
                self.shtStack_screen_display_factor = 1.25
            elif "150" == self.shtStack_screen_display_factor_mode:
                self.shtStack_screen_display_factor = 1.5
            elif "175" == self.shtStack_screen_display_factor_mode:
                self.shtStack_screen_display_factor = 1.75
        else:
            self.shtStack_screen_display_factor = 1.0

    shtStack_screen_display_factor_mode: EnumProperty(
        name="Windows Screen Factor Mode",
        description=(
            "*** Windows Only ***"
            "Set the scale factor for the display of the Shots Stack so that the shot clips match the line size of the Dopesheet editor."
            "In Windows this parameter corresponds to the Display Scale Percentage. Usually it should be let to Auto, unless you"
            "use 2 screens with different display factors"
        ),
        items=(
            ("AUTO", "Auto", "Screen resolution factor is automatically detected"),
            ("100", "100%", "(default)"),
            ("125", "125%", ""),
            ("150", "150%", ""),
            ("175", "175%", ""),
        ),
        update=_update_shtStack_screen_display_factor_mode,
        default="AUTO",
    )

    shtStack_screen_display_factor: FloatProperty(
        name="Windows Screen Factor Value",
        description="Hidden value",
        min=1.0,
        max=1.75,
        step=0.25,
        default=1.0,
    )

    ###################################
    # camera hud ######################
    ###################################

    cameraHUD_shotNameSize: IntProperty(
        name="Shot Name Size",
        description="Size of the shot name displayed in the viewport over the cameras" "\n(Add-on preference)",
        min=8,
        soft_max=26,
        max=180,
        default=12,
    )

    cameraHUD_settings_expanded: BoolProperty(
        name="Expand Panel Settings",
        default=False,
    )

    ###################################
    # frame range tool ################
    ###################################

    def _update_display_frame_range_tool(self, context):
        # print("\n*** _update_display_frame_range_tool. New state: ", self.display_frame_range_tool)
        display_frame_range_in_editor(self.display_frame_range_tool)

    display_frame_range_tool: BoolProperty(
        name="Frame Time Range",
        description="Easy get and set the time range from the Timeline editor."
        "\nA tool from Ubisoft Shot Manager"
        "\n\n(saved in the add-on preferences)",
        update=_update_display_frame_range_tool,
        default=True,
    )

    ###################################
    # markers nav bar tool ############
    ###################################

    def _update_display_markersNavBar_tool(self, context):
        # print("\n*** _update_display_markersNavBar_tool. New state: ", self.display_frame_range_tool)
        display_markersNavBar_in_editor(self.display_markersNavBar_tool)

    display_markersNavBar_tool: BoolProperty(
        name="Markers Nav Bar",
        description="Jump from marker to marker, filter them for faster navigation."
        "\nA tool from Ubisoft Shot Manager"
        "\n\n(saved in the add-on preferences)",
        update=_update_display_markersNavBar_tool,
        default=False,
    )

    mnavbar_settings_expanded: BoolProperty(
        name="Expand Panel Settings",
        default=False,
    )

    mnavbar_display_in_timeline: BoolProperty(
        name="Display in Timeline",
        description="Display Markers Nav Bar in the Timeline toolbar",
        default=False,
    )
    mnavbar_display_in_dopesheet: BoolProperty(
        name="Display in Dopesheet",
        description="Display Markers Nav Bar in the Dopesheet toolbar",
        default=False,
    )
    mnavbar_display_in_vse: BoolProperty(
        name="Display in VSE",
        description="Display Markers Nav Bar in the VSE toolbar",
        default=True,
    )
    mnavbar_display_addRename: BoolProperty(
        name="Display Add and Rename",
        description="Display buttons for Add and Rename markers",
        default=True,
    )
    mnavbar_display_filter: BoolProperty(
        name="Display Filter",
        description="Display the filter tools",
        default=True,
    )

    # Markers Nav Bar component controls ###

    markerEmptyField: StringProperty(name=" ")

    mnavbar_use_filter: BoolProperty(
        name="Filter Markers",
        default=False,
    )

    mnavbar_filter_text: StringProperty(
        name="Filter Text",
        default="",
    )

    # TOFIX: replace ops by functions
    def _update_mnavbar_use_view_frame(self, context):
        if self.mnavbar_use_view_frame:
            # timeline
            try:
                bpy.ops.action.view_frame()
            except Exception as e:
                _logger.debug_ext(f"Exception in _update_mnavbar_use_view_frame. e: {e}")
            # vse
            try:
                bpy.ops.sequencer.view_frame()
            except Exception as e:
                _logger.debug_ext(f"Exception in _update_mnavbar_use_view_frame. e: {e}")

    mnavbar_use_view_frame: BoolProperty(
        name="View Frame",
        default=True,
        update=_update_mnavbar_use_view_frame,
    )

    ########################################################################
    # stamp info ###
    ########################################################################

    stampInfo_separatedPanel: BoolProperty(
        name="Separated Stamp Info Panel",
        description=(
            "If checked, the Stamp Info panels will be a tab separated from Shot Manager panel."
            "\nIn not, then these panels will be displayed in the Render panel"
        ),
        default=False,
    )

    stampInfo_display_properties: BoolProperty(
        name="Display Panel",
        description="Display the Stamp Info properties panel in the tab list in the 3D View",
        default=False,
    )

    write_still: BoolProperty(
        name="Write rendered still images on disk",
        description="If checked then writes rendered still images on disk.\n"
        "If not checked (most common approach) then the images are written with a name starting with '_Still_' in order to prevent modification on a single frame"
        "in an already rendered image sequences",
        default=False,
        options=set(),
    )

    delete_temp_scene: BoolProperty(
        name="Delete the temporary scene used for VSE rendering",
        description="Delete temporary scene used for VSE rendering",
        default=True,
        options=set(),
    )

    delete_temp_images: BoolProperty(
        name="Delete the temporary images used for VSE rendering",
        description="Delete temporary images used for VSE rendering",
        default=True,
        options=set(),
    )

    # -----------------------------------------------------------
    # UI user preferences - Not exposed
    # -----------------------------------------------------------
    stampInfo_mode_expanded: BoolProperty(
        name="Expand Render Mode Properties",
        default=True,
    )

    stampInfo_mainPanel_expanded: BoolProperty(
        name="Expand Panel",
        default=True,
    )
    stampInfo_timePanel_expanded: BoolProperty(
        name="Expand Panel",
        default=False,
    )
    stampInfo_shotPanel_expanded: BoolProperty(
        name="Expand Panel",
        default=False,
    )
    stampInfo_metadataPanel_expanded: BoolProperty(
        name="Expand Panel",
        default=False,
    )
    stampInfo_layoutPanel_expanded: BoolProperty(
        name="Expand Panel",
        default=False,
    )
    stampInfo_settingsPanel_expanded: BoolProperty(
        name="Expand Panel",
        default=False,
    )

    ########################################################################
    # tools ui   ###
    ########################################################################

    toggleShotsEnabledState: BoolProperty(name=" ", default=False)

    ##################
    # shots features #
    ##################
    toggleCamsBG: BoolProperty(name=" ", default=False)
    toggleCamsSoundBG: BoolProperty(name=" ", default=False)
    enableGreasePencil: BoolProperty(name=" ", default=False)

    # -----------------------------------------------------------
    # ui helpers - Not exposed
    # -----------------------------------------------------------
    # used for example as a placehoder in VSM to have a text field when no strip is selected
    emptyField: StringProperty(name=" ")
    emptyBool: BoolProperty(name=" ", default=False)

    def _get_projectSeqName(self):
        # print(" get_projectSeqName")
        # val = self.get("projectSeqName", "-")
        props = config.getAddonProps(bpy.context.scene)
        val = props.getSequenceName("FULL")
        return val

    def _set_projectSeqName(self, value):
        #  print(" set_projectSeqName: value: ", value)
        props = config.getAddonProps(bpy.context.scene)
        val = props.getSequenceName("FULL")
        self["projectSeqName"] = val

    def _update_projectSeqName(self, context):
        # update the main UI when the value is changed
        for region in context.area.regions:
            if region.type == "UI":
                region.tag_redraw()
        return None

    projectSeqName: StringProperty(
        name="(read-only)",
        description="Shot name of the current sequence, as defined by the project settings",
        get=_get_projectSeqName,
        set=_set_projectSeqName,
        update=_update_projectSeqName,
        default="",
    )

    ##################
    # Overlays - Not exposed in the prefs
    ##################

    # overlay ########
    ##################
    def _get_overlays_toggleoverlays_ui(self):
        val = getOverlaysPropertyState(bpy.context, "show_overlays")
        return val

    def _set_overlays_toggleoverlays_ui(self, value):
        self["overlays_toggleoverlays_ui"] = value

    def _update_overlays_toggleoverlays_ui(self, context):
        props = config.getAddonProps(context.scene)
        applyToAllViewports = "ALL" == props.shotsGlobalSettings.stb_overlaysViewportMode
        bpy.ops.uas_shot_manager.overlays_toggleoverlays(
            allViewports=applyToAllViewports, newState=not self.overlays_toggleoverlays_ui
        )

    # ui property used only as a visual component to display a checkbox for an operator
    overlays_toggleoverlays_ui: BoolProperty(
        name="Shot Overlays",
        description="Display overlayes like gizmos and outlines",
        get=_get_overlays_toggleoverlays_ui,
        set=_set_overlays_toggleoverlays_ui,
        update=_update_overlays_toggleoverlays_ui,
        default=True,
    )

    # onion skin #####
    ##################
    def _get_overlays_toggleonionskin_ui(self):
        val = getOverlaysPropertyState(bpy.context, "use_gpencil_onion_skin")
        return val

    def _set_overlays_toggleonionskin_ui(self, value):
        self["overlays_toggleonionskin_ui"] = value

    def _update_overlays_toggleonionskin_ui(self, context):
        props = config.getAddonProps(context.scene)
        applyToAllViewports = "ALL" == props.shotsGlobalSettings.stb_overlaysViewportMode
        bpy.ops.uas_shot_manager.overlays_toggleonionskin(
            allViewports=applyToAllViewports, newState=not self.overlays_toggleonionskin_ui
        )

    # ui property used only as a visual component to display a checkbox for an operator
    overlays_toggleonionskin_ui: BoolProperty(
        name="Onion Skin",
        description="Show ghosts of the keyframes before and after the current keyframe",
        get=_get_overlays_toggleonionskin_ui,
        set=_set_overlays_toggleonionskin_ui,
        update=_update_overlays_toggleonionskin_ui,
        default=True,
    )

    # grid ###########
    ##################
    def _get_overlays_togglegrid_ui(self):
        val = getOverlaysPropertyState(bpy.context, "use_gpencil_grid")
        return val

    def _set_overlays_togglegrid_ui(self, value):
        self["overlays_togglegrid_ui"] = value

    def _update_overlays_togglegrid_ui(self, context):
        props = config.getAddonProps(context.scene)
        applyToAllViewports = "ALL" == props.shotsGlobalSettings.stb_overlaysViewportMode
        bpy.ops.uas_shot_manager.overlays_togglegrid(
            allViewports=applyToAllViewports, newState=not self.overlays_togglegrid_ui
        )

    # ui property used only as a visual component to display a checkbox for an operator
    overlays_togglegrid_ui: BoolProperty(
        name="Use Grid",
        description="Display a grid over Grease Pencil paper",
        get=_get_overlays_togglegrid_ui,
        set=_set_overlays_togglegrid_ui,
        update=_update_overlays_togglegrid_ui,
        default=True,
    )

    def _get_stb_overlay_grid_opacity(self):
        props = config.getAddonProps(bpy.context.scene)
        spaceDataViewport = props.getValidTargetViewportSpaceData(bpy.context)
        if spaceDataViewport is not None:
            val = spaceDataViewport.overlay.gpencil_grid_opacity
        else:
            val = 1.0
        return val

    def _set_stb_overlay_grid_opacity(self, value):
        self["stb_overlay_grid_opacity"] = value

    def _update_stb_overlay_grid_opacity(self, context):
        props = config.getAddonProps(context.scene)
        applyToAllViewports = "ALL" == props.shotsGlobalSettings.stb_overlaysViewportMode
        bpy.ops.uas_shot_manager.overlays_gridopacity(
            allViewports=applyToAllViewports, opacity=self["stb_overlay_grid_opacity"]
        )
        # spaceDataViewport = props.getValidTargetViewportSpaceData(context)
        # if spaceDataViewport is not None:
        #     # spaceDataViewport.overlay.gpencil_fade_layer = utils.value_to_linear(self["stb_overlay_grid_opacity"])
        #     spaceDataViewport.overlay.gpencil_grid_opacity = self["stb_overlay_grid_opacity"]

    stb_overlay_grid_opacity: FloatProperty(
        name="Grid Opacity",
        description="Opacity of the Grease Pencil grid (also called Canvas) in the viewport overlay",
        min=0.1,
        max=1.0,
        step=0.01,
        precision=2,
        get=_get_stb_overlay_grid_opacity,
        set=_set_stb_overlay_grid_opacity,
        update=_update_stb_overlay_grid_opacity,
        default=1.0,
        options=set(),
    )

    def _get_overlays_togglegridtofront_ui(self):
        val = getOverlaysPropertyState(bpy.context, "use_gpencil_canvas_xray")
        return val

    def _set_overlays_togglegridtofront_ui(self, value):
        self["use_gpencil_canvas_xray"] = value

    def _update_overlays_togglegridtofront_ui(self, context):
        props = config.getAddonProps(context.scene)
        applyToAllViewports = "ALL" == props.shotsGlobalSettings.stb_overlaysViewportMode
        bpy.ops.uas_shot_manager.overlays_togglegridtofront(
            allViewports=applyToAllViewports, newState=not self.overlays_togglegridtofront_ui
        )

    # ui property used only as a visual component to display a checkbox for an operator
    overlays_togglegridtofront_ui: BoolProperty(
        name="Canvas X-Ray",
        description="Toggle canvas grid between front and back for the specifed viewports",
        get=_get_overlays_togglegridtofront_ui,
        set=_set_overlays_togglegridtofront_ui,
        update=_update_overlays_togglegridtofront_ui,
        default=True,
    )

    # fade layers ####
    ##################
    def _get_overlays_togglefadelayers_ui(self):
        val = getOverlaysPropertyState(bpy.context, "use_gpencil_fade_layers")
        return val

    def _set_overlays_togglefadelayers_ui(self, value):
        self["overlays_togglefadelayers_ui"] = value

    def _update_overlays_togglefadelayers_ui(self, context):
        props = config.getAddonProps(context.scene)
        applyToAllViewports = "ALL" == props.shotsGlobalSettings.stb_overlaysViewportMode
        bpy.ops.uas_shot_manager.overlays_togglefadelayers(
            allViewports=applyToAllViewports, newState=not self.overlays_togglefadelayers_ui
        )

    # ui property used only as a visual component to display a checkbox for an operator
    overlays_togglefadelayers_ui: BoolProperty(
        name="Fade Layers",
        description="Toggle fading of Greazse Pencil layers except the active one",
        get=_get_overlays_togglefadelayers_ui,
        set=_set_overlays_togglefadelayers_ui,
        update=_update_overlays_togglefadelayers_ui,
        default=True,
    )

    def _get_stb_overlay_layers_opacity(self):
        props = config.getAddonProps(bpy.context.scene)
        spaceDataViewport = props.getValidTargetViewportSpaceData(bpy.context)
        if spaceDataViewport is not None:
            val = spaceDataViewport.overlay.gpencil_fade_layer
        else:
            val = 1.0
        return val

    def _set_stb_overlay_layers_opacity(self, value):
        self["stb_overlay_layers_opacity"] = value

    def _update_stb_overlay_layers_opacity(self, context):
        props = config.getAddonProps(context.scene)
        applyToAllViewports = "ALL" == props.shotsGlobalSettings.stb_overlaysViewportMode
        # spaceDataViewport = props.getValidTargetViewportSpaceData(context)
        # if spaceDataViewport is not None:
        #     # spaceDataViewport.overlay.gpencil_fade_layer = utils.value_to_linear(self["stb_overlay_layers_opacity"])
        #     spaceDataViewport.overlay.gpencil_fade_layer = self["stb_overlay_layers_opacity"]
        bpy.ops.uas_shot_manager.overlays_fadelayersopacity(
            allViewports=applyToAllViewports, opacity=self["stb_overlay_layers_opacity"]
        )

    stb_overlay_layers_opacity: FloatProperty(
        name="Layers Opacity",
        description="Opacity of the Grease Pencil layers in the viewport overlay",
        min=0.0,
        max=1.0,
        step=0.01,
        precision=2,
        get=_get_stb_overlay_layers_opacity,
        set=_set_stb_overlay_layers_opacity,
        update=_update_stb_overlay_layers_opacity,
        default=1.0,
        options=set(),
    )

    ##################
    # dialog boxes
    ##################

    # -----------------------------------------------------------
    # add new shot  - Not exposed
    # -----------------------------------------------------------

    def _get_addShot_start(self):
        val = self.get("addShot_start", 25)
        return val

    # *** behavior here must match the one of start and end of shot properties ***
    def _set_addShot_start(self, value):
        self["addShot_start"] = value
        # increase end value if start is superior to end
        # if self.addShot_start > self.addShot_end:
        #     self["addShot_end"] = self.addShot_start

        # prevent start to go above end (more user error proof)
        if self.addShot_start > self.addShot_end:
            self["addShot_start"] = self.addShot_end

    addShot_start: IntProperty(
        name="New Shot Start",
        description="Value of the first included frame of the shot",
        soft_min=0,
        get=_get_addShot_start,
        set=_set_addShot_start,
        default=25,
    )

    def _get_addShot_end(self):
        val = self.get("addShot_end", 30)
        return val

    # *** behavior here must match the one of start and end of shot properties ***
    def _set_addShot_end(self, value):
        self["addShot_end"] = value
        # reduce start value if end is lowr than start
        # if self.addShot_start > self.addShot_end:
        #    self["addShot_start"] = self.addShot_end

        # prevent end to go below start (more user error proof)
        if self.addShot_start > self.addShot_end:
            self["addShot_end"] = self.addShot_start

    addShot_end: IntProperty(
        name="New Shot End",
        description="Value of the last included frame of the shot",
        soft_min=0,
        get=_get_addShot_end,
        set=_set_addShot_end,
        default=50,
    )

    ##################
    # remove shot ###
    ##################
    removeShot_deleteCameras: BoolProperty(
        name="Delete Shots Cameras",
        description="Store the user preference regarding the camera deletion",
        default=False,
    )

    ##################
    # global temps values   ###
    ##################

    ####################
    # playblast
    ####################

    playblastFileName: StringProperty(name="Temporary Playblast File", default="toto.mp4")

    playblastImagesOutputFormat: EnumProperty(
        name="Playblast Image Output Format",
        description="File format for the rendered output images of the playblast, BEFORE composition with the Stamp Info framing images"
        "\nExpected values: JPEG, PNG",
        items=(
            ("JPEG", "JPEG", ""),
            ("PNG", "PNG", ""),
        ),
        default="JPEG",
    )

    ##################
    # markers ###
    ##################

    mnavbar_use_filter: BoolProperty(
        name="Filter Markers",
        default=False,
    )

    mnavbar_filter_text: StringProperty(
        name="Filter Text",
        default="",
    )

    ##################################################################################
    # draw
    ##################################################################################
    def draw(self, context):
        draw_addon_prefs(self, context)

    ##################################################################################
    # key mapping
    ##################################################################################

    def _update_kmap_shots_nav_invert_direction(self, context):
        playbar_keymaps.unregisterKeymaps()
        playbar_keymaps.registerKeymaps()

    kmap_shots_nav_invert_direction: BoolProperty(
        name="Invert Shots Navigation Direction",
        description=(
            "Invert Up and Down arrows to navigate between shots boundaries."
            "\nBy default Up goes to Next shots and Down to Previous shots"
        ),
        update=_update_kmap_shots_nav_invert_direction,
        default=False,
    )


_classes = (UAS_ShotManager_AddonPrefs,)


def register():
    _logger.debug_ext("       - Registering Add-on Preferences", form="REG")

    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    _logger.debug_ext("       - Unregistering Add-on Preferences", form="UNREG")

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
