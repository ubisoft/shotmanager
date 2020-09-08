import logging

_logger = logging.getLogger(__name__)

import bpy
from bpy.types import Panel, Operator, Menu
from bpy.props import StringProperty

from ..config import config
from ..viewport_3d.ogl_ui import UAS_ShotManager_DrawTimeline

from ..utils import utils


######
# Shot Manager main panel #
######


class UAS_PT_ShotManager(Panel):
    #    bl_label = f"UAS Shot Manager {'.'.join ( str ( v ) for v in bl_info[ 'version'] ) }"
    bl_label = " UAS Shot Manager   V. " + utils.addonVersion("UAS Shot Manager")[0]
    bl_idname = "UAS_PT_Shot_Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        props = context.scene.UAS_shot_manager_props
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)

        # if context.window_manager.  warning on addons missing - to do:
        #     row.alert = True
        # else:
        #     row.alert = False

        icon = config.icons_col["General_Ubisoft_32"]
        row.operator("uas_shot_manager.about", text="", icon_value=icon.icon_id)

        if props.use_project_settings:
            if "" == props.project_name:
                row.alert = True
                row.label(text="<No Project Name>")
                row.alert = False
            else:
                row.label(text=props.project_name)

    def draw_header_preset(self, context):
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)

        row.operator("utils.launchrender", text="", icon="RENDER_STILL").renderMode = "STILL"
        row.operator("utils.launchrender", text="", icon="RENDER_ANIMATION").renderMode = "ANIMATION"
        row.separator(factor=2)

        #    row.operator("render.opengl", text="", icon='IMAGE_DATA')
        #   row.operator("render.opengl", text="", icon='RENDER_ANIMATION').animation = True
        #    row.operator("screen.screen_full_area", text ="", icon = 'FULLSCREEN_ENTER').use_hide_panels=False

        row.operator("uas_shot_manager.go_to_video_shot_manager", text="", icon="SEQ_STRIP_DUPLICATE")

        row.separator(factor=2)
        icon = config.icons_col["General_Explorer_32"]
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
            bpy.data.filepath
        )

        row.separator(factor=2)
        row.menu("UAS_MT_Shot_Manager_prefs_mainmenu", icon="PREFERENCES", text="")

        row.separator(factor=3)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.UAS_shot_manager_props

        import addon_utils

        addonWarning = [
            addon.bl_info.get("warning", "")
            for addon in addon_utils.modules()
            if addon.bl_info["name"] == "UAS Shot Manager"
        ]

        if "" != addonWarning[0]:
            row = layout.row()
            row.alignment = "CENTER"
            row.alert = True
            row.label(text=f" ***  {addonWarning[0]}  ***")
            row.alert = False

        if config.uasDebug:
            row = layout.row()
            row.alignment = "CENTER"
            row.alert = True
            row.label(text=" *** Debug Mode ***")
            row.alert = False

        # if not "UAS_shot_manager_props" in context.scene:
        if not props.isInitialized:
            layout.separator()
            row = layout.row()
            row.alert = True
            row.operator("uas_shot_manager.initialize")
            row.alert = False
            layout.separator()

        # play and timeline
        ################
        row = layout.row()
        row.scale_y = 1.2
        row.prop(
            context.window_manager,
            "UAS_shot_manager_shots_play_mode",
            text="Shots Play Mode" if context.window_manager.UAS_shot_manager_shots_play_mode else "Standard Play Mode",
            toggle=True,
            icon="ANIM",
        )
        row.prop(context.window_manager, "UAS_shot_manager_display_timeline", text="", toggle=True, icon="TIME")
        row.prop(context.window_manager, "UAS_shot_manager_toggle_montage_interaction", text="", toggle=True)

        row.emboss = "PULLDOWN_MENU"
        row.operator("uas_shot_manager.playbar_prefs", text="", icon="SETTINGS")

        # play bar
        ################
        row = layout.row(align=True)

        split = row.split(align=True)
        split.separator()
        row.alignment = "CENTER"
        subrow = row.row(align=True)
        subrow.enabled = 0 < len(props.get_shots())
        subrow.operator("uas_shot_manager.playbar_gotofirstshot", text="", icon="REW")
        subrow.operator("uas_shot_manager.playbar_gotopreviousshot", text="", icon="PREV_KEYFRAME")
        subrow.operator("uas_shot_manager.playbar_gotopreviousframe", text="", icon="FRAME_PREV")

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
        subrow = row.row(align=True)
        subrow.enabled = 0 < len(props.get_shots())
        subrow.operator("uas_shot_manager.playbar_gotonextframe", text="", icon="FRAME_NEXT")
        subrow.operator("uas_shot_manager.playbar_gotonextshot", text="", icon="NEXT_KEYFRAME")
        subrow.operator("uas_shot_manager.playbar_gotolastshot", text="", icon="FF")

        # separated frame spinner
        row.separator(factor=2.0)
        split = row.split(align=True)
        split.separator()
        row.prop(scene, "frame_current", text="")  # directly binded to the scene property
        split = row.split(align=True)
        row.separator(factor=3.0)
        # split.separator ( )
        # wkip mettre une propriété
        # row.prop(scene.render, "fps_base", text="")  # directly binded to the scene property
        if props.playSpeedGlobal != 100:
            row.alert = True
        row.prop(props, "playSpeedGlobal", text="")  # directly binded to the scene property
        row.alert = False

        layout.separator(factor=0.5)

        ################
        # stop draw here if perfs are required
        ################
        if props.dontRefreshUI():
            return None

        # editing
        ################
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

        if props.use_project_settings and props.project_fps != scene.render.fps:
            row.alert = True
        row.label(text=str(scene.render.fps) + " fps")

        # warnings
        ################
        warningsList = props.getWarnings(scene)
        if len(warningsList):
            for w in warningsList:
                row = layout.row()
                row.separator()
                row.alert = True
                row.label(text=w)
                row.alert = False

        # takes
        ################
        row = layout.row()  # just to give some space...
        box = layout.box()
        row = box.row()
        #    row.scale_y = 1.5
        row.prop(props, "current_take_name")
        #    row.menu(UAS_MT_ShotManager_Takes_ToolsMenu.bl_idname,text="Tools",icon='TOOL_SETTINGS')
        row.menu("UAS_MT_Shot_Manager_takes_toolsmenu", icon="TOOL_SETTINGS", text="")

        # shots
        ################
        if len(props.takes):
            box = layout.box()
            row = box.row()
            # numShots = len(props.getShotsList(ignoreDisabled=False))
            # numEnabledShots = len(props.getShotsList(ignoreDisabled=True))
            numShots = props.getNumShots()
            numEnabledShots = props.getNumShots(ignoreDisabled=True)

            column_flow = row.column_flow(columns=3)
            subrow = column_flow.row()
            subrow.alignment = "LEFT"
            subrow.scale_x = 1.0
            subrow.label(text=f"Shots ({numEnabledShots}/{numShots}):")
            # subrow.separator()
            #  column_flow.scale_x = 1.0
            subrow = column_flow.row()
            subrow.alignment = "LEFT"
            #   subrow.scale_x = 1.0
            subrow.operator("uas_shot_manager.enabledisableall", text="", icon="CHECKBOX_HLT")

            # subrow.separator(factor=0.2)
            subrow.prop(
                props, "display_edit_times_in_shotlist", text="Edit Times", toggle=True, icon="SEQ_STRIP_DUPLICATE"
            )

            subrow = column_flow.row()
            subrow.scale_x = 0.9
            subrow.alignment = "RIGHT"

            if props.useLockCameraView:
                subrow.alert = True
            subrow.prop(props, "useLockCameraView", text="", icon="CAMERA_DATA")
            if props.useLockCameraView:
                subrow.alert = False

            subrow.separator()
            subrow.operator("uas_shot_manager.scenerangefromshot", text="", icon="PREVIEW_RANGE")
            #    row.operator("uas_shot_manager.scenerangefromenabledshots", text="", icon="PREVIEW_RANGE")
            subrow.operator("uas_shot_manager.scenerangefrom3dedit", text="", icon="PREVIEW_RANGE")

            row.emboss = "PULLDOWN_MENU"
            row.operator("uas_shot_manager.shots_prefs", text="", icon="SETTINGS")

            row = box.row()
            row.template_list(
                "UAS_UL_ShotManager_Items", "", props.getCurrentTake(), "shots", props, "selected_shot_index", rows=6
            )

            col = row.column(align=True)
            col.operator("uas_shot_manager.add_shot", icon="ADD", text="")
            col.operator("uas_shot_manager.duplicate_shot", icon="DUPLICATE", text="")
            col.operator("uas_shot_manager.remove_shot", icon="REMOVE", text="")
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

        # marker_list = context.scene.timeline_markers
        # list_marked_cameras = [o.camera for o in marker_list if o != None]

        # Copy menu entries[ ---
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
# Shot Item
#############


