import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty

from ..config import config


class UAS_ShotManager_AddonPrefs(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package
    bl_idname = "shotmanager"

    ##################
    # general ###
    ##################

    new_shot_duration: IntProperty(
        min=0, default=50,
    )

    ##################
    # add new shot ###
    ##################

    def _get_addShot_start(self):
        val = self.get("addShot_start", 25)
        return val

    # *** behavior here must match the one of start and end of shot properties ***
    def _set_addShot_start(self, value):
        self["addShot_start"] = value
        # increase end value if start is superior to end
        # if self.addShot_start > self.addShot_end:
        #     self["addShot_end"] = self.addShot_start

        # prevent start to go above end (more user error proof)
        if self.addShot_start > self.addShot_end:
            self["addShot_start"] = self.addShot_end

    addShot_start: IntProperty(
        name="Add Shot Start UI Only", soft_min=0, get=_get_addShot_start, set=_set_addShot_start, default=25,
    )

    def _get_addShot_end(self):
        val = self.get("addShot_end", 30)
        return val

    # *** behavior here must match the one of start and end of shot properties ***
    def _set_addShot_end(self, value):
        self["addShot_end"] = value
        # reduce start value if end is lowr than start
        # if self.addShot_start > self.addShot_end:
        #    self["addShot_start"] = self.addShot_end

        # prevent end to go below start (more user error proof)
        if self.addShot_start > self.addShot_end:
            self["addShot_end"] = self.addShot_start

    addShot_end: IntProperty(
        name="Add Shot End UI Only", soft_min=0, get=_get_addShot_end, set=_set_addShot_end, default=50,
    )

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons["shotmanager"].preferences

        box = layout.box()
        box.use_property_decorate = False
        col = box.column()
        col.use_property_split = True
        col.prop(prefs, "new_shot_duration", text="Default Shot Length")

        layout.label(
            text="Temporary preference values (for dialogs for instance) are only visible when global variable uasDebug is True."
        )

        if config.uasDebug:
            layout.label(text="Add New Shot Dialog:")
            box = layout.box()
            col = box.column(align=False)
            col.prop(self, "addShot_start")
            col.prop(self, "addShot_end")


_classes = (UAS_ShotManager_AddonPrefs,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

