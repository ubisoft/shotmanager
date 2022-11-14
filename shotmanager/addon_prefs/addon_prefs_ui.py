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
from shotmanager.utils.utils import convertVersionIntToStr
from shotmanager.utils.utils_ui import collapsable_panel, propertyColumn

from shotmanager.prefs.prefs_features import draw_features_prefs


##################################################################################
# Draw
##################################################################################


def draw_addon_prefs(self, context):
    layout = self.layout
    layout = layout.column(align=False)
    padding_left = 4

    if config.devDebug:
        layout.label(
            text=f"Previously Installed Version: {self.previousInstalledVersion} - Current version: {self.version()[1]}"
        )

    if self.previousInstalledVersion > self.version()[1]:
        warningRow = layout.row()
        warningRow.alert = True
        restartRow.alignment = "CENTER"
        warningRow.label(
            text="***  Warning: The add-on version that has been installed is older than the one that was in place  ***"
        )

        restartRow = layout.row()
        restartRow.alert = True
        restartRow.alignment = "CENTER"
        restartRow.label(text="***  Please re-start Blender to finish the update of the add-on Preferences ***")

    elif 0 != self.previousInstalledVersion and self.previousInstalledVersion < self.version()[1]:
        restartRow = layout.row()
        restartRow.alignment = "CENTER"
        restartRow.label(
            text=f"--  Version {self.version()[0]} has just been installed over version {convertVersionIntToStr(self.previousInstalledVersion)}  --"
        )
        restartRow = layout.row()
        restartRow.alert = True
        restartRow.alignment = "CENTER"
        restartRow.label(text="***  Please re-start Blender to finish the update of the add-on Preferences ***")

    # Dependencies
    ###############
    drawDependencies(context, layout)

    # General and updates
    ###############
    drawGeneral(context, self, layout)

    # Settings
    ###############
    drawSettings(context, self, layout)

    # Features
    ###############
    drawFeatures(context, self, layout)

    # Shot manipulations
    ###############
    drawShotManipulations(context, self, layout)

    # General UI
    ###############
    # drawGeneralUI(context, self, layout)

    # Render
    ###############
    drawRender(context, self, layout)

    # Stamp Info
    ###############
    drawStampInfo(context, self, layout)

    # Key Mapping
    ###############
    drawKeyMapping(context, self, layout, padding_left)

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


def drawGeneral(context, prefs, layout):
    box = layout.box()
    # collapsable_panel(box, prefs, "addonPrefs_ui_expanded", text="UI")
    # if prefs.addonPrefs_ui_expanded:
    uiSplitFactor = 0.15

    # column component here is technicaly not necessary but reduces the space between lines
    col = box.column()

    # split = col.split(factor=uiSplitFactor)
    # rowLeft = split.row()
    # rowLeft.separator()
    # rowRight = split.row()
    row = col.row()
    row.separator(factor=3)
    row.prop(prefs, "checkForNewAvailableVersion", text="Check for Updates")


def drawSettings(context, prefs, layout):
    box = layout.box()
    collapsable_panel(box, prefs, "addonPrefs_settings_expanded", text="Sequences and Shots Default Settings")
    if prefs.addonPrefs_settings_expanded:
        leftSepFactor = 2
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
        subRow = row.row()
        subRow.separator(factor=leftSepFactor)
        subRow.label(text="Storyboard:")

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