class UAS_UL_ShotManager_Items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        props = context.scene.UAS_shot_manager_props
        current_shot_index = props.current_shot_index

        itemHasWarnings = False

        cam = "Cam" if current_shot_index == index else ""
        currentFrame = context.scene.frame_current

        # check if the camera still exists in the scene
        cameraIsValid = item.isCameraValid()
        itemHasWarnings = not cameraIsValid

        # draw the Duration components

        if item.enabled:
            icon = config.icons_col[f"ShotMan_Enabled{cam}"]
            if item.start <= context.scene.frame_current <= item.end:
                icon = config.icons_col[f"ShotMan_EnabledCurrent{cam}"]
        else:
            icon = config.icons_col[f"ShotMan_Disabled{cam}"]

        if item.camera is None or itemHasWarnings:
            layout.alert = True

        row = layout.row()

        row.operator("uas_shot_manager.set_current_shot", icon_value=icon.icon_id, text="").index = index

        if props.display_selectbut_in_shotlist or props.display_color_in_shotlist:
            row = layout.row(align=True)
            row.scale_x = 1.0
            if props.display_selectbut_in_shotlist:
                row.operator("uas_shot_manager.shots_selectcamera", text="", icon="RESTRICT_SELECT_OFF").index = index

            if props.display_notes_in_properties and props.display_notes_in_shotlist:
                row = row.row(align=True)
                row.scale_x = 1.0

                if item.hasNotes():
                    notesIcon = "TEXT"
                    notesIcon = "OUTLINER_DATA_GP_LAYER"
                    notesIcon = "ALIGN_TOP"
                    row.operator("uas_shot_manager.shots_shownotes", text="", icon=notesIcon).index = index
                else:
                    emptyIcon = config.icons_col["General_Empty_32"]
                    row.operator(
                        "uas_shot_manager.shots_shownotes", text="", icon_value=emptyIcon.icon_id
                    ).index = index
                row.scale_x = 0.9

            if props.display_color_in_shotlist:
                row = row.row(align=True)
                row.scale_x = 0.2
                row.prop(item, "color", text="")
                row.scale_x = 0.45

        row = layout.row(align=True)

        row.scale_x = 1.0
        if props.display_enabled_in_shotlist:
            row.prop(item, "enabled", text="")
            row.separator(factor=0.9)
        row.scale_x = 0.8
        row.label(text=item.name)

        ###########
        # shot values
        ###########

        row = layout.row(align=True)
        row.scale_x = 2.0
        grid_flow = row.grid_flow(align=True, columns=7, even_columns=False)
        grid_flow.use_property_split = False
        button_x_factor = 0.6

        # currentFrameInEdit = props.
        # start
        ###########
        if props.display_edit_times_in_shotlist:
            # grid_flow.scale_x = button_x_factor
            # if props.display_getsetcurrentframe_in_shotlist:
            #     grid_flow.operator(
            #         "uas_shot_manager.getsetcurrentframe", text="", icon="TRIA_DOWN_BAR"
            #     ).shotSource = f"[{index},0]"

            grid_flow.scale_x = 0.4
            shotEditStart = item.getEditStart()
            if currentFrame == item.start:
                if props.highlight_all_shot_frames or current_shot_index == index:
                    grid_flow.alert = True
            # grid_flow.prop(item, "start", text="")
            # grid_flow.label(text=str(shotDuration))
            grid_flow.operator("uas_shot_manager.shottimeinedit", text=str(shotEditStart)).shotSource = f"[{index},0]"
            grid_flow.alert = False
        else:
            grid_flow.scale_x = button_x_factor
            if props.display_getsetcurrentframe_in_shotlist:
                grid_flow.operator(
                    "uas_shot_manager.getsetcurrentframe", text="", icon="TRIA_DOWN_BAR"
                ).shotSource = f"[{index},0]"

            grid_flow.scale_x = 0.4
            if currentFrame == item.start:
                if props.highlight_all_shot_frames or current_shot_index == index:
                    grid_flow.alert = True
            grid_flow.prop(item, "start", text="")
            grid_flow.alert = False

        # duration
        ###########

        # display_duration_after_time_range
        if not props.display_duration_after_time_range:
            grid_flow.scale_x = button_x_factor - 0.1
            grid_flow.prop(
                item,
                "durationLocked",
                text="",
                icon="DECORATE_LOCKED" if item.durationLocked else "DECORATE_UNLOCKED",
                toggle=True,
            )

            if (
                item.start < currentFrame
                and currentFrame < item.end
                or (item.start == item.end and currentFrame == item.start)
            ):
                if props.highlight_all_shot_frames or current_shot_index == index:
                    grid_flow.alert = True

            if props.display_duration_in_shotlist:
                grid_flow.scale_x = 0.3
                grid_flow.prop(item, "duration_fp", text="")
            else:
                grid_flow.scale_x = 0.05
                grid_flow.operator("uas_shot_manager.shot_duration", text="").index = index
            grid_flow.alert = False
        else:
            grid_flow.scale_x = 1.5

        # end
        ###########
        if props.display_edit_times_in_shotlist:
            grid_flow.scale_x = 0.4
            shotEditEnd = item.getEditEnd()
            if currentFrame == item.end:
                if props.highlight_all_shot_frames or current_shot_index == index:
                    grid_flow.alert = True
            grid_flow.operator("uas_shot_manager.shottimeinedit", text=str(shotEditEnd)).shotSource = f"[{index},1]"
            grid_flow.alert = False

            # grid_flow.scale_x = button_x_factor - 0.2
            # if props.display_getsetcurrentframe_in_shotlist:
            #     grid_flow.operator(
            #         "uas_shot_manager.getsetcurrentframe", text="", icon="TRIA_DOWN_BAR"
            #     ).shotSource = f"[{index},1]"
        else:
            grid_flow.scale_x = 0.4
            if currentFrame == item.end:
                if props.highlight_all_shot_frames or current_shot_index == index:
                    grid_flow.alert = True
            grid_flow.prop(item, "end", text="")
            grid_flow.alert = False

            grid_flow.scale_x = button_x_factor - 0.2
            if props.display_getsetcurrentframe_in_shotlist:
                grid_flow.operator(
                    "uas_shot_manager.getsetcurrentframe", text="", icon="TRIA_DOWN_BAR"
                ).shotSource = f"[{index},1]"

        if props.display_duration_after_time_range:
            row = layout.row(align=True)
            grid_flow = row.grid_flow(align=True, columns=2, even_columns=False)
            grid_flow.use_property_split = False
            # grid_flow.scale_x = button_x_factor - 0.1
            if props.display_duration_in_shotlist:
                grid_flow.scale_x = 1.5
            grid_flow.prop(
                item,
                "durationLocked",
                text="",
                icon="DECORATE_LOCKED" if item.durationLocked else "DECORATE_UNLOCKED",
                toggle=True,
            )

            if (
                item.start < currentFrame
                and currentFrame < item.end
                or (item.start == item.end and currentFrame == item.start)
            ):
                if props.highlight_all_shot_frames or current_shot_index == index:
                    grid_flow.alert = True

            if props.display_duration_in_shotlist:
                grid_flow.scale_x = 0.6
                grid_flow.prop(item, "duration_fp", text="")
            else:
                pass
                # grid_flow.scale_x = 0.1
                # grid_flow.operator("uas_shot_manager.shot_duration", text="").index = index
            grid_flow.alert = False

        # camera
        ###########
        row = layout.row(align=True)
        grid_flow = row.grid_flow(align=True, columns=2, even_columns=False)
        grid_flow.use_property_split = False
        grid_flow.scale_x = 1.0

        if props.display_camera_in_shotlist:
            if item.camera is None:
                grid_flow.alert = True
            grid_flow.prop(item, "camera", text="")
            if item.camera is None:
                grid_flow.alert = False

        if props.display_lens_in_shotlist:
            grid_flow.scale_x = 0.4
            grid_flow.use_property_decorate = True
            if item.camera is not None:
                grid_flow.prop(item.camera.data, "lens", text="Lens")
            else:
                grid_flow.alert = True
                grid_flow.operator("uas_shot_manager.nolens", text="-").index = index
                grid_flow.alert = False
            grid_flow.scale_x = 1.0


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

    tmpBGPath: StringProperty()

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShot(props.selected_shot_index)
        val = len(context.scene.UAS_shot_manager_props.getTakes()) and shot
        val = val and not props.dontRefreshUI()
        return val

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        propertiesModeStr = "Current Shot Properties"
        if "SELECTED" == scene.UAS_shot_manager_props.current_shot_properties_mode:
            propertiesModeStr = "Selected Shot Properties"
        row.label(text=propertiesModeStr)

    def draw_header_preset(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        shot = None
        # if shotPropertiesModeIsCurrent is true then the displayed shot properties are taken from the CURRENT shot, else from the SELECTED one
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShot(props.selected_shot_index)

        cameraIsValid = shot.isCameraValid()
        itemHasWarnings = not cameraIsValid

        if itemHasWarnings:
            self.layout.alert = True
            self.layout.label(text="*** Warning: Camera not in scene !*** ")

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        iconExplorer = config.icons_col["General_Explorer_32"]

        #  shotPropertiesModeIsCurrent = not ('SELECTED' == props.current_shot_properties_mode)

        shot = None
        # if shotPropertiesModeIsCurrent is true then the displayed shot properties are taken from the CURRENT shot, else from the SELECTED one
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShot(props.selected_shot_index)

        layout = self.layout
        layout.use_property_decorate = False

        if shot is not None:
            box = layout.box()
            box.use_property_decorate = False

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
            grid_flow = c.grid_flow(align=True, columns=4, even_columns=False)
            # row.label ( text = r"Duration: " + str(shot.getDuration()) + " frames" )
            grid_flow.label(text="Duration: ")

            grid_flow.use_property_split = False
            grid_flow.prop(
                shot,
                "durationLocked",
                text="",
                icon="DECORATE_LOCKED" if shot.durationLocked else "DECORATE_UNLOCKED",
                toggle=True,
            )

            grid_flow.prop(shot, "duration_fp", text="")

            #    grid_flow.label(text=str(shot.getDuration()) + " frames")
            grid_flow.prop(props, "display_duration_in_shotlist", text="")
            row.separator(factor=0.5)  # prevents stange look when panel is narrow

            # camera and lens

            cameraIsValid = shot.isCameraValid()

            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            if not cameraIsValid:
                grid_flow.alert = True
            grid_flow.prop(shot, "camera", text="Camera")
            if not cameraIsValid:
                grid_flow.alert = False
            grid_flow.prop(props, "display_camera_in_shotlist", text="")

            # c.separator( factor = 0.5 )   # prevents stange look when panel is narrow
            grid_flow.scale_x = 0.7
            #     row.label ( text = "Lens: " )
            grid_flow.use_property_decorate = True
            if not cameraIsValid:
                grid_flow.alert = True
                grid_flow.operator("uas_shot_manager.nolens", text="No Lens")
                grid_flow.alert = False
            else:
                grid_flow.prop(shot.camera.data, "lens", text="Lens")
            grid_flow.scale_x = 1.0
            grid_flow.prop(props, "display_lens_in_shotlist", text="")
            row.separator(factor=0.5)  # prevents strange look when panel is narrow

            box.separator(factor=0.5)

            # Output
            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            grid_flow.label(text="Output: ")
            grid_flow.label(text=str(shot.getOutputFileName()))
            grid_flow.operator("uas_shot_manager.open_explorer", emboss=True, icon_value=iconExplorer.icon_id, text="")
            row.separator(factor=0.5)  # prevents strange look when panel is narrow

            # row.prop ( context.props, "display_duration_in_shotlist", text = "" )

            # Notes
            ######################
            if props.display_notes_in_properties and shot.camera is not None:
                box = layout.box()
                box.use_property_decorate = False
                row = box.row()
                row.separator(factor=1.0)
                c = row.column()
                # grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
                subrow = c.row()
                subrow.label(text="Notes:")
                subrow.prop(props, "display_notes_in_shotlist", text="")
                subrow.separator(factor=0.5)  # prevents strange look when panel is narrow
                row = box.row()
                row.separator(factor=1.0)
                row.prop(shot, "note01", text="")
                row.separator(factor=1.0)
                row = box.row()
                row.separator(factor=1.0)
                row.prop(shot, "note02", text="")
                row.separator(factor=1.0)
                row = box.row()
                row.separator(factor=1.0)
                row.prop(shot, "note03", text="")
                row.separator(factor=1.0)

            # Camera background images
            ######################

            if props.display_camerabgtools_in_properties and shot.camera is not None:
                box = layout.box()
                box.use_property_decorate = False
                row = box.row()
                row.separator(factor=1.0)
                c = row.column()
                grid_flow = c.grid_flow(align=True, columns=4, even_columns=False)

                # grid_flow.prop(shot.camera.data.background_images[0].clip.name)
                if len(shot.camera.data.background_images) and shot.camera.data.background_images[0].clip is not None:
                    grid_flow.prop(shot.camera.data.background_images[0].clip, "filepath")
                else:
                    # tmpBGPath
                    grid_flow.operator(
                        "uas_shot_manager.openfilebrowser_for_cam_bg", text="", icon="FILEBROWSER", emboss=True
                    ).pathProp = "inputOverMediaPath"

                grid_flow.operator(
                    "uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE", emboss=True
                ).shotIndex = props.getShotIndex(shot)

                row = box.row()
                if not len(shot.camera.data.background_images):
                    row.enabled = False
                row.separator(factor=1.0)
                row.prop(shot, "bgImages_linkToShotStart")
                row.prop(shot, "bgImages_offset")


class UAS_PT_ShotManager_ShotsGlobalSettings(Panel):
    bl_label = "Shots Global Control"  # "Current Shot Properties" # keep the space !!
    bl_idname = "UAS_PT_Shot_Manager_Shots_GlobalSettings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager"

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        val = props.display_camerabgtools_in_properties and len(props.getTakes()) and len(props.get_shots())
        val = val and not props.dontRefreshUI()
        return val

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        layout = self.layout
        layout.prop(props.shotsGlobalSettings, "alsoApplyToDisabledShots")

        # Camera background images
        ######################

        if props.display_camerabgtools_in_properties:

            layout.label(text="Camera Background Images:")

            box = layout.box()
            box.use_property_decorate = False

            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            grid_flow.operator("uas_shots_settings.use_background", text="Turn On").useBackground = True
            grid_flow.operator("uas_shots_settings.use_background", text="Turn Off").useBackground = False
            grid_flow.prop(props.shotsGlobalSettings, "backgroundAlpha", text="Alpha")
            row.separator(factor=0.5)  # prevents stange look when panel is narrow

            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            c.enabled = False
            c.prop(props.shotsGlobalSettings, "proxyRenderSize")

            c = row.column()
            c.operator("uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE", emboss=True)

            # c = row.column()
            # grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            # grid_flow.prop(props.shotsGlobalSettings, "proxyRenderSize")

            # grid_flow.operator("uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE", emboss=True)

            row.separator(factor=0.5)  # prevents stange look when panel is narrow


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_ShotManager_OpenFileBrowserForCamBG(Operator):  # from bpy_extras.io_utils import ImportHelper
    bl_idname = "uas_shot_manager.openfilebrowser_for_cam_bg"
    bl_label = "Camera Background"
    bl_description = "Open a file browser to define the image or video to use as camera background"
    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    pathProp: StringProperty()

    filepath: StringProperty(subtype="FILE_PATH")

    filter_glob: StringProperty(default="*.mov;*.mp4", options={"HIDDEN"})

    def invoke(self, context, event):  # See comments at end  [1]

        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}

    def execute(self, context):
        """Use the selected file as a stamped logo"""
        #  filename, extension = os.path.splitext(self.filepath)
        #   print('Selected file:', self.filepath)
        #   print('File name:', filename)
        #   print('File extension:', extension)
        props = context.scene.UAS_shot_manager_props
        shot = props.getCurrentShot()

        # start frame of the background video is not set here since it will be linked to the shot start frame
        utils.add_background_video_to_cam(
            shot.camera.data, str(self.filepath), 0, alpha=props.shotsGlobalSettings.backgroundAlpha
        )

        shot.bgImages_linkToShotStart = shot.bgImages_linkToShotStart
        shot.bgImages_offset = shot.bgImages_offset

        return {"FINISHED"}


