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

from ..config import config


##################################################################################
# Draw
##################################################################################
def draw_shotmanager_addon_prefs(self, context):
    layout = self.layout
    prefs = context.preferences.addons["shotmanager"].preferences

    box = layout.box()
    box.use_property_decorate = False
    col = box.column()
    col.use_property_split = True
    col.prop(prefs, "new_shot_duration", text="Default Shot Length")
    #    col.prop(prefs, "useLockCameraView", text="Use Lock Camera View")

    layout.label(text="Rendering:")
    box = layout.box()
    row = box.row()
    row.separator(factor=1)
    row.prop(prefs, "separatedRenderPanel")

    layout.label(
        text="Temporary preference values (for dialogs for instance) are only visible when global variable uasDebug is True."
    )

    if config.uasDebug:
        layout.label(text="Add New Shot Dialog:")
        box = layout.box()
        col = box.column(align=False)
        col.prop(self, "addShot_start")
        col.prop(self, "addShot_end")

