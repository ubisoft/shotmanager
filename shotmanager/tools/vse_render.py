import os

import bpy

from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import (
    IntProperty,
    IntVectorProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    PointerProperty,
    FloatVectorProperty,
)


# ------------------------------------------------------------------------#
#                                VSE tool Panel                             #
# ------------------------------------------------------------------------#
class UAS_PT_VSERender(Panel):
    bl_idname = "UAS_PT_VSE_Render"
    bl_label = "VSE Render"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS VSE"
    #  bl_options      = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

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

        layout.separator()
        row = layout.row()

        row.label(text="Render:")
        #     row.prop(scene.UAS_StampInfo_Settings, "debug_DrawTextLines")
        # #    row.prop(scene.UAS_StampInfo_Settings, "offsetToCenterHNorm")

        #     row = layout.row()
        row.operator("vse.compositevideoinvse", emboss=True)
        # row.prop ( context.window_manager, "UAS_shot_manager_handler_toggle",

    #     row = layout.row()
    #     row.operator("debug.lauchrrsrender", emboss=True)

    #     if not utils_render.isRenderPathValid(context.scene):
    #         row = layout.row()
    #         row.alert = True
    #         row.label( text = "Invalid render path")

    #     row = layout.row()
    #     row.operator("debug.createcomponodes", emboss=True)
    #     row.operator("debug.clearcomponodes", emboss=True)


class UAS_VSETruc(Operator):
    bl_idname = "vse.truc"
    bl_label = "fff"
    bl_description = ""

    def execute(self, context):
        """UAS_VSETruc"""
        print("")

        return {"FINISHED"}


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_VSE_OpenFileBrowser(Operator):  # from bpy_extras.io_utils import ImportHelper
    bl_idname = "uasvse.openfilebrowser"
    bl_label = "Open"
    bl_description = (
        "Open the file browser to define the image to stamp\n"
        "Relative path must be set directly in the text field and must start with ''//''"
    )

    pathProp: StringProperty()

    filepath: StringProperty(subtype="FILE_PATH")

    filter_glob: StringProperty(default="*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.tga;*.mp4", options={"HIDDEN"})

    def execute(self, context):
        """Use the selected file as a stamped logo"""
        filename, extension = os.path.splitext(self.filepath)
        #   print('Selected file:', self.filepath)
        #   print('File name:', filename)
        #   print('File extension:', extension)
        context.window_manager.UAS_vse_render[self.pathProp] = self.filepath

        return {"FINISHED"}

    def invoke(self, context, event):  # See comments at end  [1]

        if self.pathProp in context.window_manager.UAS_vse_render:
            self.filepath = context.window_manager.UAS_vse_render[self.pathProp]
        else:
            self.filepath = ""
        # https://docs.blender.org/api/current/bpy.types.WindowManager.html
        #    self.directory = bpy.context.scene.UAS_shot_manager_props.renderRootPath
        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}


class UAS_compositeVideoInVSE(Operator):
    bl_idname = "vse.compositevideoinvse"
    bl_label = "CreateSceneAndAddClips"
    bl_description = ""

    def execute(self, context):
        """UAS_VSETruc"""
        print("Op compositeVideoInVSE")
        vse_render = context.window_manager.UAS_vse_render
        scene = context.scene

        scene = context.window_manager.UAS_vse_render.compositeVideoInVSE(20, "c:\\tmp\\MyVSEOutput.mp4")

        return {"FINISHED"}


