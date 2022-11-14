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
Prefs overlays tools
"""

import bpy
from bpy.types import Operator

from shotmanager import config


class UAS_ShotManager_OverlayTools_Prefs(Operator):
    bl_idname = "uas_shot_manager.overlay_tools_prefs"
    bl_label = "Overlay Tools Settings"
    bl_description = (
        "Display the Sequence Timeline, Interactive Shots Stack and Edit Settings panel"
        "\nfor the Shot Manager instanced in this scene"
    )
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context):
        # props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()

        layout = self.layout
        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        ###################################
        # Toggle overlay tools ######
        ###################################

        icon = config.icons_col["ShotManager_Tools_OverlayTools_32"]
        layout.label(text="Toggle Overlay Tools:", icon_value=icon.icon_id)
        box = layout.box()
        box.use_property_decorate = False

        # main column, to allow title offset
        maincol = box.column()
        row = maincol.row()
        row.separator(factor=2)
        row.label(text="Check the tools that will be enabled and disabled with the Overlay Tools mode:")

        # empty spacer column
        row = maincol.row()
        col = row.column()
        col.scale_x = 0.3
        col.label(text=" ")
        col = row.column()

        col.use_property_split = False
        linerow = col.row()
        linerow.prop(
            prefs,
            "toggle_overlays_turnOn_sequenceTimeline",
            text="Sequence Timeline",
        )
        linerow.prop(
            prefs,
            "toggle_overlays_turnOn_interactiveShotsStack",
            text="Interactive Shots Stack",
        )

        ###################################
        # # Best play perfs ######
        ###################################
        layout.label(text="Best Play Performance:", icon="INDIRECT_ONLY_ON")
        box = layout.box()
        box.use_property_decorate = False

        # main column, to allow title offset
        maincol = box.column()
        row = maincol.row()
        row.separator(factor=2)
        row.label(text="Check the tools and features that will be disabled when animation is playing:")

        # empty spacer column
        row = maincol.row()
        col = row.column()
        col.scale_x = 0.3
        col.label(text=" ")
        col = row.column()

        col.use_property_split = False
        linerow = col.row()
        linerow.prop(
            prefs,
            "best_play_perfs_turnOff_sequenceTimeline",
            text="Sequence Timeline",
        )
        linerow.prop(
            prefs,
            "best_play_perfs_turnOff_interactiveShotsStack",
            text="Interactive Shots Stack",
        )
        linerow.prop(prefs, "best_play_perfs_turnOff_mainUI", text="Main Panel UI")

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


_classes = (UAS_ShotManager_OverlayTools_Prefs,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
