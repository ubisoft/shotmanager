import os
import importlib
from pathlib import Path
import subprocess
import platform

import bpy

from bpy.props import BoolProperty, PointerProperty
from bpy.types import Panel, Operator, Menu

import opentimelineio as otio


from ..properties import vsm_props
from ..operators import tracks

icons_col = None


######
# Video Shot Manager main panel #
######


class UAS_PT_VideoShotManager(Panel):
    bl_label = "UAS Video Shot Manager"
    bl_idname = "UAS_PT_Video_Shot_Manager"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "UAS Video Shot Man"

    def draw_header(self, context):
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        # About... panel
        if context.window_manager.UAS_video_shot_manager_displayAbout:
            # _emboss = True
            row.alert = True
        else:
            #    _emboss = False
            row.alert = False

        global icons_col
        if icons_col is not None:
            icon = icons_col["General_Ubisoft_32"]
            row.prop(
                context.window_manager, "UAS_video_shot_manager_displayAbout", icon_value=icon.icon_id, icon_only=True
            )
        else:
            row.prop(context.window_manager, "UAS_video_shot_manager_displayAbout")

    # def draw_header_preset(self, context):
    #     layout = self.layout
    #     layout.emboss = "NONE"
    #     row = layout.row(align=True)

    #     row.operator("uas_shot_manager.render_openexplorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
    #         bpy.data.filepath
    #     )

    #     #    row.operator("render.opengl", text="", icon='IMAGE_DATA')
    #     #   row.operator("render.opengl", text="", icon='RENDER_ANIMATION').animation = True
    #     #    row.operator("screen.screen_full_area", text ="", icon = 'FULLSCREEN_ENTER').use_hide_panels=False
    #     row.separator(factor=3)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        vsm_props = scene.UAS_vsm_props

        row = layout.row()

        ################
        # About... panel
        if context.window_manager.UAS_video_shot_manager_displayAbout:
            row = layout.row()
            aboutStr = "About UAS Video Shot Manager..."
            row.label(text=aboutStr)

            row = layout.row()
            box = row.box()
            #    aboutStr = "Create a set of camera shots and edit them\nin the 3D View as you would do with video clips."
            box.label(text="Create a set of camera shots and edit them")
            box.label(text="in the 3D View as you would do with video clips.")
            #    box = row.box()

            row = layout.row()
            row.separator(factor=1.4)

        ################
        # tracks

        row = layout.row()  # just to give some space...
        row.label(text="Tracks")

        box = layout.box()
        row = box.row()
        templateList = row.template_list(
            "UAS_UL_VideoShotManager_Items", "", vsm_props, "tracks", vsm_props, "selected_track_index", rows=6,
        )

        col = row.column(align=True)
        col.operator("uas_video_shot_manager.add_track", icon="ADD", text="")
        col.operator("uas_video_shot_manager.duplicate_track", icon="DUPLICATE", text="")
        col.operator("uas_video_shot_manager.remove_track", icon="REMOVE", text="")
        col.separator()
        col.operator("uas_video_shot_manager.list_action", icon="TRIA_UP", text="").action = "UP"
        col.operator("uas_video_shot_manager.list_action", icon="TRIA_DOWN", text="").action = "DOWN"
        col.separator()
        col.menu("UAS_MT_Video_Shot_Manager_toolsmenu", icon="TOOL_SETTINGS", text="")

    # layout.separator ( factor = 1 )


#############
# tracks
#############


class UAS_UL_VideoShotManager_Items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        global icons_col
        vsm_props = context.scene.UAS_vsm_props
        current_track_index = vsm_props.current_track_index

        c = layout.column()
        #         c.operator("uas_shot_manager.set_current_shot", icon_value=icon.icon_id, text="").index = index
        #         layout.separator(factor=0.1)

        #         c = layout.column()
        grid_flow = c.grid_flow(align=False, columns=9, even_columns=False)

        if vsm_props.display_color_in_tracklist:
            grid_flow.scale_x = 0.15
            grid_flow.prop(item, "color", text="")
            grid_flow.scale_x = 1.0

        #         #  grid_flow.prop ( item, "enabled", text = item.name )

        grid_flow.scale_x = 0.08
        # grid_flow.alignment = 'LEFT'
        grid_flow.prop(item, "enabled", text=" ")  # keep the space in the text !!!
        #   grid_flow.separator( factor = 0.5)
        grid_flow.scale_x = 0.6
        grid_flow.prop(item, "vseTrackIndex", text=" ")
        grid_flow.scale_x = 0.8
        grid_flow.label(text=item.name)

        grid_flow.prop(item, "shotManagerScene", text=" ")
        # grid_flow.prop(item, "shotManagerTake", text=" ")
        grid_flow.prop(item, "current_take_name")
        grid_flow.prop(item, "trackType", text=" ")

        grid_flow.operator(
            "uas_video_shot_manager.update_vse_track", text="", icon="FILE_REFRESH"
        ).trackName = item.name

        grid_flow.operator("uas_video_shot_manager.go_to_specified_scene").trackName = item.name


# ##################
# # track properties
# ##################


class UAS_PT_VideoShotManager_TrackProperties(Panel):
    bl_label = " "  # "Current Track Properties" # keep the space !!
    bl_idname = "UAS_PT_Video_Shot_Manager_TrackProperties"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "UAS Video Shot Man"
    bl_parent_id = "UAS_PT_Video_Shot_Manager"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        row.label(text="Selected Track Properties")

    def draw(self, context):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props

        track = vsm_props.getTrack(vsm_props.selected_track_index)

        layout = self.layout

        if track is not None:
            box = layout.box()

            # name and color
            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            grid_flow.prop(track, "name", text="Name")
            #   grid_flow.scale_x = 0.7
            grid_flow.prop(track, "color", text="")
            #   grid_flow.scale_x = 1.0
            grid_flow.prop(vsm_props, "display_color_in_tracklist", text="")
            row.separator(factor=0.5)  # prevents stange look when panel is narrow

    @classmethod
    def poll(cls, context):
        vsm_props = context.scene.UAS_vsm_props
        track = vsm_props.getTrack(vsm_props.selected_track_index)
        val = track

        return val


#################
# tools for tracks
#################


class UAS_MT_VideoShotManager_ToolsMenu(Menu):
    bl_idname = "UAS_MT_Video_Shot_Manager_toolsmenu"
    bl_label = "Tracks Tools"
    bl_description = "Tracks Tools"

    def draw(self, context):

        # Copy menu entries[ ---
        layout = self.layout
        row = layout.row(align=True)

        # row.label(text="Tools for Tracks:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_video_shot_manager.remove_multiple_tracks", text="Remove Disabled Tracks").action = "DISABLED"

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_video_shot_manager.remove_multiple_tracks", text="Remove All Tracks").action = "ALL"

        layout.separator()


_classes = (
    UAS_PT_VideoShotManager,
    UAS_PT_VideoShotManager_TrackProperties,
    UAS_UL_VideoShotManager_Items,
    UAS_MT_VideoShotManager_ToolsMenu,
)


def register():
    print("\n *** *** Resistering Video Shot Manager *** *** \n")
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
