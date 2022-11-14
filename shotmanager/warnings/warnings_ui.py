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

from shotmanager.config import config


def drawWarnings(context, ui_component, warningsList, panelType="MAIN"):
    """panelType can be 'MAIN' or 'RENDER'"""

    if not len(warningsList):
        return

    numWarnings_All = 0
    numWarnings_Main = 0
    numWarnings_Render = 0

    sepHeight = 0.5

    for _i, w in enumerate(warningsList):
        if "ALL" == w[2]:
            numWarnings_All += 1
        elif "MAIN" == w[2]:
            numWarnings_Main += 1
        elif "RENDER" == w[2]:
            numWarnings_Render += 1

    if "MAIN" == panelType:
        numWarnings = numWarnings_All + numWarnings_Main
    # elif "RENDER" == panelType:
    else:
        numWarnings = numWarnings_All + numWarnings_Render

    if not numWarnings:
        return

    prefs = config.getAddonPrefs()
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
            if "ALL" == w[2] or panelType == w[2]:
                messages = w[0].split("\n")

                row = warningsRow.row()
                row.alert = True
                warningCol = row.column(align=False)
                warningCol.scale_y = 0.7
                for i, mess in enumerate(messages):
                    if 0 == i:
                        warningCol.label(text="-  " + mess)
                    else:
                        warningCol.label(text="   " + mess)

                # add camera binding conversion buttons
                if 60 == w[1]:
                    warningCol.scale_y = 1.0
                    butsrow = warningCol.row()
                    butsrow.separator(factor=0.5)
                    butsrow.operator("uas_shot_manager.clear_markers_from_camera_binding", text="Clear Binding")
                    butsrow.operator(
                        "uas_shot_manager.convert_markers_from_cam_binding_to_shots", text="Convert Binding"
                    )
                    butsrow.separator(factor=0.5)

                ##############################
                # dependencies - 7x
                ##############################

                # add go to stamp info download button
                elif 71 == w[1]:
                    butsrow = warningCol.row()
                    butsrow.separator(factor=0.5)
                    butsrow.scale_y = 2.0
                    doc_op = butsrow.operator(
                        "shotmanager.open_documentation_url", text="Get Stamp Info Latest Release", icon="WORLD_DATA"
                    )
                    doc_op.path = "https://github.com/ubisoft/stampinfo/releases/latest"
                    doc_op.tooltip = "Open Stamp Info latest release page on GitHub: " + doc_op.path
                    butsrow.separator(factor=0.5)

                ##############################
                # rendering - 1xx
                ##############################

                # add render settings preset reset button
                elif 110 == w[1]:
                    warningCol.scale_y = 1.0
                    butsrow = warningCol.row()
                    butsrow.separator(factor=0.5)
                    resetOp = butsrow.operator(
                        "uas_shotmanager.querybox", text="Reset Render to Default Values...", icon="LOOP_BACK"
                    )
                    resetOp.width = 400
                    resetOp.message = "Reset all the rendering properties to their default value?"
                    resetOp.function_name = "reset_render_properties"
                    butsrow.separator(factor=0.5)

                # render resolution is the same as the one set in project settings
                elif 131 == w[1]:
                    warningCol.separator(factor=sepHeight)
                    butsrow = warningCol.row()
                    butsrow.scale_y = 1.4
                    butsrow.separator(factor=0.5)
                    butsrow.operator("uas_shot_manager.set_render_res_as_project_res", text="Apply Project Resolution")
                    butsrow.separator(factor=0.5)

                # render pixel aspects X or Y are used
                elif 134 == w[1]:
                    warningCol.separator(factor=sepHeight)
                    butsrow = warningCol.row()
                    butsrow.scale_y = 1.4
                    butsrow.separator(factor=0.5)
                    butsrow.operator("uas_shot_manager.turn_off_pixel_aspect", text="Reset Render Pixel Aspect")
                    butsrow.separator(factor=0.5)

                # current fps is valid according to the project settings
                elif 136 == w[1]:
                    warningCol.separator(factor=sepHeight)
                    butsrow = warningCol.row()
                    butsrow.scale_y = 1.4
                    butsrow.separator(factor=0.5)
                    butsrow.operator("uas_shot_manager.set_render_fps_as_project_fps", text="Apply Project FPS")
                    butsrow.separator(factor=0.5)

                # scene metadata activated and they will be written on rendered images
                elif 140 == w[1]:
                    warningCol.separator(factor=sepHeight)
                    butsrow = warningCol.row()
                    butsrow.scale_y = 1.4
                    butsrow.separator(factor=0.5)
                    butsrow.operator("uas_shot_manager.turn_off_burn_into_image", text="Turn Off Burn Into Images")
                    butsrow.separator(factor=0.5)

                warningCol.separator(factor=1.0)
