# -*- coding: utf-8 -*-
#
# This addon blabla
#
# Installation:
#
#
# Things to know:
#   - 1 shot manager instance per scene (= possible differences in preferences per scene)
#
#   - time on media (= output videos) starts at frame 0 (and then last frame index is equal to Durantion - 1)
#   - Shots:
#       - end frame is INCLUDED in the shot frames (and then rendered)
#
#
# Dev notes:
#  * Pb:
#   cleanner le patch dégueu des indices de takes lors de la suppression des shots disabled
#       - about à finir
#       - jog pas parfait
#       - script unique cam en rade
#       - getsion des viewports
#       - sortir les properties de shot
#
#
#  * To do:
#       - mettre des modifiers CTRL et Alt pour jogguer entre les débuts et fin seulement de plans
#       - ajouter un bouton Help
#       - prefix Name
#       - take verouille les cams
#
#       - mettre des vraies prefs utilisateurs
#
#       - installer open timeline io
#


import os
from pathlib import Path
import subprocess

import bpy
import bpy.utils.previews
from bpy.props import BoolProperty
from bpy.types import Panel, Operator, Menu

try:
    import opentimelineio as otio
except ModuleNotFoundError:
    subprocess.run([bpy.app.binary_path_python, "-m", "pip", "install", "opentimelineio==0.11.0"])
    import opentimelineio as otio

from .ogl_ui import UAS_ShotManager_DrawTimeline, UAS_ShotManager_DrawCameras_UI

from .properties import props

from .handlers import jump_to_shot

from .utils import utils

from .operators import takes
from .operators import shots
from .operators import renderProps
from .operators import playbar
from .operators import prefs
from .utils import utils_render

from .scripts import precut_tools

from .tools import vse_render


bl_info = {
    "name": "UAS Shot Manager",
    "author": "Romain Carriquiry Borchiari, Julien Blervaque (aka Werwack)",
    "description": "Manage a sequence of shots and cameras in the 3D View - Ubisoft Animation Studio",
    "blender": (2, 82, 0),
    "version": (1, 1, 17),
    "location": "View3D > UAS Shot Manager",
    "wiki_url": "https://mdc-web-tomcat17.ubisoft.org/confluence/display/UASTech/UAS+Shot+Manager",
    "warning": "",
    "category": "UAS",
}

icons_col = None


######
# Shot Manager main panel #
######


