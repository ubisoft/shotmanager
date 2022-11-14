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

from shotmanager.utils.utils_markers import sceneContainsCameraBinding


from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def draw_shots_stack_toolbar_in_editor(self, context):
    props = config.getAddonProps(context.scene)
    prefs = config.getAddonPrefs()
    layout = self.layout
    butScale = 1.4

    row = layout.row(align=True)
    row.separator(factor=3)
    row.alignment = "RIGHT"

    playEnabled = not sceneContainsCameraBinding(context.scene)
    rowPlayButton = row.row(align=True)
    rowPlayButton.scale_x = butScale
    rowPlayButton.enabled = playEnabled
    rowPlayButton.prop(
        context.window_manager,
        "UAS_shot_manager_shots_play_mode",
        # text="Shots Play Mode" if context.window_manager.UAS_shot_manager_shots_play_mode else "Standard Play Mode",
        text="",
        toggle=True,
        icon="ANIM" if context.window_manager.UAS_shot_manager_shots_play_mode else "FORWARD",
    )

    toggleButRow = row.row(align=True)
    toggleButRow.operator_context = "INVOKE_DEFAULT"
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

    if config.devDebug:
        row.separator(factor=0.8)
        # row.operator(
        #     "uas_gpu.dopesheet_gpu_sample",
        #     text="GPU",
        #     depress=context.window_manager.UAS_shot_manager_display_dopesheet_gpu_sample,
        #     # icon_value=icon.icon_id,
        # )
        row.prop(
            context.window_manager,
            "UAS_shot_manager_display_dopesheet_gpu_sample",
            text="GPU",
            # depress=context.window_manager.UAS_shot_manager_display_dopesheet_gpu_sample,
            # icon_value=icon.icon_id,
        )

    row.separator(factor=0.8)

    row.operator(
        "uas_shot_manager.toggle_shots_stack_with_overlay_tools",
        text="",
        icon="NLA_PUSHDOWN",
        depress=prefs.toggle_overlays_turnOn_interactiveShotsStack,
    )

    butsrow = row.row(align=True)
    butsrow.enabled = prefs.toggle_overlays_turnOn_interactiveShotsStack

    interacButRow = butsrow.row(align=True)
    # interacButRow.scale_x = butScale
    #  interacButRow.enabled = context.window_manager.UAS_shot_manager_display_overlay_tools
    interacButRow.enabled = prefs.toggle_overlays_turnOn_interactiveShotsStack
    interacButRow.operator(
        "uas_shot_manager.toggle_shots_stack_interaction",
        text="",
        icon="ARROW_LEFTRIGHT",
        depress=context.window_manager.UAS_shot_manager_toggle_shots_stack_interaction,
    )

    # wkip to remove and to put in the settings menu??
    interacButRow.operator(
        "uas_shot_manager.display_disabledshots_in_overlays",
        text="",
        icon="NLA",
        depress=props.interactShotsStack_displayDisabledShots,
    )

    # interacButRow.prop(
    #     props, "interactShotsStack_displayDisabledShots", text="", icon="NLA",
    # )

    interacButRow.prop(props, "interactShotsStack_displayInCompactMode", text="", icon="SEQ_STRIP_META")
    #     text="Compact Shots Display (= decrease visual stack height)",

    #    butsrow.menu("UAS_MT_Shot_Manager_Interact_Shots_Stack_Settings_Menu", text="", icon="PROPERTIES")

    # butsrow.operator(
    #     "uas_shot_manager.interact_shots_stack_settings", text="x", icon="PROPERTIES",
    # )
    # butsrow.operator(
    row.operator(
        "uas_shot_manager.interact_shots_stack_settings_wind",
        text="",
        icon="PROPERTIES",
    )

    # # # butsrow.separator()
    # # # butsrow.prop(context.window_manager, "UAS_shot_manager__useInteracShotsStack", text="", icon="FUND")


def display_shots_stack_toolbar_in_editor(display_value):
    if display_value:
        bpy.types.TIME_MT_editor_menus.append(draw_shots_stack_toolbar_in_editor)

    else:
        bpy.types.TIME_MT_editor_menus.remove(draw_shots_stack_toolbar_in_editor)


# https://blender.stackexchange.com/questions/34434/timeline-header-python-modification
# _classes = (,)


def register():
    _logger.debug_ext("       - Registering Shots Stack Toolbar", form="REG")

    #     for cls in _classes:
    #         bpy.utils.register_class(cls)


#   bpy.types.TIME_HT_editor_buttons.append(draw_frame_rate_property)


def unregister():
    _logger.debug_ext("       - Unregistering Shots Stack Toolbar", form="UNREG")

    #     for cls in reversed(_classes):
    #         bpy.utils.unregister_class(cls)


#  bpy.types.TIME_HT_editor_buttons.remove(draw_frame_rate_property)