#################
# tools for shots
#################


class UAS_MT_ShotManager_Shots_ToolsMenu(Menu):
    bl_idname = "UAS_MT_Shot_Manager_shots_toolsmenu"
    bl_label = "Shots Tools"
    bl_description = "Shots Tools"

    def draw(self, context):
        # marker_list         = context.scene.timeline_markers
        # list_marked_cameras = [o.camera for o in marker_list if o != None]

        # Copy menu entries[ ---
        layout = self.layout
        row = layout.row(align=True)

        # row.label(text="Tools for Shots:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.remove_multiple_shots", text="Remove Disabled Shots...").action = "DISABLED"

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.remove_multiple_shots", text="Remove All Shots...").action = "ALL"

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

        # tools for shots ###
        row = layout.row(align=True)
        row.label(text="Tools for Shots:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.create_shots_from_each_camera")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.create_n_shots")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.unique_cameras")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.shots_removecamera")

        # import shots ###

        layout.separator()
        row = layout.row(align=True)
        row.label(text="Import Shots:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uasotio.openfilebrowser", text="Create Shots From EDL").importMode = "CREATE_SHOTS"

        # wkip debug - to remove:
        if config.uasDebug:
            row = layout.row(align=True)
            row.operator("uasshotmanager.createshotsfromotio_rrs", text="Create Shots From EDL - Debug")

        if config.uasDebug:
            row = layout.row(align=True)
            row.operator(
                "uasshotmanager.createshotsfromotio_rrs", text="Create Shots From EDL - Debug + file"
            ).otioFile = (
                # r"Z:\_UAS_Dev\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere.xml"
                # r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere_to40.xml"  # _to40
                r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\PredecAct01_To40_RefDebug.xml"  # _to40
            )

        # tools for precut ###
        layout.separator()
        row = layout.row(align=True)
        row.label(text="Tools for Precut:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.predec_shots_from_single_cam")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.print_montage_info")

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


#########
# MISC
#########


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
    UAS_PT_ShotManager_ShotsGlobalSettings,
    UAS_MT_ShotManager_Shots_ToolsMenu,
    UAS_ShotManager_DrawTimeline,
    UAS_PT_ShotManager_Initialize,
    #  UAS_Retimer,
    UAS_ShotManager_OpenFileBrowserForCamBG,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
