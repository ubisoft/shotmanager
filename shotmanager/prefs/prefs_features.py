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
Features preference panel
"""

import bpy
from bpy.types import Operator

from shotmanager.overlay_tools.interact_shots_stack import shots_stack_prefs
from shotmanager.overlay_tools.viewport_camera_hud import camera_hud_prefs

from shotmanager.utils import utils_ui
from shotmanager.utils.utils_ui import propertyColumn, collapsable_panel

from shotmanager.tools.markers_nav_bar import markers_nav_bar_prefs_ui

from shotmanager.config import config


class UAS_ShotManager_Features(Operator):
    bl_idname = "shot_manager.features"
    bl_label = "Feature Toggles"
    bl_description = "Controls the display of additional features available with Shot Manager or displayed on its panel"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        prefs = config.getAddonPrefs()

        # close all the panels
        prefs.features_layoutSettings_expanded = False
        prefs.cameraHUD_settings_expanded = False
        prefs.seqTimeline_settings_expanded = False
        prefs.shtStack_settings_expanded = False

        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        draw_features_prefs("SCENE", layout)

    def execute(self, context):
        return {"FINISHED"}


def draw_features_prefs(mode, layout):
    """Display the panel to configure each supported preset. This function is called by a scene operator
    and by the add-on Preferences UI, each one having its own properties to store the configuration.
    Args:
        mode:   Can be SCENE or ADDON_PREFS
    """
    # TOFIX: the bpy.context calls should be double-checked

    prefs = config.getAddonPrefs()
    if "SCENE" == mode:
        props = config.getAddonProps(bpy.context.scene)
        propsLayout = props.getCurrentLayout()
        currentLayoutIsStb = "STORYBOARD" == props.currentLayoutMode()
        layoutPrefix = ""
    else:
        props = prefs
        propsLayout = prefs
        currentLayoutIsStb = "STORYBOARD" == prefs.layout_mode
        layoutPrefix = "stb_" if currentLayoutIsStb else "pvz_"

    separatorLeft = 0.33
    separatorRight = 0.25
    separatorVertTopics = 0.2
    leftSepFactor = 3
    leftSepFact_props = 9

    def _draw_separator_row(layout, factor=0.9):
        separatorrow = layout.row()
        separatorrow.scale_y = factor
        separatorrow.separator()

    split = layout.split(factor=0.25)
    layoutRow = split.row()
    if "SCENE" == mode:
        layoutRow.label(text="Layout: ")
    else:
        layoutRow.label(text="Default Layout: ")

    layoutRowRight = split.row()
    # layoutRow.scale_x = 0.8
    layoutRowRight.scale_y = 1.2
    layoutRowRight.alignment = "LEFT"

    stbIcon = config.icons_col["ShotManager_Storyboard_32"]
    previzIcon = config.icons_col["ShotManager_32"]

    layoutRowRight.prop(props, "layout_but_storyboard", text=" Storyboard  ", toggle=1, icon_value=stbIcon.icon_id)
    layoutRowRight.prop(props, "layout_but_previz", text="     Previz        ", toggle=1, icon_value=previzIcon.icon_id)

    if config.devDebug:
        if "SCENE" == mode:
            #   layoutRowRight.prop(props, "current_layout_index", text="layout Ind")
            layoutRowRight.label(text=f"layout ind:{props.current_layout_index}")
        else:
            layoutRowRight.label(text=f"layout_mode:{props.layout_mode}")

    #################################################################
    #################################################################

    # box = layout.box()
    # collapsable_panel(box, prefs, "features_layoutSettings_expanded", text="Layout Settings")
    # if prefs.features_layoutSettings_expanded:
    #     leftSepFactor = 2

    #     mainRow = box.row()
    #     mainCol = mainRow.column(align=True)
    #     mainCol.label(text="When Selected Shot Is Changed:  (Settings stored in the Add-on Preferences):")

    #     propsRow = mainCol.row()
    #     propsRow.separator(factor=leftSepFactor)
    #     propsCol = propsRow.column(align=True)
    #     propsCol.label(text="Storyboard Layout:")
    #     row = propsCol.row()
    #     row.separator(factor=3)
    #     subCol = row.column(align=True)

    #     # NOTE: when the Continuous Editing mode is on then the selected and current shots are tied anyway
    #     subCol.prop(
    #         prefs,
    #         "stb_selected_shot_changes_current_shot",
    #         text="Storyboard Shots List: Set Selected Shot to Current One",
    #     )
    #     subCol.prop(
    #         prefs,
    #         "stb_selected_shot_in_shots_stack_changes_current_shot",
    #         text="Shots Stack: Set Selected Shot to Current One",
    #     )

    #     propsRow = mainCol.row()
    #     propsRow.separator(factor=leftSepFactor)
    #     propsCol = propsRow.column(align=True)
    #     propsCol.label(text="Previz Layout:")
    #     row = propsCol.row()
    #     row.separator(factor=3)
    #     subCol = row.column(align=True)
    #     subCol.prop(
    #         prefs,
    #         "pvz_selected_shot_changes_current_shot",
    #         text="Previz Shots List: Set Selected Shot to Current One",
    #     )
    #     subCol.prop(
    #         prefs,
    #         "pvz_selected_shot_in_shots_stack_changes_current_shot",
    #         text="Shots Stack: Set Selected Shot to Current One",
    #     )

    #################################################################
    #################################################################

    if "SCENE" == mode:
        layout.separator(factor=separatorVertTopics)

    row = layout.row(align=True)
    leftRow = row.row(align=True)
    leftRow.alignment = "LEFT"
    # leftRow.label(text="Takes and Shots features to toggle with the selected layout:")
    subLeftRow01 = leftRow.row(align=True)
    subLeftRow01.alignment = "RIGHT"
    subLeftRow01.label(text="Takes and Shots features")
    subLeftRow02 = subLeftRow01.row(align=True)
    subLeftRow02.alert = True
    subLeftRow02.alignment = "LEFT"
    txt = (
        " toggled with the selected layout:"
        if "SCENE" == mode
        else " to enable by default with the selected layout in new scenes:"
    )
    subLeftRow02.label(text=txt)

    if "SCENE" == mode:
        rightRow = row.row(align=False)
        rightRow.alignment = "RIGHT"
        resetOp = rightRow.operator("uas_shotmanager.querybox", text="Reset", icon="LOOP_BACK")
        resetOp.width = 400
        resetOp.message = "Reset the selected layout properties to its default values?"
        resetOp.function_name = "reset_layout_settings"
        resetOp.function_arguments = "'STORYBOARD'" if currentLayoutIsStb else "'PREVIZ'"
        resetOp.tooltip = f"Reset {'Storyboard' if currentLayoutIsStb else 'Previz'} layout to the default values set \nin the add-on Preferences"
        rightRow.operator("preferences.addon_show", text="", icon="PREFERENCES").module = "shotmanager"
    #  rightRow.separator()

    # else:
    #     layout.label(text="Takes and Shots features to enable by default with the selected layout:")
    box = layout.box()

    boxSplit = box.split(factor=0.5)
    leftCol = boxSplit.column()

    # empty spacer column
    row = leftCol.row()
    col = row.column()
    col.scale_x = separatorLeft
    col.label(text=" ")
    col = row.column()

    ################
    # Storyboard Grease Pencil
    subrow = col.row()
    subrow.scale_x = 1.5
    icon = config.icons_col["ShotManager_CamGPVisible_32"]
    subrow.prop(propsLayout, f"{layoutPrefix}display_storyboard_in_properties", text="", icon_value=icon.icon_id)
    subSubrow = subrow.row()
    # subSubrow.enabled = props != prefs
    subSubrow.scale_x = 0.9
    subSubrow.operator("uas_shot_manager.greasepencil_template_panel", text="", icon="LONGDISPLAY").mode = mode
    subrow.label(text="Storyboard")

    ################
    # Camera BG
    subrow = col.row()
    subrow.scale_x = 1.5
    icon = config.icons_col["ShotManager_CamBGVisible_32"]
    subrow.prop(propsLayout, f"{layoutPrefix}display_cameraBG_in_properties", text="", icon_value=icon.icon_id)
    subrow.label(text="Camera Backgrounds")

    _draw_separator_row(col)

    ################
    # Edit mode
    subrow = col.row()
    subrow.scale_x = 1.5
    subrow.prop(propsLayout, f"{layoutPrefix}display_editmode_in_properties", text="", icon="SEQ_SEQUENCER")
    subrow.label(text="Edit Mode")

    # Global Edit Integration
    subrow = col.row()
    subrow.scale_x = 1.5
    subrow.prop(propsLayout, f"{layoutPrefix}display_globaleditintegr_in_properties", text="", icon="SEQ_STRIP_META")
    subrow.label(text="Global Edit Integration")

    # _draw_separator_row(col)

    ################################################################
    rightCol = boxSplit.column()

    # empty spacer
    row = rightCol.row()
    row.separator(factor=separatorRight)
    col = row.column()

    ################
    # Take and shot notes
    subrow = col.row()
    subrow.scale_x = 1.5
    icon = config.icons_col["ShotManager_NotesData_32"]
    # notesIcon = "TEXT"
    # notesIcon = "WORDWRAP_OFF"
    subrow.prop(propsLayout, f"{layoutPrefix}display_notes_in_properties", text="", icon_value=icon.icon_id)
    subrow.label(text="Takes and Shots Notes")

    ################
    # Take render settings
    subrow = col.row()
    subrow.scale_x = 1.5
    subrow.prop(propsLayout, f"{layoutPrefix}display_takerendersettings_in_properties", text="", icon="OUTPUT")
    subrow.label(text="Takes Render Settings")

    _draw_separator_row(col)

    ################
    # Advanced infos
    subrow = col.row()
    subrow.scale_x = 1.5
    subrow.prop(propsLayout, f"{layoutPrefix}display_advanced_infos", text="", icon="SYNTAX_ON")
    subrow.label(text="Display Advanced Infos")

    # ################
    # # Selection settings
    # propsRow = box.row()
    # propsRow.separator(factor=leftSepFactor)
    # propsCol = propsRow.column(align=True)
    # propsCol.label(text="Make the selected shot also the current one when it is selected from:")
    # row = propsCol.row()
    # row.separator(factor=3)

    # # subCol = row.column(align=True)
    # split = row.split(factor=0.35)

    # # NOTE: when the Continuous Editing mode is on then the selected and current shots are tied anyway
    # split.prop(
    #     propsLayout,
    #     f"{layoutPrefix}selected_shot_changes_current_shot",
    #     text="The Shots List",
    # )
    # split.prop(
    #     propsLayout,
    #     f"{layoutPrefix}selected_shot_in_shots_stack_changes_current_shot",
    #     text="The Interactive Shots Stack",
    # )

    # ################
    # # Timeline zoom settings
    # propsRow = box.row()
    # propsRow.separator(factor=leftSepFactor)
    # propsCol = propsRow.column(align=True)
    # propsCol.label(text="When current shot is changed:")
    # row = propsCol.row()
    # row.separator(factor=3)

    # subCol = row.column(align=True)

    # # NOTE: when the Continuous Editing mode is on then the selected and current shots are tied anyway
    # subCol.prop(
    #     propsLayout,
    #     f"{layoutPrefix}current_shot_changes_time_zoom",
    #     text="Zoom Timeline Content to Frame The Current Shot",
    # )

    #################################################################
    #
    #################################################################
    if "ADDON_PREFS" != mode:
        layout.separator(factor=separatorVertTopics)
    layout.label(text="Shot Manager Panels:")
    box = layout.box()

    boxSplit = box.split(factor=0.5)
    leftCol = boxSplit.column()

    # empty spacer column
    row = leftCol.row()
    col = row.column()
    col.scale_x = separatorLeft
    col.label(text=" ")

    col = row.column()

    ################
    # Grease pencil tools
    subrow = col.row()
    subrow.scale_x = 1.5
    icon = config.icons_col["ShotManager_CamGPVisible_32"]
    subrow.prop(prefs, "display_25D_greasepencil_panel", text="", icon_value=icon.icon_id)
    subrow.label(text="2.5D Grease Pencil")

    # ################
    # # Renderer
    # subrow = col.row()
    # subrow.scale_x = 1.5
    # icon = config.icons_col["ShotManager_Retimer_32"]
    # subrow.prop(prefs, "display_render_panel", text="", icon="RENDER_ANIMATION")
    # subrow.label(text="Render")

    ################################################################
    rightCol = boxSplit.column()

    # empty spacer
    row = rightCol.row()
    row.separator(factor=separatorRight)
    col = row.column()

    ################
    # Retimer
    subrow = col.row()
    subrow.scale_x = 1.5
    icon = config.icons_col["ShotManager_Retimer_32"]
    subrow.prop(prefs, "display_retimer_panel", text="", icon_value=icon.icon_id)
    subrow.label(text="Retimer")

    ################
    ################
    if "ADDON_PREFS" != mode:
        layout.separator(factor=separatorVertTopics)
    layout.label(text="Additional Tools in Editors:")

    ###################################
    # Renderer
    ###################################
    # if "ADDON_PREFS" != mode:
    box = layout.box()
    subrow = box.row()
    subrow.separator(factor=3.5)

    icon = config.icons_col["ShotManager_Retimer_32"]
    butsubrow = subrow.row()
    butsubrow.scale_x = 1.5
    butsubrow.prop(prefs, "display_render_panel", text="", icon="RENDER_ANIMATION")
    subrow.label(text="Render Panel")

    subrowright = subrow.row()
    subrowright.alignment = "RIGHT"
    subrowright.label(text="(in 3D View tab)")

    ###################################
    # Stamp Info ######################
    ###################################

    box = layout.box()
    subrow = box.row()
    subrow.separator(factor=3.5)
    subrow.enabled = utils_ui.drawStampInfoBut(subrow)
    subrow.label(text="Stamp Info")

    subrowright = subrow.row()
    subrowright.alignment = "RIGHT"
    subrowright.label(text="(in 3D View tab)")

    ###################################
    # Camera HUD ######################
    ###################################
    if "ADDON_PREFS" != mode:
        box = layout.box()
        subrow = box.row()

        panelIcon = "TRIA_DOWN" if prefs.cameraHUD_settings_expanded else "TRIA_RIGHT"
        subrow.prop(prefs, "cameraHUD_settings_expanded", text="", icon_only=True, icon=panelIcon, emboss=False)

        icon = config.icons_col["ShotManager_Retimer_32"]
        butsubrow = subrow.row()
        butsubrow.scale_x = 1.5
        butsubrow.operator(
            "uas_shot_manager.camerahud_toggle_display",
            text="",
            icon="CAMERA_DATA",
            depress=props.camera_hud_display_in_viewports or props.camera_hud_display_in_pov,
        )
        subrow.label(text="Camera HUD   ")

        subrowright = subrow.row()
        subrowright.alignment = "RIGHT"
        subrowright.label(text="(in 3D View)")

        if prefs.cameraHUD_settings_expanded:
            subrow = box.row()
            propCol = propertyColumn(subrow, padding_left=leftSepFact_props)
            camera_hud_prefs.draw_settings(bpy.context, propCol)

    ###################################
    # Sequence timeline ######
    ###################################
    if "ADDON_PREFS" != mode:
        box = layout.box()
        subrow = box.row()

        panelIcon = "TRIA_DOWN" if prefs.seqTimeline_settings_expanded else "TRIA_RIGHT"
        subrow.prop(prefs, "seqTimeline_settings_expanded", text="", icon_only=True, icon=panelIcon, emboss=False)

        icon = config.icons_col["ShotManager_Retimer_32"]
        butsubrow = subrow.row()
        butsubrow.scale_x = 1.5
        butsubrow.operator(
            "uas_shot_manager.toggle_seq_timeline_with_overlay_tools",
            text="",
            icon="SEQ_STRIP_DUPLICATE",
            depress=prefs.toggle_overlays_turnOn_sequenceTimeline,
        )
        subrow.label(text="Sequence Timeline")

        subrowright = subrow.row()
        subrowright.alignment = "RIGHT"
        subrowright.label(text="(in 3D View)")

        if prefs.seqTimeline_settings_expanded:
            subrow = box.row()
            propCol = propertyColumn(subrow, padding_left=leftSepFact_props)
            propCol.prop(props, "seqTimeline_displayDisabledShots", text="Display Disabled Shots")
            propCol.prop(prefs, "seqTimeline_not_disabled_with_overlays")

    ###################################
    # Interactive Shots Stack ######
    ###################################
    if "ADDON_PREFS" != mode:
        box = layout.box()
        subrow = box.row()

        panelIcon = "TRIA_DOWN" if prefs.shtStack_settings_expanded else "TRIA_RIGHT"
        subrow.prop(prefs, "shtStack_settings_expanded", text="", icon_only=True, icon=panelIcon, emboss=False)

        icon = config.icons_col["ShotManager_Retimer_32"]
        butsubrow = subrow.row()
        butsubrow.scale_x = 1.5
        butsubrow.operator(
            "uas_shot_manager.toggle_shots_stack_with_overlay_tools",
            text="",
            icon="NLA_PUSHDOWN",
            depress=prefs.toggle_overlays_turnOn_interactiveShotsStack,
        )
        subrow.label(text="Interactive Shots Stack")

        subrowright = subrow.row()
        subrowright.alignment = "RIGHT"
        subrowright.label(text="(in Timeline and Dopesheet)")

        if prefs.shtStack_settings_expanded:
            subrow = box.row()
            propCol = propertyColumn(subrow, padding_left=leftSepFact_props)
            shots_stack_prefs.draw_settings(bpy.context, propCol)

    ###################################
    # Frame Range #####################
    ###################################
    box = layout.box()
    subrow = box.row()
    subrow.separator(factor=3.5)
    butsubrow = subrow.row()
    butsubrow.scale_x = 1.5
    butsubrow.prop(prefs, "display_frame_range_tool", text="", icon="CENTER_ONLY")
    subrow.label(text="Frame Range Tool")

    subrowright = subrow.row()
    subrowright.alignment = "RIGHT"
    subrowright.label(text="(on Timeline Menu)")

    ###################################
    # Markers Nav Bar #################
    ###################################
    box = layout.box()
    subrow = box.row()

    panelIcon = "TRIA_DOWN" if prefs.mnavbar_settings_expanded else "TRIA_RIGHT"
    subrow.prop(prefs, "mnavbar_settings_expanded", text="", icon_only=True, icon=panelIcon, emboss=False)

    butsubrow = subrow.row()
    butsubrow.scale_x = 1.5
    butsubrow.prop(prefs, "display_markersNavBar_tool", text="", icon="CENTER_ONLY")
    subrow.label(text="Markers Nav Bar")

    subrowright = subrow.row()
    subrowright.alignment = "RIGHT"
    subrowright.label(text="(on Timeline Menu)")

    if prefs.mnavbar_settings_expanded:
        subrow = box.row()
        propCol = propertyColumn(subrow, padding_left=leftSepFact_props)
        markers_nav_bar_prefs_ui.draw_markers_nav_bar_settings(propCol)

    ###################################

    layout.separator(factor=separatorVertTopics)
    if "ADDON_PREFS" != mode:
        layout.separator(factor=2)


_classes = (UAS_ShotManager_Features,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
