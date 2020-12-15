import bpy
from bpy.types import Panel, Operator, Menu

from ...config import config

#############
# Preferences
#############


class UAS_MT_VideoShotManager_Prefs_MainMenu(Menu):
    bl_idname = "UAS_MT_Video_Shot_Manager_prefs_mainmenu"
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


class UAS_VideoShotManager_General_Prefs(Operator):
    bl_idname = "uas_video_shot_manager.general_prefs"
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
        col = box.column()
        col.use_property_split = True
        # col.use_property_decorate = False

        col.prop(prefs, "new_shot_duration", text="Default Shot Length")

        layout.separator()
        if props.use_project_settings:
            row = layout.row()
            row.alert = True
            row.label(text="Overriden by Project Settings:")
        else:
            # layout.label(text="Others")
            pass
        box = layout.box()
        box.enabled = not props.use_project_settings
        col = box.column()
        col.use_property_split = True
        col.prop(props, "new_shot_prefix", text="Default Shot Prefix")

        # row = layout.row()
        # row.label(text="Handles:")
        col.prop(props, "render_shot_prefix")
        col.prop(props, "handles", text="Handles Duration")

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


_classes = (
    UAS_MT_VideoShotManager_Prefs_MainMenu,
    UAS_VideoShotManager_General_Prefs,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
