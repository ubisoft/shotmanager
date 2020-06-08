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
# Shot Manager main panel #
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
        row.label(text="Tot4o")

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
        # shots

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
# Shots
#############


class UAS_UL_VideoShotManager_Items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        global icons_col
        vsm_props = context.scene.UAS_vsm_props
        current_track_index = vsm_props.current_track_index

        #         if item.enabled:
        #             icon = icons_col[f"ShotMan_Enabled{cam}"]
        #             if item.start <= context.scene.frame_current <= item.end:
        #                 icon = icons_col[f"ShotMan_EnabledCurrent{cam}"]
        #         else:
        #             icon = icons_col[f"ShotMan_Disabled{cam}"]

        c = layout.column()
        #         c.operator("uas_shot_manager.set_current_shot", icon_value=icon.icon_id, text="").index = index
        #         layout.separator(factor=0.1)

        #         c = layout.column()
        grid_flow = c.grid_flow(align=True, columns=9, even_columns=False)
        #         if item.camera is None:
        #             grid_flow.alert = True

        #         if props.display_color_in_shotlist:
        #             grid_flow.scale_x = 0.15
        #             grid_flow.prop(item, "color", text="")
        #             grid_flow.scale_x = 1.0

        #         #  grid_flow.prop ( item, "enabled", text = item.name )

        #         grid_flow.scale_x = 0.08
        #         # grid_flow.alignment = 'LEFT'
        #         grid_flow.prop(item, "enabled", text=" ")  # keep the space in the text !!!
        #         #   grid_flow.separator( factor = 0.5)
        #         grid_flow.scale_x = 0.8
        grid_flow.label(text=item.name)


#         #   grid_flow.alignment = 'RIGHT'

#         grid_flow.scale_x = 0.5


# ##################
# # track properties
# ##################


class UAS_PT_VideoShotManager_TrackProperties(Panel):
    bl_label = " "  # "Current Track Properties" # keep the space !!
    bl_idname = "UAS_PT_Video_Shot_Manager_track_properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    # bl_parent_id = "UAS_PT_VideoShotManager"
    #     def draw_header(self, context):
    #         scene = context.scene
    #         layout = self.layout
    #         layout.emboss = "NONE"
    #         row = layout.row(align=True)

    #         propertiesModeStr = "Current Shot Properties"
    #         if "SELECTED" == scene.UAS_shot_manager_props.current_shot_properties_mode:
    #             propertiesModeStr = "Selected Shot Properties"
    #         row.label(text=propertiesModeStr)

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props


#         #  shotPropertiesModeIsCurrent = not ('SELECTED' == props.current_shot_properties_mode)

#         shot = None
#         # if shotPropertiesModeIsCurrent is true then the displayed shot properties are taken from the CURRENT shot, else from the SELECTED one
#         if not ("SELECTED" == props.current_shot_properties_mode):
#             shot = props.getCurrentShot()
#         else:
#             shot = props.getShot(props.selected_shot_index)

#         layout = self.layout

#         if shot is not None:
#             box = layout.box()

#             # name and color
#             row = box.row()
#             row.separator(factor=1.0)
#             c = row.column()
#             grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
#             grid_flow.prop(shot, "name", text="Name")
#             #   grid_flow.scale_x = 0.7
#             grid_flow.prop(shot, "color", text="")
#             #   grid_flow.scale_x = 1.0
#             grid_flow.prop(props, "display_color_in_shotlist", text="")
#             row.separator(factor=0.5)  # prevents stange look when panel is narrow

#             # Duration
#             row = box.row()
#             row.separator(factor=1.0)
#             c = row.column()
#             grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
#             # row.label ( text = r"Duration: " + str(shot.getDuration()) + " frames" )
#             grid_flow.label(text="Duration: ")
#             grid_flow.label(text=str(shot.getDuration()) + " frames")
#             grid_flow.prop(props, "display_duration_in_shotlist", text="")
#             row.separator(factor=0.5)  # prevents stange look when panel is narrow

#             # camera and lens
#             row = box.row()
#             row.separator(factor=1.0)
#             c = row.column()
#             grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
#             if shot.camera is None:
#                 grid_flow.alert = True
#             grid_flow.prop(shot, "camera", text="Camera")
#             if shot.camera is None:
#                 grid_flow.alert = False
#             grid_flow.prop(props, "display_camera_in_shotlist", text="")

#             # c.separator( factor = 0.5 )   # prevents stange look when panel is narrow
#             grid_flow.scale_x = 0.7
#             #     row.label ( text = "Lens: " )
#             grid_flow.use_property_decorate = True
#             if shot.camera is not None:
#                 grid_flow.prop(shot.camera.data, "lens", text="Lens")
#             else:
#                 grid_flow.alert = True
#                 grid_flow.operator("uas_shot_manager.empty", text="No Lens")
#                 grid_flow.alert = False
#             grid_flow.scale_x = 1.0
#             grid_flow.prop(props, "display_lens_in_shotlist", text="")
#             row.separator(factor=0.5)  # prevents stange look when panel is narrow

#             box.separator(factor=0.5)

#             # Output
#             row = box.row()
#             row.separator(factor=1.0)
#             c = row.column()
#             grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
#             grid_flow.label(text="Output: ")
#             grid_flow.label(text=str(shot.getOutputFileName()))
#             grid_flow.operator("uas_shot_manager.render_openexplorer", emboss=True, icon="FILEBROWSER", text="")
#             row.separator(factor=0.5)  # prevents stange look when panel is narrow

