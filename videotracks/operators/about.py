import bpy
from bpy.types import Operator

from ..utils import utils


class UAS_ShotManager_OT_About(Operator):
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
        try:
            import opentimelineio as otio

            otioVersion = otio.__version__
            row.label(text="V." + otioVersion)
        except Exception as e:
            row.label(text="Module not found")

        row = box.row()
        row.separator()
        row.label(text="- UAS Stamp Info")
        if props.isStampInfoAvailable():
            versionStr = utils.addonVersion("UAS_StampInfo")
            row.label(text="V." + versionStr[0])
        else:
            row.label(text="Add-on not found")

        box.separator()

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


_classes = (UAS_ShotManager_OT_About,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
