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


from shotmanager.utils.utils_ui import propertyColumn, quickTooltip

from shotmanager.config import config


def drawApplyTo(context, retimerProps, layout):
    prefs = config.getShotManagerPrefs()
    retimerSettings = retimerProps.getCurrentApplyToSettings()

    propCol = propertyColumn(layout, padding_left=2, align=False)
    # layout = layout.box()
    # layout = propCol

    if config.devDebug or "DEFAULT" == retimerSettings.id:
        settingsNameRow = propCol.row()

        if "DEFAULT" != retimerSettings.id:
            settingsNameRow.label(text="Settings:")
            settingsNameRow = settingsNameRow.row()
            settingsNameRow.label(text=f"{retimerSettings.name}")
        else:
            settingsNameRow.alert = True
            settingsNameRow.label(text="*** Invalid Settings: Default ***")
            settingsNameRow = settingsNameRow.row()
            settingsNameRow.operator("uas_shot_manager.retimerinitialize", text="Reset", icon="LOOP_BACK")

        propCol.separator(factor=0.5)

    if "SCENE" == retimerSettings.id:
        propCol.label(text="Retiming is applied to EVERYTHING in the scene, except:")

        messagesCol = propertyColumn(propCol, padding_left=4, padding_bottom=1, scale_y=0.8)
        messagesCol.label(text="- Compositor content: Currently not supported by the Retimer")
        messagesCol.label(text="- NLA Editor content: Currently not supported by the Retimer")
        # messagesCol.label(text="- Storyboard Shots: Their temporality is not related to the scene")
        messagesCol.label(text="- Unchecked entities below:")

        entitiesCol = propertyColumn(propCol, padding_left=6, padding_bottom=0, scale_y=1)

        stbRow = entitiesCol.row()
        stbRow.prop(
            retimerSettings,
            "applyToStoryboardShots",
            text="Storyboard Shots",
        )
        # text="Storyboard Shots: Their temporality is not related to the scene",

        # doesnt work, need an enum
        # stbRow.prop_with_popover(
        #     retimerSettings, "applyToStoryboardShots", panel="UAS_PT_SM_quicktooltip", text="tototo", icon="INFO"
        # )

        stbRowRight = stbRow.row()
        stbRowRight.alert = retimerSettings.applyToStoryboardShots

        quickHelpInfo = retimerProps.getQuickHelp("APPLYTO_STORYBOARDSHOTS")
        # doc_op = stbRowRight.operator("shotmanager.open_documentation_url", text="", icon="INFO", emboss=False)
        # doc_op.path = quickHelpInfo[3]
        # tooltipStr = quickHelpInfo[1]
        # tooltipStr += f"\n{quickHelpInfo[2]}"
        # tooltipStr += f"\n\nOpen Shot Manager Retimer online documentation:\n     {doc_op.path}"
        # doc_op.tooltip = tooltipStr

        # quickTooltip(stbRowRight, "patate", title="Storyboard Shots", alert=retimerSettings.applyToStoryboardShots)
        quickTooltip(
            stbRowRight, quickHelpInfo[2], title=quickHelpInfo[1], alert=retimerSettings.applyToStoryboardShots
        )

        entitiesCol.separator(factor=0.5)
        entitiesCol.prop(prefs, "applyToTimeCursor", text="Time Cursor")
        entitiesCol.prop(prefs, "applyToSceneRange", text="Scene Range")

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

        row = col.row(align=True)
        row.prop(retimerSettings, "applyToMarkers")

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
            row.prop(retimerSettings, "applyToMarkers")

        row = col.row(align=True)
        row.scale_y = 0.3

        row = col.row(align=True)
        row.prop(retimerSettings, "applyToCameraShots")
        row.prop(retimerSettings, "applyToVSE")
        row.label(text="")

    # time cursor and range
    ##########################
    if "LEGACY" == retimerSettings.id or config.devDebug:
        box = propCol.box()
        # box.alert = "SCENE" != retimerSettings.id

        col = box.column()

        row = col.row(align=True)
        row.prop(prefs, "applyToTimeCursor", text="Time Cursor")
        row.prop(prefs, "applyToSceneRange", text="Scene Range")
        # row.label(text="")
