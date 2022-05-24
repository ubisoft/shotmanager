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

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty

# from ..config import config

from .addon_prefs_ui import draw_addon_prefs

from shotmanager.features.greasepencil.greasepencil_frame_template import UAS_GreasePencil_FrameTemplate
from shotmanager.utils import utils
from shotmanager.utils.utils_os import get_latest_release_version

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
    prefs = context.preferences.addons["shotmanager"].preferences
    """

    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package
    bl_idname = "shotmanager"

    install_failed: BoolProperty(
        name="Install failed",
        default=False,
    )

    def version(self):
        """Return the add-on version in the form of a tupple made by:
            - a string x.y.z (eg: "1.21.3")
            - an integer. x.y.z becomes xxyyyzzz (eg: "1.21.3" becomes 1021003)
        Return None if the addon has not been found
        """
        return utils.addonVersion("Shot Manager")

    newAvailableVersion: IntProperty(
        description="Store the version of the latest release of the add-on as an integer if there is an online release"
        "\nthat is more recent than this version. If there is none then the value is 0",
        # default=2005001,
        default=1007016,
    )

    isInitialized: BoolProperty(
        default=False,
    )

    def initialize_shot_manager_prefs(self):
        print("\nInitializing Shot Manager Preferences...")

        self.stb_frameTemplate.initialize(mode="ADDON_PREFS")

        versionStr = get_latest_release_version(
            "https://github.com/ubisoft/shotmanager/releases/latest", verbose=True, use_debug=True
        )

        if versionStr is not None:
            # version string from the tags used by our releases on GitHub is formated as this: v<int>.<int>.<int>
            version = utils.convertVersionStrToInt(versionStr)

            _logger.debug_ext(
                f"Checking for updates: Latest version of Ubisoft Shot Manager online is: {versionStr}", col="BLUE"
            )
            if self.version()[1] < version:
                _logger.debug_ext("   New version available online...", col="BLUE")
                self.newAvailableVersion = version
            else:
                self.newAvailableVersion = 0
        else:
            self.newAvailableVersion = 0

        self.isInitialized = True

    ########################################################################
    # general ###
    ########################################################################

    # ****** settings exposed to the user in the prefs panel:
    # ------------------------------

    output_first_frame: IntProperty(
        name="Output First Frame Index",
        description="Index of the first frame for rendered image sequences and videos."
        "\nThis is 0 in most editing applications, sometimes 1."
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
            prefs = bpy.context.preferences.addons["shotmanager"].preferences
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

    # storyboard panel
    ####################
    stb_canvas_props_expanded: BoolProperty(
        name="Expand Canvas Properties",
        default=False,
    )

    stb_anim_props_expanded: BoolProperty(
        name="Expand Animation Properties",
        default=False,
    )

    def _get_stb_overlay_layers_opacity(self):
        # print(" get_projectSeqName")
        props = bpy.context.scene.UAS_shot_manager_props
        spaceDataViewport = props.getValidTargetViewportSpaceData(bpy.context)
        if spaceDataViewport is not None:
            val = spaceDataViewport.overlay.gpencil_fade_layer
        else:
            val = 1.0
        return val

    def _set_stb_overlay_layers_opacity(self, value):
        #  print(" set_projectSeqName: value: ", value)
        self["stb_overlay_layers_opacity"] = value

    def _update_stb_overlay_layers_opacity(self, context):
        # print("stb_overlay_layers_opacity")
        props = context.scene.UAS_shot_manager_props
        spaceDataViewport = props.getValidTargetViewportSpaceData(context)
        if spaceDataViewport is not None:
            spaceDataViewport.overlay.gpencil_fade_layer = utils.to_sRGB(self["stb_overlay_layers_opacity"])

    stb_overlay_layers_opacity: FloatProperty(
        name="Layers Opacity",
        description="Opacity of the Grease Pencil layers in the viewport overlay",
        min=0.0,
        max=1.0,
        step=0.1,
        get=_get_stb_overlay_layers_opacity,
        set=_set_stb_overlay_layers_opacity,
        update=_update_stb_overlay_layers_opacity,
        default=1.0,
        options=set(),
    )

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
            props = bpy.context.scene.UAS_shot_manager_props
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
    #     props = context.scene.UAS_shot_manager_props
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
    addonPrefs_features_expanded: BoolProperty(
        name="Expand Features Preferences",
        default=False,
    )
    addonPrefs_tools_expanded: BoolProperty(
        name="Expand Tools Preferences",
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
    current_shot_changes_time_zoom: BoolProperty(
        name="Zoom Timeline to Shot Range",
        description="Automatically zoom the timeline content to frame the shot when the current shot is changed.\n(Add-on preference)",
        default=False,
    )

    playblastFileName: StringProperty(name="Temporary Playblast File", default="toto.mp4")

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

    def _update_layout_mode(self, context):
        #   print("\n*** Prefs _update_layout_mode updated. New state: ", self._update_layout_mode)
        # self.layout_but_storyboard = "STORYBOARD" == self.layout_mode
        # self.layout_but_previz = "PREVIZ" == self.layout_mode
        if "STORYBOARD" == self.layout_mode:
            self.display_storyboard_in_properties = True
            self.display_notes_in_properties = True
            self.display_greasepenciltools_in_properties = True
        else:
            self.display_storyboard_in_properties = False
            self.display_notes_in_properties = False
            self.display_greasepenciltools_in_properties = False
        pass

    layout_mode: EnumProperty(
        name="Layout Mode",
        description="Defines if Shot Manager panel should be appropriate for storyboarding or for previz",
        items=(
            ("STORYBOARD", "Storyboard", "Storyboard layout"),
            ("PREVIZ", "Previz", "Previz layout"),
        ),
        update=_update_layout_mode,
        default="PREVIZ",
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
    # features to display by default   ###
    ########################################################################

    display_storyboard_in_properties: BoolProperty(
        name="Storyboard Frames and Grease Pencil Tools",
        description="Display the storyboard frames properties and tools in the Shot properties panel."
        "\nA storyboard frame is a Grease Pencil drawing surface associated to the camera of each shot",
        default=True,
    )

    display_notes_in_properties: BoolProperty(
        name="Takes and Shots Notes",
        description="Display the takes and shots notes in the Shot Properties panels",
        default=False,
    )

    display_cameraBG_in_properties: BoolProperty(
        name="Camera Background Tools",
        description="Display the camera background image tools and controls in the Shot Properties panel",
        default=False,
    )

    display_takerendersettings_in_properties: BoolProperty(
        name="Take Render Settings",
        description="Display the take render settings in the Take Properties panel."
        "\nThese options allow each take to be rendered with its own output resolution",
        default=False,
    )

    display_editmode_in_properties: BoolProperty(
        name="Display Global Edit Integration Tools",
        description="Display the advanced properties of the takes used to specify their position in a global edit",
        default=False,
    )

    display_globaleditintegr_in_properties: BoolProperty(
        name="Display Global Edit Integration Tools",
        description="Display the advanced properties of the takes used to specify their position in a global edit",
        default=False,
    )

    display_advanced_infos: BoolProperty(
        name="Display Advanced Infos",
        description="Display technical information and feedback in the UI",
        default=False,
    )

    ########################################################################
    # grease pencil tools ui   ###
    ########################################################################

    # ****** settings exposed to the user in the prefs panel:
    # ------------------------------

    display_greasepenciltools_in_properties: BoolProperty(
        name="Display 2.5d Grease Pencil",
        description="Display the 2.5D Grease Pencil sub-panel in the Shot Manager panel.\n(saved in the add-on preferences)",
        default=True,
    )

    ########################################################################
    # rendering ui   ###
    ########################################################################

    # ****** settings exposed to the user in the prefs panel:
    # ------------------------------

    display_render_in_properties: BoolProperty(
        name="Display Renderer",
        description="Display the Render sub-panel in the Shot Manager panel.\n(saved in the add-on preferences)",
        default=True,
    )

    separatedRenderPanel: BoolProperty(
        name="Separated Render Panel",
        description="If checked, the render panel will be a tab separated from Shot Manager panel",
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
    ### Overlay tools
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
        default=False,
        options=set(),
    )

    ### Retimer
    display_retimer_in_properties: BoolProperty(
        name="Display Retimer",
        description="Display the Retimer sub-panel in the Shot Manager panel.\n(saved in the add-on preferences)",
        default=False,
    )
    applyToTimeCursor: BoolProperty(
        name="Apply to Time Cursor",
        description="Apply retime operation to the time cursor.\n(saved in the add-on preferences)",
        default=True,
    )
    applyToSceneRange: BoolProperty(
        name="Apply to Scene Range",
        description="Apply retime operation to the animation start and end of the scene.\n(saved in the add-on preferences)",
        default=True,
    )

    ########################################################################
    # additional tools ###
    ########################################################################

    ###################################
    # Sequence Timeline ###############
    ###################################

    # displayed when toggle overlays button is on
    def _update_toggle_overlays_turnOn_sequenceTimeline(self, context):
        _logger.debug_ext("_update_toggle_overlays_turnOn_sequenceTimeline")

        ## toggle on or off the overlay tools mode
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
    # Interactive Shots Stack #########
    ###################################

    # displayed when toggle overlays button is on
    def _update_toggle_overlays_turnOn_interactiveShotsStack(self, context):
        _logger.debug_ext("_update_toggle_overlays_turnOn_interactiveShotsStack")

        ## toggle on or off the overlay tools mode
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

    intShStack_settings_expanded: BoolProperty(
        name="Expand Panel Settings",
        default=False,
    )

    def _update_display_intShStack_toolbar(self, context):
        # print("\n*** _update_display_frame_range_tool. New state: ", self.display_frame_range_tool)
        from shotmanager.overlay_tools.interact_shots_stack.shots_stack_toolbar import (
            display_shots_stack_toolbar_in_editor,
        )

        display_shots_stack_toolbar_in_editor(self.display_intShStack_toolbar)

    display_intShStack_toolbar: BoolProperty(
        name="Display Interactive Shots Stack Toolbar",
        description="Display Interactive Shots Stack toolbar in the Timeline editor",
        update=_update_display_intShStack_toolbar,
        default=True,
    )

    ###################################
    # Camera HUD ######################
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
    # Frame Range #####################
    ###################################
    def _update_display_frame_range_tool(self, context):
        # print("\n*** _update_display_frame_range_tool. New state: ", self.display_frame_range_tool)
        from shotmanager.tools.frame_range.frame_range_operators import display_frame_range_in_editor

        display_frame_range_in_editor(self.display_frame_range_tool)

    display_frame_range_tool: BoolProperty(
        name="Frame Time Range",
        description="Easily get and set the time range from the Timeline editor.\nA tool from Ubisoft Shot Manager",
        update=_update_display_frame_range_tool,
        default=True,
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

    ##################
    # ui helpers   ###
    ##################

    # used for example as a placehoder in VSM to have a text field when no strip is selected
    emptyField: StringProperty(name=" ")
    emptyBool: BoolProperty(name=" ", default=False)

    def _get_projectSeqName(self):
        # print(" get_projectSeqName")
        # val = self.get("projectSeqName", "-")
        props = bpy.context.scene.UAS_shot_manager_props
        val = props.getSequenceName("FULL")
        return val

    def _set_projectSeqName(self, value):
        #  print(" set_projectSeqName: value: ", value)
        props = bpy.context.scene.UAS_shot_manager_props
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
    # add new shot ###
    ##################

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
    # global temps values   ###
    ##################

    # Playblast
    ####################

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
    # Draw
    ##################################################################################
    def draw(self, context):
        draw_addon_prefs(self, context)


_classes = (UAS_ShotManager_AddonPrefs,)


def register():
    _logger.debug_ext("       - Registering Add-on Preferences", form="REG")

    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    _logger.debug_ext("       - Unregistering Add-on Preferences", form="UNREG")

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
