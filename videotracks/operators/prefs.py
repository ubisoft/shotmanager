import bpy
from bpy.types import Panel, Operator, Menu

from ..config import config

#############
# Preferences
#############


class UAS_MT_ShotManager_Prefs_MainMenu(Menu):
    bl_idname = "UAS_MT_Shot_Manager_prefs_mainmenu"
    bl_label = "General Preferences"
    # bl_description = "General Preferences"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("uas_shot_manager.general_prefs", text="Preferences...")
        row = layout.row(align=True)
        row.operator("uas_shot_manager.project_settings_prefs", text="Project Settings...")

        if config.uasDebug:
            layout.separator()
            row = layout.row(align=True)
            row.operator_context = "INVOKE_DEFAULT"
            row.operator("uas_shot_manager.playbar_prefs", text="Playbar Settings...")  # , icon="SETTINGS")

            row = layout.row(align=True)
            row.operator_context = "INVOKE_DEFAULT"
            row.operator("uas_shot_manager.shots_prefs", text="Shots Settings...")  # , icon="SETTINGS")

            layout.separator()
            row = layout.row(align=True)
            row.label(text="Tools for Debug:")

            row = layout.row(align=True)
            row.operator_context = "INVOKE_DEFAULT"
            row.label(text="Add debug operator here")
            # row.operator("uas_shot_manager.predec_shots_from_single_cam")

        layout.separator()
        row = layout.row(align=True)

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.file_info", text="File Info...")

        layout.separator()
        row = layout.row(align=True)

        row.operator("uas_shot_manager.about", text="About...")


class UAS_ShotManager_General_Prefs(Operator):
    bl_idname = "uas_shot_manager.general_prefs"
    bl_label = "General Preferences"
    bl_description = "Display the General Preferences panel"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences
        layout = self.layout

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        box = layout.box()
        box.use_property_decorate = False
        col = box.column()
        col.use_property_split = True
        # col.use_property_decorate = False

        col.prop(prefs, "new_shot_duration", text="Default Shot Length")

        ##################
        # Overriden by project settings
        ##################

        layout.separator()
        if props.use_project_settings:
            row = layout.row()
            row.alert = True
            row.label(text="Overriden by Project Settings:")
        else:
            # layout.label(text="Others")
            pass
        box = layout.box()
        box.use_property_decorate = False
        box.enabled = not props.use_project_settings
        col = box.column()
        col.use_property_split = True
        col.prop(props, "new_shot_prefix", text="Default Shot Prefix")

        # row = layout.row()
        # row.label(text="Handles:")
        col.prop(props, "render_shot_prefix")
        col.prop(props, "renderSingleFrameShotAsImage")

        col.separator()
        row = col.row()
        row.prop(props, "use_handles", text="Use Handles")
        subrow = row.row()
        subrow.enabled = props.project_use_shot_handles
        subrow.prop(props, "handles", text="Handles")
        col.separator()

        box = layout.box()
        box.use_property_decorate = False
        row = box.row()
        row.label(text="Debug Mode:")
        subrow = row.row()
        subrow.operator("uas_shot_manager.enable_debug", text="On").enable_debug = True
        subrow.operator("uas_shot_manager.enable_debug", text="Off").enable_debug = False

        # col.use_property_split = True
        # col.o
        # col.use_property_decorate = False

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


