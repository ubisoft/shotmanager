import bpy

from bpy.types import Panel, Menu, Operator
from bpy.props import IntProperty, EnumProperty, BoolProperty, FloatProperty, StringProperty

from ..properties import vsm_props
from ..operators import tracks

import shotmanager.config as config
from shotmanager.utils import utils

from .vsm_ui import UAS_PT_VideoShotManager


######
# Time control panel #
######


class UAS_PT_VideoShotManagerTimeControl(Panel):
    bl_idname = "UAS_PT_VideoShotManagerTimeControlPanel"
    bl_label = "Time Control"
    bl_description = "Time Control Options"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "UAS Video Shot Man"
    #  bl_parent_id = "UAS_PT_Video_Shot_Manager"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props
        layout = self.layout

        #########################################
        # Markers
        #########################################

        layout.label(text="Markers:")
        box = layout.box()
        row = box.row()
        subRow = row.row(align=True)
        subRow.operator("uas_video_shot_manager.go_to_marker", text="", icon="REW").goToMode = "FIRST"
        subRow.operator("uas_video_shot_manager.go_to_marker", text="", icon="TRIA_LEFT").goToMode = "PREVIOUS"
        currentMarker = utils.getMarkerAtFrame(scene, scene.frame_current)
        if currentMarker is not None:
            row.label(text=f"Marker: {currentMarker.name}")
            subRow = row.row(align=True)
            subRow.operator(
                "uas_video_shot_manager.add_marker", text="", icon="SYNTAX_OFF"
            ).markerName = currentMarker.name
            subRow.operator("uas_video_shot_manager.delete_marker", text="", icon="X")
        else:
            row.label(text="Marker: -")
            subRow = row.row(align=True)
            subRow.operator(
                "uas_video_shot_manager.add_marker", text="", icon="ADD"
            ).markerName = f"F_{scene.frame_current}"
            subSubRow = subRow.row(align=True)
            subSubRow.enabled = False
            subSubRow.operator("uas_video_shot_manager.delete_marker", text="", icon="X")

        subRow = row.row(align=True)
        subRow.operator("uas_video_shot_manager.go_to_marker", text="", icon="TRIA_RIGHT").goToMode = "NEXT"
        subRow.operator("uas_video_shot_manager.go_to_marker", text="", icon="FF").goToMode = "LAST"

        prefs = context.preferences.addons["shotmanager"].preferences
        subRow = row.row(align=True)
        subRow.prop(prefs, "mnavbar_use_filter", text="", icon="FILTER")
        subSubRow = subRow.row(align=True)
        subSubRow.enabled = prefs.mnavbar_use_filter
        subSubRow.prop(prefs, "mnavbar_filter_text", text="")

        #########################################
        # Zoom
        #########################################

        # layout.separator(factor=1)
        layout.label(text="Zoom:")

        box = layout.box()
        row = box.row()
        row.operator("uas_video_shot_manager.zoom_view", text="Current Frame").zoomMode = "TOCURRENTFRAME"
        row.operator("uas_video_shot_manager.zoom_view", text="Time Range").zoomMode = "TIMERANGE"
        row.operator("uas_video_shot_manager.zoom_view", text="Sel. Clips").zoomMode = "SELECTEDCLIPS"
        row.operator("uas_video_shot_manager.zoom_view", text="All Clips").zoomMode = "ALLCLIPS"
        # op = row.operator("uas_video_shot_manager.zoom_view", text="Track Clips").zoomMode = "TRACKCLIPS"
        op = row.operator("uas_video_shot_manager.zoom_view", text="Track Clips")
        op.zoomMode = "TRACKCLIPS"
        op.trackIndex = vsm_props.selected_track_index

        #########################################
        # Time
        #########################################

        # layout.separator(factor=1)
        layout.label(text="Time Range:")

        box = layout.box()
        row = box.row()
        row.operator("uas_video_shot_manager.frame_time_range", text="Frame Selected Clips").frameMode = "SELECTEDCLIPS"
        row.operator("uas_video_shot_manager.frame_time_range", text="Frame All Clips").frameMode = "ALLCLIPS"

        row = box.row(align=False)
        subRow = row.row(align=False)
        subRow.prop(scene, "use_preview_range", text="")
        subRow = row.row(align=True)
        if scene.use_preview_range:
            # row.use_property_split = False
            subRow.operator("uas_utils.get_current_frame_for_time_range", text="", icon="TRIA_UP_BAR").opArgs = (
                "{'frame_preview_start': " + str(scene.frame_current) + "}"
            )
            subRow.prop(scene, "frame_preview_start", text="Start")
            # subRow.operator("uas_video_shot_manager.frame_time_range", text="", icon="CENTER_ONLY")
            subRow.operator("uas_video_shot_manager.zoom_view", text="", icon="CENTER_ONLY").zoomMode = "TIMERANGE"
            subRow.prop(scene, "frame_preview_end", text="End")
            subRow.operator("uas_utils.get_current_frame_for_time_range", text="", icon="TRIA_UP_BAR").opArgs = (
                "{'frame_preview_end': " + str(scene.frame_current) + "}"
            )
            row.label(text=f"Duration: {scene.frame_preview_end - scene.frame_preview_start + 1}")
        else:
            subRow.operator("uas_utils.get_current_frame_for_time_range", text="", icon="TRIA_UP_BAR").opArgs = (
                "{'frame_start': " + str(scene.frame_current) + "}"
            )
            subRow.prop(scene, "frame_start", text="Start")
            # subRow.operator("uas_video_shot_manager.frame_time_range", text="", icon="CENTER_ONLY")
            subRow.operator("uas_video_shot_manager.zoom_view", text="", icon="CENTER_ONLY").zoomMode = "TIMERANGE"
            subRow.prop(scene, "frame_end", text="End")
            subRow.operator("uas_utils.get_current_frame_for_time_range", text="", icon="TRIA_UP_BAR").opArgs = (
                "{'frame_end': " + str(scene.frame_current) + "}"
            )
            row.label(text=f"Duration: {scene.frame_end - scene.frame_start + 1}")


_classes = (UAS_PT_VideoShotManagerTimeControl,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
