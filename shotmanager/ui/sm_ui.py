import bpy
from bpy.types import Panel, Operator

from shotmanager.config import config
from shotmanager.viewport_3d.ogl_ui import UAS_ShotManager_DrawTimeline

from shotmanager.utils import utils

from . import sm_shots_ui
from . import sm_takes_ui
from . import sm_shot_settings_ui
from . import sm_shots_global_settings_ui

import logging

_logger = logging.getLogger(__name__)

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

        # row.operator("utils.launchrender", text="", icon="RENDER_STILL").renderMode = "STILL"
        # row.operator("utils.launchrender", text="", icon="RENDER_ANIMATION").renderMode = "ANIMATION"
        # row.separator(factor=2)

        #    row.operator("render.opengl", text="", icon='IMAGE_DATA')
        #   row.operator("render.opengl", text="", icon='RENDER_ANIMATION').animation = True
        #    row.operator("screen.screen_full_area", text ="", icon = 'FULLSCREEN_ENTER').use_hide_panels=False

        row.operator(
            "uas_shot_manager.go_to_video_shot_manager", text="", icon="SEQ_STRIP_DUPLICATE"
        ).vseSceneName = "RRS_CheckSequence"

        row.separator(factor=0.5)
        icon = config.icons_col["General_Explorer_32"]
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
            bpy.data.filepath
        )

        row.separator(factor=0.5)
        row.menu("UAS_MT_Shot_Manager_prefs_mainmenu", icon="PREFERENCES", text="")

        row.separator(factor=1.0)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences
        currentTake = props.getCurrentTake()
        currentTakeInd = props.getCurrentTakeIndex()

        # addon warning message - for beta message display
        ###############
        # import addon_utils

        # addonWarning = [
        #     addon.bl_info.get("warning", "")
        #     for addon in addon_utils.modules()
        #     if addon.bl_info["name"] == "UAS Shot Manager"
        # ]

        addonWarning = [""]
        if "" != addonWarning[0]:
            row = layout.row()
            row.alignment = "CENTER"
            row.alert = True
            row.label(text=f" ***  {addonWarning[0]}  ***")
            row.alert = False

        if config.uasDebug:
            row = layout.row()
            row.alignment = "CENTER"
            strDebug = " *** Debug Mode ***"
            # if props.useBGSounds:
            #     strDebug += "  BG Sounds Used"
            row.alert = True
            row.label(text=strDebug)
            row.prop(props, "useBGSounds")
            row.alert = False

        # if not "UAS_shot_manager_props" in context.scene:
        if not props.isInitialized:
            layout.separator()
            row = layout.row()
            row.alert = True
            row.operator("uas_shot_manager.initialize")
            row.alert = False
            layout.separator()

        # scene warnings
        ################
        warningsList = props.getWarnings(scene)
        if len(warningsList):
            for w in warningsList:
                row = layout.row()
                row.separator()
                row.alert = True
                row.label(text=w)
                row.alert = False

        if props.use_project_settings and "Scene" in scene.name:
            c = layout.column()
            c.alert = True
            c.alignment = "CENTER"
            c.label(text=" *************************************** ")
            c.label(text=" *    SCENE NAME IS INVALID !!!    * ")
            c.label(text=" *************************************** ")

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
        subRow = row.row(align=True)
        subRow.prop(context.window_manager, "UAS_shot_manager_display_timeline", text="", toggle=True, icon="TIME")
        subSubRow = subRow.row(align=True)
        subSubRow.enabled = context.window_manager.UAS_shot_manager_display_timeline
        subSubRow.prop(
            context.window_manager,
            "UAS_shot_manager_toggle_montage_interaction",
            text="",
            icon="ARROW_LEFTRIGHT",
            toggle=True,
        )

        # row.emboss = "PULLDOWN_MENU"
        row.operator("uas_shot_manager.features", text="", icon="PROPERTIES")

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

        # takes
        ################
        panelIcon = "TRIA_DOWN" if prefs.take_properties_extended else "TRIA_RIGHT"

        layout.separator(factor=0.3)
        box = layout.box()
        row = box.row(align=False)
        row.prop(prefs, "take_properties_extended", text="", icon=panelIcon, emboss=False)

        takeStr = "Take:" if not props.display_advanced_infos else f"Take ({currentTakeInd + 1}/{props.getNumTakes()}):"
        row.label(text=takeStr)
        subrow = row.row(align=True)
        #    row.scale_y = 1.5
        subrow.scale_x = 2.0

        subsubrow = subrow.row(align=False)
        subsubrow.scale_x = 0.8

        takeHasNotes = False
        if currentTake is not None:
            takeHasNotes = currentTake.hasNotes()
            if takeHasNotes:
                # if item.hasNotes():
                notesIcon = "ALIGN_TOP"
                notesIcon = "ALIGN_JUSTIFY"
                notesIcon = "WORDWRAP_OFF"
                # notesIcon = "TEXT"
                # notesIcon = "OUTLINER_DATA_GP_LAYER"
                subsubrow.prop(prefs, "take_notes_extended", text="", icon=notesIcon, emboss=prefs.take_notes_extended)
            else:
                if props.display_notes_in_properties:
                    notesIcon = "WORDWRAP_ON"
                    notesIcon = "MESH_PLANE"
                    subsubrow.prop(
                        prefs, "take_notes_extended", text="", icon=notesIcon, emboss=prefs.take_notes_extended
                    )
                    # emptyIcon = config.icons_col["General_Empty_32"]
                    # row.operator(
                    #     "uas_shot_manager.shots_shownotes", text="", icon_value=emptyIcon.icon_id
                    # ).index = index

        subrow.prop(props, "current_take_name", text="")
        #    row.menu(UAS_MT_ShotManager_Takes_ToolsMenu.bl_idname,text="Tools",icon='TOOL_SETTINGS')

        # row = row.row(align=False)
        row.menu("UAS_MT_Shot_Manager_takes_toolsmenu", icon="TOOL_SETTINGS", text="")

        if prefs.take_properties_extended:
            row = box.row()
            row.label(text="Take Properties:")
            subBox = box.box()
            subRow = subBox.row()
            subRow.separator()
            subRow.prop(currentTake, "globalEditDirectory", text="Edit Dir")
            subRow = subBox.row()
            subRow.separator()
            subRow.prop(currentTake, "globalEditVideo", text="Edit Animatic")
            subRow = subBox.row()
            subRow.separator()
            subRow.prop(currentTake, "startInGlobalEdit", text="Start in Global Edit")

        # Notes
        ######################
        if currentTake is not None and (
            (props.display_notes_in_properties and prefs.take_properties_extended)
            or (props.display_notes_in_properties and prefs.take_notes_extended)
            or (takeHasNotes and prefs.take_notes_extended)
        ):
            # or (props.display_notes_in_properties and prefs.take_properties_extended)
            # ):
            panelIcon = "TRIA_DOWN" if prefs.take_notes_extended else "TRIA_RIGHT"

            box = box.box()
            box.use_property_decorate = False
            row = box.row()
            row.prop(prefs, "take_notes_extended", text="", icon=panelIcon, emboss=False)
            # row.separator(factor=1.0)
            c = row.column()
            # grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            subrow = c.row()
            subrow.label(text="Take Notes:")
            subrow.separator(factor=0.5)  # prevents strange look when panel is narrow

            if prefs.take_notes_extended:
                row = box.row()
                row.separator(factor=1.0)
                row.prop(currentTake, "note01", text="")
                row.separator(factor=1.0)
                row = box.row()
                row.separator(factor=1.0)
                row.prop(currentTake, "note02", text="")
                row.separator(factor=1.0)
                row = box.row()
                row.separator(factor=1.0)
                row.prop(currentTake, "note03", text="")
                row.separator(factor=1.0)
                box.separator(factor=0.1)

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

            shotsStr = "Shots:" if not props.display_advanced_infos else f"Shots ({numEnabledShots}/{numShots}):"
            subrow.label(text=shotsStr)
            # subrow.separator()
            #  column_flow.scale_x = 1.0
            subrow = column_flow.row()
            subrow.alignment = "LEFT"
            #   subrow.scale_x = 1.0
            prefs = context.preferences.addons["shotmanager"].preferences
            iconCheckBoxes = "CHECKBOX_HLT" if not prefs.toggleShotsEnabledState else "CHECKBOX_DEHLT"
            subrow.operator("uas_shot_manager.enabledisableall", text="", icon=iconCheckBoxes)

            # subrow.separator(factor=0.2)
            subrow.prop(
                props, "display_edit_times_in_shotlist", text="Edit Times", toggle=True, icon="SEQ_STRIP_DUPLICATE"
            )

            subrow = column_flow.row()
            subrow.scale_x = 0.9
            subrow.alignment = "RIGHT"

            if config.uasDebug:
                subrow.operator("uas_shot_manager.enabledisablegreasepencil", text="", icon="OUTLINER_OB_GREASEPENCIL")
            subrow.operator("uas_shot_manager.enabledisablecamsbg", text="", icon="VIEW_CAMERA")

            if props.useLockCameraView:
                subrow.alert = True
            subrow.prop(props, "useLockCameraView", text="", icon="CAMERA_DATA")
            if props.useLockCameraView:
                subrow.alert = False

            subrow.separator()
            subrow.operator("uas_shot_manager.scenerangefromshot", text="", icon="PREVIEW_RANGE")
            #    row.operator("uas_shot_manager.scenerangefromenabledshots", text="", icon="PREVIEW_RANGE")
            subrow.operator("uas_shot_manager.scenerangefrom3dedit", text="", icon="PREVIEW_RANGE")

            col = row.column(align=True)
            col.separator(factor=3.0)
            # row.operator("uas_shot_manager.shots_prefs", text="", icon="SETTINGS")

            row = box.row()
            row.template_list(
                "UAS_UL_ShotManager_Items", "", currentTake, "shots", props, "selected_shot_index", rows=6
            )

            col = row.column(align=True)
            col.operator("uas_shot_manager.shot_add", icon="ADD", text="")
            col.operator("uas_shot_manager.shot_duplicate", icon="DUPLICATE", text="")
            col.operator("uas_shot_manager.shot_remove", icon="REMOVE", text="")
            col.separator()
            col.operator("uas_shot_manager.shot_move", icon="TRIA_UP", text="").action = "UP"
            col.operator("uas_shot_manager.shot_move", icon="TRIA_DOWN", text="").action = "DOWN"
            col.separator()
            col.menu("UAS_MT_Shot_Manager_shots_toolsmenu", icon="TOOL_SETTINGS", text="")

            # layout.separator ( factor = 1 )


#########
# MISC
#########


class UAS_PT_ShotManager_Initialize(Operator):
    bl_idname = "uas_shot_manager.initialize"
    bl_label = "Initialize Shot Manager"
    bl_description = "Initialize Shot Manager"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.scene.UAS_shot_manager_props.initialize_shot_manager()

        return {"FINISHED"}


classes = (
    UAS_PT_ShotManager,
    UAS_ShotManager_DrawTimeline,
    UAS_PT_ShotManager_Initialize,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    sm_takes_ui.register()
    sm_shots_ui.register()
    sm_shot_settings_ui.register()
    sm_shots_global_settings_ui.register()


def unregister():
    sm_shots_global_settings_ui.unregister()
    sm_shot_settings_ui.unregister()
    sm_shots_ui.unregister()
    sm_takes_ui.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