class UAS_ShotManager_ProjectSettings_Prefs(Operator):
    bl_idname = "uas_shot_manager.project_settings_prefs"
    bl_label = "Project Settings"
    bl_description = "Display the Project Settings panel"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        print("Invoke prefs")
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.UAS_shot_manager_props

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        layout.prop(props, "use_project_settings")
        box = layout.box()
        box.use_property_decorate = False
        box.enabled = props.use_project_settings
        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.separator(factor=1)

        col.prop(props, "project_name")
        col.prop(props, "project_fps")
        col.prop(props, "project_resolution_x")
        col.prop(props, "project_resolution_y")
        col.prop(props, "project_resolution_framed_x")
        col.prop(props, "project_resolution_framed_y")
        col.prop(props, "project_shot_format")

        col.separator(factor=1)
        row = col.row()
        row.prop(props, "project_use_shot_handles")
        subrow = row.row()
        subrow.enabled = props.project_use_shot_handles
        subrow.prop(props, "project_shot_handle_duration", text="Handles")
        col.separator(factor=1)

        col.prop(props, "project_output_format")
        col.prop(props, "project_color_space")
        col.prop(props, "project_asset_name")

        # additional settings
        box.separator()
        box.label(text="Additional Settings:")
        col = box.column()
        col.enabled = props.use_project_settings
        col.use_property_split = True
        col.use_property_decorate = False
        col.separator(factor=1)

        stampInfoStr = "Use Stamp Info Add-on"
        if not props.isStampInfoAvailable():
            stampInfoStr += "  (Warning: Currently NOT installed)"
        col.prop(props, "project_use_stampinfo", text=stampInfoStr)

        col.prop(props, "project_images_output_format")

        col.separator(factor=1)

        # project settings summary display
        if config.uasDebug:
            settingsList = props.applyProjectSettings(settingsListOnly=True)
            box = layout.box()
            for prop in settingsList:
                row = box.row(align=True)
                row.label(text=prop[0] + ":")
                row.label(text=str(prop[1]))

    def execute(self, context):
        print("exec proj settings")
        context.scene.UAS_shot_manager_props.applyProjectSettings()
        return {"FINISHED"}

    def cancel(self, context):
        print("cancel proj settings")
        # since project properties are immediatly applied to Shot Manager properties then we also force the
        # application of the settings in the scene even if the user is not clicking on OK button
        context.scene.UAS_shot_manager_props.applyProjectSettings()


class UAS_PT_ShotManagerPref_General(Panel):
    bl_label = "General"
    bl_idname = "UAS_PT_Shot_Manager_Pref_General"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager_Pref"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column()
        col.use_property_split = True
        col.label(text="PlaceHolder")


class UAS_ShotManager_Playbar_Prefs(Operator):
    bl_idname = "uas_shot_manager.playbar_prefs"
    bl_label = "Playbar, Timeline ad Edit Settings"
    bl_description = "Display the Playbar, Timeline and Edit Preferences panel"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props

        layout = self.layout
        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        # Playbar ######
        # layout.label(text="Playbar:")
        # box = layout.box()
        # col = box.column()

        # col.use_property_split = True
        # col.separator(factor=1.7)
        # col.prop(props, "current_shot_properties_mode")
        # box.separator(factor=0.5)

        # Play ######
        # layout.separator(factor=1)
        layout.label(text="Shot Play Mode:")
        box = layout.box()
        box.use_property_decorate = False
        col = box.column()

        col.use_property_split = True
        col.prop(props, "refreshUIDuringPlay")

        # Timeline ######
        # layout.separator(factor=1)
        layout.label(text="Timeline:")
        box = layout.box()
        box.use_property_decorate = False
        col = box.column()

        col.use_property_split = True
        # col.use_property_decorate = False
        col.prop(
            props, "display_disabledshots_in_timeline", text="Display Disabled Shots",
        )

        # Edit ######
        layout.separator(factor=1)
        layout.label(text="Edit:")
        box = layout.box()
        box.use_property_decorate = False
        col = box.column()

        col.use_property_split = True
        col.prop(props, "editStartFrame", text="Index of the First Frame in the Edit:")
        # box.separator(factor=0.5)

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


