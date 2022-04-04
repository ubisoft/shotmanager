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
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty

# from ..config import config

from .addon_prefs_ui import draw_shotmanager_addon_prefs

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


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
        subtype="TIME",
        default=0,
    )

    img_name_digits_padding: IntProperty(
        name="Image Name Digit Padding",
        description="Number of digits to use for the index of an output image in its name."
        "\nIf the Project Settings are active then the value provided there is used instead",
        min=1,
        default=5,
    )

    new_shot_duration: IntProperty(
        name="Default Shot Duration",
        description="Default duration for new shots, in frames",
        min=0,
        subtype="TIME",
        default=50,
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
        default=True,
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
    toggleGreasePencil: BoolProperty(name=" ", default=False)

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
        draw_shotmanager_addon_prefs(self, context)


_classes = (UAS_ShotManager_AddonPrefs,)


def register():
    _logger.debug_ext("       - Registering Add-on Preferences", form="REG")

    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    _logger.debug_ext("       - Unregistering Add-on Preferences", form="UNREG")

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
