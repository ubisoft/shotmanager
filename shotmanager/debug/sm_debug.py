import os

import bpy

from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import (
    IntVectorProperty,
    StringProperty,
    PointerProperty,
)


# ------------------------------------------------------------------------#
#                                debug Panel                              #
# ------------------------------------------------------------------------#
class UAS_PT_Shot_Manager_Debug(Panel):
    bl_idname = "UAS_PT_shot_manager_debug"
    bl_label = "Shot Manager Debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SM Debug"
    #  bl_options      = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        #     row.prop(scene.UAS_StampInfo_Settings, "debugMode")

        row = layout.row(align=True)
        row.separator(factor=3)
        # if not props.isRenderRootPathValid():
        #     row.alert = True
        row.prop(context.window_manager.UAS_vse_render, "inputOverMediaPath")
        row.alert = False
        row.operator("uasvse.openfilebrowser", text="", icon="FILEBROWSER", emboss=True).pathProp = "inputOverMediaPath"
        row.separator()

        row = layout.row(align=True)
        row.prop(context.window_manager.UAS_vse_render, "inputOverResolution")

        #    row.operator ( "uas_shot_manager.render_openexplorer", text="", icon='FILEBROWSER').path = props.renderRootPath
        layout.separator()

        row = layout.row(align=True)
        row.separator(factor=3)
        # if not props.isRenderRootPathValid():
        #     row.alert = True
        row.prop(context.window_manager.UAS_vse_render, "inputBGMediaPath")
        row.alert = False
        row.operator("uasvse.openfilebrowser", text="", icon="FILEBROWSER", emboss=True).pathProp = "inputBGMediaPath"
        row.separator()
        row = layout.row(align=True)
        row.prop(context.window_manager.UAS_vse_render, "inputBGResolution")

        row = layout.row(align=True)
        row.prop(context.window_manager.UAS_vse_render, "inputAudioMediaPath")
        row.operator(
            "uasvse.openfilebrowser", text="", icon="FILEBROWSER", emboss=True
        ).pathProp = "inputAudioMediaPath"
        row.separator()

        layout.separator()
        row = layout.row()

        row.label(text="Render:")
        #     row.prop(scene.UAS_StampInfo_Settings, "debug_DrawTextLines")
        # #    row.prop(scene.UAS_StampInfo_Settings, "offsetToCenterHNorm")

        #     row = layout.row()
        row.operator("vse.compositevideoinvse", text="Composite in VSE", emboss=True)
        # row.prop ( context.window_manager, "UAS_shot_manager_shots_play_mode",

        #     row = layout.row()
        #     row.operator("debug.lauchrrsrender", emboss=True)

        #     if not utils_render.isRenderPathValid(context.scene):
        #         row = layout.row()
        #         row.alert = True
        #         row.label( text = "Invalid render path")

        #     row = layout.row()
        #     row.operator("debug.createcomponodes", emboss=True)
        #     row.operator("debug.clearcomponodes", emboss=True)

        layout.separator()
        row = layout.row()
        row.label(text="Import Sound from XML:")
        # row.operator("uasvse.openfilebrowser", text="", icon="FILEBROWSER", emboss=True).pathProp = "inputBGMediaPath"
        row.operator("uasshotmanager.importsoundotio")

        layout.separator()
        row = layout.row()
        row.label(text="Scripts:")
        row = layout.row()
        row.operator("uas_utils.run_script", text="API First Steps").path = "//../api/api_first_steps.py"
        row = layout.row()
        row.operator("uas_utils.run_script", text="API Otio").path = "//../api/api_otio_samples.py"
        row = layout.row()
        row.operator("uas_utils.run_script", text="API RRS").path = "//../api/api_rrs_samples.py"


class UAS_VSETruc(Operator):
    bl_idname = "vse.truc"
    bl_label = "fff"
    bl_description = ""

    def execute(self, context):
        """UAS_VSETruc"""
        print("")

        return {"FINISHED"}


_classes = (UAS_PT_Shot_Manager_Debug,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

