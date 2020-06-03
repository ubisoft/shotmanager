import bpy
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, FloatVectorProperty


class UAS_ShotsSettings_UseBackground(Operator):
    bl_idname = "uas_shots_settings.use_background"
    bl_label = "Use Background"
    bl_description = "Use Background for every shot"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        # for each cam... turn on and off
        # if cam has bg media...
        # faire un press button

        return {"FINISHED"}


_classes = (UAS_ShotsSettings_UseBackground,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
