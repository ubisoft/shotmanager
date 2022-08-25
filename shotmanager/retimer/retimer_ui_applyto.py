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
Retimer UI
"""

import bpy

from shotmanager.utils.utils_ui import collapsable_panel, propertyColumn, separatorLine

from shotmanager.config import config


def drawApplyTo(context, layout):
    retimerProps = context.scene.UAS_shot_manager_props.retimer
    prefs = config.getShotManagerPrefs()

    propCol = propertyColumn(layout, padding_left=2, align=False)
    # layout = layout.box()
    layout = propCol

    split = layout.split(factor=0.326)
    row = split.row(align=True)
    row.separator(factor=0.7)
    row.prop(retimerProps, "onlyOnSelection", text="Selection Only")
    row = split.row(align=True)
    row.prop(retimerProps, "includeLockAnim", text="Include Locked Anim")

    box = layout.box()
    col = box.column()

    row = col.row(align=True)
    row.prop(retimerProps, "applyToObjects")
    row.prop(retimerProps, "applyToShapeKeys")
    row.prop(retimerProps, "applytToGreasePencil")

    row = col.row(align=True)
    row.scale_y = 0.3

    row = col.row(align=True)
    row.prop(retimerProps, "applyToCameraShots")
    row.prop(retimerProps, "applyToVSE")
    row.label(text="")

    box = layout.box()
    col = box.column()

    row = col.row(align=True)
    row.prop(prefs, "applyToTimeCursor", text="Time Cursor")
    row.prop(prefs, "applyToSceneRange", text="Scene Range")
    # row.label(text="")
