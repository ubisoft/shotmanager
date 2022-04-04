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
Settings panel for the Interactive Shots Stack overlay tool
"""

import bpy
from bpy.types import Operator
from bpy.types import Menu


def draw_settings(context, layout):
    """Used in Shot Manager Feature Toggles panel"""
    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences
    # layout = self.layout

    leftCol = layout.column()

    # empty spacer column
    row = leftCol.row()
    col = row.column()
    col.scale_x = 0.25
    col.label(text=" ")
    col = row.column(align=True)

    col.prop(prefs, "display_intShStack_toolbar")

    col.prop(props, "interactShotsStack_displayDisabledShots", text="Display Disabled Shots")

    col.prop(
        props,
        "interactShotsStack_displayInCompactMode",
        text="Compact Shots Display (= decrease visual stack height)",
    )
    # return {"FINISHED"}


# def draw_settings_in_menu(self, context):
#     """Used in Shot Manager Feature Toggles panel
#     """
#     props = context.scene.UAS_shot_manager_props
#     prefs = context.preferences.addons["shotmanager"].preferences
#     layout = self.layout

#     layout.alert = True
#     # activeindrow = layout.row(align=True)
#     # activeindrow.scale_x = 0.4
#     subactiveindrow = layout.row(align=False)
#     subactiveindrow.prop(
#         context.window_manager, "UAS_shot_manager_identify_dopesheets", text="", toggle=True, icon="WORDWRAP_ON",
#     )
#     targdoperow = subactiveindrow.row(align=False)
#     expected_target_area_ind = props.getTargetViewportIndex(context, only_valid=False)
#     target_area_ind = props.getTargetViewportIndex(context, only_valid=True)
#     # print(f"display area targ: expected_target_area_ind:{expected_target_area_ind}, targ:{target_area_ind}")
#     targdoperow.alert = target_area_ind < expected_target_area_ind
#     targdoperow.prop(props, "target_viewport_index", text="Target Dopesheet Editor: ")


# class UAS_ShotManager_OT_InteractShotsStackSettings(Operator):
#     bl_idname = "uas_shot_manager.interact_shots_stack_settings"
#     bl_label = "Interactive Shots Stack Settings"
#     bl_description = "Display Interactive Shots Stack tool Settings"
#     bl_options = {"INTERNAL"}

#     def invoke(self, context, event):
#         # return context.window_manager.invoke_props_dialog(self, width=360)
#         # dialog box with no OK button
#         context.window_manager.popup_menu(draw_settings_in_menu)
#         return {"FINISHED"}

#     # def draw(self, context):
#     #     layout = self.layout
#     #     draw_settings_in_menu(context, layout)

#     # def execute(self, context):
#     #     return {"FINISHED"}


class UAS_ShotManager_OT_InteractShotsStackSettingsWind(Operator):
    bl_idname = "uas_shot_manager.interact_shots_stack_settings_wind"
    bl_label = "Interactive Shots Stack Settings"
    bl_description = "Display Interactive Shots Stack tool Settings"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        # return context.window_manager.invoke_props_dialog(self, width=360)
        return context.window_manager.invoke_popup(self, width=250)
        # # dialog box with no OK button
        # context.window_manager.popup_menu(draw_settings_in_menu)
        # return {"FINISHED"}

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences
        layout = self.layout

        # targetrow.separator(factor=1.0)

        #######################
        # target dopesheet
        #######################
        targetrow = layout.row(align=True)
        # activeindrow.scale_x = 0.4
        targetrow.separator(factor=4)

        split = targetrow.split(factor=0.6)
        split.label(text="Target Dopesheet Editor")

        targetrow = split.row(align=True)
        targetrow.prop(
            context.window_manager,
            "UAS_shot_manager_identify_dopesheets",
            text="",
            toggle=True,
            icon="WORDWRAP_ON",
        )

        targdoperow = targetrow.row(align=True)
        expected_target_area_ind = props.getTargetDopesheetIndex(context, only_valid=False)
        target_area_ind = props.getTargetDopesheetIndex(context, only_valid=True)
        # print(f"display area targ: expected_target_area_ind:{expected_target_area_ind}, targ:{target_area_ind}")
        targdoperow.alert = target_area_ind < expected_target_area_ind
        targdoperow.prop(props, "interactShotsStack_target_dopesheet_index", text="")

        #######################
        # seq timeline
        #######################

        targetrow = layout.row(align=True)
        targetrow.operator(
            "uas_shot_manager.toggle_seq_timeline_with_overlay_tools",
            text="",
            icon="SEQ_STRIP_DUPLICATE",
            depress=prefs.toggle_overlays_turnOn_sequenceTimeline,
        )
        targetrow.separator()
        targetrow.label(text="Sequence Timeline (in Viewport)")

    def execute(self, context):
        return {"FINISHED"}


