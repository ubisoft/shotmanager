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
Layout settings: UI parameters to store the Storyboard and the Previz layout
"""

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty, StringProperty

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_LayoutSettings(PropertyGroup):
    """Store the information to display the specified layout, either Storyboard or Previz"""

    name: StringProperty(name="Name", default="Layout Settings")

    layoutMode: EnumProperty(
        name="Layout Mode",
        description="Layout Mode",
        items=(
            ("STORYBOARD", "Storyboard", ""),
            ("PREVIZ", "Previz", ""),
        ),
        default="PREVIZ",
    )

    # selected_shot_changes_current_shot: BoolProperty(
    #     name="Set selected shot to current",
    #     description="When a shot is selected in the shot list, the shot is also set to be the current one",
    #     default=False,
    # )
    # selected_shot_in_shots_stack_changes_current_shot: BoolProperty(
    #     name="Set selected shot in Shots Stack to current",
    #     description="When a shot is selected in the Interactive Shots Stack, the shot is also set to be the current one",
    #     default=False,
    # )

    # current_shot_changes_time_zoom: BoolProperty(
    #     name="Zoom Timeline to Shot Range",
    #     description="Automatically zoom the timeline content to frame the shot when the current shot is changed",
    #     default=False,
    # )

    display_storyboard_in_properties: BoolProperty(
        name="Storyboard Frames and Grease Pencil Tools",
        description="Display the storyboard frames properties and tools in the Shot properties panel."
        "\nA storyboard frame is a Grease Pencil drawing surface associated to the camera of each shot",
        default=False,
        options=set(),
    )

    display_notes_in_properties: BoolProperty(
        # name="Display Shot Notes in Shot Properties",
        description="Display shot notes in the Shot Properties panels",
        default=False,
        options=set(),
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

    display_advanced_infos: BoolProperty(
        name="Display Advanced Infos",
        description="Display technical information and feedback in the UI",
        default=False,
        options=set(),
    )

    def initialize(self, layoutMode):
        """
        Args:
            layoutMode: the layout mode of the settings. Can be STORYBOARD, PREVIZ
        """
        _logger.debug_ext(f"initialize Layout Settings {layoutMode}", col="GREEN")

        prefs = config.getAddonPrefs()

        # common values

        # storyboard
        if "STORYBOARD" == layoutMode:
            self.name = "Storyboard"
            self.layoutMode = "STORYBOARD"

            # self.selected_shot_changes_current_shot = prefs.stb_selected_shot_changes_current_shot
            # self.selected_shot_in_shots_stack_changes_current_shot = (
            #     prefs.stb_selected_shot_in_shots_stack_changes_current_shot
            # )
            # self.current_shot_changes_time_zoom = prefs.stb_current_shot_changes_time_zoom
            self.display_storyboard_in_properties = prefs.stb_display_storyboard_in_properties
            self.display_notes_in_properties = prefs.stb_display_notes_in_properties
            self.display_cameraBG_in_properties = prefs.stb_display_cameraBG_in_properties
            self.display_takerendersettings_in_properties = prefs.stb_display_takerendersettings_in_properties
            self.display_editmode_in_properties = prefs.stb_display_editmode_in_properties
            self.display_globaleditintegr_in_properties = prefs.stb_display_globaleditintegr_in_properties
            self.display_advanced_infos = prefs.stb_display_advanced_infos

        # previz
        if "PREVIZ" == layoutMode:
            self.name = "Previz"
            self.layoutMode = "PREVIZ"

            # self.selected_shot_changes_current_shot = prefs.pvz_selected_shot_changes_current_shot
            # self.selected_shot_in_shots_stack_changes_current_shot = (
            #     prefs.pvz_selected_shot_in_shots_stack_changes_current_shot
            # )
            # self.current_shot_changes_time_zoom = prefs.pvz_current_shot_changes_time_zoom
            self.display_storyboard_in_properties = prefs.pvz_display_storyboard_in_properties
            self.display_notes_in_properties = prefs.pvz_display_notes_in_properties
            self.display_cameraBG_in_properties = prefs.pvz_display_cameraBG_in_properties
            self.display_takerendersettings_in_properties = prefs.pvz_display_takerendersettings_in_properties
            self.display_editmode_in_properties = prefs.pvz_display_editmode_in_properties
            self.display_globaleditintegr_in_properties = prefs.pvz_display_globaleditintegr_in_properties
            self.display_advanced_infos = prefs.pvz_display_advanced_infos

    # def updateUI(self, props):
    #     props.getCurrentLayout().display_storyboard_in_properties = prefs.display_storyboard_in_properties
    #     self.display_notes_in_properties = prefs.display_notes_in_properties
    #     self.display_cameraBG_in_properties = prefs.display_cameraBG_in_properties
    #     self.display_takerendersettings_in_properties = prefs.display_takerendersettings_in_properties
    #     self.display_editmode_in_properties = prefs.display_editmode_in_properties
    #     self.display_globaleditintegr_in_properties = prefs.display_globaleditintegr_in_properties
    #     self.display_advanced_infos = prefs.display_advanced_infos