class UAS_PT_ShotManager(Panel):
    bl_label = f"UAS Shot Manager {'.'.join ( str ( v ) for v in bl_info[ 'version'] ) }"
    bl_idname = "UAS_PT_Shot_Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"

    def draw_header(self, context):
        scene = context.scene

        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        # About... panel
        if context.window_manager.UAS_shot_manager_displayAbout:
            _emboss = True
            row.alert = True
        else:
            #    _emboss = False
            row.alert = False

        row.prop(context.window_manager, "UAS_shot_manager_displayAbout", icon="SETTINGS", icon_only=True)

    def draw_header_preset(self, context):
        scene = context.scene

        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        row.operator("utils.launchrender", text="", icon="RENDER_STILL").renderMode = "STILL"
        row.operator("utils.launchrender", text="", icon="RENDER_ANIMATION").renderMode = "ANIMATION"
        # row.label(text = "|")
        row.separator(factor=2)
        row.operator("uas_shot_manager.render_openexplorer", text="", icon="FILEBROWSER").path = bpy.path.abspath(
            bpy.data.filepath
        )

        #    row.operator("render.opengl", text="", icon='IMAGE_DATA')
        #   row.operator("render.opengl", text="", icon='RENDER_ANIMATION').animation = True
        #    row.operator("screen.screen_full_area", text ="", icon = 'FULLSCREEN_ENTER').use_hide_panels=False
        row.separator(factor=3)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.UAS_shot_manager_props

        ################
        # About... panel
        if context.window_manager.UAS_shot_manager_displayAbout:
            row = layout.row()
            aboutStr = "About UAS Shot Manager..."
            row.label(text=aboutStr)

            row = layout.row()
            box = row.box()
            #    aboutStr = "Create a set of camera shots and edit them\nin the 3D View as you would do with video clips."
            box.label(text="Create a set of camera shots and edit them")
            box.label(text="in the 3D View as you would do with video clips.")
            #    box = row.box()

            row = layout.row()
            row.separator(factor=1.4)

        # if not "UAS_shot_manager_props" in context.scene:
        if not props.isInitialized:
            layout.separator()
            row = layout.row()
            row.alert = True
            row.operator("uas_shot_manager.initialize")
            row.alert = False
            layout.separator()

        ################
        # play and timeline
        row = layout.row()
        row.scale_y = 1.2
        row.prop(
            context.window_manager,
            "UAS_shot_manager_handler_toggle",
            text="Shots Play Mode" if context.window_manager.UAS_shot_manager_handler_toggle else "Standard Play Mode",
            toggle=True,
            icon="ANIM",
        )
        row.prop(context.window_manager, "UAS_shot_manager_display_timeline", text="", toggle=True, icon="TIME")
        # row.prop ( props, "display_timeline", text = "", toggle = True, icon = "TIME" )

        ################
        # play bar
        row = layout.row(align=True)
        row.alignment = "CENTER"
        row.operator("uas_shot_manager.playbar_gotofirstshot", text="", icon="REW")
        row.operator("uas_shot_manager.playbar_gotopreviousshot", text="", icon="PREV_KEYFRAME")
        row.operator("uas_shot_manager.playbar_gotopreviousframe", text="", icon="FRAME_PREV")

        split = row.split(align=True)
        split.separator()
        # row.ui_units_x = 40
        row.scale_x = 1.8
        row.operator(
            "SCREEN_OT_animation_play", text="", icon="PLAY" if not context.screen.is_animation_playing else "PAUSE"
        )
        row.scale_x = 1
        # if display_prev_next_buttons
        #  row.operator ( "SCREEN_OT_frame_jump", text = "", icon = "PLAY" if not context.screen.is_animation_playing else "PAUSE" )
        #     row.prop(context.scene, "frame_current", text = "")            # prend la propriété direct ds la scene

        split = row.split(align=True)
        split.separator()
        row.operator("uas_shot_manager.playbar_gotonextframe", text="", icon="FRAME_NEXT")
        row.operator("uas_shot_manager.playbar_gotonextshot", text="", icon="NEXT_KEYFRAME")
        row.operator("uas_shot_manager.playbar_gotolastshot", text="", icon="FF")

        # separated frame spinner
        row.separator(factor=2.0)
        split = row.split(align=True)
        split.separator()
        row.prop(scene, "frame_current", text="")  # directly binded to the scene property
        row.separator(factor=2.0)
        split = row.split(align=True)
        # split.separator ( )
        # wkip mettre une propriété
        row.prop(scene.render, "fps_base", text="")  # directly binded to the scene property

        layout.separator(factor=0.5)

        ################
        # editing
        row = layout.row(align=True)
        editingDuration = props.getEditDuration()
        editingDurationStr = "-" if -1 == editingDuration else (str(editingDuration) + " frames")
        row.label(text="Editing Duration: " + editingDurationStr)

        row.separator()
        #    row = layout.row(align=True)
        # context.props.getCurrentShotIndex(ignoreDisabled = False
        editingCurrentTime = props.getEditCurrentTime()
        editingCurrentTimeStr = "-" if -1 == editingCurrentTime else str(editingCurrentTime)
        row.label(text="Current Time in Edit: " + editingCurrentTimeStr)

        row.alignment = "RIGHT"
        row.label(text=str(scene.render.fps) + " fps")

        ################
        # status text line

        # row = layout.row(align=True)
        # row.alert = True
        # myStr = "UAS_RRS_PROJECTNAME : "
        # myStrValue = os.environ['UAS_RRS_PROJECTNAME']
        # row.label ( text = myStr + myStrValue )

        ################
        # takes
        row = layout.row()  # just to give some space...
        box = layout.box()
        row = box.row()
        #    row.scale_y = 1.5
        row.prop(props, "current_take_name")
        #    row.menu(UAS_MT_ShotManager_Takes_ToolsMenu.bl_idname,text="Tools",icon='TOOL_SETTINGS')
        row.menu("UAS_MT_Shot_Manager_takes_toolsmenu", icon="TOOL_SETTINGS", text="")

        # row.operator ( "uas_shot_manager.rename_take", icon = "SYNTAX_ON", text = "" )
        # row.separator (  )

        # split = row.split ( align = True )
        # split.operator ( "uas_shot_manager.add_take", icon = "ADD", text = "" )
        # split.operator ( "uas_shot_manager.duplicate_take", icon = "DUPLICATE", text = "" )
        # split.operator ( "uas_shot_manager.remove_take", icon = "REMOVE", text = "" )

        ################
        # shots
        if len(props.takes):
            box = layout.box()
            row = box.row()
            row.label(text="Shots: ")

            row = box.row()
            templateList = row.template_list(
                "UAS_UL_ShotManager_Items", "", props.getCurrentTake(), "shots", props, "selected_shot_index", rows=6
            )

            col = row.column(align=True)
            col.operator("uas_shot_manager.add_shot", icon="ADD", text="")
            col.operator("uas_shot_manager.duplicate_shot", icon="DUPLICATE", text="")
            col.operator("uas_shot_manager.remove_shot", icon="REMOVE", text="")
            #   col.operator ( "uas_shot_manager.list_action", icon = 'REMOVE', text = "" ).action = 'REMOVE'
            col.separator()
            col.operator("uas_shot_manager.list_action", icon="TRIA_UP", text="").action = "UP"
            col.operator("uas_shot_manager.list_action", icon="TRIA_DOWN", text="").action = "DOWN"
            col.separator()
            col.menu("UAS_MT_Shot_Manager_shots_toolsmenu", icon="TOOL_SETTINGS", text="")

            # layout.separator ( factor = 1 )


