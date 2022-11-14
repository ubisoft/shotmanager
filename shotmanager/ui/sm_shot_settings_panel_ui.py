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
Shot settings UI
"""

import bpy
from bpy.types import Panel
from bpy.props import StringProperty

from shotmanager.utils import utils

from shotmanager.ui.sm_shot_properties_ui import draw_shot_properties, draw_shots_global_properties

# from shotmanager.features.soundBG import soundBG_ui as sBG
from shotmanager.features.cameraBG.cameraBG_ui import draw_cameraBG_shot_properties, draw_cameraBG_global_properties
from shotmanager.features.storyboard.storyboard_ui import (
    draw_greasepencil_shot_properties,
    draw_greasepencil_global_properties,
)

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


##################
# shot properties
##################


def drawShotPropertiesToolbar(layout, context, shot):
    props = config.getAddonProps(context.scene)
    row = layout.row(align=False)

    cameraIsValid = shot.isCameraValid()
    propsCurrentLayout = props.getCurrentLayout()

    # if propsCurrentLayout.display_notes_in_properties or propsCurrentLayout.display_cameraBG_in_properties or propsCurrentLayout.display_storyboard_in_properties:
    if True:
        # leftrow = row.row(align=False)
        # leftrow.alignment = "LEFT"

        # propertiesModeStr = "Current Shot:  "
        # if "SELECTED" == scene.UAS_shot_manager_props.current_shot_properties_mode:
        #     propertiesModeStr = "Selected Shot:  "
        # leftrow.label(text=propertiesModeStr)

        buttonsrow = row.row(align=True)
        buttonsrow.alignment = "LEFT"
        buttonsrow.separator()

        subrow = buttonsrow.row()
        subrow.alert = not cameraIsValid
        subrow.scale_x = 0.9
        panelIcon = "TRIA_DOWN" if props.expand_shot_properties else "TRIA_RIGHT"
        subrow.prop(props, "expand_shot_properties", toggle=True, icon=panelIcon)

        if propsCurrentLayout.display_cameraBG_in_properties:
            subrow = buttonsrow.row()
            subrow.scale_x = 0.9
            panelIcon = "TRIA_DOWN" if props.expand_cameraBG_properties else "TRIA_RIGHT"
            subrow.prop(props, "expand_cameraBG_properties", toggle=True, icon=panelIcon)
        if propsCurrentLayout.display_storyboard_in_properties:
            subrow = buttonsrow.row()
            subrow.scale_x = 0.9
            panelIcon = "TRIA_DOWN" if props.expand_storyboard_properties else "TRIA_RIGHT"
            subrow.prop(props, "expand_storyboard_properties", text="Storyboard", toggle=True, icon=panelIcon)
        if propsCurrentLayout.display_notes_in_properties:
            subrow = buttonsrow.row()
            subrow.scale_x = 0.9
            panelIcon = "TRIA_DOWN" if props.expand_notes_properties else "TRIA_RIGHT"
            subrow.prop(props, "expand_notes_properties", toggle=True, icon=panelIcon)

        buttonsrow.separator()
    else:
        propertiesModeStr = (
            "Selected Shot Notes:" if "SELECTED" == props.current_shot_properties_mode else "Current Shot Notes:"
        )
        row.label(text=propertiesModeStr)


class UAS_PT_ShotManager_ShotProperties(Panel):
    bl_label = " "  # "Current Shot Properties" # keep the space !! # Note: text is drawn in gray, not white
    bl_idname = "UAS_PT_Shot_Manager_Shot_Prefs"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng"
    bl_options = {"DEFAULT_CLOSED", "HIDE_HEADER"}
    bl_parent_id = "UAS_PT_Shot_Manager"

    tmpBGPath: StringProperty()

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShotByIndex(props.selected_shot_index)
        val = len(props.getTakes()) and shot is not None
        val = val and not props.dontRefreshUI()
        val = val and (
            props.expand_shot_properties
            or props.expand_notes_properties
            or props.expand_cameraBG_properties
            or props.expand_storyboard_properties
        )
        return val

    def draw_header(self, context):
        props = config.getAddonProps(context.scene)
        layout = self.layout
        # layout.emboss = "NONE"
        propertiesModeStr = (
            "Selected Shot Notes:" if "SELECTED" == props.current_shot_properties_mode else "Current Shot Notes:"
        )
        layout.label(text=propertiesModeStr)

    def draw_header_preset(self, context):
        scene = context.scene
        layout = self.layout
        props = config.getAddonProps(scene)
        shot = None
        # if shotPropertiesModeIsCurrent is true then the displayed shot properties are taken from the CURRENT shot, else from the SELECTED one
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShotByIndex(props.selected_shot_index)

        cameraIsValid = shot.isCameraValid()
        itemHasWarnings = not cameraIsValid

        if itemHasWarnings:
            row = layout.row()
            layout.alignment = "RIGHT"
            row.alignment = "RIGHT"
            row.alert = True
            if shot.camera is None:
                row.label(text="*** Camera not defined ! ***")
            else:
                row.label(text="*** Referenced camera not in scene ! ***")

        versionStr = utils.addonVersion("Video Tracks")
        row = layout.row()
        row.enabled = versionStr is not None
        row.operator(
            "uas_shot_manager.go_to_video_tracks", text="", icon="SEQ_STRIP_DUPLICATE"
        ).vseSceneName = "SM_CheckSequence"

    def draw(self, context):
        scene = context.scene
        prefs = config.getAddonPrefs()
        props = config.getAddonProps(scene)
        # iconExplorer = config.icons_col["General_Explorer_32"]

        #  shotPropertiesModeIsCurrent = not ('SELECTED' == props.current_shot_properties_mode)

        shot = None
        # if shotPropertiesModeIsCurrent is true then the displayed shot properties are taken from the CURRENT shot, else from the SELECTED one
        if "SELECTED" == props.current_shot_properties_mode:
            shot = props.getShotByIndex(props.selected_shot_index)
            propertiesModeStr = "Selected "
        else:
            shot = props.getCurrentShot()
            propertiesModeStr = "Current "

        if shot is None:
            return

        layout = self.layout
        propsCurrentLayout = props.getCurrentLayout()

        ######################
        # Properties
        ######################

        if (
            not (
                propsCurrentLayout.display_notes_in_properties
                or propsCurrentLayout.display_cameraBG_in_properties
                or propsCurrentLayout.display_storyboard_in_properties
            )
            or props.expand_shot_properties
        ):
            draw_shot_properties(layout, context, shot)
            draw_shots_global_properties(layout, context)

        ######################
        # Notes
        ######################
        if propsCurrentLayout.display_notes_in_properties and props.expand_notes_properties:
            panelIcon = "TRIA_DOWN" if prefs.shot_notes_expanded else "TRIA_RIGHT"

            box = layout.box()
            box.use_property_decorate = False

            row = box.row()
            # row.prop(prefs, "shot_notes_expanded", text="", icon=panelIcon, emboss=False)
            # row.separator(factor=1.0)
            c = row.column()
            # grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            subrow = c.row()
            # subrow.label(text="Shot Notes:")

            propertiesModeStr = (
                "Selected Shot Notes:" if "SELECTED" == props.current_shot_properties_mode else "Current Shot Notes:"
            )
            subrow.label(text=propertiesModeStr)

            subrow.prop(props, "display_notes_in_shotlist", text="")
            #    subrow.separator(factor=0.5)

            # if prefs.shot_notes_expanded:
            row = box.row()
            row.separator(factor=1.0)
            mainCol = row.column()
            mainCol.scale_y = 0.95
            mainCol.prop(shot, "note01", text="")
            mainCol.prop(shot, "note02", text="")
            mainCol.prop(shot, "note03", text="")
            row.separator(factor=1.0)
            box.separator(factor=0.1)

        ######################
        # Camera background images
        ######################
        if propsCurrentLayout.display_cameraBG_in_properties and props.expand_cameraBG_properties:
            draw_cameraBG_shot_properties(layout, context, shot)
            draw_cameraBG_global_properties(layout, context)

        ######################
        # Grease pencil
        ######################
        if propsCurrentLayout.display_storyboard_in_properties and props.expand_storyboard_properties:
            draw_greasepencil_shot_properties(layout, context, shot)
            draw_greasepencil_global_properties(layout, context)


classes = (UAS_PT_ShotManager_ShotProperties,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
