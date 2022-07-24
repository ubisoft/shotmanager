# GPLv3 License
#
# Copyright (C) 2022 Ubisoft
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
UI utilities specific to StampInfo
"""


import bpy
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty


# TODO: Cleaning
# Dev note: This function has to be here for the moment cause it is passed
# in stampinfo code to a call to uas_sm_stamp_info.querybox
def reset_all_properties():
    from shotmanager import stampinfo

    print("reset_all_properties")
    stampinfo.stampInfo_resetProperties()


class UAS_SMStampInfo_OT_Querybox(Operator):
    """Display a query dialog box

    A message can be drawn on several lines when containing the separator \n
    """

    bl_idname = "uas_sm_stamp_info.querybox"
    bl_label = "Please confirm:"
    bl_description = "..."
    bl_options = {"INTERNAL"}

    descriptionText: StringProperty(default="")
    width: IntProperty(default=400)
    message: StringProperty(default="Do you confirm the operation?")
    function_name: StringProperty(default="")

    @classmethod
    def description(self, context, properties):
        return properties.descriptionText

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=self.width)

    def draw(self, context):

        messages = self.message.split("\n")

        layout = self.layout
        layout.separator(factor=1)

        for s in messages:
            layout.label(text=s)

        # row = layout.row()
        # row.separator(factor=2)
        # row.label(text=self.message)

        layout.separator()

    def execute(self, context):
        eval(self.function_name + "()")
        # try:
        #     eval(self.function_name + "()")
        # except Exception:
        #     print(f"*** Function {self.function_name} not found ***")

        return {"FINISHED"}


####################################################################


_classes = (UAS_SMStampInfo_OT_Querybox,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