#############
# tools for Takes
#############


class UAS_MT_ShotManager_Takes_ToolsMenu(Menu):
    bl_idname = "UAS_MT_Shot_Manager_takes_toolsmenu"
    bl_label = "Take Tools"
    bl_description = "Take Tools"

    def draw(self, context):
        scene = context.scene

        marker_list = context.scene.timeline_markers
        # list_marked_cameras = [o.camera for o in marker_list if o != None]

        ## Copy menu entries[ ---
        layout = self.layout
        row = layout.row(align=True)

        #    row.label(text="Tools for Current Take:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.add_take", text="Add...", icon="ADD")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.duplicate_take", text="Duplicate...", icon="DUPLICATE")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.remove_take", text="Remove", icon="REMOVE")

        layout.separator()

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.rename_take", text="Rename...")  # , icon = "SYNTAX_ON"),

        layout.separator()

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.reset_takes_to_default", text="Reset to Default...")


#############
# Shots
#############


class UAS_UL_ShotManager_Items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        global icons_col
        props = context.scene.UAS_shot_manager_props
        current_shot_index = props.current_shot_index

        cam = "Cam" if current_shot_index == index else ""
        currentFrame = context.scene.frame_current

        if item.enabled:
            icon = icons_col[f"ShotMan_Enabled{cam}"]
            if item.start <= context.scene.frame_current <= item.end:
                icon = icons_col[f"ShotMan_EnabledCurrent{cam}"]
        else:
            icon = icons_col[f"ShotMan_Disabled{cam}"]

        c = layout.column()
        c.operator("uas_shot_manager.set_current_shot", icon_value=icon.icon_id, text="").index = index
        layout.separator(factor=0.1)

        c = layout.column()
        grid_flow = c.grid_flow(align=True, columns=9, even_columns=False)
        if item.camera is None:
            grid_flow.alert = True

        if props.display_color_in_shotlist:
            grid_flow.scale_x = 0.15
            grid_flow.prop(item, "color", text="")
            grid_flow.scale_x = 1.0

        #  grid_flow.prop ( item, "enabled", text = item.name )

        grid_flow.scale_x = 0.08
        # grid_flow.alignment = 'LEFT'
        grid_flow.prop(item, "enabled", text=" ")  # keep the space in the text !!!
        #   grid_flow.separator( factor = 0.5)
        grid_flow.scale_x = 0.8
        grid_flow.label(text=item.name)
        #   grid_flow.alignment = 'RIGHT'

        grid_flow.scale_x = 0.5

        ### start
        if currentFrame == item.start:
            if props.highlight_all_shot_frames or current_shot_index == index:
                grid_flow.alert = True
        grid_flow.prop(item, "start", text="")
        grid_flow.alert = False

        ### duration
        if (
            item.start < currentFrame
            and currentFrame < item.end
            or (item.start == item.end and currentFrame == item.start)
        ):
            if props.highlight_all_shot_frames or current_shot_index == index:
                grid_flow.alert = True
        # bpy.ops.uas_shot_manager.empty.myEmpty.description = "toto"

        if props.display_duration_in_shotlist:
            grid_flow.scale_x = 0.2
            # grid_flow.label ( text = str(item.getDuration()) )
            grid_flow.operator("uas_shot_manager.shot_duration", text=str(item.getDuration())).index = index
        else:
            grid_flow.scale_x = 0.05
            grid_flow.operator("uas_shot_manager.shot_duration", text="").index = index
        grid_flow.scale_x = 0.5
        grid_flow.alert = False

        ### end
        if currentFrame == item.end:
            if props.highlight_all_shot_frames or current_shot_index == index:
                grid_flow.alert = True
        grid_flow.prop(item, "end", text="")
        grid_flow.alert = False

        grid_flow.scale_x = 1.0

        if props.display_camera_in_shotlist:
            if None == item.camera:
                grid_flow.alert = True
            grid_flow.prop(item, "camera", text="")
            if None == item.camera:
                grid_flow.alert = False

        if props.display_lens_in_shotlist:
            grid_flow.scale_x = 0.4
            grid_flow.use_property_decorate = True
            if None != item.camera:
                grid_flow.prop(item.camera.data, "lens", text="Lens")
            else:
                grid_flow.alert = True
                grid_flow.operator("uas_shot_manager.empty", text="-").index = index
                grid_flow.alert = False
            grid_flow.scale_x = 1.0
        # split = row.split ( align = True )
        # split.separator ( )

        #    grid_flow ( align = False)        # interline
        # layout.separator ( factor = 0.1 )

        if props.display_selectbut_in_shotlist:
            c = layout.column()
            c.operator("uas_shot_manager.shots_selectcamera", text="", icon="RESTRICT_SELECT_OFF").index = index


