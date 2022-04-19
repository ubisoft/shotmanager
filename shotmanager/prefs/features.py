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
To do: module description here.
"""

import bpy
from bpy.types import Panel, Operator, Menu

from shotmanager.config import config
from shotmanager.overlay_tools.interact_shots_stack import shots_stack_prefs
from shotmanager.overlay_tools.viewport_camera_hud import camera_hud_prefs


class UAS_ShotManager_Features(Operator):
    bl_idname = "shot_manager.features"
    bl_label = "Feature Toggles"
    bl_description = "Controls the display of additional features available with Shot Manager or displayed on its panel"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences
        separatorLeft = 0.33
        separatorRight = 0.25
        separatorVertTopics = 0.2

        def _draw_separator_row(layout):
            separatorrow = layout.row()
            separatorrow.scale_y = 0.7
            separatorrow.separator()

        layout = self.layout
        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        layout.label(text="Display Takes and Shots additionnal features:")
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
        # Take and shot notes
        subrow = col.row()
        subrow.scale_x = 1.5
        icon = config.icons_col["ShotManager_NotesData_32"]
        notesIcon = "TEXT"
        notesIcon = "WORDWRAP_OFF"
        subrow.prop(props, "display_notes_in_properties", text="", icon_value=icon.icon_id)
        subrow.label(text="Takes and Shots Notes")

        ################
        # Take render settings
        subrow = col.row()
        subrow.scale_x = 1.5
        subrow.prop(props, "display_takerendersettings_in_properties", text="", icon="OUTPUT")
        subrow.label(text="Takes Render Settings")

        _draw_separator_row(col)

        ################
        # Edit mode
        subrow = col.row()
        subrow.scale_x = 1.5
        subrow.prop(props, "display_editmode_in_properties", text="", icon="SEQ_SEQUENCER")
        subrow.label(text="Edit Mode")

        # Global Edit Integration
        subrow = col.row()
        subrow.scale_x = 1.5
        subrow.prop(props, "display_globaleditintegr_in_properties", text="", icon="SEQ_STRIP_META")
        subrow.label(text="Global Edit Integration")

        _draw_separator_row(col)

        ################################################################
        rightCol = boxSplit.column()

        # empty spacer
        row = rightCol.row()
        row.separator(factor=separatorRight)
        col = row.column()

        ################
        # Camera BG
        subrow = col.row()
        subrow.scale_x = 1.5
        icon = config.icons_col["ShotManager_CamBGVisible_32"]
        subrow.prop(props, "display_camerabgtools_in_properties", text="", icon_value=icon.icon_id)
        subrow.label(text="Camera Backgrounds")

        ################
        # Grease Pencil
        if config.devDebug:
            subrow = col.row()
            subrow.scale_x = 1.5
            icon = config.icons_col["ShotManager_CamGPVisible_32"]
            subrow.prop(props, "display_greasepencil_in_properties", text="", icon_value=icon.icon_id)
            subrow.label(text="Camera Grease Pencil")
        else:
            subrow = col.row()
            subrow.label(text=" ")

        _draw_separator_row(col)

        ################
        # Advanced infos
        subrow = col.row()
        subrow.scale_x = 1.5
        subrow.prop(props, "display_advanced_infos", text="", icon="SYNTAX_ON")
        subrow.label(text="Display Advanced Infos")

        ################
        ################
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
        # Retimer
        subrow = col.row()
        subrow.scale_x = 1.5
        icon = config.icons_col["ShotManager_Retimer_32"]
        subrow.prop(prefs, "display_retimer_in_properties", text="", icon_value=icon.icon_id)
        subrow.label(text="Retimer Panel")

        ################################################################
        rightCol = boxSplit.column()

        # empty spacer
        row = rightCol.row()
        row.separator(factor=separatorRight)
        col = row.column()

        ################
        # Renderer
        subrow = col.row()
        subrow.scale_x = 1.5
        icon = config.icons_col["ShotManager_Retimer_32"]
        subrow.prop(prefs, "display_render_in_properties", text="", icon="RENDER_ANIMATION")
        subrow.label(text="Renderer Panel")

        ################
        ################
        layout.separator(factor=separatorVertTopics)
        layout.label(text="Additional Tools in Editors:")
        separatorLeftWidgets = 1.0

        ###################################
        # Sequence timeline ######
        ###################################
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
        subrow.label(text="Sequence Timeline (in Viewport)")

        if prefs.seqTimeline_settings_expanded:
            leftCol = box.column()

            # empty spacer column
            row = leftCol.row()
            col = row.column()
            col.scale_x = 0.25
            col.label(text=" ")
            col = row.column(align=True)

            col.prop(props, "seqTimeline_displayDisabledShots", text="Display Disabled Shots")
            col.prop(prefs, "seqTimeline_not_disabled_with_overlays")

        ###################################
        # Interactive Shots Stack ######
        ###################################
        box = layout.box()
        subrow = box.row()

        panelIcon = "TRIA_DOWN" if prefs.intShStack_settings_expanded else "TRIA_RIGHT"
        subrow.prop(prefs, "intShStack_settings_expanded", text="", icon_only=True, icon=panelIcon, emboss=False)

        icon = config.icons_col["ShotManager_Retimer_32"]
        butsubrow = subrow.row()
        butsubrow.scale_x = 1.5
        butsubrow.operator(
            "uas_shot_manager.toggle_shots_stack_with_overlay_tools",
            text="",
            icon="NLA_PUSHDOWN",
            depress=prefs.toggle_overlays_turnOn_interactiveShotsStack,
        )
        subrow.label(text="Interaction Shots Stack (in Timeline)")

        if prefs.intShStack_settings_expanded:
            shots_stack_prefs.draw_settings(context, box)

        ###################################
        # Camera HUD ######################
        ###################################
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
        subrow.label(text="Camera HUD (in Viewport)")

        if prefs.cameraHUD_settings_expanded:
            camera_hud_prefs.draw_settings(context, box)

        ###################################
        # Frame Range #####################
        ###################################
        box = layout.box()
        subrow = box.row()
        subrow.separator(factor=3.5)
        butsubrow = subrow.row()
        butsubrow.scale_x = 1.5
        butsubrow.prop(prefs, "display_frame_range_tool", text="", icon="CENTER_ONLY")
        subrow.label(text="Frame Range Tool (on Timeline Menu)")

        layout.separator(factor=separatorVertTopics)

        layout.separator(factor=2)

    def execute(self, context):
        return {"FINISHED"}


_classes = (UAS_ShotManager_Features,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
