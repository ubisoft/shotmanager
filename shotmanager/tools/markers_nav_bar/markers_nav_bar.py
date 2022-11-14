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
Markers navigation toolbar
"""

import bpy

from shotmanager.utils import utils_markers

from shotmanager.config import config


def draw_markers_nav_bar_in_timeline(self, context):
    prefs = config.getAddonPrefs()
    if prefs.mnavbar_display_in_timeline:
        row = self.layout.row(align=False)
        row.separator(factor=3)
        row.alignment = "RIGHT"
        draw_markers_nav_bar(context, row)


def draw_markers_nav_bar_in_dopesheet(self, context):
    prefs = config.getAddonPrefs()
    if prefs.mnavbar_display_in_dopesheet:
        row = self.layout.row(align=False)
        row.separator(factor=3)
        row.alignment = "RIGHT"
        draw_markers_nav_bar(context, row)


def draw_markers_nav_bar_in_vse(self, context):
    prefs = config.getAddonPrefs()
    if prefs.mnavbar_display_in_vse:
        row = self.layout.row(align=False)
        row.separator(factor=3)
        row.alignment = "RIGHT"
        draw_markers_nav_bar(context, row)


def draw_markers_nav_bar(context, layout):
    scene = context.scene
    prefs = config.getAddonPrefs()

    # layout = self.layout

    row = layout.row(align=False)
    # row.separator(factor=3)
    # row.alignment = "RIGHT"

    # row.label(text="toto dsf trterte")
    # row.operator("bpy.ops.time.view_all")

    # layout.label(text="Markers:")
    # box = layout.box()
    # row = box.row()
    subRow = row.row(align=True)
    subRow.operator("uas_video_tracks.go_to_marker", text="", icon="REW").goToMode = "FIRST"
    subRow.operator("uas_video_tracks.go_to_marker", text="", icon="TRIA_LEFT").goToMode = "PREVIOUS"

    subRow = row.row(align=True)
    # subRow.prop(prefs, "mnavbar_use_view_frame")

    icon = config.icons_col["MarkersNavBar_ViewFrame_32"]
    # subRow.operator(
    #     "uas_video_tracks.view_frame", depress=prefs.mnavbar_use_view_frame, text="", icon_value=icon.icon_id
    # )
    subRow.prop(prefs, "mnavbar_use_view_frame", text="", icon_value=icon.icon_id)

    subRow = row.row(align=True)
    subRow.operator("uas_video_tracks.go_to_marker", text="", icon="TRIA_RIGHT").goToMode = "NEXT"
    subRow.operator("uas_video_tracks.go_to_marker", text="", icon="FF").goToMode = "LAST"

    if prefs.mnavbar_display_addRename:
        currentMarker = utils_markers.getMarkerAtFrame(scene, scene.frame_current)

        if currentMarker is not None:
            row.label(text=f"Marker: {currentMarker.name}")
            subRow = row.row(align=True)
            subRow.operator("uas_video_tracks.add_marker", text="", icon="SYNTAX_OFF").markerName = currentMarker.name
            subRow.operator("uas_video_tracks.delete_marker", text="", icon="X")
        else:
            row.label(text="Marker: -")
            subRow = row.row(align=True)
            subRow.operator("uas_video_tracks.add_marker", text="", icon="ADD").markerName = f"F_{scene.frame_current}"
            subSubRow = subRow.row(align=True)
            subSubRow.enabled = False
            subSubRow.operator("uas_video_tracks.delete_marker", text="", icon="X")

    if prefs.mnavbar_display_filter:
        subRow = row.row(align=True)
        subRow.prop(prefs, "mnavbar_use_filter", text="", icon="FILTER")
        subSubRow = subRow.row(align=True)
        subSubRow.enabled = prefs.mnavbar_use_filter
        subSubRow.prop(prefs, "mnavbar_filter_text", text="")


def display_markersNavBar_in_editor(display_value):
    if display_value:
        # timeline:
        bpy.types.TIME_MT_editor_menus.append(draw_markers_nav_bar_in_timeline)
        # dopesheet:
        bpy.types.DOPESHEET_MT_editor_menus.append(draw_markers_nav_bar_in_dopesheet)
        # vse:
        bpy.types.SEQUENCER_MT_editor_menus.append(draw_markers_nav_bar_in_vse)
    else:
        # timeline:
        bpy.types.TIME_MT_editor_menus.remove(draw_markers_nav_bar_in_timeline)
        # dopesheet:
        bpy.types.DOPESHEET_MT_editor_menus.remove(draw_markers_nav_bar_in_dopesheet)
        # vse:
        bpy.types.SEQUENCER_MT_editor_menus.remove(draw_markers_nav_bar_in_vse)


def register():
    # lets add ourselves to the main header
    # bpy.types.TIME_MT_editor_menus.prepend(draw_op_item)

    # bpy.types.TIME_MT_editor_menus.append(draw_markers_nav_bar_in_timeline)
    # #   bpy.types.SEQUENCER_HT_header.append(draw_markers_nav_bar_in_vse)
    # #  bpy.types.SEQUENCER_HT_tool_header.append(draw_markers_nav_bar_in_vse)
    # #  bpy.types.SEQUENCER_MT_navigation.append(draw_markers_nav_bar_in_vse)
    # bpy.types.SEQUENCER_MT_editor_menus.append(draw_markers_nav_bar_in_vse)

    #   bpy.types.TIME_HT_editor_buttons.append(draw_op_item)
    # bpy.types.TIME_MT_editor_menus.append(draw_item)
    # bpy.types.TIME_MT_view.append(draw_item)

    prefs = config.getAddonPrefs()
    display_markersNavBar_in_editor(prefs.display_markersNavBar_tool)


def unregister():
    display_markersNavBar_in_editor(False)

    # bpy.types.TIME_MT_editor_menus.remove(draw_markers_nav_bar_in_timeline)
    # # bpy.types.SEQUENCER_HT_header.remove(draw_markers_nav_bar_in_vse)
    # # bpy.types.SEQUENCER_HT_tool_header.remove(draw_markers_nav_bar_in_vse)
    # bpy.types.SEQUENCER_MT_editor_menus.remove(draw_markers_nav_bar_in_vse)


# if __name__ == "__main__":
#     register()

#     # The menu can also be called from scripts
#     bpy.ops.wm.call_menu(name=MyCustomMenu.bl_idname)