##################
# shot properties
##################


class UAS_PT_ShotManager_ShotProperties(Panel):
    bl_label = " "  # "Current Shot Properties" # keep the space !!
    bl_idname = "UAS_PT_Shot_Manager_Shot_Prefs"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager"

    def draw_header(self, context):
        scene = context.scene
        render = scene.render
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        propertiesModeStr = "Current Shot Properties"
        if "SELECTED" == scene.UAS_shot_manager_props.current_shot_properties_mode:
            propertiesModeStr = "Selected Shot Properties"
        row.label(text=propertiesModeStr)

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        #  shotPropertiesModeIsCurrent = not ('SELECTED' == props.current_shot_properties_mode)

        shot = None
        # if shotPropertiesModeIsCurrent is true then the displayed shot properties are taken from the CURRENT shot, else from the SELECTED one
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShot(props.selected_shot_index)

        layout = self.layout

        if shot is not None:
            box = layout.box()

            # name and color
            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            grid_flow.prop(shot, "name", text="Name")
            #   grid_flow.scale_x = 0.7
            grid_flow.prop(shot, "color", text="")
            #   grid_flow.scale_x = 1.0
            grid_flow.prop(props, "display_color_in_shotlist", text="")
            row.separator(factor=0.5)  # prevents stange look when panel is narrow

            # Duration
            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            # row.label ( text = r"Duration: " + str(shot.getDuration()) + " frames" )
            grid_flow.label(text="Duration: ")
            grid_flow.label(text=str(shot.getDuration()) + " frames")
            grid_flow.prop(props, "display_duration_in_shotlist", text="")
            row.separator(factor=0.5)  # prevents stange look when panel is narrow

            # camera and lens
            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            if None == shot.camera:
                grid_flow.alert = True
            grid_flow.prop(shot, "camera", text="Camera")
            if None == shot.camera:
                grid_flow.alert = False
            grid_flow.prop(props, "display_camera_in_shotlist", text="")

            # c.separator( factor = 0.5 )   # prevents stange look when panel is narrow
            grid_flow.scale_x = 0.7
            #     row.label ( text = "Lens: " )
            grid_flow.use_property_decorate = True
            if None != shot.camera:
                grid_flow.prop(shot.camera.data, "lens", text="Lens")
            else:
                grid_flow.alert = True
                grid_flow.operator("uas_shot_manager.empty", text="No Lens")
                grid_flow.alert = False
            grid_flow.scale_x = 1.0
            grid_flow.prop(props, "display_lens_in_shotlist", text="")
            row.separator(factor=0.5)  # prevents stange look when panel is narrow

            box.separator(factor=0.5)

            # Output
            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            grid_flow.label(text="Output: ")
            grid_flow.label(text=str(shot.getOutputFileName()))
            grid_flow.operator("uas_shot_manager.render_openexplorer", emboss=True, icon="FILEBROWSER", text="")
            row.separator(factor=0.5)  # prevents stange look when panel is narrow

            # row.prop ( context.props, "display_duration_in_shotlist", text = "" )

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShot(props.selected_shot_index)
        val = len(context.scene.UAS_shot_manager_props.getTakes()) and shot

        return val


