# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Shot Manager debug ui panel
"""


import bpy

from bpy.types import Panel
from ..config import config
from ..utils import utils

# ------------------------------------------------------------------------#
#                                debug Panel                              #
# ------------------------------------------------------------------------#


class UAS_PT_Shot_Manager_Debug(Panel):
    bl_idname = "UAS_PT_shot_manager_debug"
    bl_label = "Shot Manager - Debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng - Debug"
    #  bl_options      = {'DEFAULT_CLOSED'}

    def __init__(self):
        pass

    @classmethod
    def poll(self, context):
        prefs = context.preferences.addons["shotmanager"].preferences
        # return True
        return config.devDebug and prefs.displaySMDebugPanel

    def draw(self, context):
        layout = self.layout

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

        row.label(text="Add-ons:")
        iconExplorer = config.icons_col["General_Explorer_32"]
        # https://blender.stackexchange.com/questions/64129/get-blender-scripts-path
        # x = bpy.utils.script_path_user()
        # bpy.utils.script_paths() returns the list of script folders
        filePath = utils.getAddonsFolder()
        row.operator(
            "uas_shot_manager.open_explorer", text="Open add-ons Folder", icon_value=iconExplorer.icon_id
        ).path = filePath

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
        row = layout.row()
        row.operator("uas.debug_print_text_color")

        layout.separator()
        row = layout.row()
        row.operator("uas_debug.timeline_modal_rect")

        layout.separator()


_classes = (UAS_PT_Shot_Manager_Debug,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