# def Interact_Shots_Stack_Settings(message="", title="Message Box", icon="INFO"):
#     """
#     # #Shows a message box with a specific message
#     # ShowMessageBox("This is a message")

#     # #Shows a message box with a message and custom title
#     # ShowMessageBox("This is a message", "This is a custom title")

#     # #Shows a message box with a message, custom title, and a specific icon
#     # ShowMessageBox("This is a message", "This is a custom title", 'ERROR')

#     Icon can be "INFO" (default), "WARNING", "ERROR"
#     """

#     # else use return context.window_manager.invoke_props_dialog(self, width=400) in a invoke function
#     def draw(self, context):
#         layout = self.layout
#         draw_settings_in_menu(layout)

#     bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


# # class INTERACSHOTSSTACK_MT_SettingsMenu(Menu):
# #     bl_idname = "UAS_MT_Shot_Manager_Interact_Shots_Stack_Settings_Menu"
# #     bl_label = "Settings"

# #     def draw(self, context):
# #         props = context.scene.UAS_shot_manager_props
# #         prefs = context.preferences.addons["shotmanager"].preferences

# #         layout = self.layout

# #         # # # layout.prop(prefs, "display_intShStack_toolbar")

# #         # # ### layout.prop(props, "interactShotsStack_displayDisabledShots", text="Display Disabled Shots")
# #         # # # disabledshotsIcon = "CHECKBOX_HLT" if props.interactShotsStack_displayDisabledShots else "CHECKBOX_DEHLT"
# #         # # # layout.operator(
# #         # # #     "uas_shot_manager.display_disabledshots_in_overlays",
# #         # # #     icon=disabledshotsIcon,
# #         # # #     depress=props.interactShotsStack_displayDisabledShots,
# #         # # # )

# #         # # # layout.prop(
# #         # # #     props,
# #         # # #     "interactShotsStack_displayInCompactMode",
# #         # # #     text="Compact Shots Display (= decrease visual stack height)",
# #         # # # )

# #         # activeindrow = layout.row(align=True)
# #         # activeindrow.scale_x = 0.4
# #         subactiveindrow = layout.row(align=False)
# #         subactiveindrow.prop(
# #             context.window_manager, "UAS_shot_manager_identify_dopesheets", text="", toggle=True, icon="WORDWRAP_ON",
# #         )
# #         targdoperow = subactiveindrow.row(align=False)
# #         expected_target_area_ind = props.getTargetViewportIndex(context, only_valid=False)
# #         target_area_ind = props.getTargetViewportIndex(context, only_valid=True)
# #         # print(f"display area targ: expected_target_area_ind:{expected_target_area_ind}, targ:{target_area_ind}")
# #         targdoperow.alert = target_area_ind < expected_target_area_ind
# #         targdoperow.prop(props, "target_viewport_index", text="Target Dopesheet Editor: ")


_classes = (
    # UAS_ShotManager_OT_InteractShotsStackSettings,
    UAS_ShotManager_OT_InteractShotsStackSettingsWind,
    # INTERACSHOTSSTACK_MT_SettingsMenu,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
