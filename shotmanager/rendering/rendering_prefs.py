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
Prefs for Shot Manager render panel
"""

from bpy.types import Operator


#############
# Preferences
#############


class UAS_ShotManager_Render_Prefs(Operator):
    bl_idname = "uas_shot_manager.render_prefs"
    bl_label = "Render Settings"
    bl_description = "Display the Shot Manager Render Settings panel"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context):
        layout = self.layout

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        # Best play perfs ######
        layout.label(text="Rendering Add-on Preferences:")
        box = layout.box()
        box.use_property_decorate = False

        # main column, to allow title offset
        maincol = box.column()
        row = maincol.row()
        row.separator(factor=2)
        #  row.label(text="Check the tools and features that will be disabled when animation is playing:")

        # empty spacer column
        row = maincol.row()
        col = row.column()
        col.scale_x = 0.3
        col.label(text=" ")
        col = row.column()

        # # Sequence timeline ######
        # # layout.separator(factor=1)
        # layout.label(text="Sequence Timeline:")
        # box = layout.box()
        # box.use_property_decorate = False

        # # empty spacer column
        # row = box.row()
        # col = row.column()
        # col.scale_x = 0.3
        # col.label(text=" ")
        # col = row.column()

        # col.use_property_split = False
        # # col.use_property_decorate = False
        # col.prop(
        #     props, "seqTimeline_displayDisabledShots", text="Display Disabled Shots",
        # )

        # # Edit ######
        # layout.separator(factor=1)
        # layout.label(text="Edit:")
        # box = layout.box()
        # box.use_property_decorate = False
        # col = box.column()

        # col.use_property_split = True
        # col.prop(props, "editStartFrame", text="Index of the First Frame in the Edit:")

        box.separator(factor=0.5)

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}
