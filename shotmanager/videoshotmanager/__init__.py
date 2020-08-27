import bpy

from .operators import tracks
from .operators import prefs
from .operators import vsm_tools
from .properties import vsm_props

# from .ui.vsm_ui import UAS_PT_VideoShotManager
from .ui import vsm_ui


# classes = (
#     ,
# )


def register():
    print("       - Registering Video Shot Manager Package")
    # for cls in classes:
    #     bpy.utils.register_class(cls)

    prefs.register()
    vsm_props.register()
    tracks.register()
    vsm_tools.register()
    vsm_ui.register()


def unregister():
    vsm_ui.unregister()
    vsm_tools.unregister()
    tracks.unregister()
    vsm_props.unregister()
    prefs.unregister()

    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)