class UAS_Vse_Render(PropertyGroup):
    def get_inputOverMediaPath(self):
        val = self.get("inputOverMediaPath", "")
        return val

    def set_inputOverMediaPath(self, value):
        self["inputOverMediaPath"] = value

    inputOverMediaPath: StringProperty(
        name="Input Media Path Over", get=get_inputOverMediaPath, set=set_inputOverMediaPath, default=""
    )

    inputOverResolution: IntVectorProperty(size=2, default=(1280, 720))

    def get_inputBGMediaPath(self):
        val = self.get("inputBGMediaPath", "")
        return val

    def set_inputBGMediaPath(self, value):
        self["inputBGMediaPath"] = value

    inputBGMediaPath: StringProperty(
        name="Input Media Path BG", get=get_inputBGMediaPath, set=set_inputBGMediaPath, default=""
    )

    inputBGResolution: IntVectorProperty(size=2, default=(1280, 960))

    def getMediaType(self, filePath):
        """ Return the type of media according to the file extension
            Eg: 'IMAGE', 'SOUND', 'MOVIE'
        """
        mediaType = "UNKNOWN"

        from pathlib import Path

        mediaExt = Path(filePath.lower()).suffix
        print("  getMediaType: mediaExt:" + mediaExt)
        if ".mp4" == mediaExt or ".avi" == mediaExt or ".mov" == mediaExt or ".mkv" == mediaExt:
            mediaType = "MOVIE"
        elif (
            ".jpg" == mediaExt
            or ".jpeg" == mediaExt
            or ".png" == mediaExt
            or ".tga" == mediaExt
            or ".tif" == mediaExt
            or ".tiff" == mediaExt
        ):
            mediaType = "IMAGE"
        elif ".mp3" == mediaExt or ".wav" == mediaExt:
            mediaType = "SOUND"

        return mediaType

    def compositeVideoInVSE(self, num_frames, output_filepath):
        # Add new scene
        scene = bpy.data.scenes.new(name="Tmp_VSE_RenderScene")
        # Make "My New Scene" the active one
        bpy.context.window.scene = scene

        # créer des clips
        if not scene.sequence_editor:
            scene.sequence_editor_create()

        # https://docs.blender.org/api/blender_python_api_2_77_0/bpy.types.Sequences.html
        # Path ( renderPath ).parent.mkdir ( parents = True, exist_ok = True )

        ### add BG
        scene.render.resolution_x = self.inputBGResolution[0]
        scene.render.resolution_y = self.inputBGResolution[1]
        scene.frame_start = 1
        scene.frame_end = num_frames
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.filepath = output_filepath
        # scene.render.ffmpeg.constant_rate_factor = video_quality

        def _createNewClip(mediaPath, channelInd, atFrame):
            newClip = None
            mediaType = self.getMediaType(mediaPath)
            if "MOVIE" == mediaType:
                newClip = scene.sequence_editor.sequences.new_movie("myVideo", mediaPath, channelInd, atFrame)
            if "IMAGE" == mediaType:
                newClip = scene.sequence_editor.sequences.new_image("myVideo", mediaPath, channelInd, atFrame)
            if "SOUND" == mediaType:
                newClip = scene.sequence_editor.sequences.new_movie("myVideo", mediaPath, channelInd, atFrame)

            return newClip

        bgClip = _createNewClip(self.inputBGMediaPath, 1, 1)
        overClip = _createNewClip(self.inputOverMediaPath, 2, 1)

        overClip.use_crop = True
        overClip.crop.min_x = -1 * int((self.inputBGResolution[0] - self.inputOverResolution[0]) / 2)
        overClip.crop.max_x = overClip.crop.min_x
        overClip.crop.min_y = -1 * int((self.inputBGResolution[1] - self.inputOverResolution[1]) / 2)
        overClip.crop.max_y = overClip.crop.min_y

        overClip.blend_type = "OVER_DROP"

        # bpy.context.scene.sequence_editor.sequences
        # get res of video: bpy.context.scene.sequence_editor.sequences[1].elements[0].orig_width
        # ne marche que sur vidéos

        bpy.ops.render.opengl(animation=True, sequencer=True)

        #    bpy.ops.scene.delete()

        return new_scene


_classes = (UAS_PT_VSERender, UAS_Vse_Render, UAS_compositeVideoInVSE, UAS_VSE_OpenFileBrowser)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.UAS_vse_render = PointerProperty(type=UAS_Vse_Render)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.UAS_vse_render
