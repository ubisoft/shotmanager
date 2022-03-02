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
Draw the warnings component
"""


def drawWarnings(context, ui_component, warningsList, panelType=None):
    """panelType can be "MAIN" or "RENDERING"
    """
    if len(warningsList):
        prefs = context.preferences.addons["shotmanager"].preferences
        panelIcon = "TRIA_DOWN" if prefs.general_warning_expanded else "TRIA_RIGHT"

        box = ui_component.box()
        panelRow = box.row()
        panelRow.prop(prefs, "general_warning_expanded", text="", icon=panelIcon, emboss=False)
        titleRow = panelRow.row()
        titleRow.alert = True
        warningStr = f"Warnings: {len(warningsList)}"
        titleRow.label(text=warningStr)

        # display text near warnings ############
        # titleRowRight = panelRow.row()
        # titleRowRight.alignment = "RIGHT"
        # titleRowRight.alert = True
        # titleRowRight.label(text="test")

        if prefs.general_warning_expanded:
            mainRow = box.row()
            mainRow.separator(factor=2.0)
            warningsRow = mainRow.column(align=False)
            for w in warningsList:
                messages = w[0].split("\n")

                row = warningsRow.row()
                row.alert = True
                warningCol = row.column(align=False)
                warningCol.scale_y = 0.5
                for i, mess in enumerate(messages):
                    if 0 == i:
                        warningCol.label(text="-  " + mess)
                    else:
                        warningCol.label(text="    " + mess)

                if "MAIN" == panelType:
                    if 60 == w[1]:
                        warningCol.scale_y = 1.0
                        butsrow = warningCol.row()
                        butsrow.separator(factor=0.5)
                        butsrow.operator("uas_shot_manager.clear_markers_from_camera_binding", text="Clear Binding")
                        butsrow.operator(
                            "uas_shot_manager.convert_markers_from_camera_binding_to_shots", text="Convert Binding"
                        )
                        butsrow.separator(factor=0.5)

                warningCol.separator(factor=1.0)
