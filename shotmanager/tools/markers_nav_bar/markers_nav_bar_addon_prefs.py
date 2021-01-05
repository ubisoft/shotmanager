import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty


class UAS_markers_nav_bar_addon_prefs(AddonPreferences):
    """
        Use this to get these prefs:
        prefs = context.preferences.addons["shotmanager"].preferences
    """

    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package
    bl_idname = "shotmanager"

    ##################
    # markers ###
    ##################

    mnavbar_use_filter: BoolProperty(
        name="Filter Markers", default=False,
    )

    mnavbar_filter_text: StringProperty(
        name="Filter Text", default="",
    )


_classes = (UAS_markers_nav_bar_addon_prefs,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

