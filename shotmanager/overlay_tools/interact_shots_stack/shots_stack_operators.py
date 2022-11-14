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
Operators for the Interactive Shots Stack overlay tool
"""

import bpy
from bpy.types import Operator

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_OT_ToggleShotsStackWithOverlayTools(Operator):
    bl_idname = "uas_shot_manager.toggle_shots_stack_with_overlay_tools"
    bl_label = "Toggle Display"
    bl_description = "Toggle Interactive Shots Stack display with overlay tools"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        prefs = config.getAddonPrefs()
        prefs.toggle_overlays_turnOn_interactiveShotsStack = not prefs.toggle_overlays_turnOn_interactiveShotsStack

        # toggle on or off the overlay tools mode
        #  context.window_manager.UAS_shot_manager_display_overlay_tools = prefs.toggle_overlays_turnOn_interactiveShotsStack

        return {"FINISHED"}


class UAS_ShotManager_OT_ToggleShotsStackInteraction(Operator):
    bl_idname = "uas_shot_manager.toggle_shots_stack_interaction"
    bl_label = "Toggle interactions in the Interactive Shots Stack"
    # bl_description = "Toggle Shots Stack Interactions"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        context.window_manager.UAS_shot_manager_toggle_shots_stack_interaction = (
            not context.window_manager.UAS_shot_manager_toggle_shots_stack_interaction
        )

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_OT_ToggleShotsStackWithOverlayTools,
    UAS_ShotManager_OT_ToggleShotsStackInteraction,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
