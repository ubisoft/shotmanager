import logging

_logger = logging.getLogger(__name__)

import bpy
from bpy.types import PointerProperty


from .rendering_props import UAS_ShotManager_RenderGlobalContext, UAS_ShotManager_RenderSettings
from . import rendering_operators

# from . import rendering_ui


_classes = (
    UAS_ShotManager_RenderGlobalContext,
    UAS_ShotManager_RenderSettings,
)


def register():
    print("       - Registering Rendering Package")

    for cls in _classes:
        bpy.utils.register_class(cls)

    rendering_operators.register()
    # rendering_ui.register()    # done in shotmanager.__init__ in order to display the panel in the right order


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

    # rendering_ui.unregister()   # done in shotmanager.__init__ in order to display the panel in the right order
    rendering_operators.unregister()
