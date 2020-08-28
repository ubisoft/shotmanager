import bpy

from . import viewport_hud
from . import timeline_draw

# from .ui import vsm_ui


# classes = (
#     ,
# )


def register():
    print("       - Registering Viewport 3D Package")
    # for cls in classes:
    #     bpy.utils.register_class(cls)

    viewport_hud.register()
    timeline_draw.register ( )


def unregister():
    viewport_hud.unregister()
    timeline_draw.unregister()

    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)
