import bpy
from bpy.props import BoolProperty
import bpy.utils.previews

from .operators import tracks
from .operators import prefs
from .properties import vsm_props

# from .ui.vsm_ui import UAS_PT_VideoShotManager
from .ui import vsm_ui


# classes = (
#     ,
# )


def register():
    print("       - Registering Video Shot Manager Package\n")
    # for cls in classes:
    #     bpy.utils.register_class(cls)

    vsm_props.register()
    tracks.register()
    prefs.register()
    vsm_ui.register()


def unregister():
    vsm_ui.unregister()
    prefs.unregister()
    tracks.unregister()
    vsm_props.unregister()

    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)