class UAS_ShotManager_Actions(Operator):
    """Move items up and down, add and remove"""

    bl_idname = "uas_shot_manager.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {"INTERNAL"}

    action: bpy.props.EnumProperty(items=(("UP", "Up", ""), ("DOWN", "Down", "")))

    def invoke(self, context, event):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        shots = props.get_shots()
        currentShotInd = props.getCurrentShotIndex()
        selectedShotInd = props.getSelectedShotIndex()
        print("  ** Action: currentShotInd: ", currentShotInd)
        print("     selectedShotInd: ", selectedShotInd)

        try:
            item = shots[currentShotInd]
        except IndexError:
            pass
        else:
            if self.action == "DOWN" and selectedShotInd < len(shots) - 1:
                shots.move(selectedShotInd, selectedShotInd + 1)
                if currentShotInd == selectedShotInd:
                    props.setCurrentShotByIndex(currentShotInd + 1)
                elif currentShotInd == selectedShotInd + 1:
                    props.setCurrentShotByIndex(selectedShotInd)
                props.setSelectedShotByIndex(selectedShotInd + 1)

            elif self.action == "UP" and selectedShotInd >= 1:
                shots.move(selectedShotInd, selectedShotInd - 1)
                if currentShotInd == selectedShotInd:
                    props.setCurrentShotByIndex(currentShotInd - 1)
                elif currentShotInd == selectedShotInd - 1:
                    props.setCurrentShotByIndex(selectedShotInd)

                props.setSelectedShotByIndex(selectedShotInd - 1)
                print("     currentShotInd 02: ", currentShotInd)
                print("     selectedShotInd 02: ", props.getSelectedShotIndex())

        return {"FINISHED"}


#################
# tools for shots
#################


class UAS_MT_ShotManager_Shots_ToolsMenu(Menu):
    bl_idname = "UAS_MT_Shot_Manager_shots_toolsmenu"
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
        row.operator("uas_shot_manager.remove_multiple_shots", text="Remove Disabled Shots").action = "DISABLED"

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.remove_multiple_shots", text="Remove All Shots").action = "ALL"

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

        layout.separator()

        ## Clear menu entries[ ---
        row = layout.row(align=True)
        row.label(text="Tools for Shots:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.create_shots_from_each_camera")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.unique_cameras")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.shots_removecamera")

        layout.separator()
        row = layout.row(align=True)
        row.label(text="Tools for Precut:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.predec_shots_from_single_cam")

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


#########
# MISC
#########


# used in the shot item
class UAS_ShotManager_ShotDuration(Operator):
    bl_idname = "uas_shot_manager.shot_duration"
    bl_label = "Shot Range"
    bl_description = "Shot Range"
    bl_options = {"INTERNAL"}

    index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        context.scene.UAS_shot_manager_props.selectCamera(self.index)
        return {"FINISHED"}


# used in the shot item
class UAS_ShotManager_Empty(Operator):
    bl_idname = "uas_shot_manager.empty"
    bl_label = "No Lens"
    bl_description = "No Lens"
    bl_options = {"INTERNAL"}

    index: bpy.props.IntProperty(default=0)


###########
# Handlers
###########


def timeline_valueChanged(self, context):
    print("  timeline_valueChanged:  self.UAS_shot_manager_display_timeline: ", self.UAS_shot_manager_display_timeline)
    if self.UAS_shot_manager_display_timeline:
        bpy.ops.uas_shot_manager.draw_timeline("INVOKE_DEFAULT")
        bpy.ops.uas_shot_manager.draw_cameras_ui("INVOKE_DEFAULT")


def install_shot_handler(self, context):
    if self.UAS_shot_manager_handler_toggle and jump_to_shot not in bpy.app.handlers.frame_change_pre:
        scene = context.scene
        shots = scene.UAS_shot_manager_props.get_shots()
        for i, shot in enumerate(shots):
            if shot.start <= scene.frame_current <= shot.end:
                scene.UAS_shot_manager_props.current_shot_index = i
                break
        bpy.app.handlers.frame_change_pre.append(jump_to_shot)

    #    bpy.ops.uas_shot_manager.draw_timeline ( "INVOKE_DEFAULT" )
    elif not self.UAS_shot_manager_handler_toggle and jump_to_shot in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(jump_to_shot)


