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
Markers navigation toolbar prefs ui
"""

from shotmanager.utils.utils_ui import propertyColumn
from shotmanager.config import config


def draw_markers_nav_bar_settings(layout):
    prefs = config.getAddonPrefs()

    propCol = propertyColumn(layout)

    propCol.label(text="Display in Editors:")
    row = propCol.row()
    row.separator(factor=5)
    row.prop(prefs, "mnavbar_display_in_timeline", text="Timeline")
    row.prop(prefs, "mnavbar_display_in_dopesheet", text="Dopesheet")
    row.prop(prefs, "mnavbar_display_in_vse", text="VSE")

    propCol.label(text="Show Widgets:")
    row = propCol.row()
    row.separator(factor=5)
    row.prop(prefs, "mnavbar_display_addRename", text="Add and Rename")
    row.prop(prefs, "mnavbar_display_filter", text="Filter")
    row.label(text=" ")
