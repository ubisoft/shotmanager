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

from ..config import config
from ..ui.dependencies_ui import drawDependencies


##################################################################################
# Draw
##################################################################################
def draw_shotmanager_addon_prefs(self, context):
    layout = self.layout
    # prefs = context.preferences.addons["shotmanager"].preferences
    splitFactor = 0.3

    # Settings
    ###############
    box = layout.box()
    box.use_property_decorate = False
    box.label(text="Settings:")

    #    col.prop(self, "useLockCameraView", text="Use Lock Camera View")

    split = box.split(factor=splitFactor)
    rowLeft = split.row()
    rowLeft.alignment = "RIGHT"
    rowLeft.label(text="Default Shot Duration")
    rowRight = split.row()
    rowRight.prop(self, "new_shot_duration", text="Frames")

    # General UI
    ###############
    box = layout.box()
    uiSplitFactor = 0.15

    # column component here is technicaly not necessary but reduces the space between lines
    col = box.column()
    col.label(text="UI:")

    split = col.split(factor=uiSplitFactor)
    rowLeft = split.row()
    rowRight = split.row()
    rowRight.prop(self, "separatedRenderPanel", text="Make Render Panel a Separated Tab in the Viewport N-Panel")

    split = col.split(factor=uiSplitFactor)
    rowLeft = split.row()
    rowRight = split.row()
    rowRight.prop(self, "display_frame_range_tool", text="Display Frame Range Tool in the Timeline Editor")

    # Dependencies
    ###############
    drawDependencies(context, layout)

    # Dev and debug
    ###############
    box = layout.box()

    split = box.split(factor=splitFactor)
    rowLeft = split.row()
    rowLeft.label(text="Development and Debug:")
    rowRight = split.row()

    if config.devDebug:
        strDebug = " *** Debug Mode is On ***"
        rowRight.alignment = "RIGHT"
        rowRight.alert = True
        rowRight.label(text=strDebug)

    split = box.split(factor=splitFactor)
    rowLeft = split.row()
    rowLeft.alignment = "RIGHT"
    rowLeft.label(text="Debug Mode")
    rowRight = split.row()
    if config.devDebug:
        rowRight.alert = True
        rowRight.operator("uas_shot_manager.enable_debug", text="Turn Off").enable_debug = False
    else:
        rowRight.operator("uas_shot_manager.enable_debug", text="Turn On").enable_debug = True

    if config.devDebug:
        box.separator(factor=0.2)
        split = box.split(factor=splitFactor)
        rowLeft = split.row()
        rowLeft.alignment = "RIGHT"
        rowRight = split.row()
        rowRight.prop(self, "displaySMDebugPanel")

    # Debug info and properties
    ###############

    if config.devDebug:
        box = layout.box()
        row = box.row()
        row.label(text="Debug Infos:")

        col = box.column()
        col.scale_y = 0.7
        col.label(text="Temporary preference values (for dialogs for instance) are")
        col.label(text="only visible when global variable devDebug is True.")

        if config.devDebug:
            split = box.split(factor=splitFactor)
            rowLeft = split.row()
            rowLeft.alignment = "RIGHT"
            rowLeft.label(text="Add New Shot Dialog")
            rowRight = split.row()
            rowRight.prop(self, "addShot_start")
            rowRight.prop(self, "addShot_end")
