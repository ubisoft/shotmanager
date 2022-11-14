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
2.5D Grease Pencil panel
"""

import bpy

from bpy.types import Panel

from shotmanager.features.greasepencil.greasepencil_ui import draw_greasepencil_play_tools

from shotmanager.config import config


class UAS_PT_ShotManagerGreasePencilPanelStdalone(Panel):
    # bl_label = "Shot Manager - Grease Pencil"
    # bl_idname = "UAS_PT_ShotManagerGreasePencilPanelStdalone"
    # bl_space_type = "VIEW_3D"
    # bl_region_type = "UI"
    # bl_category = "Shot Mng - Render"

    bl_idname = "UAS_PT_ShotManagerGreasePencilPanelStdalone"
    bl_label = "2.5D Grease Pencil Tools"
    bl_description = "Tools for 2.5D Grease Pencil Drawing"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        # props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()
        # displayPanel = prefs.preferences.separatedRenderPanel
        # displayPanel = displayPanel and props.getCurrentShot() is not None
        # return displayPanel and prefs.display_25D_greasepencil_panel
        return prefs.display_25D_greasepencil_panel

    # def draw_header(self, context):
    #     layout = self.layout
    #     layout.emboss = "NONE"

    #     row = layout.row(align=True)
    #     # icon = config.icons_col["ShotManager_Retimer_32"]
    #     # row.label(icon=icon.icon_id)
    #     row.label(icon="RENDER_ANIMATION")

    # def draw_header_preset(self, context):
    #     drawHeaderPreset(self, context)

    def draw(self, context):
        draw_greasepencil_play_tools(self, context, None)


_classes = (UAS_PT_ShotManagerGreasePencilPanelStdalone,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
