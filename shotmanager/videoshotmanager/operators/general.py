import bpy
from bpy.types import Panel, Operator, Menu

from shotmanager.config import config


class UAS_VideoShotManager_SelectedToActive(Operator):
    bl_idname = "uas_shot_manager.selected_to_active"
    bl_label = "Selected to Active"
    bl_description = "Set the first selected clip of a VSE as the active clip"
    bl_options = {"INTERNAL"}

    # @classmethod
    # def poll(cls, context):
    #     props = context.scene.UAS_shot_manager_props
    #     val = len(props.getTakes()) and len(props.get_shots())
    #     return val

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props

        return {"FINISHED"}

    # def execute(self, context):
    #     scene = context.scene
    #     props = scene.UAS_shot_manager_props
    #     return {"FINISHED"}


_classes = (UAS_VideoShotManager_SelectedToActive,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