#             # row.prop ( context.props, "display_duration_in_shotlist", text = "" )

#     @classmethod
#     def poll(cls, context):
#         props = context.scene.UAS_shot_manager_props
#         if not ("SELECTED" == props.current_shot_properties_mode):
#             shot = props.getCurrentShot()
#         else:
#             shot = props.getShot(props.selected_shot_index)
#         val = len(context.scene.UAS_shot_manager_props.getTakes()) and shot

#         return val


#################
# tools for shots
#################


class UAS_MT_VideoShotManager_ToolsMenu(Menu):
    bl_idname = "UAS_MT_Video_Shot_Manager_toolsmenu"
    bl_label = "Shots Tools"
    bl_description = "Shots Tools"

    def draw(self, context):
        scene = context.scene

        # marker_list         = context.scene.timeline_markers
        # list_marked_cameras = [o.camera for o in marker_list if o != None]

        ## Copy menu entries[ ---
        layout = self.layout
        row = layout.row(align=True)

        # row.label(text="Tools for Shots:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_video_shot_manager.remove_multiple_tracks", text="Remove Disabled Tracks").action = "DISABLED"

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_video_shot_manager.remove_multiple_tracks", text="Remove All Tracks").action = "ALL"

        layout.separator()

        # row = layout.row(align=True)
        # row.operator_context = 'INVOKE_DEFAULT'
        # row.operator ( "uas_shot_manager.debug_fixshotsparent")

        # row = layout.row(align=True)
        # if len(selectedObj) <= 1 or scene.camera not in selectedObj: row.enabled = False
        # else: row.enabled = True
        # row.operator_context = 'INVOKE_DEFAULT'
        # row.operator("cameramanager.camera_tools",text='copy Rotation').tool='ROTATION'

        # row = layout.row(align=True)
        # if len(selectedObj) <= 1 or scene.camera not in selectedObj: row.enabled = False
        # else: row.enabled = True
        # row.operator("cameramanager.camera_tools",text="copy Lens Settings").tool="LENS"
        # ## ]Copy menu entries

        # layout.separator()

        # # tools for shots ###
        # row = layout.row(align=True)
        # row.label(text="Tools for Shots:")

        # row = layout.row(align=True)
        # row.operator_context = "INVOKE_DEFAULT"
        # row.operator("uas_shot_manager.create_shots_from_each_camera")

        # row = layout.row(align=True)
        # row.operator_context = "INVOKE_DEFAULT"
        # row.operator("uas_shot_manager.unique_cameras")

        # row = layout.row(align=True)
        # row.operator_context = "INVOKE_DEFAULT"
        # row.operator("uas_shot_manager.shots_removecamera")

        # # import shots ###

        # layout.separator()
        # row = layout.row(align=True)
        # row.label(text="Import Shots:")

        # row = layout.row(align=True)
        # row.operator_context = "INVOKE_DEFAULT"
        # row.operator("uasotio.openfilebrowser", text="Import Shots From OTIO")
        # # wkip debug - to remove:
        # row = layout.row(align=True)
        # row.operator("uasshotmanager.importotio", text="Import Shots From OTIO - Debug")

        # # tools for precut ###
        # layout.separator()
        # row = layout.row(align=True)
        # row.label(text="Tools for Precut:")

        # row = layout.row(align=True)
        # row.operator_context = "INVOKE_DEFAULT"
        # row.operator("uas_shot_manager.predec_shots_from_single_cam")

        # row = layout.row(align=True)
        # row.enabled = False
        # if _adc == False: row.enabled = False
        # else: row.enabled = True
        # row.operator_context = 'INVOKE_DEFAULT'
        # row.operator("cameramanager.camera_tools",text='Clear Animation Datas').tool='CLEARANIMDATA'

        # row = layout.row(align=True)
        # row.enabled = False
        # if _cdc == False: row.enabled = False
        # else: row.enabled = True
        # row.operator_context = 'INVOKE_DEFAULT'
        # row.operator("cameramanager.camera_tools",text='Clear Custom Resolution').tool='CLEARRESOLUTION'

        # row = layout.row(align=True)
        # row.enabled = False
        # if _cc == False: row.enabled = False
        # else: row.enabled = True
        # row.operator_context = 'INVOKE_DEFAULT'
        # row.operator("cameramanager.camera_tools",text='Clear Track To Constraint').tool='CLEARTRACKTO'

        # row = layout.row(align=True)
        # row.enabled = False
        # if _mc == False: row.enabled = False
        # else: row.enabled = True
        # row.operator_context = 'INVOKE_DEFAULT'
        # row.operator("cameramanager.camera_tools",text='Clear Timeline Marker').tool='CLEARMARKER'

        # row = layout.row(align=True)
        # row.enabled = False
        # if _cAll == False: row.enabled = False
        # else: row.enabled = True
        # row.operator_context = 'INVOKE_DEFAULT'
        # row.operator("cameramanager.camera_tools",text='Clear All').tool='CLEARALL'
        ## ]Clear menu entries


_classes = (
    UAS_PT_VideoShotManager,
    UAS_UL_VideoShotManager_Items,
    UAS_PT_VideoShotManager_TrackProperties,
    UAS_MT_VideoShotManager_ToolsMenu,
)


def register():
    print("\n *** *** Resistering Video Shot Manager *** *** \n")
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
