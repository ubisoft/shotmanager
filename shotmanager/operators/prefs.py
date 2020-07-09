import bpy
from bpy.types import Panel, Operator

from ..utils import utils

#############
# Preferences
#############


class UAS_PT_ShotManagerPrefPanel(Panel):
    bl_label = "Preferences"
    bl_idname = "UAS_PT_Shot_Manager_Pref"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

    # shots preferences
    # row = layout.row()
    # row.label ( text = "Shots:" )
    # box = layout.box()
    # col = box.column()
    # col.use_property_split = True
    # col.prop ( context.scene.UAS_shot_manager_props, "display_camera_in_shotlist",text = "Display Camera in Shot List" )
    # col.prop ( context.scene.UAS_shot_manager_props, "new_shot_duration", text = "Default Shot Length" )
    # col.prop ( context.scene.UAS_shot_manager_props, "new_shot_prefix", text = "Default Shot Prefix" )

    # timeline preferences
    # row = layout.row()
    # row.label ( text = "Timeline:" )
    # box = layout.box()
    # col = box.column()
    # col.use_property_split = True
    # col.prop ( context.scene.UAS_shot_manager_props, "change_time", text = "Set Current Frame On Shot Selection" )
    # col.prop ( context.scene.UAS_shot_manager_props, "display_disabledshots_in_timeline", text = "Display Disabled Shots in Timeline" )


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


class UAS_PT_ShotManagerPref_Project(Panel):
    bl_label = "Project"
    bl_idname = "UAS_PT_Shot_Manager_Pref_Project"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager_Pref"

    def draw(self, context):
        layout = self.layout
        props = context.scene.UAS_shot_manager_props
        layout.use_property_split = True

        col = layout.column()
        col.use_property_split = True
        col.prop(props, "new_shot_duration", text="Default Shot Length")
        col.prop(props, "new_shot_prefix", text="Default Shot Prefix")

        # row = layout.row()
        # row.label(text="Handles:")
        col.prop(props, "handles", text="Handles Duration")


class UAS_ShotManager_Playbar_Prefs(Operator):
    bl_idname = "uas_shot_manager.playbar_prefs"
    bl_label = "Playbar, Timeline ad Edit Settings"
    bl_description = "Display the Playbar, Timeline ad Edit Preferences panel"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props

        layout = self.layout

        # Playbar ######
        # layout.label(text="Playbar:")
        # box = layout.box()
        # col = box.column()

        # col.use_property_split = True
        # col.separator(factor=1.7)
        # col.prop(props, "current_shot_properties_mode")
        # box.separator(factor=0.5)

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

        # Shot List ######
        layout.label(text="Shot List:")
        box = layout.box()
        col = box.column()

        col.separator(factor=0.5)
        col.use_property_split = True
        col.prop(props, "display_selectbut_in_shotlist", text="Display Camera Select Button")
        col.prop(props, "display_enabled_in_shotlist", text="Display Enabled State")
        col.prop(props, "display_getsetcurrentframe_in_shotlist", text="Display Get/Set current Frame Buttons")

        col.prop(props, "highlight_all_shot_frames", text="Highlight Framing Values When Equal to Current Time")

        col.separator(factor=1.0)
        col.prop(props, "use_camera_color", text="Use Camera Color for Shots ")

        col.separator(factor=1.0)
        col.prop(props, "change_time", text="Set Current Frame To Shot Start When Current Shot Is Changed")

        col.use_property_split = True
        col.separator(factor=1.7)
        col.prop(props, "current_shot_properties_mode")
        box.separator(factor=0.5)

        # Shot infos displayed in viewport ######
        layout.separator(factor=1)
        layout.label(text="Shot Info Displayed in 3D Viewport:")
        box = layout.box()
        col = box.column()

        col.use_property_split = True
        col.prop(props, "display_shotname_in_3dviewport", text="Display Shot name in 3D Viewport")

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

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


class UAS_PT_ShotManager_Render_StampInfoProperties(Panel):
    bl_label = "Stamp Info Properties"
    bl_idname = "UAS_PT_Shot_Manager_Pref_StampInfoPrefs"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager_Pref"

    def draw_header_preset(self, context):
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

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

    def draw(self, context):
        box = self.layout.box()
        row = box.row()
        row.prop(context.scene.UAS_shot_manager_props, "useStampInfoDuringRendering")


_classes = (
    UAS_PT_ShotManagerPrefPanel,
    UAS_PT_ShotManagerPref_Project,
    UAS_PT_ShotManager_Render_StampInfoProperties,
    # UAS_PT_ShotManagerPref_General,
    UAS_ShotManager_Playbar_Prefs,
    UAS_ShotManager_Shots_Prefs,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
