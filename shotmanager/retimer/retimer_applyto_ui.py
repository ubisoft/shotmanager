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
Retimer ApplyTo UI
"""


from shotmanager.utils.utils_ui import propertyColumn

from shotmanager.config import config


def drawApplyTo(context, retimerSettings, layout):
    prefs = config.getShotManagerPrefs()

    propCol = propertyColumn(layout, padding_left=2, align=False)
    # layout = layout.box()
    # layout = propCol

    if config.devDebug:
        propCol.label(text=f"Settings: {retimerSettings.name}")
        propCol.separator(factor=0.5)

    if "SCENE" == retimerSettings.id:
        propCol.label(text="Retime is applied to EVERYTHING in the scene, except:")

        messagesCol = propertyColumn(propCol, padding_left=4, padding_bottom=2, scale_y=0.8)
        messagesCol.label(text="- Storyboard Shots: Their temporality is not related to the scene")
        messagesCol.label(text="- Compositor content: Currently not supported by the Retimer")
        messagesCol.label(text="- NLA Editor content: Currently not supported by the Retimer")

    if "SELECTED_OBJECTS" == retimerSettings.id:
        split = propCol.split(factor=0.326)
        row = split.row(align=True)
        row.separator(factor=0.7)
        row.prop(retimerSettings, "onlyOnSelection", text="Selection Only")
        row = split.row(align=True)
        row.prop(retimerSettings, "includeLockAnim", text="Include Locked Anim")

        box = propCol.box()
        col = box.column()

        row = col.row(align=True)
        row.prop(retimerSettings, "applyToObjects")
        row.prop(retimerSettings, "applyToShapeKeys")
        row.prop(retimerSettings, "applytToGreasePencil")

    if "LEGACY" == retimerSettings.id or config.devDebug:

        propRow = propCol.row()
        propRow.alert = config.devDebug and "LEGACY" != retimerSettings.id

        if config.devDebug and "LEGACY" != retimerSettings.id:
            propRow.label(text="Debug Infos:")

        if "SELECTED_OBJECTS" != retimerSettings.id:
            split = propRow.split(factor=0.326)
            row = split.row(align=True)
            row.separator(factor=0.7)
            row.prop(retimerSettings, "onlyOnSelection", text="Selection Only")
            row = split.row(align=True)
            row.prop(retimerSettings, "includeLockAnim", text="Include Locked Anim")

        propRow = propCol.row()
        propRow.alert = config.devDebug and "LEGACY" != retimerSettings.id

        box = propRow.box()
        col = box.column()

        if "SELECTED_OBJECTS" != retimerSettings.id:
            row = col.row(align=True)
            row.prop(retimerSettings, "applyToObjects")
            row.prop(retimerSettings, "applyToShapeKeys")
            row.prop(retimerSettings, "applytToGreasePencil")

        row = col.row(align=True)
        row.scale_y = 0.3

        row = col.row(align=True)
        row.prop(retimerSettings, "applyToCameraShots")
        row.prop(retimerSettings, "applyToVSE")
        row.label(text="")

    # time cursor and range
    ##########################

    box = propCol.box()
    col = box.column()

    row = col.row(align=True)
    row.prop(prefs, "applyToTimeCursor", text="Time Cursor")
    row.prop(prefs, "applyToSceneRange", text="Scene Range")
    # row.label(text="")
