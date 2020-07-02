import bpy
from bpy.types import Panel, Operator, Menu
from bpy.props import StringProperty, IntProperty

from ..config import config
from ..ogl_ui import UAS_ShotManager_DrawTimeline, UAS_ShotManager_DrawCameras_UI

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

    # About panel ###
    def draw_header(self, context):
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        if context.window_manager.UAS_shot_manager_displayAbout:
            # _emboss = True
            row.alert = True
        else:
            #    _emboss = False
            row.alert = False

        icon = config.icons_col["General_Ubisoft_32"]
        row.prop(context.window_manager, "UAS_shot_manager_displayAbout", icon_value=icon.icon_id, icon_only=True)

    def draw_header_preset(self, context):
        props = context.scene.UAS_shot_manager_props
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)

        row.operator("utils.launchrender", text="", icon="RENDER_STILL").renderMode = "STILL"
        row.operator("utils.launchrender", text="", icon="RENDER_ANIMATION").renderMode = "ANIMATION"
        # row.label(text = "|")
        row.separator(factor=2)

        icon = config.icons_col["General_Explorer_32"]
        row.operator("uas_shot_manager.render_openexplorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
            bpy.data.filepath
        )

        #    row.operator("render.opengl", text="", icon='IMAGE_DATA')
        #   row.operator("render.opengl", text="", icon='RENDER_ANIMATION').animation = True
        #    row.operator("screen.screen_full_area", text ="", icon = 'FULLSCREEN_ENTER').use_hide_panels=False

        row.separator(factor=2)
        row.operator("uas_shot_manager.go_to_video_shot_manager", text="", icon="SEQ_STRIP_DUPLICATE")

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

        row.emboss = "PULLDOWN_MENU"
        row.operator("uas_shot_manager.playbar_prefs", text="", icon="SETTINGS")

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
        # wkip to remove - check with project fps!!
        if 25 != scene.render.fps:
            row.alert = True
        row.label(text=str(scene.render.fps) + " fps")

        ################
        # warnings
        warningsList = props.getWarnings(scene)
        if len(warningsList):
            for w in warningsList:
                row = layout.row()
                row.separator()
                row.alert = True
                row.label(text=w)
                row.alert = False

        ################
        # takes
        row = layout.row()  # just to give some space...
        box = layout.box()
        row = box.row()
        #    row.scale_y = 1.5
        row.prop(props, "current_take_name")
        #    row.menu(UAS_MT_ShotManager_Takes_ToolsMenu.bl_idname,text="Tools",icon='TOOL_SETTINGS')
        row.menu("UAS_MT_Shot_Manager_takes_toolsmenu", icon="TOOL_SETTINGS", text="")

        ################
        # shots
        if len(props.takes):
            box = layout.box()
            row = box.row()
            numShots = len(props.getShotsList(ignoreDisabled=False))
            numEnabledShots = len(props.getShotsList(ignoreDisabled=True))
            row.label(text=f"Shots ({numEnabledShots}/{numShots}): ")

            row.separator(factor=1)
            row.operator("uas_shot_manager.enabledisableall", text="", icon="CHECKBOX_HLT")

            row.operator("uas_shot_manager.scenerangefromshot", text="", icon="PREVIEW_RANGE")
            #    row.operator("uas_shot_manager.scenerangefromenabledshots", text="", icon="PREVIEW_RANGE")
            row.operator("uas_shot_manager.scenerangefrom3dedit", text="", icon="PREVIEW_RANGE")

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

        cam = "Cam" if current_shot_index == index else ""
        currentFrame = context.scene.frame_current

        if item.enabled:
            icon = config.icons_col[f"ShotMan_Enabled{cam}"]
            if item.start <= context.scene.frame_current <= item.end:
                icon = config.icons_col[f"ShotMan_EnabledCurrent{cam}"]
        else:
            icon = config.icons_col[f"ShotMan_Disabled{cam}"]

        row = layout.row()
        row.operator("uas_shot_manager.set_current_shot", icon_value=icon.icon_id, text="").index = index

        row = layout.row(align=True)
        row.scale_x = 1.0
        if props.display_selectbut_in_shotlist:
            row.operator("uas_shot_manager.shots_selectcamera", text="", icon="RESTRICT_SELECT_OFF").index = index

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
        grid_flow = row.grid_flow(align=True, columns=9, even_columns=False)
        grid_flow.use_property_split = False
        button_x_factor = 0.6

        # start
        ###########

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
            # grid_flow.label ( text = str(item.getDuration()) )
            grid_flow.operator("uas_shot_manager.shot_duration", text=str(item.getDuration())).index = index
        else:
            grid_flow.scale_x = 0.05
            grid_flow.operator("uas_shot_manager.shot_duration", text="").index = index
        grid_flow.alert = False

        # end
        ###########

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

        # camera
        ###########

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

    def draw_header(self, context):
        scene = context.scene
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
            if shot.camera is None:
                grid_flow.alert = True
            grid_flow.prop(shot, "camera", text="Camera")
            if shot.camera is None:
                grid_flow.alert = False
            grid_flow.prop(props, "display_camera_in_shotlist", text="")

            # c.separator( factor = 0.5 )   # prevents stange look when panel is narrow
            grid_flow.scale_x = 0.7
            #     row.label ( text = "Lens: " )
            grid_flow.use_property_decorate = True
            if shot.camera is not None:
                grid_flow.prop(shot.camera.data, "lens", text="Lens")
            else:
                grid_flow.alert = True
                grid_flow.operator("uas_shot_manager.nolens", text="No Lens")
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

            if shot.camera is not None:
                box = layout.box()
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

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShot(props.selected_shot_index)
        val = len(context.scene.UAS_shot_manager_props.getTakes()) and shot

        return val


