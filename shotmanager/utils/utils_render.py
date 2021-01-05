import os

import bpy
from bpy.types import Operator


def isRenderPathValid(scene):
    filepath = bpy.path.abspath(scene.render.filepath)

    head, tail = os.path.split(filepath)

    filePathIsValid = os.path.exists(head)

    return filePathIsValid


class Utils_LaunchRender(Operator):
    bl_idname = "utils.launchrender"
    bl_label = "Render"
    bl_description = "Render."
    bl_options = {"INTERNAL"}

    renderMode: bpy.props.EnumProperty(
        name="Render", description="", items=(("STILL", "Still", ""), ("ANIMATION", "Animation", "")), default="STILL"
    )

    def execute(self, context):

        if "STILL" == self.renderMode:
            #     bpy.ops.render.view_show()
            #     bpy.ops.render.render(use_viewport = True)
            bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=False)
        elif "ANIMATION" == self.renderMode:

            bpy.ops.render.render("INVOKE_DEFAULT", animation=True)

            # en bg, ne s'arrete pas
            # bpy.ops.render.render(animation = True)

            # bpy.ops.render.opengl ( animation = True )

        return {"FINISHED"}


_classes = (Utils_LaunchRender,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
