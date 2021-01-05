import bpy

from bpy.types import Panel, Operator
from bpy.props import StringProperty


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

    def __init__(self):
        pass

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
        # row.operator("uasshotmanager.importsoundotio")

        layout.separator()
        row = layout.row()
        row.label(text="Scripts:")
        row = layout.row()
        row.operator("uas_utils.run_script", text="API First Steps").path = "//../api/api_first_steps.py"
        row = layout.row()
        row.operator("uas_utils.run_script", text="API Otio").path = "//../api/api_otio_samples.py"
        row = layout.row()
        row.operator("uas_utils.run_script", text="API RRS").path = "//../api/api_rrs_samples.py"

        layout.separator()
        row = layout.row()
        row.operator("uas.motiontrackingtab", text="Open Motion Tracking")

        layout.separator()
        row = layout.row()
        row.operator("uas.debug_runfunction", text="parseOtioFile").functionName = "parseOtioFile"

        layout.separator()
        row = layout.row()
        row.operator("uas_utils.run_script", text="Parse XML").path = "//../debug/debug_parse_xml.py"

        layout.separator()


class UAS_Debug_RunFunction(Operator):
    bl_idname = "uas.debug_runfunction"
    bl_label = "fff"
    bl_description = ""

    functionName: StringProperty()

    def execute(self, context):
        print("\n----------------------------------------------------")
        print("\nUAS_Debug_RunFunction: ", self.functionName)
        print("\n")

        if "parseOtioFile" == self.functionName:
            from ..otio.otio_wrapper import parseOtioFile
            from ..otio.imports import getSequenceListFromOtio

            otioFile = (
                r"Z:\EvalSofts\Blender\DevPython_Data\UAS_ShotManager_Data\ImportEDLPremiere\ImportEDLPremiere.xml"
            )
            otioFile = r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere.xml"
            #  otioFile = r"Z:\_UAS_Dev\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere.xml"
            # getSequenceListFromOtio(otioFile)
            # parseOtioFile(otioFile)

        return {"FINISHED"}


class UAS_MotionTrackingTab(Operator):
    bl_idname = "uas.motiontrackingtab"
    bl_label = "fff"
    bl_description = ""

    def execute(self, context):
        """UAS_VSETruc"""
        print(" Open VSE")
        #    getSceneVSE(bpy.context.scene.name)
        # getSceneMotionTracking(bpy.context.scene.name)

        previousType = bpy.context.area.ui_type
        bpy.context.area.ui_type = "SEQUENCE_EDITOR"

        bpy.context.object.data.background_images[0].clip.use_proxy = True
        bpy.context.object.data.background_images[0].clip.proxy.build_50 = True

        bpy.context.object.data.background_images[0].clip_user.proxy_render_size = "PROXY_50"

        for area in bpy.context.screen.areas:
            if area.type == "SEQUENCE_EDITOR":
                ctx = bpy.context.copy()
                # ctx = {"area": area}
                ctx["area"] = area
                # bpy.ops.clip.rebuild_proxy("EXEC_AREA")
                bpy.ops.sequencer.rebuild_proxy(ctx)
                break

        # bpy.context.area.ui_type = "CLIP_EDITOR"
        # # bpy.context.object.data.background_images[0].clip.proxy
        # # ctx = bpy.context.copy()
        # # ctx["area"] = bpy.context.area
        # bpy.ops.clip.rebuild_proxy()

        bpy.context.area.ui_type = previousType

        # bpy.context.object.data.proxy_render_size = 'PROXY_25'

        return {"FINISHED"}


class UAS_VSETruc(Operator):
    bl_idname = "vse.truc"
    bl_label = "fff"
    bl_description = ""

    def execute(self, context):
        """UAS_VSETruc"""
        print("")

        return {"FINISHED"}


_classes = (
    UAS_PT_Shot_Manager_Debug,
    UAS_MotionTrackingTab,
    UAS_Debug_RunFunction,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

