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
    # prefs = config.getAddonPrefs()
    retimerApplyToSettings = retimerProps.getCurrentApplyToSettings()

    propCol = propertyColumn(layout, padding_left=2, align=False)
    # layout = layout.box()
    # layout = propCol

    if config.devDebug or "DEFAULT" == retimerApplyToSettings.id:
        settingsNameRow = propCol.row()

        if "DEFAULT" != retimerApplyToSettings.id:
            settingsNameRow.label(text="Settings:")
            settingsNameRow = settingsNameRow.row()
            settingsNameRow.label(text=f"{retimerApplyToSettings.name}")
        else:
            settingsNameRow.alert = True
            settingsNameRow.label(text="*** Invalid Settings: Default ***")
            settingsNameRow = settingsNameRow.row()
            settingsNameRow.operator("uas_shot_manager.retimerinitialize", text="Reset", icon="LOOP_BACK")

        propCol.separator(factor=0.5)

    if "SCENE" == retimerApplyToSettings.id:
        propCol.label(text="Retiming is applied to EVERYTHING in the scene, except:")

        messagesCol = propertyColumn(propCol, padding_left=4, padding_bottom=1, scale_y=0.8)
        messagesCol.label(text="- Compositor content: Currently not supported by the Retimer")
        messagesCol.label(text="- NLA Editor content: Currently not supported by the Retimer")
        # messagesCol.label(text="- Storyboard Shots: Their temporality is not related to the scene")
        messagesCol.label(text="- Unchecked entities below:")

        entitiesCol = propertyColumn(propCol, padding_left=6, padding_bottom=0, scale_y=1)

        stbRow = entitiesCol.row()
        stbRow.prop(
            retimerApplyToSettings,
            "applyToStoryboardShotRanges",
            text="Storyboard Shots",
        )
        # text="Storyboard Shots: Their temporality is not related to the scene",

        # doesnt work, need an enum
        # stbRow.prop_with_popover(
        #     retimerApplyToSettings, "applyToStoryboardShotRanges", panel="UAS_PT_SM_quicktooltip", text="tototo", icon="INFO"
        # )

        stbRowRight = stbRow.row()
        stbRowRight.alert = retimerApplyToSettings.applyToStoryboardShotRanges

        quickHelpInfo = retimerProps.getQuickHelp("APPLYTO_STORYBOARDSHOTS")
        # doc_op = stbRowRight.operator("shotmanager.open_documentation_url", text="", icon="INFO", emboss=False)
        # doc_op.path = quickHelpInfo[3]
        # tooltipStr = quickHelpInfo[1]
        # tooltipStr += f"\n{quickHelpInfo[2]}"
        # tooltipStr += f"\n\nOpen Shot Manager Retimer online documentation:\n     {doc_op.path}"
        # doc_op.tooltip = tooltipStr

        # quickTooltip(stbRowRight, "patate", title="Storyboard Shots", alert=retimerApplyToSettings.applyToStoryboardShotRanges)
        quickTooltip(
            stbRowRight,
            quickHelpInfo[2],
            title=quickHelpInfo[1],
            alert=retimerApplyToSettings.applyToStoryboardShotRanges,
        )

        entitiesCol.separator(factor=0.5)
        entitiesCol.prop(retimerApplyToSettings, "applyToTimeCursor", text="Time Cursor")
        entitiesCol.prop(retimerApplyToSettings, "applyToSceneRange", text="Scene Range")

    if "SELECTED_OBJECTS" == retimerApplyToSettings.id:
        split = propCol.split(factor=0.326)
        row = split.row(align=True)
        row.separator(factor=0.7)
        row.prop(retimerApplyToSettings, "onlyOnSelection", text="Selection Only")
        row = split.row(align=True)
        row.prop(retimerApplyToSettings, "includeLockAnim", text="Include Locked Anim")

        row = propCol.row(align=True)
        row.separator(factor=0.7)
        row.prop(retimerApplyToSettings, "snapKeysToFrames", text="Snap Keys to Frames")

        box = propCol.box()
        col = box.column()

        row = col.row(align=True)
        row.prop(retimerApplyToSettings, "applyToObjects")
        row.prop(retimerApplyToSettings, "applyToShapeKeys")
        row.prop(retimerApplyToSettings, "applytToGreasePencil")

        row = col.row(align=True)
        row.prop(retimerApplyToSettings, "applyToMarkers")

    if "LEGACY" == retimerApplyToSettings.id or config.devDebug:

        propRow = propCol.row()
        propRow.alert = config.devDebug and "LEGACY" != retimerApplyToSettings.id

        if config.devDebug and "LEGACY" != retimerApplyToSettings.id:
            propRow.label(text="Debug Infos:")

        if "SELECTED_OBJECTS" != retimerApplyToSettings.id:
            split = propRow.split(factor=0.326)
            row = split.row(align=True)
            row.separator(factor=0.7)
            row.prop(retimerApplyToSettings, "onlyOnSelection", text="Selection Only")
            row = split.row(align=True)
            row.prop(retimerApplyToSettings, "includeLockAnim", text="Include Locked Anim")

            row = propCol.row(align=True)
            row.separator(factor=0.7)
            row.prop(retimerApplyToSettings, "snapKeysToFrames", text="Snap Keys to Frames")

        propRow = propCol.row()
        propRow.alert = config.devDebug and "LEGACY" != retimerApplyToSettings.id

        box = propRow.box()
        col = box.column()

        if "SELECTED_OBJECTS" != retimerApplyToSettings.id:
            row = col.row(align=True)
            row.prop(retimerApplyToSettings, "applyToObjects")
            row.prop(retimerApplyToSettings, "applyToShapeKeys")
            row.prop(retimerApplyToSettings, "applytToGreasePencil")

            row = col.row(align=True)
            row.prop(retimerApplyToSettings, "applyToMarkers")

        row = col.row(align=True)
        row.scale_y = 0.3

        row = col.row(align=True)
        row.prop(retimerApplyToSettings, "applyToCameraShotRanges")
        row.prop(retimerApplyToSettings, "applyToVSE")
        row.label(text="")

    # time cursor and range
    ##########################
    if "LEGACY" == retimerApplyToSettings.id or config.devDebug:
        box = propCol.box()
        # box.alert = "SCENE" != retimerApplyToSettings.id

        col = box.column()

        row = col.row(align=True)
        row.prop(retimerApplyToSettings, "applyToTimeCursor", text="Time Cursor")
        row.prop(retimerApplyToSettings, "applyToSceneRange", text="Scene Range")
        # row.label(text="")
