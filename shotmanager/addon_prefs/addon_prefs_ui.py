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
        text="Temporary preference values (for dialogs for instance) are only visible when global variable devDebug is True."
    )

    layout.label(text="Development and Debug:")
    box = layout.box()

    row = box.row()
    row.separator(factor=1)
    row.label(text="Debug Mode:")
    subrow = row.row()
    subrow.operator("uas_shot_manager.enable_debug", text="On").enable_debug = True
    subrow.operator("uas_shot_manager.enable_debug", text="Off").enable_debug = False

    if config.devDebug:
        subrow = box.row()
        strDebug = " *** Debug Mode is On ***"
        subrow.alert = True
        subrow.label(text=strDebug)

    box = layout.box()
    row = box.row()
    row.label(text="Debug Infos:")

    if config.devDebug:
        row = box.row()
        row.separator(factor=1)
        row.label(text="Add New Shot Dialog:")
        row = box.row()
        subbox = row.box()
        col = subbox.column(align=False)
        col.prop(self, "addShot_start")
        col.prop(self, "addShot_end")
