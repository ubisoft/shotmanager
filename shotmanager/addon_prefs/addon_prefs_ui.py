import bpy

from ..config import config


##################################################################################
# Draw
##################################################################################
def draw_shotmanager_addon_prefs(self, context):
    layout = self.layout
    prefs = context.preferences.addons["shotmanager"].preferences

    box = layout.box()
    box.use_property_decorate = False
    col = box.column()
    col.use_property_split = True
    col.prop(prefs, "new_shot_duration", text="Default Shot Length")
    #    col.prop(prefs, "useLockCameraView", text="Use Lock Camera View")

    layout.label(text="Rendering:")
    box = layout.box()
    row = box.row()
    row.separator(factor=1)
    row.prop(prefs, "separatedRenderPanel")

    layout.label(
        text="Temporary preference values (for dialogs for instance) are only visible when global variable uasDebug is True."
    )

    if config.uasDebug:
        layout.label(text="Add New Shot Dialog:")
        box = layout.box()
        col = box.column(align=False)
        col.prop(self, "addShot_start")
        col.prop(self, "addShot_end")