def drawShotManipulations(context, prefs, layout):
    box = layout.box()
    collapsable_panel(box, prefs, "addonPrefs_shotManips_expanded", text="Shot Manipulations")
    if prefs.addonPrefs_shotManips_expanded:

        mainCol = propertyColumn(box, padding_left=3)
        mainCol.label(text="When Current Shot Is Changed:")

        propsCol = propertyColumn(mainCol, padding_left=4)

        propsCol.prop(
            prefs,
            "current_shot_changes_current_time_to_start",
            text="Set Current Frame To Shot Start",
        )
        propsCol.prop(
            prefs,
            "current_shot_changes_time_range",
            text="Set Scene Animation Range To Shot Range",
        )

        propsCol.prop(
            prefs,
            "current_stb_shot_select_stb_frame",
        )
        propsCol.prop(
            prefs,
            "current_pvz_shot_select_stb_frame",
        )

        propsCol.separator(factor=0.8)

        # in storyboard mode
        ##########################
        stbLayoutCol = propertyColumn(propsCol, padding_left=0)

        stbLayoutRow = stbLayoutCol.row()
        stbLayoutRow.label(text="In Storyboard Layout:")

        stbLayoutPropsCol = propertyColumn(stbLayoutCol, padding_left=3)

        # propsCol.prop(
        #     prefs,
        #     "current_shot_changes_edited_frame_in_stb",
        #     text="Storyboard Shots List: Set Selected Shot to Edited One",
        # )

        # storyboard shots #######
        # propsCol.separator(factor=0.5)
        # propsCol.label(text="Storyboard Shots:")

        stbLayoutPropsCol.prop(
            prefs,
            "stb_selected_shot_changes_current_shot",
        )
        stbLayoutPropsCol.prop(
            prefs,
            "stb_selected_shot_in_shots_stack_changes_current_shot",
        )

        stbLayoutPropsCol.prop(
            prefs,
            "stb_current_stb_shot_changes_time_zoom",
        )
        stbLayoutPropsCol.prop(
            prefs,
            "stb_current_pvz_shot_changes_time_zoom",
        )

        propsCol.separator(factor=0.8)

        # in previz mode
        ##########################
        pvzLayoutCol = propertyColumn(propsCol, padding_left=0)

        pvzLayoutRow = pvzLayoutCol.row()
        pvzLayoutRow.label(text="In Previz Layout:")

        pvzLayoutPropsCol = propertyColumn(pvzLayoutCol, padding_left=3)

        # pvzLayoutPropsCol.prop(
        #     prefs,
        #     "current_stb_shot_select_stb_frame",
        # )
        # pvzLayoutPropsCol.prop(
        #     prefs,
        #     "current_pvz_shot_select_stb_frame",
        # )

        pvzLayoutPropsCol.prop(
            prefs,
            "pvz_selected_shot_changes_current_shot",
        )
        pvzLayoutPropsCol.prop(
            prefs,
            "pvz_selected_shot_in_shots_stack_changes_current_shot",
        )

        pvzLayoutPropsCol.prop(
            prefs,
            "pvz_current_stb_shot_changes_time_zoom",
        )
        pvzLayoutPropsCol.prop(
            prefs,
            "pvz_current_pvz_shot_changes_time_zoom",
        )

        # storyboard shots #######
        # propsCol.separator(factor=0.5)
        # propsCol.label(text="Storyboard Shots:")

        # stbPropsCol = propertyColumn(propsCol, padding_left=3)
        # stbPropsCol.prop(
        #     prefs,
        #     "current_stb_shot_select_stb_frame",
        #     text="Select Storyboard Frame of the Current Storyboard Short",
        # )

        # # previz shots ###########
        # propsCol.separator(factor=0.5)
        # propsCol.label(text="Camera Shots:")

        # pvzPropsCol = propertyColumn(propsCol, padding_left=3)
        # pvzPropsCol.prop(
        #     prefs,
        #     "current_pvz_shot_select_stb_frame",
        #     text="Select Storyboard Frame of the Current Camera Short",
        # )

        propsCol.separator(factor=0.8)
        propsCol.label(text="(*) : Automaticaly activated in Continuous Draw Mode")

        mainCol.separator(factor=0.8)


def drawGeneralUI(context, prefs, layout):
    box = layout.box()
    collapsable_panel(box, prefs, "addonPrefs_ui_expanded", text="UI")
    if prefs.addonPrefs_ui_expanded:
        uiSplitFactor = 0.15

        col = box.column()

        split = col.split(factor=uiSplitFactor)
        rowLeft = split.row()
        rowLeft.separator()
        rowRight = split.row()
        rowRight.prop(prefs, "separatedRenderPanel", text="Make Render Panel a Separated Tab in the Viewport N-Panel")


def drawRender(context, prefs, layout):
    box = layout.box()
    collapsable_panel(box, prefs, "addonPrefs_render_expanded", text="Render")
    if prefs.addonPrefs_render_expanded:
        leftSepFactor = 2
        mainRow = box.row()
        mainRow.separator(factor=leftSepFactor)

        col = mainRow.column(align=True)
        col.prop(prefs, "separatedRenderPanel", text="Make Render Panel a Separated Tab in the Viewport N-Panel")


