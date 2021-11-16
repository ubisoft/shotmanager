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
Shots Stack menubar
"""

import bpy
from bpy.types import Operator
from bpy.props import FloatProperty

from shotmanager.config import config


def display_state_changed_intShStack(context):
    print("display_state_changed_intShStack")
    prefs = context.preferences.addons["shotmanager"].preferences
    if (
        context.window_manager.UAS_shot_manager_display_overlay_tools and prefs.toggle_overlays_turnOn_sequenceTimeline
    ) or context.window_manager.UAS_shot_manager__useSequenceTimeline:
        bpy.ops.uas_shot_manager.interactive_shots_stack("INVOKE_DEFAULT")


class UAS_ShotManager_displayShotsStack(Operator):
    bl_idname = "uas_shot_manager.display_shots_stack"
    bl_label = "Display Shots Stack"
    bl_description = "Display Shots Stack"
    bl_options = {"INTERNAL"}

    # @classmethod
    # def poll(cls, context):
    #     return bpy.context.preferences.addons["shotmanager"].preferences.display_frame_range_tool

    def invoke(self, context, event):
        context.window_manager.UAS_shot_manager__useInteracShotsStack = (
            not context.window_manager.UAS_shot_manager__useInteracShotsStack
        )
        print(
            f"Invoke uas_shot_manager.display_shots_stack: UAS_shot_manager__useInteracShotsStack: {context.window_manager.UAS_shot_manager__useInteracShotsStack}"
        )
        return {"FINISHED"}


def draw_shots_stack_toolbar_in_editor(self, context):
    props = context.scene.UAS_shot_manager_props
    layout = self.layout
    butScale = 1.4

    row = layout.row(align=True)
    row.separator(factor=3)
    row.alignment = "RIGHT"

    toggleButRow = row.row(align=True)
    toggleButRow.scale_x = butScale
    icon = config.icons_col["ShotManager_Tools_OverlayTools_32"]
    # toggleButRow.prop(
    #     context.window_manager, "UAS_shot_manager_display_overlay_tools", text="", toggle=True, icon_value=icon.icon_id,
    # )
    toggleButRow.operator(
        "uas_shot_manager.display_overlay_tools",
        text="",
        depress=context.window_manager.UAS_shot_manager_display_overlay_tools,
        icon_value=icon.icon_id,
    )

    interacButRow = row.row(align=True)
    # interacButRow.scale_x = butScale
    interacButRow.enabled = context.window_manager.UAS_shot_manager_display_overlay_tools
    interacButRow.operator(
        "uas_shot_manager.toggle_shots_stack_interaction",
        text="",
        icon="ARROW_LEFTRIGHT",
        depress=context.window_manager.UAS_shot_manager_toggle_shots_stack_interaction,
    )
    interacButRow.prop(
        props, "display_disabledshots_in_interactShotsStack", text="", icon="NLA",
    )
    interacButRow.prop(props, "interactShotsStack_displayInCompactMode", text="", icon="SEQ_STRIP_META")
    #     text="Compact Shots Display (= decrease visual stack height)",

    row.separator()
    row.operator(
        "uas_shot_manager.display_shots_stack",
        text="",
        depress=context.window_manager.UAS_shot_manager__useInteracShotsStack,
        icon="NLA_PUSHDOWN",
    )
    row.prop(context.window_manager, "UAS_shot_manager__useInteracShotsStack", text="", icon="FUND")


def display_shots_stack_toolbar_in_editor(display_value):
    if display_value:
        bpy.types.TIME_MT_editor_menus.append(draw_shots_stack_toolbar_in_editor)
    else:
        bpy.types.TIME_MT_editor_menus.remove(draw_shots_stack_toolbar_in_editor)


_classes = (UAS_ShotManager_displayShotsStack,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    # lets add ourselves to the main header
    # bpy.types.TIME_MT_editor_menus.prepend(draw_shots_stack_toolbar_in_editor)

    # display_shots_stack_toolbar_in_editor(context.window_manager.UAS_shot_manager__useInteracShotsStack)

    # vse
    # bpy.types.SEQUENCER_HT_header.append(draw_shots_stack_toolbar_in_editor)


#   bpy.types.TIME_HT_editor_buttons.append(draw_shots_stack_toolbar_in_editor)
# bpy.types.TIME_MT_editor_menus.append(draw_item)
# bpy.types.TIME_MT_view.append(draw_item)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

    # display_shots_stack_toolbar_in_editor(False)
