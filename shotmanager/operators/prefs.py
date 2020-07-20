import bpy
from bpy.types import Panel, Operator, Menu

from ..utils import utils

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

        layout.separator()
        row = layout.row(align=True)

        row.operator("uas_shot_manager.about", text="About...")


class UAS_ShotManager_About(Operator):
    bl_idname = "uas_shot_manager.about"
    bl_label = "About UAS Shot Manager..."
    bl_description = "More information about UAS Shot Manager..."
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props
        layout = self.layout
        box = layout.box()

        # Version
        ###############
        row = box.row()
        row.separator()
        row.label(
            text="Version:" + props.version()[0] + "   -    (" + "July 2020" + ")" + "   -    Ubisoft Animation Studio"
        )

        # Authors
        ###############
        row = box.row()
        row.separator()
        row.label(text="Written by Julien Blervaque (aka Werwack), Romain Carriquiry Borchiari")

        # Purpose
        ###############
        row = box.row()
        row.label(text="Purpose:")
        row = box.row()
        row.separator()
        row.label(text="Create a set of camera shots and edit them")
        row = box.row()
        row.separator()
        row.label(text="in the 3D View as you would do with video clips.")

        # Dependencies
        ###############
        row = box.row()
        row.label(text="Dependencies:")
        row = box.row()
        row.separator()
        row.label(text="- OpenTimelineIO")
        row = box.row()
        row.separator()
        row.label(text="- UAS Stamp Info")

        if "UAS_StampInfo_Settings" not in context.scene or context.scene["UAS_StampInfo_Settings"] is None:
            # row.alert = True
            row.label(text="Version not found")
            row.alert = False
        else:
            try:
                versionStr = utils.addonVersion("UAS_StampInfo")
                row.label(text="Loaded - V." + versionStr)
                # row.label(text="Loaded - V." + context.scene.UAS_StampInfo_Settings.version())
            except Exception as e:
                #    row.alert = True
                row.label(text="Not found")

        row.separator()

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


class UAS_ShotManager_General_Prefs(Operator):
    bl_idname = "uas_shot_manager.general_prefs"
    bl_label = "General Preferences"
    bl_description = "Display the General Preferences panel"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props
        layout = self.layout

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        box = layout.box()
        col = box.column()

        col.use_property_split = True
        # col.use_property_decorate = False

        col.prop(props, "new_shot_duration", text="Default Shot Length")
        col.prop(props, "new_shot_prefix", text="Default Shot Prefix")

        # row = layout.row()
        # row.label(text="Handles:")
        col.prop(props, "handles", text="Handles Duration")

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


class UAS_ShotManager_ProjectSettings_Prefs(Operator):
    bl_idname = "uas_shot_manager.project_settings_prefs"
    bl_label = "Project Settings"
    bl_description = "Display the Project Settings panel"
    bl_options = {"INTERNAL"}

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
        col = box.column()
        col.enabled = props.use_project_settings
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

        col.prop(props, "project_shot_handle_duration")

        col.prop(props, "project_output_format")
        col.prop(props, "project_color_space")
        col.prop(props, "project_asset_name")

        col.separator(factor=2)
        col.prop(props, "project_use_stampinfo")
        col.separator(factor=1)

        settingsList = props.restoreProjectSettings(settingsListOnly=True)

        # project settings summary display
        # box = layout.box()
        # for prop in settingsList:
        #     row = box.row(align=True)
        #     row.label(text=prop[0] + ":")
        #     row.label(text=str(prop[1]))

    def execute(self, context):
        print("exec prefs")
        return {"FINISHED"}


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
        return context.window_manager.invoke_props_dialog(self, width=400)

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
        col = box.column()

        col.use_property_split = True
        col.prop(props, "refreshUIDuringPlay")

        # Timeline ######
        # layout.separator(factor=1)
        layout.label(text="Timeline:")
        box = layout.box()
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
        return context.window_manager.invoke_props_dialog(self, width=400)

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
        col = box.column()

        col.separator(factor=0.5)
        col.use_property_split = True
        col.prop(props, "display_selectbut_in_shotlist", text="Display Camera Select Button")
        col.prop(props, "display_enabled_in_shotlist", text="Display Enabled State")
        col.prop(props, "display_getsetcurrentframe_in_shotlist", text="Display Get/Set current Frame Buttons")
        col.prop(props, "display_edit_times_in_shotlist", text="Display Edit Times in Shot List")

        col.separator(factor=1.7)
        col.prop(props, "highlight_all_shot_frames", text="Highlight Framing Values When Equal to Current Time")

        col.separator(factor=1.0)
        col.prop(props, "use_camera_color", text="Use Camera Color for Shots ")

        col.separator(factor=1.0)
        col.prop(props, "change_time", text="Set Current Frame To Shot Start When Current Shot Is Changed")

        col.use_property_split = True
        col.separator(factor=1.7)
        col.prop(props, "current_shot_properties_mode")
        box.separator(factor=0.5)

        # Shot infos displayed in viewport
        ###############
        layout.separator(factor=1)
        layout.label(text="Shot Info Displayed in 3D Viewport:")
        box = layout.box()
        col = box.column()

        col.use_property_split = True
        col.prop(props, "display_shotname_in_3dviewport", text="Display Shot name in 3D Viewport")

        # Properties themes
        ###############
        layout.separator(factor=1)
        layout.label(text="Additional Properties and Tools by Themes:")
        box = layout.box()
        row = box.row()

        # row.use_property_split = True
        row.alignment = "CENTER"
        row.label(text="Camera Backgrounds")
        row.scale_x = 1.5
        row.prop(props, "display_camerabgtools_in_properties", text="", icon="VIEW_CAMERA")

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

#         if "UAS_StampInfo_Settings" not in context.scene or context.scene["UAS_StampInfo_Settings"] is None:
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
    UAS_ShotManager_About,
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
