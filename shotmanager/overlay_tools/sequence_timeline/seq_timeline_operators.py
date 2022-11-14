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
UI for the Sequence Timeline overlay tool
"""

import bpy
from bpy.types import Operator

from shotmanager.config import config

# def display_state_changed_seqTimeline(context):
#     print("display_state_changed_seqTimeline")
#     prefs = config.getAddonPrefs()
#     # if (
#     #     context.window_manager.UAS_shot_manager_display_overlay_tools
#     #     and prefs.toggle_overlays_turnOn_interactiveShotsStack
#     # ):
#     bpy.ops.uas_shot_manager.sequence_timeline("INVOKE_DEFAULT")


class UAS_ShotManager_OT_ToggleSeqTimelineWithOverlayTools(Operator):
    bl_idname = "uas_shot_manager.toggle_seq_timeline_with_overlay_tools"
    bl_label = "Toggle Display"
    bl_description = "Toggle Sequence Timeline display with overlay tools"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        prefs = config.getAddonPrefs()
        prefs.toggle_overlays_turnOn_sequenceTimeline = not prefs.toggle_overlays_turnOn_sequenceTimeline

        # toggle on or off the overlay tools mode
        #  context.window_manager.UAS_shot_manager_display_overlay_tools = prefs.toggle_overlays_turnOn_sequenceTimeline

        return {"FINISHED"}


_classes = (UAS_ShotManager_OT_ToggleSeqTimelineWithOverlayTools,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