class UAS_PT_ShotManager_Initialize(Operator):
    bl_idname = "uas_shot_manager.initialize"
    bl_label = "Initialize"
    bl_description = "Initialize"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        print("*** uas_shot_manager.render ***")
        context.scene.UAS_shot_manager_props.initialize_shot_manager()

        return {"FINISHED"}


classes = (
    UAS_UL_ShotManager_Items,
    UAS_PT_ShotManager,
    UAS_MT_ShotManager_Takes_ToolsMenu,
    UAS_PT_ShotManager_ShotProperties,
    UAS_MT_ShotManager_Shots_ToolsMenu,
    UAS_ShotManager_Actions,
    UAS_ShotManager_ShotDuration,
    UAS_ShotManager_Empty,
    UAS_ShotManager_DrawTimeline,
    UAS_PT_ShotManager_Initialize,
    UAS_ShotManager_DrawCameras_UI,
)


def verbose_set(key: str, default: bool, override: str, verbose: bool = True) -> None:
    default_value = str(default)
    if key in os.environ.keys():
        if override and os.environ[key] != default_value:
            if verbose:
                print(f"Overrinding value for '{key}': {default}")
            os.environ[key] = default_value
        return  # already set

    if verbose:
        print(f"Key '{key}' not in the default environment, setting it to {default_value}")
    os.environ[key] = default_value


def setup_project_env(override_existing: bool, verbose: bool = True) -> None:

    verbose_set("UAS_PROJECT_NAME", "RRSpecial", override_existing, verbose)
    verbose_set("UAS_PROJECT_FRAMERATE", "25.0", override_existing, verbose)
    verbose_set("UAS_PROJECT_RESOLUTION", "[1280,720]", override_existing, verbose)
    verbose_set("UAS_PROJECT_RESOLUTIONFRAMED", "[1280,960]", override_existing, verbose)
    verbose_set("UAS_PROJECT_OUTPUTFORMAT", "mp4", override_existing, verbose)
    verbose_set("UAS_PROJECT_COLORSPACE", "", override_existing, verbose)
    verbose_set("UAS_PROJECT_ASSETNAME", "", override_existing, verbose)


# setup_project_env(True,False)


def register():
    # set RRS Environment variables for project
    setup_project_env(True, True)

    for cls in classes:
        bpy.utils.register_class(cls)

    takes.register()
    shots.register()
    utils.register()
    playbar.register()
    renderProps.register()
    vse_render.register()
    prefs.register()
    precut_tools.register()
    props.register()
    utils_render.register()

    # declaration of properties that will not be saved in the scene

    ### About button panel Quick Settings[ -----------------------------
    bpy.types.WindowManager.UAS_shot_manager_displayAbout = BoolProperty(
        name="About...", description="Display About Informations", default=False
    )

    bpy.types.WindowManager.UAS_shot_manager_isInitialized = BoolProperty(
        name="Shot Manager is initialized", description="", default=False
    )

    bpy.types.WindowManager.UAS_shot_manager_handler_toggle = BoolProperty(
        name="frame_handler",
        description="Override the standard animation Play mode to play the enabled shots\nin the specified order",
        default=False,
        update=install_shot_handler,
    )

    bpy.types.WindowManager.UAS_shot_manager_display_timeline = BoolProperty(
        name="display_timeline",
        description="Display a timeline in the 3D Viewport with the shots in the specified order",
        default=False,
        update=timeline_valueChanged,
    )

    pcoll = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    for png in Path(my_icons_dir).rglob("*.png"):
        pcoll.load(png.stem, str(png), "IMAGE")

    global icons_col
    icons_col = pcoll


def unregister():
    utils_render.unregister()
    props.unregister()
    precut_tools.unregister()
    prefs.unregister()
    vse_render.unregister()
    renderProps.unregister()
    playbar.unregister()
    utils.unregister()
    shots.unregister()
    takes.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    if jump_to_shot in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(jump_to_shot)

    del bpy.types.WindowManager.UAS_shot_manager_displayAbout
    del bpy.types.WindowManager.UAS_shot_manager_handler_toggle
    del bpy.types.WindowManager.UAS_shot_manager_display_timeline

    global icons_col
    bpy.utils.previews.remove(icons_col)
    icons_col = None
