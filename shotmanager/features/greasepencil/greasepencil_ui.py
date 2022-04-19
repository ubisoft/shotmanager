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
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, StringProperty

from shotmanager.utils import utils
from shotmanager.utils import utils_greasepencil


def draw_greasepencil_shot_properties(sm_ui, context, shot):
    layout = sm_ui.layout
    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences
    scene = context.scene

    gp_child = None
    if shot is not None:
        shotIndex = props.getShotIndex(shot)
        if shot.camera is None:
            pass
        else:
            gp_child = utils.get_greasepencil_child(shot.camera)

    panelIcon = "TRIA_DOWN" if prefs.shot_greasepencil_expanded and gp_child is not None else "TRIA_RIGHT"

    box = layout.box()
    box.use_property_decorate = False
    row = box.row()
    extendSubRow = row.row(align=True)
    extendSubRow.prop(prefs, "shot_greasepencil_expanded", text="", icon=panelIcon, emboss=False)
    # row.separator(factor=1.0)

    subRow = row.row(align=False)
    # subRow.scale_x = 0.6
    subRow.label(text="Grease Pencil:")

    if gp_child is None:
        extendSubRow.enabled = False
        row.operator(
            "uas_shot_manager.add_grease_pencil", text="", icon="ADD", emboss=True
        ).cameraGpName = shot.camera.name

        # subSubRow.separator(factor=1.0)
        row.prop(props, "display_greasepencil_in_shotlist", text="")
        # subSubRow.separator(factor=0.5)  # prevents stange look when panel is narrow

    else:
        subRow.label(text=gp_child.name)
        subRow.operator("uas_shot_manager.select_grease_pencil", text="", icon="RESTRICT_SELECT_OFF").index = shotIndex
        subSubRow = subRow.row(align=True)
        subSubRow.prop(gp_child, "hide_select", text="")
        subSubRow.prop(gp_child, "hide_viewport", text="")
        subSubRow.prop(gp_child, "hide_render", text="")

        subRow = row.row(align=True)
        subRow.operator("uas_shot_manager.remove_grease_pencil", text="", icon="PANEL_CLOSE").shotIndex = shotIndex
        subRow.separator()
        subRow.prop(props, "display_greasepencil_in_shotlist", text="")

        if prefs.shot_greasepencil_expanded:
            row = box.row()
            row.prop(gp_child, "location")

        row = box.row()
        row.label(text="Canvas: ")

        canvasLayer = utils_greasepencil.get_grease_pencil_layer(
            gp_child, gpencil_layer_name="GP_Canvas", create_layer=False
        )
        if canvasLayer is None:
            # utils_greasepencil.get_grease_pencil_layer
            row.operator("uas_shot_manager.add_canvas_to_grease_pencil", text="+").gpName = gp_child.name
        else:
            row.prop(canvasLayer, "hide", text="")
            row.prop(canvasLayer, "opacity", text="")

        # row = box.row()
        # row.operator("uas_shot_manager.change_grease_pencil_opacity").gpObjectName = gp_child

