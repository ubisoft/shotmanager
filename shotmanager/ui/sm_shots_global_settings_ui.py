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
Shot global properties
"""

import bpy
from bpy.types import Panel

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_PT_ShotManager_ShotsGlobalSettings(Panel):
    bl_label = "Shots Global Control"  # "Current Shot Properties" # keep the space !!
    bl_idname = "UAS_PT_Shot_Manager_Shots_GlobalSettings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager"

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        val = (
            (props.display_camerabgtools_in_properties or props.display_greasepencil_in_properties)
            and len(props.getTakes())
            and len(props.get_shots())
        )
        val = val and not props.dontRefreshUI()
        return val

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        layout = self.layout
        box = layout.box()
        box.prop(props.shotsGlobalSettings, "alsoApplyToDisabledShots")

        # Camera background images
        ######################

        if props.display_camerabgtools_in_properties:

            # box.label(text="Camera Background Images:")

            subBox = box.box()
            subBox.use_property_decorate = False

            row = subBox.row()
            # row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            grid_flow.label(text="Camera BG Images:")
            grid_flow.operator("uas_shots_settings.use_background", text="Turn On").useBackground = True
            grid_flow.operator("uas_shots_settings.use_background", text="Turn Off").useBackground = False
            grid_flow.prop(props.shotsGlobalSettings, "backgroundAlpha", text="Alpha")
            c = row.column()
            c.operator("uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE")
            #  row.separator(factor=0.5)  # prevents stange look when panel is narrow

            if config.devDebug:
                row = subBox.row()
                row.separator(factor=1.0)
                c = row.column()
                c.enabled = False
                c.prop(props.shotsGlobalSettings, "proxyRenderSize")

            row = subBox.row()
            # row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            grid_flow.label(text="Camera BG Sound:")
            grid_flow.operator("uas_shots_settings.use_background_sound", text="Turn On").useBackgroundSound = True
            grid_flow.operator("uas_shots_settings.use_background_sound", text="Turn Off").useBackgroundSound = False
            grid_flow.prop(props.shotsGlobalSettings, "backgroundVolume", text="Volume")
            # row.separator(factor=0.5)  # prevents stange look when panel is narrow
            c.separator(factor=0.5)  # prevents stange look when panel is narrow

            # c = row.column()
            # grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            # grid_flow.prop(props.shotsGlobalSettings, "proxyRenderSize")

            # grid_flow.operator("uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE", emboss=True)

        #  row.separator(factor=0.5)  # prevents stange look when panel is narrow

        # Shot grease pencil
        ######################

        if props.display_greasepencil_in_properties:

            # box.label(text="Camera Background Images:")

            subBox = box.box()
            subBox.use_property_decorate = False

            row = subBox.row()
            # row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            grid_flow.label(text="Grease Pencil:")
            grid_flow.operator("uas_shots_settings.use_greasepencil", text="Turn On").useGreasepencil = True
            grid_flow.operator("uas_shots_settings.use_greasepencil", text="Turn Off").useGreasepencil = False
            grid_flow.prop(props.shotsGlobalSettings, "greasepencilAlpha", text="Alpha")
            c = row.column()
            c.operator("uas_shot_manager.remove_grease_pencil", text="", icon="PANEL_CLOSE")

            #  row.separator(factor=0.5)  # prevents stange look when panel is narrow


classes = (UAS_PT_ShotManager_ShotsGlobalSettings,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