class UAS_PT_ShotManager_ShotsGlobalSettings(Panel):
    bl_label = "Shots Global Control"  # "Current Shot Properties" # keep the space !!
    bl_idname = "UAS_PT_Shot_Manager_Shots_GlobalSettings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager"

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        layout = self.layout

        layout.label(text="Camera Background Images:")
        box = layout.box()

        row = box.row()
        row.separator(factor=1.0)
        c = row.column()
        grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
        grid_flow.operator("uas_shots_settings.use_background", text="Turn On").useBackground = True
        grid_flow.operator("uas_shots_settings.use_background", text="Turn Off").useBackground = False
        grid_flow.prop(props.shotsGlobalSettings, "backgroundAlpha", text="Alpha")
        grid_flow.prop(props.shotsGlobalSettings, "proxyRenderSize")

        row.separator(factor=0.5)  # prevents stange look when panel is narrow

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        val = len(props.getTakes()) and len(props.get_shots())

        return val


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


class UAS_ShotManager_RemoveBGImages(Operator):
    bl_idname = "uas_shot_manager.remove_bg_images"
    bl_label = "Remove BG Images"
    bl_description = "Remove the camera background images"
    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    shotIndex: IntProperty()

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props
        shot = props.getShot(self.shotIndex)
        if shot.camera is not None and len(shot.camera.data.background_images):
            # if shot.camera.data.background_images[0].clip is not None:
            shot.camera.data.show_background_images = False
            # shot.camera.data.background_images[0].clip = None
            shot.camera.data.background_images.clear()
            # shot.camera.data.background_images[0].clip.filepath = ""
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
        row.operator("uasotio.openfilebrowser", text="Import Shots From OTIO")
        # wkip debug - to remove:
        row = layout.row(align=True)
        row.operator("uasshotmanager.importotio", text="Import Shots From OTIO - Debug")

        # tools for precut ###
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


class UAS_ShotManager_EnableDisableAll(Operator):
    bl_idname = "uas_shot_manager.enabledisableall"
    bl_label = "Enable / Disable All Shots"
    bl_description = "Enable all shots,\nClick + Ctrl: Disable all shots,\nClick + Shift: Invert shots state"
    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    def invoke(self, context, event):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        enableMode = "ENABLEALL"
        if event.shift:
            enableMode = "INVERT"
        elif event.ctrl:
            enableMode = "DISABLEALL"

        selectedShotInd = props.getSelectedShotIndex()
        shotsList = props.getShotsList()
        for shot in shotsList:
            if "ENABLEALL" == enableMode:
                shot.enabled = True
            elif "DISABLEALL" == enableMode:
                shot.enabled = False
            elif "INVERT" == enableMode:
                shot.enabled = not shot.enabled

        props.setSelectedShotByIndex(selectedShotInd)

        return {"FINISHED"}


class UAS_ShotManager_SceneRangeFromShot(Operator):
    bl_idname = "uas_shot_manager.scenerangefromshot"
    bl_label = "Scene Range From Shot"
    bl_description = "Set scene time range with CURRENT shot range"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        currentShot = props.getCurrentShot()
        scene.use_preview_range = True

        scene.frame_preview_start = currentShot.start
        scene.frame_preview_end = currentShot.end

        return {"FINISHED"}


# # operator here must be a duplicate of UAS_ShotManager_SceneRangeFromShot is order to use a different description
# class UAS_ShotManager_SceneRangeFromEnabledShots(Operator):
#     bl_idname = "uas_shot_manager.scenerangefromenabledshots"
#     bl_label = "Scene Range From Enabled Shot"
#     bl_description = "Set scene time range with enabled shots range"
#     bl_options = {"INTERNAL"}

#     def execute(self, context):
#         scene = context.scene
#         props = scene.UAS_shot_manager_props

#         shotList = props.getShotsList(ignoreDisabled=True)

#         if len(shotList):
#             scene.use_preview_range = True

#             scene.frame_preview_start = shotList[0].start
#             scene.frame_preview_end = shotList[len(shotList) - 1].end

#         return {"FINISHED"}


# operator here must be a duplicate of UAS_ShotManager_SceneRangeFromShot is order to use a different description
class UAS_ShotManager_SceneRangeFrom3DEdit(Operator):
    bl_idname = "uas_shot_manager.scenerangefrom3dedit"
    bl_label = "Scene Range From 3D Edit"
    bl_description = "Set scene time range with the the 3D edit range"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        shotList = props.getShotsList(ignoreDisabled=True)

        if 0 < len(shotList):
            scene.use_preview_range = True
            scene.frame_preview_start = shotList[0].start
            scene.frame_preview_end = shotList[len(shotList) - 1].end

        return {"FINISHED"}


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
    UAS_ShotManager_DrawCameras_UI,
    #  UAS_Retimer,
    UAS_ShotManager_EnableDisableAll,
    UAS_ShotManager_SceneRangeFromShot,
    #    UAS_ShotManager_SceneRangeFromEnabledShots,
    UAS_ShotManager_SceneRangeFrom3DEdit,
    UAS_ShotManager_OpenFileBrowserForCamBG,
    UAS_ShotManager_RemoveBGImages,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
