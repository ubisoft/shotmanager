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
UI for the Add-on Preferences
"""

from shotmanager.config import config
from shotmanager.ui.dependencies_ui import drawDependencies
from shotmanager.utils.utils_ui import collapsable_panel

from shotmanager.prefs.features import draw_features_prefs

##################################################################################
# Draw
##################################################################################


def draw_shotmanager_addon_prefs(self, context):
    layout = self.layout
    layout = layout.column(align=False)
    # prefs = context.preferences.addons["shotmanager"].preferences

    # Dependencies
    ###############
    drawDependencies(context, layout)

    # Features
    ###############
    drawFeatures(context, self, layout)

    # Settings
    ###############
    drawSettings(context, self, layout)

    # General UI
    ###############
    drawGeneralUI(context, self, layout)

    # Tools
    ###############
    # box = layout.box()
    # collapsable_panel(box, self, "addonPrefs_tools_expanded", text="Tools")
    # if self.addonPrefs_tools_expanded:
    #     uiSplitFactor = 0.15

    #     # column component here is technicaly not necessary but reduces the space between lines
    #     col = box.column()

    #     split = col.split(factor=uiSplitFactor)
    #     rowLeft = split.row()
    #     rowRight = split.row()
    #     rowRight.prop(self, "display_frame_range_tool", text="Display Frame Range Tool in the Timeline Editor")

    # Dev and debug
    ###############
    drawDevAndDebug(context, self, layout)


##################################################################
# Draw functions
##################################################################


def drawSettings(context, prefs, layout):
    box = layout.box()
    collapsable_panel(box, prefs, "addonPrefs_settings_expanded", text="Settings")
    if prefs.addonPrefs_settings_expanded:
        settingsSplitFactor = 0.5
        col = box.column(align=False)

        row = col.row()
        split = row.split(factor=settingsSplitFactor)
        rowLeft = split.row()
        rowLeft.alignment = "RIGHT"
        rowLeft.label(text="Output First Frame Index")
        rowRight = split.row()
        rowRight.prop(prefs, "output_first_frame", text="Start Frame")

        row = col.row()
        split = row.split(factor=settingsSplitFactor)
        rowLeft = split.row()
        rowLeft.alignment = "RIGHT"
        rowLeft.label(text="Image Name Digit Padding")
        rowRight = split.row()
        rowRight.prop(prefs, "img_name_digits_padding", text="Padding")

        row = col.row()
        split = row.split(factor=settingsSplitFactor)
        rowLeft = split.row()
        rowLeft.alignment = "RIGHT"
        rowLeft.label(text="Default Shot Duration")
        rowRight = split.row()
        rowRight.prop(prefs, "new_shot_duration", text="Frames")

        # Storyboard
        ################
        # sepRow = col.row()
        # sepRow.separator(factor=1.0)

        row = col.row()
        row.label(text="Storyboard:")

        row = col.row()
        split = row.split(factor=settingsSplitFactor)
        rowLeft = split.row()
        rowLeft.alignment = "RIGHT"
        rowLeft.label(text="Default Canvas Opacity")
        rowRight = split.row()
        rowRight.prop(prefs, "storyboard_default_canvasOpacity", slider=True, text="Opacity")

        row = col.row()
        split = row.split(factor=settingsSplitFactor)
        rowLeft = split.row()
        rowLeft.alignment = "RIGHT"
        rowLeft.label(text="Default Distance to Camera")
        rowRight = split.row()
        rowRight.prop(prefs, "storyboard_default_distanceFromOrigin", slider=True, text="Distance")

        row = col.row()
        split = row.split(factor=settingsSplitFactor)
        rowLeft = split.row()
        rowLeft.alignment = "RIGHT"
        rowLeft.label(text="Frame Default Start Time")
        rowRight = split.row()
        rowRight.prop(prefs, "storyboard_default_start_frame", slider=True, text="Frame")

        row = col.row()
        split = row.split(factor=settingsSplitFactor)
        rowLeft = split.row()
        rowLeft.alignment = "RIGHT"
        rowLeft.label(text="Default Shot Duration")
        rowRight = split.row()
        rowRight.prop(prefs, "storyboard_new_shot_duration", slider=True, text="Frames")


def drawGeneralUI(context, prefs, layout):
    box = layout.box()
    collapsable_panel(box, prefs, "addonPrefs_ui_expanded", text="UI")
    if prefs.addonPrefs_ui_expanded:
        uiSplitFactor = 0.15

        # column component here is technicaly not necessary but reduces the space between lines
        col = box.column()

        split = col.split(factor=uiSplitFactor)
        rowLeft = split.row()
        rowRight = split.row()
        rowRight.prop(prefs, "separatedRenderPanel", text="Make Render Panel a Separated Tab in the Viewport N-Panel")


def drawFeatures(context, prefs, layout):
    box = layout.box()
    collapsable_panel(box, prefs, "addonPrefs_features_expanded", text="Layout and Features to Display in New Scenes")
    if prefs.addonPrefs_features_expanded:
        uiSplitFactor = 0.15

        draw_features_prefs("ADDON_PREFS", box)


def drawDevAndDebug(context, self, layout):
    splitFactor = 0.3

    box = layout.box()

    split = box.split(factor=0.5)
    rowLeft = split.row()
    rowLeft.label(text="Development and Debug:")
    rowRight = split.row()

    if config.devDebug:
        strDebug = " *** Debug Mode is On ***"
        rowRight.alignment = "RIGHT"
        rowRight.alert = True
        rowRight.label(text=strDebug)

    split = box.split(factor=splitFactor)
    rowLeft = split.row()
    rowLeft.alignment = "RIGHT"
    rowLeft.label(text="Debug Mode")
    rowRight = split.row()
    if config.devDebug:
        rowRight.alert = True
        rowRight.operator("uas_shot_manager.enable_debug", text="On").enable_debug = False
    else:
        rowRight.operator("uas_shot_manager.enable_debug", text="Off").enable_debug = True

    if config.devDebug:
        box.separator(factor=0.2)
        split = box.split(factor=splitFactor)
        rowLeft = split.row()
        rowLeft.alignment = "RIGHT"
        rowRight = split.row()
        rowRight.prop(self, "displaySMDebugPanel")

    # Debug info and properties
    ###############

    if config.devDebug:
        box = layout.box()
        row = box.row()
        row.label(text="Debug Infos:")

        col = box.column()
        col.scale_y = 0.7
        col.label(text="Temporary preference values (for dialogs for instance) are")
        col.label(text="only visible when global variable devDebug is True.")

        if config.devDebug:
            split = box.split(factor=splitFactor)
            rowLeft = split.row()
            rowLeft.alignment = "RIGHT"
            rowLeft.label(text="Add New Shot Dialog")
            rowRight = split.row()
            rowRight.prop(self, "addShot_start")
            rowRight.prop(self, "addShot_end")