def drawStampInfo(context, prefs, layout):
    box = layout.box()
    collapsable_panel(box, prefs, "addonPrefs_stampInfo_expanded", text="Stamp Info")
    if prefs.addonPrefs_stampInfo_expanded:
        leftSepFactor = 2
        mainRow = box.row()
        mainRow.separator(factor=leftSepFactor)
        col = mainRow.column(align=True)

        # col.prop(prefs, "stampInfo_display_properties", text="Display Stamp Info panel in the 3D View tabs")
        col.prop(
            prefs, "stampInfo_separatedPanel", text="Make Stamp Info Panel a Separated Tab in the Viewport N-Panel"
        )
        if config.devDebug:
            col.separator()
            col.label(text="Parameter only used by the Stamp Info Render buttons, in Debug mode:")
            col.prop(prefs, "write_still")

        # Technical settings
        ###############
        mainRow = box.row()
        mainCol = mainRow.column(align=True)
        mainCol.label(text="Technical Settings:")
        propsRow = mainCol.row()
        propsRow.separator(factor=leftSepFactor)
        propsCol = propsRow.column(align=True)

        propsCol.label(text="Stamped Images Compositing:")
        row = propsCol.row()
        row.separator(factor=3)
        subCol = row.column(align=True)
        subCol.prop(prefs, "delete_temp_scene")
        subCol.prop(prefs, "delete_temp_images")


def drawFeatures(context, prefs, layout):
    box = layout.box()
    # title = "Features Settings and Layout for New Scenes"
    title = "Layout and Features to Display in New Scenes"
    collapsable_panel(box, prefs, "addonPrefs_features_expanded", text=title)
    if prefs.addonPrefs_features_expanded:
        draw_features_prefs("ADDON_PREFS", box)


def drawKeyMapping(context, prefs, layout, padding_left):
    box = layout.box()
    title = "Key Mapping"
    collapsable_panel(box, prefs, "addonPrefs_keymapping_expanded", text=title)
    if prefs.addonPrefs_keymapping_expanded:
        propCol = propertyColumn(box, padding_left=padding_left, padding_bottom=0.2, scale_y=0.8)
        propCol.label(text="Key mappings are located in the Keymap section of this Preferences panel.")
        propCol.label(text='They can be listed by typing "Ubisoft Shot Mng" in the Keympap Search field.')

        propCol = propertyColumn(box, padding_left=padding_left)
        propCol.prop(prefs, "kmap_shots_nav_invert_direction")


def drawDevAndDebug(context, prefs, layout):
    box = layout.box()
    collapsable_panel(box, prefs, "addonPrefs_debug_expanded", text="Dev and Debug")
    if prefs.addonPrefs_debug_expanded:
        leftSepFactor = 2
        # mainRow = box.row()
        # mainRow.separator(factor=leftSepFactor)
        # col = mainRow.column(align=True)

        splitFactor = 0.3

        split = box.split(factor=0.5)
        rowLeft = split.row()
        rowLeft.label(text="Development and Debug:")
        rowRight = split.row()

        if config.devDebug:
            strDebug = " *** Debug Mode is On ***"
            rowRight.alignment = "RIGHT"
            rowRight.alert = True
            rowRight.label(text=strDebug)

        box.operator("uas_utils.ckeckinternetconnection")

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
            rowRight.prop(prefs, "displaySMDebugPanel")

        # Debug info and properties
        ###############

        if config.devDebug:
            subBox = box.box()
            row = subBox.row()
            row.label(text="Debug Infos:")

            col = subBox.column()
            col.scale_y = 0.7
            col.label(text="Temporary preference values (for dialogs for instance) are")
            col.label(text="only visible when global variable devDebug is True.")

            # initialization state
            initRow = col.row()
            initRow.prop(prefs, "isInitialized")

            tempValsRow = col.row()
            split = tempValsRow.split(factor=splitFactor)
            rowLeft = split.row()
            rowLeft.alignment = "RIGHT"
            rowLeft.label(text="Add New Shot Dialog")
            rowRight = split.row()
            rowRight.prop(prefs, "addShot_start")
            rowRight.prop(prefs, "addShot_end")