class UAS_ShotManager_Shots_Prefs(Operator):
    bl_idname = "uas_shot_manager.shots_prefs"
    bl_label = "Shots Settings"
    bl_description = "Display the Shots Preferences panel"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props

        layout = self.layout

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        # Shot List
        ##############
        layout.label(text="Shot List:")
        box = layout.box()
        box.use_property_decorate = False

        # empty spacer column
        row = box.row()
        col = row.column()
        col.scale_x = 0.4
        col.label(text=" ")
        col = row.column()

        col.separator(factor=0.5)
        col.use_property_split = False
        col.prop(props, "display_selectbut_in_shotlist", text="Display Camera Select Button")
        col.prop(props, "display_enabled_in_shotlist", text="Display Enabled State")
        col.prop(props, "display_getsetcurrentframe_in_shotlist", text="Display Get/Set current Frame Buttons")
        col.prop(props, "display_edit_times_in_shotlist", text="Display Edit Times in Shot List")

        col.separator(factor=1.7)
        col.prop(props, "highlight_all_shot_frames", text="Highlight Framing Values When Equal to Current Time")
        col.prop(props, "display_duration_after_time_range", text="Display Shot Duration After Time Range")

        col.separator(factor=1.0)
        col.prop(props, "use_camera_color", text="Use Camera Color for Shots ")

        col.use_property_split = False
        col.separator(factor=1.7)
        col.prop(props, "current_shot_properties_mode")

        box.separator(factor=0.5)

        # User Prefs at addon level
        ###############
        prefs = bpy.context.preferences.addons["shotmanager"].preferences

        # empty spacer column
        row = box.row()
        col = row.column()
        col.scale_x = 0.4
        col.label(text=" ")
        col = row.column()

        col.separator(factor=2.0)
        #  col.label(text="User Preferenes (in Preference Add-on Window):")
        col.prop(
            prefs,
            "current_shot_changes_current_time",
            text="Set Current Frame To Shot Start When Current Shot Is Changed",
        )
        col.prop(
            prefs, "current_shot_changes_time_range", text="Set Time Range To Shot Range When Current Shot Is Changed"
        )

        # Shot infos displayed in viewport
        ###############
        layout.separator(factor=1)
        layout.label(text="Shot Info Displayed in 3D Viewport:")
        box = layout.box()
        col = box.column()

        col.use_property_split = True
        col.prop(props, "display_shotname_in_3dviewport", text="Display Shot name in 3D Viewport")
        col.prop(props, "display_hud_in_3dviewport", text="Display HUD in 3D Viewport")

        # col.prop(
        #     props, "display_selectbut_in_shotlist", text="Display Camera Select Button",
        # )
        # col.prop(
        #     props, "highlight_all_shot_frames", text="Highlight Framing Values When Equal to Current Time",
        # )

        # col.separator(factor=0.7)
        # col.prop(props, "use_camera_color", text="Use Camera Color for Shots ")

        # col.separator(factor=0.7)
        # col.prop(props, "change_time", text="Set Current Frame To Shot Start When Current Shot Is Changed")

        # col.use_property_split = True
        # col.separator(factor=1.7)
        # col.prop(props, "current_shot_properties_mode")
        # box.separator(factor=0.5)

        layout.separator(factor=2)

    def execute(self, context):
        return {"FINISHED"}


# class UAS_PT_ShotManager_Render_StampInfoProperties(Panel):
#     bl_label = "Stamp Info Properties"
#     bl_idname = "UAS_PT_Shot_Manager_Pref_StampInfoPrefs"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "UAS Shot Man"
#     bl_options = {"DEFAULT_CLOSED"}
#     bl_parent_id = "UAS_PT_Shot_Manager_Pref"

#     def draw_header_preset(self, context):
#         layout = self.layout
#         layout.emboss = "NONE"
#         row = layout.row(align=True)

#         if getattr(scene, "UAS_StampInfo_Settings", None) is not None:
#             # row.alert = True
#             row.label(text="Version not found")
#             row.alert = False
#         else:
#             try:
#                 versionStr = utils.addonVersion("UAS_StampInfo")
#                 row.label(text="Loaded - V." + versionStr)
#                 # row.label(text="Loaded - V." + context.scene.UAS_StampInfo_Settings.version())
#             except Exception as e:
#                 #    row.alert = True
#                 row.label(text="Not found")

#     def draw(self, context):
#         box = self.layout.box()
#         row = box.row()
#         row.prop(context.scene.UAS_shot_manager_props, "useStampInfoDuringRendering")


_classes = (
    UAS_MT_ShotManager_Prefs_MainMenu,
    UAS_ShotManager_General_Prefs,
    UAS_ShotManager_ProjectSettings_Prefs,
    # UAS_PT_ShotManagerPref_General,
    UAS_ShotManager_Playbar_Prefs,
    UAS_ShotManager_Shots_Prefs,
    # UAS_PT_ShotManager_Render_StampInfoProperties,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
