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
To do: module description here.
"""

from shotmanager.config import config

from bpy.types import Panel


class UAS_PT_ShotManager_RRS_Debug(Panel):
    bl_label = "ShotManager_RRS_Debug"
    bl_idname = "UAS_PT_Shot_Manager_rrs_debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        displayPanel = not props.dontRefreshUI() and config.devDebug
        return displayPanel

    def draw(self, context):
        props = config.getAddonProps(context.scene)

        layout = self.layout
        row = layout.row(align=False)
        row.label(text="RRS Specific (debug temp):")
        row = layout.row(align=False)
        row.prop(props, "rrs_useRenderRoot")
        row.prop(props, "rrs_fileListOnly")
        row = layout.row(align=False)
        row.prop(props, "rrs_rerenderExistingShotVideos")
        row.prop(props, "rrs_renderAlsoDisabled")
        row = layout.row(align=False)
        row.alert = True
        row.operator("uas_shot_manager.initialize_rrs_project", text="Debug - RRS Initialyze")
        row.operator("uas_shot_manager.lauch_rrs_render", text="Debug - RRS Publish").prodFilePath = (
            "c:\\tmpRezo\\" + context.scene.name + "\\"
        )
        row.alert = False

        row = layout.row()
        row.operator("uas_shot_manager.fix_entities_parent")
        # if config.devDebug:
        #     row = layout.row(align=False)
        #     # row.enabled = False
        #     row.prop(context.window_manager, "UAS_shot_manager_progressbar", text="Rendering...")

        layout.separator(factor=1)
