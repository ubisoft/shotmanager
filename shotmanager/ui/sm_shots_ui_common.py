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
Common UI parts for the shots in the shots list component
"""


from shotmanager.config import config

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


#####################################################################
# Draw functions
#####################################################################


def drawStoryboardRow(layout, props, item, index):
    row = layout.row(align=True)
    row.scale_x = 1.1

    gp = item.getGreasePencilObject("STORYBOARD")
    if gp is None:
        icon = config.icons_col["ShotManager_CamGPNoShot_32"]
        row.operator("uas_shot_manager.greasepencilitem", text="", icon_value=icon.icon_id).index = index
    else:
        # if gp == context.active_object and context.active_object.mode == "PAINT_GPENCIL":
        if gp.mode == "PAINT_GPENCIL":
            icon = "GREASEPENCIL"
            row.alert = True
            row.operator("uas_shot_manager.greasepencilitem", text="", icon=icon).index = index
        else:
            if "STORYBOARD" == item.shotType:
                icon = config.icons_col["ShotManager_CamGPStb_32"]
            else:
                icon = config.icons_col["ShotManager_CamGPShot_32"]
            row.operator("uas_shot_manager.greasepencilitem", text="", icon_value=icon.icon_id).index = index
    row.scale_x = 0.9


def drawNotesRow(layout, props, item, index):
    row = layout.row(align=True)
    row.scale_x = 1.0

    if item.hasNotes():
        icon = config.icons_col["ShotManager_NotesData_32"]
        row.operator("uas_shot_manager.shots_shownotes", text="", icon_value=icon.icon_id).index = index
    else:
        icon = config.icons_col["ShotManager_NotesNoData_32"]
        row.operator("uas_shot_manager.shots_shownotes", text="", icon_value=icon.icon_id).index = index
        # emptyIcon = config.icons_col["General_Empty_32"]
        # row.operator(
        #     "uas_shot_manager.shots_shownotes", text="", icon_value=emptyIcon.icon_id
        # ).index = index
    row.scale_x = 1.0


#####################################################################
# Functions
#####################################################################


def drawShotName(layout, props, item):
    row = layout.row(align=True)
    row.scale_x = 1.0
    if props.display_enabled_in_shotlist:
        row.prop(item, "enabled", text="")
        row.separator(factor=0.9)
    row.scale_x = 0.8
    row.label(text=item.name)
